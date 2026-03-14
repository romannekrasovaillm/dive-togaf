#!/usr/bin/env python3
"""Build all DIVE-TOGAF resource pools."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.pools.tool_pool_builder import build_tool_pool, save_tool_pool
from src.pools.seed_pool_builder import build_seed_pool, save_seed_pool
from src.pools.exemplar_pool_builder import build_exemplar_pool, save_exemplar_pool
from src.pools.models import ToolType


def main():
    print("=" * 60)
    print("DIVE-TOGAF Resource Pool Builder")
    print("=" * 60)

    # Build Tool Pool
    path, count = save_tool_pool()
    tools = build_tool_pool()
    retrieval = sum(1 for t in tools if t.tool_type == ToolType.RETRIEVAL)
    processing = count - retrieval
    print(f"\nTool Pool: {path}")
    print(f"  Total: {count} tools")
    print(f"  Retrieval: {retrieval}")
    print(f"  Processing: {processing}")

    domains = {}
    for t in tools:
        d = t.domain.value
        domains[d] = domains.get(d, 0) + 1
    for d, n in sorted(domains.items()):
        print(f"  Domain '{d}': {n}")

    # Build Seed Pool
    path, count = save_seed_pool()
    seeds = build_seed_pool()
    print(f"\nSeed Pool: {path}")
    print(f"  Total: {count} seeds")
    categories = {}
    for s in seeds:
        c = s.category.value
        categories[c] = categories.get(c, 0) + 1
    for c, n in sorted(categories.items()):
        print(f"  Category '{c}': {n}")

    # Build Exemplar Pool
    path, count = save_exemplar_pool()
    exemplars = build_exemplar_pool()
    print(f"\nExemplar Pool: {path}")
    print(f"  Total: {count} exemplars")
    families = {}
    for e in exemplars:
        f = e.family.value
        families[f] = families.get(f, 0) + 1
    for f, n in sorted(families.items()):
        print(f"  Family '{f}': {n}")

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Total resources: {len(tools)} tools + {len(seeds)} seeds + {len(exemplars)} exemplars")
    print(f"Combinatorial space: {len(tools)} × {len(seeds)} × C({len(exemplars)},4) configurations")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
