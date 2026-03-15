#!/usr/bin/env python3
"""DIVE-TOGAF Phase 2: Evidence-Driven Synthesis — Main Entry Point.

Usage:
    python run_synthesis.py [options]                # Stage 1: synthesize D_task
    python run_synthesis.py --teacher [options]      # Stage 1 + Stage 2: D_task → D_sft
    python run_synthesis.py --teacher-only [options] # Stage 2 only: existing D_task → D_sft

Stage 1 (Synthesis):
    Collector gathers evidence → Generator produces (Q, A) pairs → dataset.jsonl

Stage 2 (Teacher rollout, DIVE §3.4):
    For each (Q, A, T) in D_task:
        τ = teacher.rollout(Q, T)    # agent trajectory with tool calls
        if verify(τ.final_answer, A): # rejection sampling
            D_sft.append(τ)          # sft_dataset.jsonl

Environment:
    KIMI_API_KEY or MOONSHOT_API_KEY — Moonshot/Kimi API key (required)
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.pools.sampler import PoolSampler
from src.synthesis.kimi_client import KimiClient
from src.synthesis.orchestrator import (
    DatasetWriter,
    SFTTrajectoryGenerator,
    SynthesisOrchestrator,
    SynthesisResult,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="DIVE-TOGAF Phase 2: Evidence-Driven Synthesis",
    )
    parser.add_argument("--batch-size", type=int, default=3,
                        help="Number of synthesis cycles (default: 3)")
    parser.add_argument("--k-iterations", type=int, default=3,
                        help="Deepening iterations per cycle (default: 3)")
    parser.add_argument("--max-tool-rounds", type=int, default=4,
                        help="Max tool-call rounds per iteration (default: 4)")
    parser.add_argument("--seed-category", type=str, default=None,
                        help="Filter seeds by category")
    parser.add_argument("--random-seed", type=int, default=None,
                        help="Random seed for reproducibility")
    parser.add_argument("--output-dir", type=str, default="output",
                        help="Output directory (default: output/)")
    parser.add_argument("--model", type=str, default="kimi-k2.5",
                        help="Kimi model name (default: kimi-k2.5)")
    parser.add_argument("--temperature", type=float, default=0.6,
                        help="LLM temperature (default: 0.6)")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable debug logging")
    parser.add_argument("--collector-thinking", action="store_true",
                        help="Enable reasoning/thinking mode for collector (disabled by default to avoid timeouts)")
    parser.add_argument("--teacher", action="store_true",
                        help="Run teacher rollout (Stage 2) after synthesis")
    parser.add_argument("--teacher-only", action="store_true",
                        help="Run teacher rollout on existing D_task (skip synthesis)")
    return parser.parse_args()


def _load_results_from_disk(full_path: Path) -> list[SynthesisResult]:
    """Load SynthesisResults from full_results.jsonl."""
    import json
    results = []
    with open(full_path, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            results.append(SynthesisResult(
                config_id=data["config_id"],
                seed=data["seed"],
                evidence=data["evidence"],
                tasks=data["tasks"],
                tool_call_count=data["tool_call_count"],
                live_tool_count=data.get("live_tool_count", 0),
                simulated_tool_count=data.get("simulated_tool_count", 0),
                iterations=data.get("iterations", 0),
                elapsed_seconds=data.get("elapsed_seconds", 0),
            ))
    return results


def main() -> None:
    args = parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    mode = "teacher-only" if args.teacher_only else "synthesis+teacher" if args.teacher else "synthesis"

    print("=" * 70)
    print("DIVE-TOGAF Phase 2: Evidence-Driven Synthesis")
    print("=" * 70)
    print(f"  Mode:            {mode}")
    print(f"  Model:           {args.model}")
    print(f"  Batch size:      {args.batch_size} cycles")
    print(f"  K iterations:    {args.k_iterations} per cycle")
    print(f"  Max tool rounds: {args.max_tool_rounds} per iteration")
    print(f"  Seed category:   {args.seed_category or 'any'}")
    print(f"  Random seed:     {args.random_seed or 'none'}")
    print(f"  Output:          {args.output_dir}/")
    print("=" * 70)

    # Initialize components
    kimi = KimiClient(
        model=args.model,
        temperature=args.temperature,
        verbose=args.verbose,
    )

    sampler = PoolSampler(
        tool_pool_path="pools/tools/tool_pool.json",
        seed_pool_path="pools/seeds/seed_pool.json",
        exemplar_pool_path="pools/exemplars/exemplar_pool.json",
    )

    stats = sampler.stats()
    print(f"\nPool stats:")
    print(f"  Tools:     {stats['tool_pool_size']}")
    print(f"  Seeds:     {stats['seed_pool_size']}")
    print(f"  Exemplars: {stats['exemplar_pool_size']}")
    print()

    output_path = Path(args.output_dir)
    results = []

    # ---- Stage 1: Synthesis (D_task) ----
    if not args.teacher_only:
        orchestrator = SynthesisOrchestrator(
            kimi_client=kimi,
            sampler=sampler,
            k_iterations=args.k_iterations,
            max_tool_rounds_per_iter=args.max_tool_rounds,
            collector_thinking=args.collector_thinking,
        )

        writer = DatasetWriter(output_dir=output_path)

        print("Stage 1: Synthesis (results saved incrementally)...")
        results = orchestrator.run_batch(
            batch_size=args.batch_size,
            seed=args.random_seed,
            seed_category=args.seed_category,
            writer=writer,
        )

        if not results:
            print("ERROR: No synthesis results produced.")
            sys.exit(1)

        summary_path = writer.write_summary(results, "summary.json")

        total_tasks = sum(len(r.tasks) for r in results)
        total_evidence = sum(len(r.evidence) for r in results)
        total_calls = sum(r.tool_call_count for r in results)
        total_live = sum(r.live_tool_count for r in results)
        total_simulated = sum(r.simulated_tool_count for r in results)
        total_time = sum(r.elapsed_seconds for r in results)
        live_rate = total_live / max(total_calls, 1)

        print()
        print("=" * 70)
        print("Stage 1 Complete: D_task")
        print("=" * 70)
        print(f"  Cycles:     {len(results)}/{args.batch_size}")
        print(f"  Tasks:      {total_tasks}")
        print(f"  Evidence:   {total_evidence}")
        print(f"  Tool calls: {total_calls} ({total_live} live, {total_simulated} sim, {live_rate:.0%} live)")
        print(f"  Time:       {total_time:.1f}s")
        print(f"  Output:     {output_path / 'dataset.jsonl'}")
        print("=" * 70)

    # ---- Stage 2: Teacher rollout (D_sft) ----
    if args.teacher or args.teacher_only:
        if not results:
            full_path = output_path / "full_results.jsonl"
            if not full_path.exists():
                print(f"ERROR: No results at {full_path}. Run synthesis first.")
                sys.exit(1)
            results = _load_results_from_disk(full_path)
            print(f"Loaded {len(results)} results from {full_path}")

        total_tasks = sum(len(r.tasks) for r in results)
        print()
        print("=" * 70)
        print(f"Stage 2: Teacher Rollout ({total_tasks} tasks)")
        print("=" * 70)

        sft_gen = SFTTrajectoryGenerator(
            kimi_client=kimi,
            sampler=sampler,
        )
        summary = sft_gen.generate_sft(results, output_path)

        print()
        print("=" * 70)
        print("Stage 2 Complete: D_sft")
        print("=" * 70)
        print(f"  Total tasks:     {summary['total_tasks']}")
        print(f"  Accepted (SFT):  {summary['accepted']}")
        print(f"  Rejected:        {summary['rejected']}")
        print(f"  Failed:          {summary['failed']}")
        print(f"  Acceptance rate: {summary['acceptance_rate']:.0%}")
        print(f"  Output:          {output_path / 'sft_dataset.jsonl'}")
        print("=" * 70)


if __name__ == "__main__":
    main()
