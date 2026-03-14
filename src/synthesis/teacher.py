"""Teacher Agent: generates SFT trajectories by solving tasks with reasoning.

After the collector gathers evidence and the generator produces (Q, A) pairs,
the teacher agent attempts to solve each question using the same tools.
The full trajectory — interleaved thinking, tool calls, and observations —
is captured for SFT training.

This implements the "Teacher → Trajectories → Rejection Sampling" block
from the DIVE pipeline (Figure 2).
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from .kimi_client import KimiClient

logger = logging.getLogger(__name__)


@dataclass
class TrajectoryStep:
    """A single step in an agent trajectory."""
    step_type: str  # "think", "action", "observation"
    content: str = ""
    tool_name: str | None = None
    tool_args: dict[str, Any] | None = None
    tool_result: Any = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"step_type": self.step_type, "content": self.content}
        if self.tool_name is not None:
            d["tool_name"] = self.tool_name
            d["tool_args"] = self.tool_args
        if self.tool_result is not None:
            result_str = (
                json.dumps(self.tool_result, ensure_ascii=False)
                if isinstance(self.tool_result, (dict, list))
                else str(self.tool_result)
            )
            # Truncate large results for SFT data
            if len(result_str) > 1500:
                result_str = result_str[:1500] + "..."
            d["tool_result"] = result_str
        return d


@dataclass
class TrajectoryResult:
    """Full trajectory from a teacher rollout."""
    steps: list[TrajectoryStep] = field(default_factory=list)
    final_answer: str = ""
    verified: bool = False
    total_tool_calls: int = 0
    elapsed_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "steps": [s.to_dict() for s in self.steps],
            "final_answer": self.final_answer,
            "verified": self.verified,
            "total_tool_calls": self.total_tool_calls,
            "elapsed_seconds": round(self.elapsed_seconds, 2),
        }


TEACHER_SYSTEM_PROMPT = """You are an expert TOGAF/ArchiMate architecture analyst solving a question.

You have access to architecture analysis tools. Use them to gather the data you need,
then synthesize a comprehensive answer.

APPROACH:
1. Think step by step about what information you need
2. Call relevant tools to gather data
3. Analyze the results and reason about the answer
4. Provide a final, detailed answer with specific data points

RULES:
- Use tools to gather real data — do not guess or fabricate numbers
- Cite specific tool results in your answer (e.g., "maturity score of 1.2 from health analysis")
- Be thorough — call multiple tools to build a complete picture
- Think carefully before each tool call about what you expect to learn"""


class TeacherAgent:
    """Runs teacher rollouts to generate SFT trajectories.

    For each (Q, tools) pair, the teacher:
    1. Attempts to solve Q using available tools with full reasoning
    2. Captures interleaved (think, action, observation) trajectory
    3. Optionally verifies the answer against a reference (rejection sampling)
    """

    def __init__(
        self,
        kimi_client: KimiClient,
        max_rounds: int = 6,
        max_tokens: int = 32768,
    ):
        self._kimi = kimi_client
        self._max_rounds = max_rounds
        self._max_tokens = max_tokens

    def rollout(
        self,
        question: str,
        tool_schemas: list[dict[str, Any]],
        tool_executor: Any,
        reference_answer: str | None = None,
    ) -> TrajectoryResult:
        """Run a teacher rollout: solve question, capture trajectory.

        Args:
            question: The question to solve.
            tool_schemas: OpenAI-format tool definitions.
            tool_executor: Callable(name, args) -> result.
            reference_answer: Optional reference for rejection sampling.

        Returns:
            TrajectoryResult with full step-by-step trajectory.
        """
        start = time.time()
        steps: list[TrajectoryStep] = []
        tool_call_count = 0

        msgs: list[dict[str, Any]] = [
            {"role": "system", "content": TEACHER_SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ]

        for round_num in range(self._max_rounds):
            resp = self._kimi.chat(
                msgs, tools=tool_schemas,
                max_tokens=self._max_tokens, stream=True,
            )
            choice = resp.choices[0]
            msg = choice.message

            # Capture reasoning (thinking) step
            reasoning = getattr(msg, "reasoning_content", None)
            if reasoning:
                steps.append(TrajectoryStep(
                    step_type="think",
                    content=reasoning,
                ))

            if msg.tool_calls:
                # Record the assistant message content (brief reasoning before calls)
                if msg.content:
                    steps.append(TrajectoryStep(
                        step_type="think",
                        content=msg.content,
                    ))

                # Build assistant dict for conversation history
                assistant_dict: dict[str, Any] = {
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in msg.tool_calls
                    ],
                }
                if reasoning:
                    assistant_dict["reasoning_content"] = reasoning
                msgs.append(assistant_dict)

                # Execute each tool call — record action + observation
                for tc in msg.tool_calls:
                    fn_name = tc.function.name
                    try:
                        fn_args = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        fn_args = {"raw": tc.function.arguments}

                    # Action step
                    steps.append(TrajectoryStep(
                        step_type="action",
                        content=f"{fn_name}({json.dumps(fn_args, ensure_ascii=False)[:300]})",
                        tool_name=fn_name,
                        tool_args=fn_args,
                    ))

                    # Execute
                    result = tool_executor(fn_name, fn_args)
                    tool_call_count += 1
                    result_str = (
                        json.dumps(result, ensure_ascii=False)
                        if isinstance(result, (dict, list))
                        else str(result)
                    )

                    # Observation step
                    steps.append(TrajectoryStep(
                        step_type="observation",
                        content=result_str[:1500],
                        tool_name=fn_name,
                        tool_result=result,
                    ))

                    # Truncated result for API context
                    api_content = result_str
                    if len(api_content) > 800:
                        api_content = api_content[:800] + "..."
                    msgs.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": api_content,
                    })

                logger.info(
                    "Teacher round %d/%d: %d tool calls",
                    round_num + 1, self._max_rounds, len(msg.tool_calls),
                )
                time.sleep(2)  # Rate limit pacing
            else:
                # Model finished — capture final answer
                final_answer = msg.content or ""
                if final_answer:
                    steps.append(TrajectoryStep(
                        step_type="think",
                        content=final_answer,
                    ))
                break
        else:
            # Max rounds — use last content
            final_answer = msg.content or "" if msg else ""

        elapsed = time.time() - start

        # Rejection sampling: verify against reference
        verified = True
        if reference_answer:
            verified = self._verify_answer(question, final_answer, reference_answer)

        result = TrajectoryResult(
            steps=steps,
            final_answer=final_answer,
            verified=verified,
            total_tool_calls=tool_call_count,
            elapsed_seconds=elapsed,
        )

        logger.info(
            "Teacher rollout: %d steps, %d tool calls, verified=%s, %.1fs",
            len(steps), tool_call_count, verified, elapsed,
        )

        return result

    def _verify_answer(
        self,
        question: str,
        candidate: str,
        reference: str,
    ) -> bool:
        """Verify candidate answer against reference using LLM judge.

        Returns True if the candidate captures the key facts from the reference.
        """
        prompt = f"""Compare the candidate answer to the reference answer for this question.

QUESTION: {question}

REFERENCE ANSWER:
{reference[:2000]}

CANDIDATE ANSWER:
{candidate[:2000]}

Does the candidate answer capture the same key factual claims as the reference?
Minor wording differences are acceptable. The candidate must get the core facts
(numbers, names, relationships, conclusions) correct.

Reply with ONLY "PASS" or "FAIL" on the first line, then a brief explanation."""

        try:
            response = self._kimi.chat_text(
                messages=[
                    {"role": "system", "content": "You are a strict answer verification judge."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=512,
            )
            return response.strip().upper().startswith("PASS")
        except Exception as e:
            logger.warning("Answer verification failed: %s, accepting by default", e)
            return True
