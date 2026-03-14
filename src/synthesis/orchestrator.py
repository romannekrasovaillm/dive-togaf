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

from src.pools.sampler import PoolSampler, SynthesisConfig

from .collector import CollectorAgent, EvidenceSet
from .generator import TaskGenerator, SynthesizedTask
from .kimi_client import KimiClient
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
    ):
        self._kimi = kimi_client
        self._sampler = sampler
        self._k = k_iterations
        self._max_tool_rounds = max_tool_rounds_per_iter
        self._generator = TaskGenerator(kimi_client)

    def run_single(
        self,
        config: SynthesisConfig | None = None,
        seed_category: str | None = None,
    ) -> SynthesisResult:
        """Run one complete synthesis cycle.

        Args:
            config: Pre-sampled config. If None, samples a new one.
            seed_category: Optional filter for seed category when sampling.

        Returns:
            SynthesisResult with all evidence and generated tasks.
        """
        start = time.time()

        # Sample configuration
        if config is None:
            config = self._sampler.sample_config(seed_category=seed_category)

        logger.info(
            "=== Synthesis cycle: %s | Seed: %s | Tools: %d | Exemplars: %d ===",
            config.config_id, config.seed.get("name", "?"),
            len(config.tools), len(config.exemplars),
        )

        # Build tool executor
        seed_context = f"{config.seed.get('name', '')}: {config.seed.get('description', '')}"
        executor = ToolExecutor(
            tool_pool=config.tools,
            kimi_client=self._kimi,
            seed_context=seed_context,
        )

        # Build OpenAI-format tool schemas
        tool_schemas = executor.get_openai_tool_schemas(config.tools)

        # Create collector
        collector = CollectorAgent(
            kimi_client=self._kimi,
            tool_executor=executor,
            tool_schemas=tool_schemas,
        )

        # Iterative evidence collection + task generation
        evidence = EvidenceSet()
        tasks: list[SynthesizedTask] = []
        prev_query: str | None = None

        for k in range(1, self._k + 1):
            logger.info("--- Iteration K=%d ---", k)

            # Collect evidence
            evidence, reasoning = collector.collect_iteration(
                seed=config.seed,
                iteration=k,
                evidence=evidence,
                prev_query=prev_query,
                max_tool_rounds=self._max_tool_rounds,
            )

            # Generate task from accumulated evidence
            task = self._generator.generate(
                seed=config.seed,
                evidence=evidence,
                exemplars=config.exemplars,
                iteration=k,
            )
            tasks.append(task)
            prev_query = task.question

            logger.info(
                "K=%d: evidence=%d items, task complexity=%d, grounding=%.2f, Q='%s'",
                k, len(evidence), task.complexity, task.grounding_score, task.question[:100],
            )

        elapsed = time.time() - start

        logger.info(
            "Cycle done: %d tool calls (%d live, %d simulated) in %.1fs",
            executor.call_count, executor.live_count, executor.simulated_count, elapsed,
        )

        return SynthesisResult(
            config_id=config.config_id,
            seed=config.seed,
            evidence=evidence.to_list(),
            tasks=[t.to_dict() for t in tasks],
            tool_call_count=executor.call_count,
            live_tool_count=executor.live_count,
            simulated_tool_count=executor.simulated_count,
            iterations=self._k,
            elapsed_seconds=round(elapsed, 2),
        )

    def run_batch(
        self,
        batch_size: int,
        seed: int | None = None,
        seed_category: str | None = None,
        writer: DatasetWriter | None = None,
    ) -> list[SynthesisResult]:
        """Run a batch of synthesis cycles with on-the-fly sampling.

        Each cycle samples a fresh random config from the pools instead of
        pre-generating all configs upfront. If a ``writer`` is provided,
        results are appended to disk after every cycle so intermediate
        data is never lost.

        Args:
            batch_size: Number of cycles to run.
            seed: Random seed for reproducibility.
            seed_category: Optional filter for seed category.
            writer: Optional DatasetWriter for incremental saves.

        Returns:
            List of SynthesisResult objects.
        """
        import random as _random
        rng = _random.Random(seed) if seed is not None else _random.Random()

        results = []
        for i in range(batch_size):
            logger.info("=== Batch item %d/%d ===", i + 1, batch_size)
            try:
                # Sample a fresh config on each iteration
                config = self._sampler.sample_config(
                    seed_category=seed_category,
                    rng=rng,
                )
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

        return results


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
