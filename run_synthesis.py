#!/usr/bin/env python3
"""DIVE-TOGAF Phase 2: Evidence-Driven Synthesis — Main Entry Point.

Usage:
    python run_synthesis.py [options]

Environment:
    KIMI_API_KEY or MOONSHOT_API_KEY — Moonshot/Kimi API key (required)

Options:
    --batch-size N       Number of synthesis cycles to run (default: 3)
    --k-iterations K     Deepening iterations per cycle (default: 3)
    --max-tool-rounds M  Max tool-call rounds per iteration (default: 8)
    --seed-category CAT  Filter seeds by category (e.g., bian_service_domain)
    --random-seed S      Random seed for reproducibility
    --output-dir DIR     Output directory (default: output/)
    --model MODEL        Kimi model name (default: kimi-k2.5)
    --temperature T      LLM temperature (default: 0.6)
    --verbose            Enable debug logging
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.pools.sampler import PoolSampler
from src.synthesis.kimi_client import KimiClient
from src.synthesis.orchestrator import DatasetWriter, SynthesisOrchestrator


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
    parser.add_argument("--no-teacher", action="store_true",
                        help="Disable teacher rollout verification")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    print("=" * 70)
    print("DIVE-TOGAF Phase 2: Evidence-Driven Synthesis")
    print("=" * 70)
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

    orchestrator = SynthesisOrchestrator(
        kimi_client=kimi,
        sampler=sampler,
        k_iterations=args.k_iterations,
        max_tool_rounds_per_iter=args.max_tool_rounds,
        enable_teacher=not args.no_teacher,
    )

    # Prepare writer for incremental saves
    writer = DatasetWriter(output_dir=Path(args.output_dir))
    dataset_path = Path(args.output_dir) / "dataset.jsonl"
    full_path = Path(args.output_dir) / "full_results.jsonl"

    # Run synthesis batch — results saved to disk after each cycle
    print("Starting synthesis (results saved incrementally)...")
    results = orchestrator.run_batch(
        batch_size=args.batch_size,
        seed=args.random_seed,
        seed_category=args.seed_category,
        writer=writer,
    )

    if not results:
        print("ERROR: No synthesis results produced.")
        sys.exit(1)

    # Write final summary (uses all accumulated results)
    summary_path = writer.write_summary(results, "summary.json")

    # Print summary
    total_tasks = sum(len(r.tasks) for r in results)
    total_evidence = sum(len(r.evidence) for r in results)
    total_calls = sum(r.tool_call_count for r in results)
    total_live = sum(r.live_tool_count for r in results)
    total_simulated = sum(r.simulated_tool_count for r in results)
    total_time = sum(r.elapsed_seconds for r in results)
    live_rate = total_live / max(total_calls, 1)

    # Teacher verification stats
    total_teacher = sum(len(r.teacher_verifications) for r in results)
    teacher_verified = sum(
        1 for r in results for tv in r.teacher_verifications if tv.get("verified")
    )

    print()
    print("=" * 70)
    print("Synthesis Complete")
    print("=" * 70)
    print(f"  Cycles completed: {len(results)}/{args.batch_size}")
    print(f"  Tasks generated:  {total_tasks}")
    print(f"  Evidence items:   {total_evidence}")
    print(f"  Tool calls:       {total_calls} ({total_live} live, {total_simulated} simulated, {live_rate:.0%} live rate)")
    if total_teacher > 0:
        print(f"  Teacher verified: {teacher_verified}/{total_teacher} ({teacher_verified/total_teacher:.0%})")
    print(f"  Total time:       {total_time:.1f}s")
    print()
    print(f"  Dataset:          {dataset_path}")
    print(f"  Full results:     {full_path}")
    print(f"  Summary:          {summary_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
