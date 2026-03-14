"""Config Sampling for DIVE-TOGAF Evidence-Driven Synthesis.

Implements the decoupled sampling strategy: independently selects
a seed, a tool subset, and exemplar templates to create a unique
synthesis configuration for each iteration.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


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
        tool_count_range: tuple[int, int] = (12, 20),
        exemplar_count_range: tuple[int, int] = (3, 5),
        seed_category: str | None = None,
        ensure_processing: bool = True,
        rng: random.Random | None = None,
    ) -> SynthesisConfig:
        """Sample a synthesis configuration.

        Args:
            tool_count_range: Min/max number of tools to sample.
            exemplar_count_range: Min/max number of exemplars to sample.
            seed_category: Optional filter for seed category.
            ensure_processing: If True, ensure at least one processing tool is included.
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

        # Sample tools
        tool_count = rng.randint(*tool_count_range)
        tool_count = min(tool_count, len(self.tool_pool))
        tools = rng.sample(self.tool_pool, tool_count)

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
