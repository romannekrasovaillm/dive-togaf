"""Teacher rollout: independently answers the same question using tools.

The teacher agent receives the generated question and available tools,
then independently produces an answer using real tool calls. This answer
serves as a reference for RLVR verification — if the student (generator)
answer and teacher answer agree on key facts, the sample is verified.

Flow:
1. Receive question + tool schemas + tool executor
2. Teacher calls tools independently (no access to student evidence)
3. Produce a grounded answer with [E<n>] citations
4. Compare key claims between student and teacher answers
5. Return verification result with agreement score
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

from .kimi_client import KimiClient
from .tool_executor import ToolExecutor

logger = logging.getLogger(__name__)


@dataclass
class TeacherResult:
    """Result of a teacher rollout verification."""
    question: str
    teacher_answer: str
    teacher_tool_calls: list[dict[str, Any]] = field(default_factory=list)
    teacher_evidence_count: int = 0
    agreement_score: float = 0.0
    key_facts_student: list[str] = field(default_factory=list)
    key_facts_teacher: list[str] = field(default_factory=list)
    matched_facts: int = 0
    total_facts: int = 0
    verified: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "teacher_answer": self.teacher_answer,
            "teacher_tool_calls": len(self.teacher_tool_calls),
            "teacher_evidence_count": self.teacher_evidence_count,
            "agreement_score": self.agreement_score,
            "matched_facts": self.matched_facts,
            "total_facts": self.total_facts,
            "verified": self.verified,
        }


TEACHER_SYSTEM_PROMPT = """You are an independent Architecture Expert verifying answers about TOGAF/ArchiMate.

You receive a question about enterprise architecture. Your task:
1. Use the available tools to gather evidence independently
2. Answer the question based ONLY on tool outputs
3. Cite every factual claim with [E<n>] where n is the tool call index (starting from 0)

RULES:
- Call 2-6 tools to gather evidence before answering
- Every claim MUST cite its source as [E<n>]
- Do NOT invent data — only use what tools return
- Be precise with numbers, names, and technical details
- After gathering evidence, provide your answer in this JSON format:

{
  "answer": "Your grounded answer with [E0], [E1] citations...",
  "key_facts": ["fact 1 with source", "fact 2 with source", ...]
}"""


COMPARISON_SYSTEM_PROMPT = """You are a fact-comparison engine. Compare two answers to the same question
and determine which key facts agree.

Return ONLY valid JSON:
{
  "student_facts": ["fact1", "fact2", ...],
  "teacher_facts": ["fact1", "fact2", ...],
  "matched_count": <number of facts that agree>,
  "total_facts": <total unique facts across both>,
  "agreement_score": <0.0 to 1.0>,
  "mismatches": ["description of disagreement 1", ...]
}"""


class TeacherAgent:
    """Independently answers questions using tools for RLVR verification."""

    def __init__(
        self,
        kimi_client: KimiClient,
        max_tool_rounds: int = 6,
    ):
        self._kimi = kimi_client
        self._max_tool_rounds = max_tool_rounds

    def rollout(
        self,
        question: str,
        tool_executor: ToolExecutor,
        tool_schemas: list[dict[str, Any]],
        student_answer: str = "",
    ) -> TeacherResult:
        """Run teacher rollout: independently answer the question, then compare.

        Args:
            question: The question to answer.
            tool_executor: Tool executor with live tool access.
            tool_schemas: OpenAI-format tool schemas.
            student_answer: The student (generator) answer to compare against.

        Returns:
            TeacherResult with verification details.
        """
        logger.info("Teacher rollout for Q='%s'", question[:80])

        # Phase 1: Teacher independently gathers evidence and answers
        messages = [
            {"role": "system", "content": TEACHER_SYSTEM_PROMPT},
            {"role": "user", "content": f"Answer this question using the available tools:\n\n{question}"},
        ]

        teacher_text, tool_call_log = self._kimi.chat_with_tools(
            messages=messages,
            tools=tool_schemas,
            tool_executor=tool_executor,
            max_rounds=self._max_tool_rounds,
            max_tokens=32768,
        )

        logger.info(
            "Teacher round done: %d tool calls",
            len(tool_call_log),
        )

        # Parse teacher answer
        teacher_answer, teacher_facts = self._parse_teacher_response(teacher_text)

        result = TeacherResult(
            question=question,
            teacher_answer=teacher_answer,
            teacher_tool_calls=tool_call_log,
            teacher_evidence_count=len(tool_call_log),
        )

        # Phase 2: Compare student and teacher answers
        if student_answer:
            comparison = self._compare_answers(question, student_answer, teacher_answer)
            result.agreement_score = comparison.get("agreement_score", 0.0)
            result.key_facts_student = comparison.get("student_facts", [])
            result.key_facts_teacher = comparison.get("teacher_facts", [])
            result.matched_facts = comparison.get("matched_count", 0)
            result.total_facts = comparison.get("total_facts", 0)
            result.verified = result.agreement_score >= 0.6

            logger.info(
                "Teacher verification: agreement=%.2f, matched=%d/%d, verified=%s",
                result.agreement_score, result.matched_facts,
                result.total_facts, result.verified,
            )
        else:
            logger.info("Teacher rollout complete (no student answer to compare)")

        return result

    def _parse_teacher_response(self, response: str) -> tuple[str, list[str]]:
        """Parse teacher LLM response into answer and key facts."""
        text = response.strip()

        # Try JSON parse
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

        try:
            data = json.loads(text)
            return data.get("answer", text), data.get("key_facts", [])
        except json.JSONDecodeError:
            # Try to find JSON in text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    data = json.loads(text[start:end])
                    return data.get("answer", text), data.get("key_facts", [])
                except json.JSONDecodeError:
                    pass

        # Fallback: use raw text as answer
        return text, []

    def _compare_answers(
        self,
        question: str,
        student_answer: str,
        teacher_answer: str,
    ) -> dict[str, Any]:
        """Compare student and teacher answers using LLM."""
        prompt = f"""Question: {question}

=== STUDENT ANSWER ===
{student_answer[:2000]}

=== TEACHER ANSWER ===
{teacher_answer[:2000]}

Compare these two answers. Identify key factual claims in each and determine which ones agree.
Return ONLY valid JSON as specified in the system prompt."""

        try:
            response = self._kimi.chat_text(
                messages=[
                    {"role": "system", "content": COMPARISON_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=4096,
            )

            # Parse comparison result
            text = response.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()

            try:
                return json.loads(text)
            except json.JSONDecodeError:
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    try:
                        return json.loads(text[start:end])
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            logger.warning("Teacher comparison failed: %s", e)

        # Fallback: simple citation overlap check
        student_citations = set(int(m) for m in re.findall(r'\[E(\d+)\]', student_answer))
        teacher_citations = set(int(m) for m in re.findall(r'\[E(\d+)\]', teacher_answer))
        overlap = len(student_citations & teacher_citations)
        total = len(student_citations | teacher_citations) or 1
        return {
            "student_facts": [f"[E{i}]" for i in sorted(student_citations)],
            "teacher_facts": [f"[E{i}]" for i in sorted(teacher_citations)],
            "matched_count": overlap,
            "total_facts": total,
            "agreement_score": round(overlap / total, 2),
            "mismatches": [],
        }
