"""Tests for DIVE-TOGAF resource pools."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pools.models import ToolType, ToolDomain, SeedCategory, ExemplarFamily
from src.pools.tool_pool_builder import build_tool_pool
from src.pools.seed_pool_builder import build_seed_pool
from src.pools.exemplar_pool_builder import build_exemplar_pool


def test_tool_pool_size():
    """Tool pool should have a substantial number of tools."""
    tools = build_tool_pool()
    assert len(tools) >= 100, f"Expected >= 100 tools, got {len(tools)}"
    print(f"  PASS: Tool pool has {len(tools)} tools (>= 100)")


def test_tool_pool_types():
    """Tool pool should have both retrieval and processing tools."""
    tools = build_tool_pool()
    retrieval = [t for t in tools if t.tool_type == ToolType.RETRIEVAL]
    processing = [t for t in tools if t.tool_type == ToolType.PROCESSING]
    assert len(retrieval) > 0, "No retrieval tools found"
    assert len(processing) > 0, "No processing tools found"
    assert len(retrieval) > len(processing), "Expected more retrieval than processing tools"
    print(f"  PASS: {len(retrieval)} retrieval, {len(processing)} processing tools")


def test_tool_pool_domains():
    """Tool pool should cover all domains."""
    tools = build_tool_pool()
    domains = {t.domain for t in tools}
    expected = {ToolDomain.ADM, ToolDomain.ARCHIMATE, ToolDomain.REPOSITORY, ToolDomain.GOVERNANCE,
                ToolDomain.GENERAL, ToolDomain.ANALYSIS, ToolDomain.TECHNOLOGY_RADAR,
                ToolDomain.SECURITY, ToolDomain.DATA_ARCHITECTURE, ToolDomain.INTEGRATION,
                ToolDomain.CLOUD_INFRASTRUCTURE}
    assert domains == expected, f"Missing domains: {expected - domains}"
    print(f"  PASS: All {len(expected)} domains covered: {[d.value for d in sorted(domains, key=lambda x: x.value)]}")


def test_tool_pool_unique_ids():
    """All tool IDs should be unique."""
    tools = build_tool_pool()
    ids = [t.id for t in tools]
    assert len(ids) == len(set(ids)), f"Duplicate IDs found: {len(ids)} total, {len(set(ids))} unique"
    print(f"  PASS: All {len(ids)} tool IDs are unique")


def test_tool_pool_has_parameters():
    """Every tool should have at least one parameter."""
    tools = build_tool_pool()
    for t in tools:
        assert len(t.parameters) > 0, f"Tool {t.id} has no parameters"
    print(f"  PASS: All {len(tools)} tools have parameters")


def test_tool_pool_has_return_schema():
    """Every tool should have a return schema."""
    tools = build_tool_pool()
    for t in tools:
        assert t.return_schema, f"Tool {t.id} has no return schema"
    print(f"  PASS: All {len(tools)} tools have return schemas")


def test_tool_pool_serialization():
    """Tools should serialize to valid JSON."""
    tools = build_tool_pool()
    for t in tools:
        d = t.to_dict()
        json_str = json.dumps(d)
        parsed = json.loads(json_str)
        assert parsed["id"] == t.id
    print(f"  PASS: All {len(tools)} tools serialize correctly")


def test_seed_pool_size():
    """Seed pool should have a substantial number of seeds."""
    seeds = build_seed_pool()
    assert len(seeds) >= 200, f"Expected >= 200 seeds, got {len(seeds)}"
    print(f"  PASS: Seed pool has {len(seeds)} seeds (>= 200)")


def test_seed_pool_categories():
    """Seed pool should cover all categories."""
    seeds = build_seed_pool()
    categories = {s.category for s in seeds}
    expected = set(SeedCategory)
    assert categories == expected, f"Missing categories: {expected - categories}"
    print(f"  PASS: All {len(expected)} seed categories covered")


def test_seed_pool_unique_ids():
    """All seed IDs should be unique."""
    seeds = build_seed_pool()
    ids = [s.id for s in seeds]
    assert len(ids) == len(set(ids)), f"Duplicate seed IDs found"
    print(f"  PASS: All {len(ids)} seed IDs are unique")


def test_seed_pool_serialization():
    """Seeds should serialize to valid JSON."""
    seeds = build_seed_pool()
    for s in seeds:
        d = s.to_dict()
        json_str = json.dumps(d, ensure_ascii=False)
        parsed = json.loads(json_str)
        assert parsed["id"] == s.id
    print(f"  PASS: All {len(seeds)} seeds serialize correctly")


def test_exemplar_pool_size():
    """Exemplar pool should have a substantial number of exemplars."""
    exemplars = build_exemplar_pool()
    assert len(exemplars) >= 100, f"Expected >= 100 exemplars, got {len(exemplars)}"
    print(f"  PASS: Exemplar pool has {len(exemplars)} exemplars (>= 100)")


def test_exemplar_pool_families():
    """Exemplar pool should cover multiple families."""
    exemplars = build_exemplar_pool()
    families = {e.family for e in exemplars}
    assert len(families) >= 5, f"Expected >= 5 families, got {len(families)}"
    print(f"  PASS: {len(families)} exemplar families covered")


def test_exemplar_pool_unique_ids():
    """All exemplar IDs should be unique."""
    exemplars = build_exemplar_pool()
    ids = [e.id for e in exemplars]
    assert len(ids) == len(set(ids)), f"Duplicate exemplar IDs found"
    print(f"  PASS: All {len(ids)} exemplar IDs are unique")


def test_exemplar_pool_complexity_range():
    """Exemplar complexity should span a range."""
    exemplars = build_exemplar_pool()
    complexities = {e.complexity for e in exemplars}
    assert min(complexities) <= 2, f"No low-complexity exemplars"
    assert max(complexities) >= 4, f"No high-complexity exemplars"
    print(f"  PASS: Complexity range {min(complexities)}-{max(complexities)}")


def test_exemplar_pool_serialization():
    """Exemplars should serialize to valid JSON."""
    exemplars = build_exemplar_pool()
    for e in exemplars:
        d = e.to_dict()
        json_str = json.dumps(d)
        parsed = json.loads(json_str)
        assert parsed["id"] == e.id
    print(f"  PASS: All {len(exemplars)} exemplars serialize correctly")


def test_pools_decoupled():
    """The three pools should be independently buildable."""
    tools = build_tool_pool()
    seeds = build_seed_pool()
    exemplars = build_exemplar_pool()
    assert len(tools) > 0
    assert len(seeds) > 0
    assert len(exemplars) > 0
    print(f"  PASS: All three pools build independently ({len(tools)}T, {len(seeds)}S, {len(exemplars)}E)")


def run_all_tests():
    """Run all pool validation tests."""
    tests = [
        test_tool_pool_size,
        test_tool_pool_types,
        test_tool_pool_domains,
        test_tool_pool_unique_ids,
        test_tool_pool_has_parameters,
        test_tool_pool_has_return_schema,
        test_tool_pool_serialization,
        test_seed_pool_size,
        test_seed_pool_categories,
        test_seed_pool_unique_ids,
        test_seed_pool_serialization,
        test_exemplar_pool_size,
        test_exemplar_pool_families,
        test_exemplar_pool_unique_ids,
        test_exemplar_pool_complexity_range,
        test_exemplar_pool_serialization,
        test_pools_decoupled,
    ]

    print("=" * 60)
    print("DIVE-TOGAF Pool Validation Tests")
    print("=" * 60)

    passed = 0
    failed = 0
    for test in tests:
        try:
            print(f"\n{test.__name__}:")
            test()
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed, {len(tests)} total")
    print(f"{'=' * 60}")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
