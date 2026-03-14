"""Collector Agent: iteratively gathers evidence via tool calls.

The collector explores a seed concept using available tools, building
an increasingly rich evidence set across K iterations. Each iteration
uses previous evidence as context for deeper exploration.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

from .kimi_client import KimiClient
from .tool_executor import ToolExecutor

logger = logging.getLogger(__name__)


@dataclass
class EvidenceItem:
    """A single piece of evidence from a tool call."""
    iteration: int
    tool_name: str
    arguments: dict[str, Any]
    result: Any
    reasoning: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "iteration": self.iteration,
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "result": self.result,
            "reasoning": self.reasoning,
        }


@dataclass
class EvidenceSet:
    """Accumulated evidence across iterations."""
    items: list[EvidenceItem] = field(default_factory=list)

    def add(self, item: EvidenceItem) -> None:
        self.items.append(item)

    def for_iteration(self, k: int) -> list[EvidenceItem]:
        return [e for e in self.items if e.iteration == k]

    def summary(self, max_items: int = 20) -> str:
        """Produce a text summary of collected evidence for use in prompts."""
        lines = []
        for item in self.items[-max_items:]:
            result_str = json.dumps(item.result, ensure_ascii=False) if isinstance(item.result, (dict, list)) else str(item.result)
            if len(result_str) > 500:
                result_str = result_str[:500] + "..."
            lines.append(
                f"[K={item.iteration}] {item.tool_name}({json.dumps(item.arguments, ensure_ascii=False)[:150]})\n"
                f"  → {result_str}"
            )
        return "\n\n".join(lines)

    def to_list(self) -> list[dict[str, Any]]:
        return [e.to_dict() for e in self.items]

    def __len__(self) -> int:
        return len(self.items)


COLLECTOR_SYSTEM_PROMPT = """You are an Architecture Evidence Collector for DIVE-TOGAF synthesis.

Your role: systematically explore architecture concepts using available tools to gather
verifiable, structured evidence. You are investigating a specific seed concept in the
TOGAF/ArchiMate/enterprise architecture domain.

RULES:
1. Call tools to gather REAL data — do not invent facts without tool support
2. Each tool call should have a clear purpose — explore a different facet of the concept
3. Start broad, then dig deeper into interesting findings
4. Prioritize tools that produce structured, quantifiable data
5. Try to cover multiple architectural perspectives: business, application, technology, governance
6. Call 3-6 tools per iteration round
7. After calling tools, briefly note what you found and what to explore next"""


def _build_iteration_prompt(
    seed: dict[str, Any],
    iteration: int,
    evidence_so_far: EvidenceSet,
    prev_query: str | None = None,
) -> str:
    """Build the user prompt for a collector iteration."""
    seed_desc = f"Seed: {seed['name']} ({seed.get('category', '')})\nDescription: {seed.get('description', '')}"
    if seed.get("metadata"):
        meta_str = json.dumps(seed["metadata"], ensure_ascii=False, indent=2)
        if len(meta_str) < 1000:
            seed_desc += f"\nMetadata: {meta_str}"

    if iteration == 1:
        return f"""INVESTIGATION TARGET:
{seed_desc}

This is iteration K=1 (initial exploration). Use the available tools to gather foundational
evidence about this concept. Cover different aspects: structure, relationships, stakeholders,
maturity, risks, dependencies.

Call several tools to build a broad evidence base."""

    evidence_summary = evidence_so_far.summary()
    prev_context = f"\nPrevious query for context: {prev_query}" if prev_query else ""

    return f"""INVESTIGATION TARGET:
{seed_desc}

This is iteration K={iteration} (deepening). You have gathered the following evidence so far:

{evidence_summary}
{prev_context}

NOW: Go deeper. Focus on the most interesting findings from previous iterations.
Explore dependencies, risks, gaps, specific details, cross-domain implications.
Use different tools than before. Increase the specificity and depth of your investigation."""


class CollectorAgent:
    """Iteratively collects evidence about a seed concept via tool calls."""

    def __init__(
        self,
        kimi_client: KimiClient,
        tool_executor: ToolExecutor,
        tool_schemas: list[dict[str, Any]],
    ):
        self._kimi = kimi_client
        self._executor = tool_executor
        self._tool_schemas = tool_schemas

    def collect_iteration(
        self,
        seed: dict[str, Any],
        iteration: int,
        evidence: EvidenceSet,
        prev_query: str | None = None,
        max_tool_rounds: int = 8,
    ) -> tuple[EvidenceSet, str]:
        """Run one iteration of evidence collection.

        Args:
            seed: The seed concept dict.
            iteration: Current iteration number (1-indexed).
            evidence: Accumulated evidence from prior iterations.
            prev_query: The query generated in the previous iteration, for context.
            max_tool_rounds: Max tool-call rounds in this iteration.

        Returns:
            (updated_evidence, collector_reasoning)
        """
        prompt = _build_iteration_prompt(seed, iteration, evidence, prev_query)

        messages = [
            {"role": "system", "content": COLLECTOR_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        reasoning, tool_log = self._kimi.chat_with_tools(
            messages=messages,
            tools=self._tool_schemas,
            tool_executor=self._executor,
            max_rounds=max_tool_rounds,
            max_tokens=4096,
        )

        # Record evidence items
        for call in tool_log:
            evidence.add(EvidenceItem(
                iteration=iteration,
                tool_name=call["tool_name"],
                arguments=call["arguments"],
                result=call["result"],
                reasoning=reasoning[:200] if reasoning else "",
            ))

        logger.info(
            "Iteration K=%d: %d tool calls, total evidence: %d items",
            iteration, len(tool_log), len(evidence),
        )

        return evidence, reasoning

    def collect(
        self,
        seed: dict[str, Any],
        k_iterations: int = 3,
        max_tool_rounds_per_iter: int = 8,
    ) -> EvidenceSet:
        """Run K iterations of evidence collection.

        Returns the final accumulated evidence set.
        """
        evidence = EvidenceSet()
        prev_query: str | None = None

        for k in range(1, k_iterations + 1):
            logger.info("=== Collector iteration K=%d ===", k)
            evidence, reasoning = self.collect_iteration(
                seed=seed,
                iteration=k,
                evidence=evidence,
                prev_query=prev_query,
                max_tool_rounds=max_tool_rounds_per_iter,
            )
            prev_query = reasoning

        return evidence
