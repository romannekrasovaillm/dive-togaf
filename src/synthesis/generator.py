"""Task Generator: creates Q/A pairs strictly from collected evidence.

Takes an evidence set and exemplar templates, produces grounded (Q, A) pairs
where every fact in the answer traces back to a specific tool output.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

from .collector import EvidenceSet
from .kimi_client import KimiClient

logger = logging.getLogger(__name__)


@dataclass
class SynthesizedTask:
    """A generated (question, answer) pair with full provenance."""
    question: str
    answer: str
    sub_questions: list[str] = field(default_factory=list)
    evidence_ids: list[int] = field(default_factory=list)
    complexity: int = 1
    iteration: int = 1
    family: str = ""
    reasoning_trace: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "answer": self.answer,
            "sub_questions": self.sub_questions,
            "evidence_ids": self.evidence_ids,
            "complexity": self.complexity,
            "iteration": self.iteration,
            "family": self.family,
            "reasoning_trace": self.reasoning_trace,
        }


GENERATOR_SYSTEM_PROMPT = """You are a TOGAF/ArchiMate Task Generator for the DIVE synthesis pipeline.

Your role: given collected evidence (real tool outputs) and structural exemplar templates,
generate a high-quality (question, answer) pair that is STRICTLY GROUNDED in the evidence.

CRITICAL RULES:
1. Every fact in the answer MUST come from a specific tool output in the evidence
2. Do NOT invent any data, numbers, names, or relationships not present in evidence
3. The question should require reasoning across multiple evidence items
4. The answer should reference specific data points from tool outputs
5. Include sub-questions that build toward the full answer
6. Match the complexity and structure of the provided exemplar template

OUTPUT FORMAT (JSON):
{
  "question": "The main question",
  "sub_questions": ["Sub-Q 1", "Sub-Q 2", ...],
  "answer": "The detailed answer citing evidence",
  "complexity": <1-5>,
  "family": "exemplar family name",
  "reasoning_trace": "Brief explanation of how evidence supports the answer"
}"""


def _build_generation_prompt(
    seed: dict[str, Any],
    evidence: EvidenceSet,
    exemplars: list[dict[str, Any]],
    iteration: int,
) -> str:
    """Build the prompt for task generation."""
    seed_str = f"Seed: {seed['name']} ({seed.get('category', '')})"

    # Format evidence
    evidence_lines = []
    for i, item in enumerate(evidence.items):
        result_str = json.dumps(item.result, ensure_ascii=False) if isinstance(item.result, (dict, list)) else str(item.result)
        if len(result_str) > 800:
            result_str = result_str[:800] + "..."
        evidence_lines.append(
            f"[E{i}] Tool: {item.tool_name} | Args: {json.dumps(item.arguments, ensure_ascii=False)[:200]}\n"
            f"Result: {result_str}"
        )
    evidence_str = "\n\n".join(evidence_lines)

    # Format exemplar templates
    exemplar_lines = []
    for ex in exemplars:
        exemplar_lines.append(
            f"- Family: {ex.get('family', 'unknown')}\n"
            f"  Template: {ex.get('template', '')}\n"
            f"  Complexity: {ex.get('complexity', 1)} | Sub-questions: {ex.get('sub_questions', 1)}"
        )
    exemplar_str = "\n".join(exemplar_lines)

    complexity_guide = {
        1: "Simple single-fact retrieval question (1 sub-question)",
        2: "Two-step question combining 2 evidence items (2 sub-questions)",
        3: "Multi-step question requiring 3+ evidence items (2-3 sub-questions)",
    }
    target_complexity = min(iteration + 1, 5)

    return f"""{seed_str}

=== COLLECTED EVIDENCE ({len(evidence)} items) ===
{evidence_str}

=== EXEMPLAR TEMPLATES (structural guidance) ===
{exemplar_str}

=== GENERATION INSTRUCTIONS ===
Iteration: K={iteration}
Target complexity: {target_complexity} — {complexity_guide.get(target_complexity, 'Complex multi-step question (3-5 sub-questions)')}

Generate a (question, answer) pair that:
1. Is fully grounded in the evidence above
2. Follows the structural pattern of one of the exemplar templates
3. Requires synthesizing information from multiple tool outputs
4. Has {max(1, iteration)} to {min(iteration + 2, 5)} sub-questions
5. References specific data points (names, numbers, relationships) from evidence

Return ONLY valid JSON in the format specified in the system prompt."""


class TaskGenerator:
    """Generates grounded Q/A tasks from evidence and exemplar templates."""

    def __init__(self, kimi_client: KimiClient):
        self._kimi = kimi_client

    def generate(
        self,
        seed: dict[str, Any],
        evidence: EvidenceSet,
        exemplars: list[dict[str, Any]],
        iteration: int,
    ) -> SynthesizedTask:
        """Generate a single Q/A task from evidence.

        Args:
            seed: The seed concept dict.
            evidence: Collected evidence set.
            exemplars: Exemplar template dicts for structural guidance.
            iteration: Current iteration number.

        Returns:
            SynthesizedTask with question, answer, and provenance.
        """
        prompt = _build_generation_prompt(seed, evidence, exemplars, iteration)

        response = self._kimi.chat_text(
            messages=[
                {"role": "system", "content": GENERATOR_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=4096,
        )

        # Parse JSON from response
        task_data = self._parse_response(response)

        return SynthesizedTask(
            question=task_data.get("question", ""),
            answer=task_data.get("answer", ""),
            sub_questions=task_data.get("sub_questions", []),
            evidence_ids=list(range(len(evidence))),
            complexity=task_data.get("complexity", iteration + 1),
            iteration=iteration,
            family=task_data.get("family", ""),
            reasoning_trace=task_data.get("reasoning_trace", ""),
        )

    def _parse_response(self, response: str) -> dict[str, Any]:
        """Parse generator LLM response into structured data."""
        text = response.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON object in the text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(text[start:end])
                except json.JSONDecodeError:
                    pass
            logger.warning("Failed to parse generator response as JSON")
            return {
                "question": text[:500],
                "answer": "Parse error — raw response captured",
                "sub_questions": [],
                "complexity": 1,
                "family": "parse_error",
                "reasoning_trace": text,
            }
