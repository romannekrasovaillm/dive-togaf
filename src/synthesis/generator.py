"""Task Generator: creates Q/A pairs strictly from collected evidence.

Takes an evidence set and exemplar templates, produces grounded (Q, A) pairs
where every fact in the answer traces back to a specific tool output.

Grounding invariant enforcement:
- Generator MUST cite evidence items as [E0], [E1], etc. in both answer and reasoning
- Cited evidence IDs are parsed and validated against the evidence set
- A post-generation grounding validator rejects answers with ungrounded claims
"""

from __future__ import annotations

import json
import logging
import re
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
    cited_evidence_ids: list[int] = field(default_factory=list)
    evidence_trajectory: list[dict[str, Any]] = field(default_factory=list)
    complexity: int = 1
    iteration: int = 1
    family: str = ""
    reasoning_trace: str = ""
    grounding_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "answer": self.answer,
            "sub_questions": self.sub_questions,
            "cited_evidence_ids": self.cited_evidence_ids,
            "evidence_trajectory": self.evidence_trajectory,
            "complexity": self.complexity,
            "iteration": self.iteration,
            "family": self.family,
            "reasoning_trace": self.reasoning_trace,
            "grounding_score": self.grounding_score,
        }


GENERATOR_SYSTEM_PROMPT = """You are a TOGAF/ArchiMate Task Generator for the DIVE synthesis pipeline.

Your role: given collected evidence (real tool outputs) and structural exemplar templates,
generate a high-quality (question, answer) pair that is STRICTLY GROUNDED in the evidence.

GROUNDING INVARIANT — THIS IS NON-NEGOTIABLE:
- Every claim in the answer MUST cite its source as [E<number>] (e.g., [E0], [E3])
- You may ONLY use data that appears in the evidence items listed below
- If a fact cannot be traced to a specific [E<n>], you MUST NOT include it
- The "cited_evidence" field MUST list exactly the evidence IDs you referenced

CRITICAL RULES:
1. Every fact in the answer MUST cite its source evidence as [E<number>]
2. Do NOT invent any data, numbers, names, or relationships not present in evidence
3. The question should require reasoning across multiple evidence items
4. The answer should be a synthesis of specific data points from tool outputs
5. Include sub-questions that build toward the full answer
6. Match the complexity and structure of the provided exemplar template

OUTPUT FORMAT (JSON):
{
  "question": "The main question",
  "sub_questions": ["Sub-Q 1 referencing [E0]", "Sub-Q 2 combining [E1]+[E3]", ...],
  "answer": "Detailed answer where every claim cites its source: ... [E0] ... [E2] ...",
  "cited_evidence": [0, 2, 3],
  "complexity": <1-5>,
  "family": "exemplar family name",
  "reasoning_trace": "Step-by-step: [E0] provides X, [E2] provides Y, combining gives Z"
}

EXAMPLE of properly grounded answer:
"The Loan Origination capability has a maturity score of 1.2 [E2], which is the lowest
among the three assessed capabilities [E1]. The Business Architecture Document [E0] is
the primary Phase B deliverable needed to address this gap. Risk assessment shows a
compliance factor of 10/10 [E4], indicating regulatory urgency."

EXAMPLE of INVALID answer (would be rejected):
"The system has been running for 15 years and needs modernization." ← No [E<n>] citation"""


def _build_generation_prompt(
    seed: dict[str, Any],
    evidence: EvidenceSet,
    exemplars: list[dict[str, Any]],
    iteration: int,
) -> str:
    """Build the prompt for task generation."""
    seed_str = f"Seed: {seed['name']} ({seed.get('category', '')})"

    # Format evidence with clear [E{i}] tags
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
        1: "Simple single-fact retrieval question (1 sub-question, cite 1-2 evidence items)",
        2: "Two-step question combining 2 evidence items (2 sub-questions)",
        3: "Multi-step question requiring 3+ evidence items (2-3 sub-questions)",
    }
    target_complexity = min(iteration + 1, 5)

    valid_ids = list(range(len(evidence)))

    return f"""{seed_str}

=== COLLECTED EVIDENCE ({len(evidence)} items, IDs: {valid_ids}) ===
{evidence_str}

=== EXEMPLAR TEMPLATES (structural guidance) ===
{exemplar_str}

=== GENERATION INSTRUCTIONS ===
Iteration: K={iteration}
Target complexity: {target_complexity} — {complexity_guide.get(target_complexity, 'Complex multi-step question (3-5 sub-questions)')}

MANDATORY: Generate a (question, answer) pair where:
1. The answer cites EVERY factual claim with [E<n>] tags (e.g., "maturity is 2.1 [E3]")
2. The "cited_evidence" array lists exactly the evidence IDs you used
3. You synthesize information from at least {max(2, iteration)} different evidence items
4. Sub-questions reference specific evidence items
5. You use ONLY data from the evidence above — no external knowledge

Available evidence IDs: {valid_ids}
Return ONLY valid JSON in the format specified in the system prompt."""


def _extract_cited_ids(text: str) -> list[int]:
    """Extract [E<number>] citations from text."""
    return sorted(set(int(m) for m in re.findall(r'\[E(\d+)\]', text)))


def _validate_grounding(
    task_data: dict[str, Any],
    evidence: EvidenceSet,
) -> tuple[float, list[str]]:
    """Validate that the generated task is grounded in evidence.

    Returns:
        (grounding_score 0.0-1.0, list of violation messages)
    """
    violations: list[str] = []
    max_eid = len(evidence) - 1

    answer = task_data.get("answer", "")
    reasoning = task_data.get("reasoning_trace", "")
    declared_ids = set(task_data.get("cited_evidence", []))

    # Extract actually cited IDs from answer + reasoning text
    answer_cited = set(_extract_cited_ids(answer))
    reasoning_cited = set(_extract_cited_ids(reasoning))
    all_cited = answer_cited | reasoning_cited

    # Check 1: answer must contain at least one [E<n>] citation
    if not answer_cited:
        violations.append("CRITICAL: Answer contains zero [E<n>] citations — not grounded")

    # Check 2: all cited IDs must be valid (within evidence set bounds)
    invalid_ids = {eid for eid in all_cited if eid < 0 or eid > max_eid}
    if invalid_ids:
        violations.append(f"Invalid evidence IDs cited: {invalid_ids} (valid range: 0-{max_eid})")

    # Check 3: declared cited_evidence should match actual citations
    if declared_ids and declared_ids != all_cited:
        missing = all_cited - declared_ids
        extra = declared_ids - all_cited
        if missing:
            violations.append(f"Evidence cited in text but not declared: {missing}")
        if extra:
            violations.append(f"Evidence declared but not cited in text: {extra}")

    # Check 4: at least 2 different evidence items should be cited for non-trivial tasks
    complexity = task_data.get("complexity", 1)
    if complexity >= 2 and len(answer_cited) < 2:
        violations.append(
            f"Complexity {complexity} but only {len(answer_cited)} evidence items cited in answer"
        )

    # Check 5: count simulated, parse-failed, and truncated evidence items
    simulated_cited = set()
    parse_failed_cited = set()
    truncated_cited = set()
    _EVIDENCE_TRUNCATION_LIMIT = 800  # must match _build_generation_prompt
    for eid in all_cited:
        if 0 <= eid <= max_eid:
            item = evidence.items[eid]
            result = item.result
            result_len = len(
                json.dumps(result, ensure_ascii=False)
                if isinstance(result, (dict, list))
                else str(result)
            )
            if result_len > _EVIDENCE_TRUNCATION_LIMIT:
                truncated_cited.add(eid)
            if isinstance(result, dict):
                if result.get("_simulated"):
                    simulated_cited.add(eid)
                if result.get("_parse_failed"):
                    parse_failed_cited.add(eid)
    if parse_failed_cited:
        violations.append(
            f"Evidence items with parse failures cited: {parse_failed_cited}"
        )
    if truncated_cited:
        logger.warning(
            "Cited evidence was truncated in generator prompt: E%s "
            "(result > %d chars). Key facts may be beyond truncation boundary.",
            truncated_cited, _EVIDENCE_TRUNCATION_LIMIT,
        )

    # Compute grounding score
    if not answer_cited:
        score = 0.0
    else:
        valid_cited = all_cited - invalid_ids
        # Score = fraction of cited evidence that is valid, penalized for zero citations
        score = len(valid_cited) / max(len(all_cited), 1)
        # Bonus for matching declared vs actual
        if declared_ids and declared_ids == all_cited:
            score = min(1.0, score + 0.1)
        # Penalty for simulated evidence (reduce by 0.05 per simulated item)
        if simulated_cited:
            penalty = len(simulated_cited) * 0.05
            score = max(0.1, score - penalty)
        # Heavier penalty for parse-failed evidence (reduce by 0.15 per item)
        if parse_failed_cited:
            penalty = len(parse_failed_cited) * 0.15
            score = max(0.05, score - penalty)

    return round(score, 2), violations


class TaskGenerator:
    """Generates grounded Q/A tasks from evidence and exemplar templates.

    Enforces the grounding invariant: every fact must cite its source evidence.
    Tasks with grounding_score < threshold can be filtered downstream.
    """

    def __init__(self, kimi_client: KimiClient, max_regen_attempts: int = 2):
        self._kimi = kimi_client
        self._max_regen = max_regen_attempts

    def generate(
        self,
        seed: dict[str, Any],
        evidence: EvidenceSet,
        exemplars: list[dict[str, Any]],
        iteration: int,
    ) -> SynthesizedTask:
        """Generate a single grounded Q/A task from evidence.

        If the first attempt fails grounding validation, retries up to
        max_regen_attempts times with an explicit correction prompt.

        Args:
            seed: The seed concept dict.
            evidence: Collected evidence set.
            exemplars: Exemplar template dicts for structural guidance.
            iteration: Current iteration number.

        Returns:
            SynthesizedTask with question, answer, provenance, and grounding score.
        """
        prompt = _build_generation_prompt(seed, evidence, exemplars, iteration)

        for attempt in range(1, self._max_regen + 1):
            messages = [
                {"role": "system", "content": GENERATOR_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]

            # On retry, append the violation feedback
            if attempt > 1:
                messages.append({
                    "role": "user",
                    "content": (
                        f"Your previous answer had grounding violations:\n"
                        f"{chr(10).join('- ' + v for v in violations)}\n\n"
                        "REGENERATE the task. Every factual claim MUST have an [E<n>] citation. "
                        "Do not include any fact that is not directly from the evidence."
                    ),
                })

            response = self._kimi.chat_text(
                messages=messages,
                temperature=0.5,
                max_tokens=32768,
            )

            task_data = self._parse_response(response)

            # Validate grounding
            grounding_score, violations = _validate_grounding(task_data, evidence)

            if not violations:
                logger.info("Grounding validation passed (score=%.2f) on attempt %d", grounding_score, attempt)
                break
            else:
                logger.warning(
                    "Grounding violations on attempt %d: %s", attempt, "; ".join(violations)
                )

        # Parse cited evidence — use actual text citations, not self-declared
        answer = task_data.get("answer", "")
        reasoning = task_data.get("reasoning_trace", "")
        cited_ids = _extract_cited_ids(answer + " " + reasoning)

        # Build evidence trajectory: the actual tool call chain for cited evidence
        trajectory = []
        for eid in cited_ids:
            if 0 <= eid < len(evidence):
                item = evidence.items[eid]
                trajectory.append({
                    "evidence_id": eid,
                    "iteration": item.iteration,
                    "tool_name": item.tool_name,
                    "arguments": item.arguments,
                    "result_summary": _truncate(
                        json.dumps(item.result, ensure_ascii=False)
                        if isinstance(item.result, (dict, list))
                        else str(item.result),
                        300,
                    ),
                })

        return SynthesizedTask(
            question=task_data.get("question", ""),
            answer=task_data.get("answer", ""),
            sub_questions=task_data.get("sub_questions", []),
            cited_evidence_ids=cited_ids,
            evidence_trajectory=trajectory,
            complexity=task_data.get("complexity", iteration + 1),
            iteration=iteration,
            family=task_data.get("family", ""),
            reasoning_trace=task_data.get("reasoning_trace", ""),
            grounding_score=grounding_score,
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
                "cited_evidence": [],
                "complexity": 1,
                "family": "parse_error",
                "reasoning_trace": text,
            }


def _truncate(s: str, max_len: int) -> str:
    return s[:max_len] + "..." if len(s) > max_len else s
