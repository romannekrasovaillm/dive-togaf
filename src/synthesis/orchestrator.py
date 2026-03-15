"""Synthesis Orchestrator: ties collector + generator + iterations.

Implements the full DIVE Phase 2 pipeline:
1. Sample a configuration (seed + tools + exemplars) from pools
2. For K iterations:
   a. Collector gathers evidence via tool calls
   b. Generator produces (Q, A) pairs from evidence
3. Output accumulated dataset
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import random as _random_mod

from src.pools.sampler import (
    PoolSampler, SynthesisConfig,
    count_affinity_tools, get_seed_affinity_domains, get_tool_domain_tags,
    MIN_AFFINITY_TOOLS,
)

from .collector import CollectorAgent, EvidenceSet
from .generator import TaskGenerator, SynthesizedTask
from .kimi_client import KimiClient
from .teacher import TeacherAgent, RolloutResult
from .tool_executor import ToolExecutor

logger = logging.getLogger(__name__)


@dataclass
class SynthesisResult:
    """Result of one complete synthesis cycle."""
    config_id: str
    seed: dict[str, Any]
    evidence: list[dict[str, Any]]
    tasks: list[dict[str, Any]]
    tool_call_count: int
    live_tool_count: int = 0
    simulated_tool_count: int = 0
    iterations: int = 0
    elapsed_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_id": self.config_id,
            "seed": {"id": self.seed.get("id"), "name": self.seed.get("name"), "category": self.seed.get("category")},
            "evidence_count": len(self.evidence),
            "task_count": len(self.tasks),
            "tool_call_count": self.tool_call_count,
            "live_tool_count": self.live_tool_count,
            "simulated_tool_count": self.simulated_tool_count,
            "iterations": self.iterations,
            "elapsed_seconds": self.elapsed_seconds,
            "evidence": self.evidence,
            "tasks": self.tasks,
        }


class SynthesisOrchestrator:
    """Runs the full DIVE synthesis pipeline."""

    def __init__(
        self,
        kimi_client: KimiClient,
        sampler: PoolSampler,
        k_iterations: int = 3,
        max_tool_rounds_per_iter: int = 4,
        collector_thinking: bool = False,
    ):
        self._kimi = kimi_client
        self._sampler = sampler
        self._k = k_iterations
        self._max_tool_rounds = max_tool_rounds_per_iter
        self._collector_thinking = collector_thinking
        self._generator = TaskGenerator(kimi_client)

    def run_single(
        self,
        config: SynthesisConfig | None = None,
        seed_category: str | None = None,
        dedup_early_stop_threshold: float = 0.6,
    ) -> SynthesisResult:
        """Run one complete synthesis cycle.

        Per-iteration toolset resampling: each iteration gets a fresh tool
        subset from the full pool, creating variability across K rounds
        (matching DIVE paper §3.2 — "each cycle samples a subset of 15-50
        tools from the full tool pool").

        If the dedup rate exceeds ``dedup_early_stop_threshold`` in an
        iteration (most tool calls duplicate prior evidence), remaining
        iterations are skipped — the exploration space is exhausted.

        Args:
            config: Pre-sampled config. If None, samples a new one.
            seed_category: Optional filter for seed category when sampling.
            dedup_early_stop_threshold: Skip remaining iterations if the
                fraction of duplicate tool calls exceeds this value.

        Returns:
            SynthesisResult with all evidence and generated tasks.
        """
        start = time.time()

        # Sample configuration (seed + initial tools + exemplars)
        if config is None:
            config = self._sampler.sample_config(seed_category=seed_category)

        logger.info(
            "=== Synthesis cycle: %s | Seed: %s | Tools: %d | Exemplars: %d ===",
            config.config_id, config.seed.get("name", "?"),
            len(config.tools), len(config.exemplars),
        )

        seed_context = f"{config.seed.get('name', '')}: {config.seed.get('description', '')}"
        rng = _random_mod.Random(hash(config.config_id))

        # Iterative evidence collection + task generation
        evidence = EvidenceSet()
        tasks: list[SynthesizedTask] = []
        prev_query: str | None = None
        total_calls = 0
        total_live = 0
        total_simulated = 0
        actual_iterations = 0

        for k in range(1, self._k + 1):
            logger.info("--- Iteration K=%d ---", k)

            # Resample tool subset per iteration for variability
            # Pass seed for affinity-aware resampling (Step 4)
            iter_tools = self._resample_tools(config.tools, k, rng, seed=config.seed)

            # Build fresh executor + schemas for this iteration's toolset
            executor = ToolExecutor(
                tool_pool=iter_tools,
                kimi_client=self._kimi,
                seed_context=seed_context,
            )
            tool_schemas = executor.get_openai_tool_schemas(iter_tools)

            collector = CollectorAgent(
                kimi_client=self._kimi,
                tool_executor=executor,
                tool_schemas=tool_schemas,
                use_thinking=self._collector_thinking,
            )

            # Track evidence count before/after for dedup rate
            evidence_before = len(evidence)

            evidence, reasoning = collector.collect_iteration(
                seed=config.seed,
                iteration=k,
                evidence=evidence,
                prev_query=prev_query,
                max_tool_rounds=self._max_tool_rounds,
            )

            total_calls += executor.call_count
            total_live += executor.live_count
            total_simulated += executor.simulated_count
            actual_iterations = k

            # Compute dedup rate for this iteration
            evidence_added = len(evidence) - evidence_before
            dedup_rate = 1.0 - (evidence_added / max(executor.call_count, 1))

            # Generate task from accumulated evidence
            task = self._generator.generate(
                seed=config.seed,
                evidence=evidence,
                exemplars=config.exemplars,
                iteration=k,
            )
            tasks.append(task)
            prev_query = task.question

            # Step 5: log affinity metrics alongside existing stats
            n_affinity = count_affinity_tools(iter_tools, config.seed)
            n_low_value = sum(
                1 for e in evidence.for_iteration(k)
                if isinstance(e.result, dict) and e.result.get("_low_value")
            )
            iter_tool_calls = max(executor.call_count, 1)
            low_value_rate = n_low_value / iter_tool_calls

            logger.info(
                "K=%d: evidence=%d (+%d new, %.0f%% dedup, %d low-value), "
                "tools=%d (%d affinity, %d other), "
                "complexity=%d, grounding=%.2f, Q='%s'",
                k, len(evidence), evidence_added, dedup_rate * 100, n_low_value,
                len(iter_tools), n_affinity, len(iter_tools) - n_affinity,
                task.complexity, task.grounding_score,
                task.question[:80],
            )

            # Early stop: exploration space exhausted
            if k < self._k and dedup_rate > dedup_early_stop_threshold:
                logger.warning(
                    "Early stop at K=%d: dedup rate %.0f%% > %.0f%% threshold. "
                    "Exploration space exhausted with current tool pool.",
                    k, dedup_rate * 100, dedup_early_stop_threshold * 100,
                )
                break

            # Rate limit pacing between iterations
            if k < self._k:
                time.sleep(3)

        elapsed = time.time() - start

        logger.info(
            "Cycle done: %d tool calls (%d live, %d simulated) in %d/%d iterations, %.1fs",
            total_calls, total_live, total_simulated, actual_iterations, self._k, elapsed,
        )

        return SynthesisResult(
            config_id=config.config_id,
            seed=config.seed,
            evidence=evidence.to_list(),
            tasks=[t.to_dict() for t in tasks],
            tool_call_count=total_calls,
            live_tool_count=total_live,
            simulated_tool_count=total_simulated,
            iterations=actual_iterations,
            elapsed_seconds=round(elapsed, 2),
        )

    def _resample_tools(
        self,
        base_tools: list[dict[str, Any]],
        iteration: int,
        rng: _random_mod.Random,
        seed: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Resample tool subset for a given iteration.

        Iteration 1 uses the base config tools. Subsequent iterations
        swap out ~30% of tools for fresh ones from the full pool,
        keeping retrieval/processing balance.

        Step 4: After swap, ensures at least MIN_AFFINITY_TOOLS affinity
        tools remain. If the swap would drop below the threshold,
        priority-fills from affinity candidates.
        """
        if iteration == 1:
            return base_tools

        full_pool = self._sampler.tool_pool
        if len(full_pool) <= len(base_tools):
            # Pool too small for meaningful resampling
            return base_tools

        # Keep ~70% of current tools, replace rest from pool
        keep_count = max(int(len(base_tools) * 0.7), 1)
        kept = rng.sample(base_tools, keep_count)
        kept_names = {t.get("name") for t in kept}

        # Candidates: tools from full pool not already kept
        candidates = [t for t in full_pool if t.get("name") not in kept_names]
        swap_count = min(len(base_tools) - keep_count, len(candidates))
        swapped = rng.sample(candidates, swap_count) if swap_count > 0 else []

        result = kept + swapped

        # Ensure at least one processing tool
        has_processing = any(t.get("tool_type") == "processing" for t in result)
        if not has_processing:
            proc_tools = [t for t in full_pool if t.get("tool_type") == "processing"]
            if proc_tools:
                result[-1] = rng.choice(proc_tools)

        # Step 4: Ensure minimum affinity tools after swap
        if seed is not None:
            affinity_domains = set(get_seed_affinity_domains(seed))
            result_names = {t.get("name") for t in result}

            # Count current affinity
            n_affinity = sum(
                1 for t in result
                if set(get_tool_domain_tags(t)) & affinity_domains
            )

            if n_affinity < MIN_AFFINITY_TOOLS:
                # Find affinity candidates not already in result
                affinity_candidates = [
                    t for t in full_pool
                    if t.get("name") not in result_names
                    and set(get_tool_domain_tags(t)) & affinity_domains
                ]
                needed = min(MIN_AFFINITY_TOOLS - n_affinity, len(affinity_candidates))
                if needed > 0:
                    # Replace last N non-affinity tools with affinity ones
                    fillers = rng.sample(affinity_candidates, needed)
                    non_affinity_indices = [
                        i for i, t in enumerate(result)
                        if not (set(get_tool_domain_tags(t)) & affinity_domains)
                    ]
                    for j, filler in enumerate(fillers):
                        if j < len(non_affinity_indices):
                            result[non_affinity_indices[-(j + 1)]] = filler

                    n_affinity = sum(
                        1 for t in result
                        if set(get_tool_domain_tags(t)) & affinity_domains
                    )
                    logger.info(
                        "K=%d: affinity repair — added %d affinity tools (now %d)",
                        iteration, needed, n_affinity,
                    )

        logger.info(
            "K=%d: resampled tools — kept %d, swapped %d (total %d)",
            iteration, len(kept), len(swapped), len(result),
        )
        return result

    def run_batch(
        self,
        batch_size: int,
        seed: int | None = None,
        seed_category: str | None = None,
        writer: DatasetWriter | None = None,
    ) -> list[SynthesisResult]:
        """Run a batch of synthesis cycles with seed diversity enforcement.

        Each cycle samples a fresh random config from the pools. Seeds are
        deduplicated within the batch — a seed will not be reused until all
        available seeds in the category have been exhausted, ensuring maximum
        diversity in the generated dataset.

        If a ``writer`` is provided, results are appended to disk after
        every cycle so intermediate data is never lost.

        Args:
            batch_size: Number of cycles to run.
            seed: Random seed for reproducibility.
            seed_category: Optional filter for seed category.
            writer: Optional DatasetWriter for incremental saves.

        Returns:
            List of SynthesisResult objects.
        """
        rng = _random_mod.Random(seed) if seed is not None else _random_mod.Random()

        # Build a pool of unique seeds, shuffled for randomness
        seed_candidates = self._sampler.seed_pool
        if seed_category:
            filtered = [s for s in seed_candidates if s.get("category") == seed_category]
            if filtered:
                seed_candidates = filtered

        # Create a rotating seed queue — exhausts all seeds before repeating
        seed_queue: list[dict[str, Any]] = []
        used_seed_ids: set[str] = set()

        def _next_seed() -> dict[str, Any]:
            nonlocal seed_queue
            if not seed_queue:
                # Refill and reshuffle
                seed_queue = list(seed_candidates)
                rng.shuffle(seed_queue)
                if used_seed_ids and len(seed_candidates) > 1:
                    logger.info(
                        "Seed pool exhausted (%d unique seeds used), recycling",
                        len(used_seed_ids),
                    )
            s = seed_queue.pop()
            used_seed_ids.add(s.get("id", ""))
            return s

        results = []
        for i in range(batch_size):
            logger.info("=== Batch item %d/%d ===", i + 1, batch_size)
            try:
                chosen_seed = _next_seed()
                config = self._sampler.sample_config(
                    seed_category=seed_category,
                    rng=rng,
                )
                # Override seed with our diversity-enforced choice
                config.seed = chosen_seed
                config.config_id = f"cfg_{chosen_seed['id']}_{rng.randint(10000, 99999)}"

                result = self.run_single(config=config)
                results.append(result)

                # Incremental save — data is persisted immediately
                if writer is not None:
                    writer.append_result(result)
                    logger.info(
                        "Intermediate save: %d/%d cycles written to disk",
                        len(results), batch_size,
                    )
            except Exception as e:
                logger.error("Synthesis cycle %d failed: %s", i + 1, e)
                continue

        logger.info(
            "Batch complete: %d/%d cycles, %d unique seeds used",
            len(results), batch_size, len(used_seed_ids),
        )
        return results


# =====================================================================
# SFT Trajectory Generator — separate post-synthesis stage (DIVE §3.4)
# =====================================================================

class SFTTrajectoryGenerator:
    """Generates SFT training data via teacher rollout + rejection sampling.

    Per DIVE §3.4:
        for (Q, A, T) in D_task:
            τ = teacher.rollout(Q, T)
            if verify(τ.final_answer, A):
                D_sft.append((Q, A, T, τ))

    Runs as a separate stage after synthesis. Reads D_task (dataset.jsonl),
    produces sft_dataset.jsonl with chat-format trajectories.
    """

    def __init__(
        self,
        kimi_client: KimiClient,
        sampler: PoolSampler,
        max_tool_rounds: int = 10,
    ):
        self._kimi = kimi_client
        self._sampler = sampler
        self._teacher = TeacherAgent(kimi_client, max_tool_rounds=max_tool_rounds)

    def generate_sft(
        self,
        results: list[SynthesisResult],
        output_dir: Path,
    ) -> dict[str, Any]:
        """Run teacher rollouts on D_task, filter by rejection sampling.

        For each (Q, A, T) in results:
            τ = teacher.rollout(Q, T)
            if verify(τ.final_answer, A):
                write τ to sft_dataset.jsonl

        Args:
            results: Completed synthesis results containing D_task.
            output_dir: Directory for sft_dataset.jsonl output.

        Returns:
            Summary dict with pass/fail counts.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        sft_path = output_dir / "sft_dataset.jsonl"

        total = 0
        accepted = 0
        rejected = 0
        failed = 0

        for r_idx, result in enumerate(results):
            logger.info(
                "=== Teacher rollout %d/%d: %s ===",
                r_idx + 1, len(results), result.config_id,
            )

            # Build tool executor with the same tools
            seed_context = f"{result.seed.get('name', '')}: {result.seed.get('description', '')}"
            config = self._sampler.sample_config(seed_category=result.seed.get("category"))
            executor = ToolExecutor(
                tool_pool=config.tools,
                kimi_client=self._kimi,
                seed_context=seed_context,
            )
            tool_schemas = executor.get_openai_tool_schemas(config.tools)

            for t_idx, task in enumerate(result.tasks):
                question = task.get("question", "")
                reference_answer = task.get("answer", "")
                grounding = task.get("grounding_score", 0.0)

                if not question or not reference_answer or grounding < 0.5:
                    logger.info(
                        "  Skip task %d: grounding=%.2f, q_len=%d, a_len=%d",
                        t_idx, grounding, len(question), len(reference_answer),
                    )
                    continue

                total += 1
                logger.info(
                    "  Rollout task %d/%d: Q='%s'",
                    t_idx + 1, len(result.tasks), question[:80],
                )

                try:
                    rollout_result = self._teacher.rollout(
                        question=question,
                        reference_answer=reference_answer,
                        tool_executor=executor,
                        tool_schemas=tool_schemas,
                    )

                    if rollout_result.verified:
                        # Rejection sampling passed — save SFT trajectory
                        sft_example = rollout_result.trajectory.to_sft_example()
                        sft_example["config_id"] = result.config_id
                        sft_example["task_index"] = t_idx
                        sft_example["reference_answer"] = reference_answer

                        with open(sft_path, "a", encoding="utf-8") as f:
                            f.write(json.dumps(sft_example, ensure_ascii=False) + "\n")

                        accepted += 1
                        logger.info(
                            "  ACCEPTED: %d tool calls, final_answer matches reference",
                            rollout_result.trajectory.tool_call_count,
                        )
                    else:
                        rejected += 1
                        logger.info(
                            "  REJECTED: final_answer does not match reference "
                            "(final='%s', ref='%s')",
                            rollout_result.trajectory.final_answer[:100],
                            reference_answer[:100],
                        )
                except Exception as e:
                    failed += 1
                    logger.warning("  FAILED: task %d: %s", t_idx, e)

                # Rate limit pacing
                time.sleep(2)

        # Write summary
        summary = {
            "total_tasks": total,
            "accepted": accepted,
            "rejected": rejected,
            "failed": failed,
            "acceptance_rate": round(accepted / max(total, 1), 3),
            "sft_path": str(sft_path),
        }
        summary_path = output_dir / "sft_summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info(
            "SFT generation complete: %d/%d accepted (%.0f%%), %d rejected, %d failed",
            accepted, total, accepted / max(total, 1) * 100, rejected, failed,
        )

        return summary


# =====================================================================
# Dataset Writer
# =====================================================================

class DatasetWriter:
    """Writes synthesis results to JSONL dataset files.

    Supports both batch writes and incremental appends so that
    intermediate results are persisted as each cycle completes.
    """

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._dataset_count = 0
        self._full_count = 0

    # ------ incremental (append) methods ------

    def append_result(
        self,
        result: SynthesisResult,
        dataset_filename: str = "dataset.jsonl",
        full_filename: str = "full_results.jsonl",
    ) -> int:
        """Append a single cycle's results to dataset files incrementally.

        Returns the number of task records appended.
        """
        count = 0

        # Append task records
        dataset_path = self.output_dir / dataset_filename
        with open(dataset_path, "a", encoding="utf-8") as f:
            for task in result.tasks:
                record = self._task_record(result, task)
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                count += 1

        # Append full result
        full_path = self.output_dir / full_filename
        with open(full_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")

        self._dataset_count += count
        self._full_count += 1
        logger.info(
            "Appended %d tasks (total: %d) to %s", count, self._dataset_count, dataset_path,
        )
        return count

    @staticmethod
    def _task_record(result: SynthesisResult, task: dict[str, Any]) -> dict[str, Any]:
        return {
            "config_id": result.config_id,
            "seed_id": result.seed.get("id", ""),
            "seed_name": result.seed.get("name", ""),
            "seed_category": result.seed.get("category", ""),
            "iteration": task["iteration"],
            "question": task["question"],
            "answer": task["answer"],
            "sub_questions": task["sub_questions"],
            "complexity": task["complexity"],
            "family": task["family"],
            "reasoning_trace": task["reasoning_trace"],
            "cited_evidence_ids": task.get("cited_evidence_ids", []),
            "evidence_trajectory": task.get("evidence_trajectory", []),
            "grounding_score": task.get("grounding_score", 0.0),
            "evidence_count": len(result.evidence),
            "tool_call_count": result.tool_call_count,
        }

    # ------ batch (overwrite) methods — kept for compatibility ------

    def write_results(
        self,
        results: list[SynthesisResult],
        filename: str = "dataset.jsonl",
    ) -> Path:
        """Write synthesis results as JSONL (one line per task)."""
        path = self.output_dir / filename
        count = 0

        with open(path, "w", encoding="utf-8") as f:
            for result in results:
                for task in result.tasks:
                    record = self._task_record(result, task)
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    count += 1

        logger.info("Wrote %d task records to %s", count, path)
        return path

    def write_full_results(
        self,
        results: list[SynthesisResult],
        filename: str = "full_results.jsonl",
    ) -> Path:
        """Write full synthesis results including all evidence."""
        path = self.output_dir / filename

        with open(path, "w", encoding="utf-8") as f:
            for result in results:
                f.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")

        logger.info("Wrote %d full result records to %s", len(results), path)
        return path

    def write_summary(
        self,
        results: list[SynthesisResult],
        filename: str = "summary.json",
    ) -> Path:
        """Write summary statistics."""
        path = self.output_dir / filename

        total_tasks = sum(len(r.tasks) for r in results)
        total_evidence = sum(len(r.evidence) for r in results)
        total_tool_calls = sum(r.tool_call_count for r in results)
        total_live = sum(r.live_tool_count for r in results)
        total_simulated = sum(r.simulated_tool_count for r in results)
        total_time = sum(r.elapsed_seconds for r in results)

        categories = {}
        families = {}
        complexities = {}
        grounding_scores = []
        for r in results:
            cat = r.seed.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
            for t in r.tasks:
                fam = t.get("family", "unknown")
                families[fam] = families.get(fam, 0) + 1
                cx = t.get("complexity", 0)
                complexities[cx] = complexities.get(cx, 0) + 1
                grounding_scores.append(t.get("grounding_score", 0.0))

        avg_grounding = round(sum(grounding_scores) / max(len(grounding_scores), 1), 3)
        fully_grounded = sum(1 for s in grounding_scores if s >= 0.9)

        summary = {
            "total_cycles": len(results),
            "total_tasks": total_tasks,
            "total_evidence_items": total_evidence,
            "total_tool_calls": total_tool_calls,
            "total_live_tool_calls": total_live,
            "total_simulated_tool_calls": total_simulated,
            "live_tool_rate": round(total_live / max(total_tool_calls, 1), 3),
            "total_elapsed_seconds": round(total_time, 2),
            "avg_seconds_per_cycle": round(total_time / max(len(results), 1), 2),
            "grounding": {
                "avg_grounding_score": avg_grounding,
                "fully_grounded_tasks": fully_grounded,
                "total_tasks": total_tasks,
                "grounding_rate": round(fully_grounded / max(total_tasks, 1), 3),
            },
            "seed_categories": categories,
            "task_families": families,
            "complexity_distribution": complexities,
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info("Summary: %d cycles, %d tasks, %d evidence items", len(results), total_tasks, total_evidence)
        return path
