"""Config Sampling for DIVE-TOGAF Evidence-Driven Synthesis.

Implements the decoupled sampling strategy: independently selects
a seed, a tool subset, and exemplar templates to create a unique
synthesis configuration for each iteration.

Soft-affinity sampling (Steps 1-3): guarantees at least
``MIN_AFFINITY_TOOLS`` domain-relevant tools per seed while keeping
random diversity in the remaining slots.
"""

from __future__ import annotations

import json
import logging
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Minimum number of affinity-matching tools guaranteed in every toolset.
MIN_AFFINITY_TOOLS = 3

# =====================================================================
# Step 1: Seed category → tool domain affinity map
# =====================================================================
# Each seed category maps to 1-3 tool domains that are most relevant.
# If a seed has an explicit ``affinity_domains`` field, it takes
# precedence over this map.

CATEGORY_DOMAIN_MAP: dict[str, list[str]] = {
    # TOGAF spec-grounded
    "togaf_phase":              ["adm", "governance", "repository"],
    "togaf_deliverable":        ["adm", "repository", "governance"],
    "togaf_artifact":           ["adm", "repository", "archimate"],
    "togaf_technique":          ["adm", "analysis", "governance"],
    "togaf_metamodel_entity":   ["adm", "archimate", "repository"],
    "togaf_viewpoint":          ["adm", "archimate", "governance"],
    # ArchiMate
    "archimate_element":        ["archimate", "governance", "general"],
    "archimate_relationship":   ["archimate", "analysis", "general"],
    "archimate_viewpoint":      ["archimate", "adm", "governance"],
    # Cross-cutting
    "industry_case":            ["general", "governance", "analysis"],
    "standard":                 ["governance", "repository", "general"],
    "capability":               ["general", "analysis", "repository"],
    "building_block":           ["repository", "general", "technology_radar"],
    "stakeholder":              ["repository", "governance", "adm"],
    # Cross-domain reference architectures
    "bian_service_domain":      ["general", "integration", "governance"],
    "tmforum_functional_block": ["integration", "general", "technology_radar"],
    "technology_building_block": ["technology_radar", "general", "analysis"],
    "team_topology":            ["analysis", "general", "governance"],
    # Domain-specific architecture seeds
    "security_architecture":    ["security", "governance", "general"],
    "data_architecture":        ["data_architecture", "integration", "governance"],
    "integration_architecture": ["integration", "general", "analysis"],
    "cloud_architecture":       ["cloud_infrastructure", "technology_radar", "security"],
}

# =====================================================================
# Step 2: Tool domain_tags derivation
# =====================================================================
# Each tool already has a single ``domain`` field. We expand it to a
# list of ``domain_tags`` using the tool's existing domain plus
# secondary domains inferred from the tool name prefix.

_NAME_PREFIX_DOMAINS: dict[str, list[str]] = {
    "adm_":             ["adm"],
    "archimate_":       ["archimate"],
    "compliance_":      ["governance"],
    "governance_":      ["governance"],
    "repo_":            ["repository"],
    "security_":        ["security"],
    "data_":            ["data_architecture"],
    "cloud_":           ["cloud_infrastructure"],
    "integration_":     ["integration"],
    "api_":             ["integration"],
    "compute_":         ["analysis"],
    "detect_":          ["analysis"],
    "evaluate_":        ["analysis"],
    "build_":           ["analysis"],
    "capability_":      ["general", "analysis"],
    "stakeholder_":     ["repository", "governance"],
    "portfolio_":       ["general", "governance"],
    "cost_":            ["general", "cloud_infrastructure"],
    "risk_":            ["governance", "security"],
    "migration_":       ["adm", "cloud_infrastructure"],
    "roadmap_":         ["adm", "governance"],
    "maturity_":        ["general", "governance"],
    "technical_debt_":  ["analysis", "general"],
    "technology_":      ["technology_radar"],
    "assess_":          ["technology_radar", "analysis"],
    "compare_":         ["technology_radar", "analysis"],
    "map_":             ["analysis"],
    "sla_":             ["governance"],
    "raci_":            ["governance"],
    "decision_":        ["governance"],
    "gap_analysis_":    ["analysis", "adm"],
    "value_stream_":    ["general", "analysis"],
    "capacity_":        ["general", "cloud_infrastructure"],
    "interoperability_": ["integration", "general"],
    "infrastructure_":  ["cloud_infrastructure"],
    "reuse_":           ["repository", "analysis"],
    "transformation_":  ["adm", "general"],
    "viewpoint_":       ["archimate"],
}


def get_tool_domain_tags(tool: dict[str, Any]) -> list[str]:
    """Return the domain_tags for a tool, deriving from name if needed."""
    # Explicit domain_tags take precedence
    if tool.get("domain_tags"):
        return tool["domain_tags"]

    tags: set[str] = set()
    primary = tool.get("domain", "general")
    tags.add(primary)

    # Add secondary domains from name prefix
    name = tool.get("name", "")
    for prefix, domains in _NAME_PREFIX_DOMAINS.items():
        if name.startswith(prefix):
            tags.update(domains)
            break  # match first prefix only

    return sorted(tags)


def get_seed_affinity_domains(seed: dict[str, Any]) -> list[str]:
    """Return the affinity domains for a seed concept."""
    # Explicit affinity_domains take precedence
    if seed.get("affinity_domains"):
        return seed["affinity_domains"]

    category = seed.get("category", "")
    return CATEGORY_DOMAIN_MAP.get(category, ["general"])


# =====================================================================
# Step 3: Stratified sampling with affinity guarantee
# =====================================================================

def sample_tools_with_affinity(
    seed: dict[str, Any],
    full_pool: list[dict[str, Any]],
    toolset_size: int,
    min_affinity: int = MIN_AFFINITY_TOOLS,
    rng: random.Random | None = None,
) -> list[dict[str, Any]]:
    """Sample a toolset guaranteeing min_affinity domain-matching tools.

    1. Compute affinity_domains for the seed.
    2. Split pool into affinity_tools (domain_tags overlap) and others.
    3. Sample min(min_affinity, len(affinity_tools)) from affinity set.
    4. Fill remaining slots from the full pool (no duplicates).
    5. Shuffle so affinity tools aren't clustered at the start.
    """
    rng = rng or random.Random()
    affinity_domains = set(get_seed_affinity_domains(seed))

    # Partition pool by affinity overlap
    affinity_tools: list[dict[str, Any]] = []
    other_tools: list[dict[str, Any]] = []
    for t in full_pool:
        tags = set(get_tool_domain_tags(t))
        if tags & affinity_domains:
            affinity_tools.append(t)
        else:
            other_tools.append(t)

    # Guarantee affinity slots
    n_affinity = min(min_affinity, len(affinity_tools))
    selected_affinity = rng.sample(affinity_tools, n_affinity)
    selected_ids = {id(t) for t in selected_affinity}

    # Fill remaining slots from full pool (excluding already selected)
    remaining_pool = [t for t in full_pool if id(t) not in selected_ids]
    n_remaining = min(toolset_size - n_affinity, len(remaining_pool))
    selected_remaining = rng.sample(remaining_pool, n_remaining)

    toolset = selected_affinity + selected_remaining
    rng.shuffle(toolset)

    logger.debug(
        "Affinity sampling: seed=%s, affinity_domains=%s, "
        "pool=%d (affinity=%d, other=%d), selected=%d (affinity=%d)",
        seed.get("name", "?"), sorted(affinity_domains),
        len(full_pool), len(affinity_tools), len(other_tools),
        len(toolset), n_affinity,
    )

    return toolset


def count_affinity_tools(
    tools: list[dict[str, Any]],
    seed: dict[str, Any],
) -> int:
    """Count how many tools in a toolset have affinity with the seed."""
    affinity_domains = set(get_seed_affinity_domains(seed))
    return sum(
        1 for t in tools
        if set(get_tool_domain_tags(t)) & affinity_domains
    )


@dataclass
class SynthesisConfig:
    """A sampled configuration for one synthesis cycle."""
    seed: dict[str, Any]
    tools: list[dict[str, Any]]
    exemplars: list[dict[str, Any]]
    config_id: str = ""

    @property
    def retrieval_tools(self) -> list[dict[str, Any]]:
        return [t for t in self.tools if t.get("tool_type") == "retrieval"]

    @property
    def processing_tools(self) -> list[dict[str, Any]]:
        return [t for t in self.tools if t.get("tool_type") == "processing"]

    def to_dict(self) -> dict:
        return {
            "config_id": self.config_id,
            "seed": self.seed,
            "tool_count": len(self.tools),
            "retrieval_tool_count": len(self.retrieval_tools),
            "processing_tool_count": len(self.processing_tools),
            "exemplar_count": len(self.exemplars),
            "exemplar_families": list({e.get("family", "") for e in self.exemplars}),
            "tools": self.tools,
            "exemplars": self.exemplars,
        }


class PoolSampler:
    """Samples configurations from the three decoupled pools."""

    def __init__(
        self,
        tool_pool_path: Path | str = "pools/tools/tool_pool.json",
        seed_pool_path: Path | str = "pools/seeds/seed_pool.json",
        exemplar_pool_path: Path | str = "pools/exemplars/exemplar_pool.json",
    ):
        self.tool_pool = self._load(tool_pool_path)
        self.seed_pool = self._load(seed_pool_path)
        self.exemplar_pool = self._load(exemplar_pool_path)

    @staticmethod
    def _load(path: Path | str) -> list[dict]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def sample_config(
        self,
        tool_count_range: tuple[int, int] = (8, 15),
        exemplar_count_range: tuple[int, int] = (3, 5),
        seed_category: str | None = None,
        ensure_processing: bool = True,
        min_affinity: int = MIN_AFFINITY_TOOLS,
        rng: random.Random | None = None,
    ) -> SynthesisConfig:
        """Sample a synthesis configuration with soft-affinity tool selection.

        Guarantees at least ``min_affinity`` tools whose domain_tags
        overlap with the seed's affinity_domains, filling remaining
        slots from the full pool for cross-domain diversity.

        Args:
            tool_count_range: Min/max number of tools to sample.
            exemplar_count_range: Min/max number of exemplars to sample.
            seed_category: Optional filter for seed category.
            ensure_processing: If True, ensure at least one processing tool.
            min_affinity: Minimum affinity-matching tools guaranteed.
            rng: Optional random number generator for reproducibility.
        """
        rng = rng or random.Random()

        # Sample seed
        seed_candidates = self.seed_pool
        if seed_category:
            seed_candidates = [s for s in self.seed_pool if s.get("category") == seed_category]
            if not seed_candidates:
                seed_candidates = self.seed_pool
        seed = rng.choice(seed_candidates)

        # Determine target toolset size
        tool_count = rng.randint(*tool_count_range)
        tool_count = min(tool_count, len(self.tool_pool))

        # Step 3: Stratified sampling with affinity guarantee
        tools = sample_tools_with_affinity(
            seed=seed,
            full_pool=self.tool_pool,
            toolset_size=tool_count,
            min_affinity=min_affinity,
            rng=rng,
        )

        # Ensure at least one processing tool
        if ensure_processing:
            has_processing = any(t.get("tool_type") == "processing" for t in tools)
            if not has_processing:
                processing_tools = [t for t in self.tool_pool if t.get("tool_type") == "processing"]
                if processing_tools:
                    replace_idx = rng.randint(0, len(tools) - 1)
                    tools[replace_idx] = rng.choice(processing_tools)

        # Sample exemplars
        exemplar_count = rng.randint(*exemplar_count_range)
        exemplar_count = min(exemplar_count, len(self.exemplar_pool))
        exemplars = rng.sample(self.exemplar_pool, exemplar_count)

        config_id = f"cfg_{seed['id']}_{rng.randint(10000, 99999)}"

        return SynthesisConfig(
            seed=seed,
            tools=tools,
            exemplars=exemplars,
            config_id=config_id,
        )

    def sample_batch(
        self,
        batch_size: int,
        seed: int | None = None,
        **kwargs,
    ) -> list[SynthesisConfig]:
        """Sample a batch of configurations with optional seed for reproducibility."""
        rng = random.Random(seed) if seed is not None else random.Random()
        return [self.sample_config(rng=rng, **kwargs) for _ in range(batch_size)]

    def stats(self) -> dict[str, Any]:
        """Return pool statistics."""
        tool_types = {}
        tool_domains = {}
        for t in self.tool_pool:
            tt = t.get("tool_type", "unknown")
            td = t.get("domain", "unknown")
            tool_types[tt] = tool_types.get(tt, 0) + 1
            tool_domains[td] = tool_domains.get(td, 0) + 1

        seed_categories = {}
        for s in self.seed_pool:
            sc = s.get("category", "unknown")
            seed_categories[sc] = seed_categories.get(sc, 0) + 1

        exemplar_families = {}
        for e in self.exemplar_pool:
            ef = e.get("family", "unknown")
            exemplar_families[ef] = exemplar_families.get(ef, 0) + 1

        return {
            "tool_pool_size": len(self.tool_pool),
            "tool_types": tool_types,
            "tool_domains": tool_domains,
            "seed_pool_size": len(self.seed_pool),
            "seed_categories": seed_categories,
            "exemplar_pool_size": len(self.exemplar_pool),
            "exemplar_families": exemplar_families,
        }
