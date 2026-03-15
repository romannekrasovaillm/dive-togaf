"""Teacher rollout: generates SFT trajectories via rejection sampling (DIVE §3.4).

The teacher is a strong model that solves tasks as a tool-using agent,
producing full conversation trajectories (reasoning → tool_call → observation
→ reasoning → ... → final_answer). Rejection sampling keeps only trajectories
where the final answer matches the reference answer A from D_task.

Flow per DIVE §3.4:
    for (Q, A, T) in D_task:
        τ = teacher.rollout(Q, T)
        if verify(τ.final_answer, A):
            D_sft.append((Q, A, T, τ))

Output format — chat-format SFT examples:
    {"messages": [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "Q + tool descriptions"},
        {"role": "assistant", "content": "<think>...</think>\\n<tool_call>...</tool_call>"},
        {"role": "tool", "content": "tool output"},
        ...
        {"role": "assistant", "content": "<think>...</think>\\nFinal answer: A"}
    ]}
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

from .kimi_client import KimiClient, _MAX_TOOL_RESULT_CHARS
from .tool_executor import ToolExecutor

logger = logging.getLogger(__name__)


TEACHER_SYSTEM_PROMPT = """You are a tool-using architecture agent. You solve enterprise architecture questions by reasoning step-by-step and calling tools.

PROCESS:
1. Think about what information you need
2. Call a tool to get that information
3. Analyze the result
4. Repeat steps 1-3 until you have enough information
5. Provide your final answer

RULES:
- Reason before every tool call: explain WHY you need this tool
- After each tool result: analyze what it tells you
- Use ONLY data from tool outputs — no external knowledge
- When you have enough evidence, state your final answer clearly
- Start your final answer with "Final answer:" on its own line"""


@dataclass
class Trajectory:
    """A complete agent trajectory: reasoning + tool calls + final answer."""
    messages: list[dict[str, Any]] = field(default_factory=list)
    final_answer: str = ""
    tool_call_count: int = 0
    verified: bool = False

    def to_sft_example(self) -> dict[str, Any]:
        """Convert to SFT training format."""
        return {"messages": self.messages}

    def to_dict(self) -> dict[str, Any]:
        return {
            "messages": self.messages,
            "final_answer": self.final_answer,
            "tool_call_count": self.tool_call_count,
            "verified": self.verified,
        }


@dataclass
class RolloutResult:
    """Result of a single teacher rollout attempt."""
    question: str
    reference_answer: str
    trajectory: Trajectory
    verified: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "reference_answer_preview": self.reference_answer[:200],
            "final_answer_preview": self.trajectory.final_answer[:200],
            "tool_call_count": self.trajectory.tool_call_count,
            "verified": self.verified,
        }


def _build_tool_descriptions(tool_schemas: list[dict[str, Any]]) -> str:
    """Format tool schemas as text for the user prompt."""
    lines = []
    for schema in tool_schemas:
        fn = schema.get("function", {})
        name = fn.get("name", "")
        desc = fn.get("description", "")
        params = fn.get("parameters", {}).get("properties", {})
        param_strs = []
        for pname, pdef in params.items():
            ptype = pdef.get("type", "string")
            pdesc = pdef.get("description", "")
            param_strs.append(f"    {pname} ({ptype}): {pdesc}")
        params_block = "\n".join(param_strs) if param_strs else "    (no parameters)"
        lines.append(f"- {name}: {desc}\n  Parameters:\n{params_block}")
    return "\n\n".join(lines)


def verify_answer(final_answer: str, reference_answer: str) -> bool:
    """Verify teacher's final answer against reference answer A.

    Uses normalized string matching: strips citations [E<n>], whitespace,
    and compares key factual fragments. A match means the teacher's
    trajectory arrived at the correct answer.
    """
    if not final_answer or not reference_answer:
        return False

    # Normalize: strip [E<n>] citations, lowercase, collapse whitespace
    def normalize(text: str) -> str:
        text = re.sub(r'\[E\d+\]', '', text)
        text = re.sub(r'\s+', ' ', text.lower().strip())
        return text

    norm_final = normalize(final_answer)
    norm_ref = normalize(reference_answer)

    # Exact match after normalization
    if norm_final == norm_ref:
        return True

    # Extract key factual tokens from reference (numbers, proper nouns, technical terms)
    # A reference is "matched" if the final answer contains the key facts
    ref_tokens = set(re.findall(r'\b(?:\d+(?:\.\d+)?|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', reference_answer))
    ref_tokens = {t.lower() for t in ref_tokens if len(t) > 2}

    if not ref_tokens:
        # No extractable tokens — fall back to substring containment
        # Check if significant portions overlap
        ref_words = set(norm_ref.split())
        final_words = set(norm_final.split())
        if not ref_words:
            return False
        overlap = len(ref_words & final_words) / len(ref_words)
        return overlap >= 0.6

    # Count how many reference tokens appear in the final answer
    matched = sum(1 for t in ref_tokens if t in norm_final)
    match_ratio = matched / len(ref_tokens)

    return match_ratio >= 0.6


def _extract_final_answer(text: str) -> str:
    """Extract the final answer from teacher's last message."""
    # Look for explicit "Final answer:" marker
    patterns = [
        r'(?:^|\n)\s*[Ff]inal\s+[Aa]nswer\s*:\s*(.*)',
        r'(?:^|\n)\s*[Aa]nswer\s*:\s*(.*)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()

    # No marker — use the full text as the answer
    return text.strip()


class TeacherAgent:
    """Generates SFT trajectories via teacher rollout + rejection sampling.

    Per DIVE §3.4: the teacher solves the task as a tool-using agent,
    producing a full trajectory τ. Rejection sampling keeps trajectories
    where verify(τ.final_answer, A) passes.
    """

    def __init__(
        self,
        kimi_client: KimiClient,
        max_tool_rounds: int = 10,
    ):
        self._kimi = kimi_client
        self._max_tool_rounds = max_tool_rounds

    def rollout(
        self,
        question: str,
        reference_answer: str,
        tool_executor: ToolExecutor,
        tool_schemas: list[dict[str, Any]],
    ) -> RolloutResult:
        """Run a single teacher rollout: solve the task, capture trajectory.

        Args:
            question: The task question Q.
            reference_answer: The reference answer A from D_task.
            tool_executor: ToolExecutor with live tool implementations.
            tool_schemas: OpenAI-format tool definitions (toolset T).

        Returns:
            RolloutResult with trajectory and verification status.
        """
        logger.info("Teacher rollout: Q='%s'", question[:80])

        # Build the user prompt with tool descriptions
        tool_desc = _build_tool_descriptions(tool_schemas)
        user_prompt = (
            f"Solve the following architecture question using the available tools.\n\n"
            f"Question: {question}\n\n"
            f"Available tools:\n{tool_desc}\n\n"
            f"Think step by step. Call tools to gather evidence. "
            f"Then provide your final answer starting with 'Final answer:'"
        )

        # System + user messages that start the trajectory
        system_msg = {"role": "system", "content": TEACHER_SYSTEM_PROMPT}
        user_msg = {"role": "user", "content": user_prompt}

        # Run the tool-calling loop, capturing the full trajectory
        trajectory_messages = [system_msg, user_msg]
        msgs = [system_msg, user_msg]
        tool_call_count = 0

        for round_num in range(self._max_tool_rounds):
            resp = self._kimi.chat(
                msgs, tools=tool_schemas,
                max_tokens=32768, stream=True,
            )
            choice = resp.choices[0]
            msg = choice.message

            if msg.tool_calls:
                # Build assistant message with reasoning + tool calls
                reasoning = getattr(msg, "reasoning_content", None) or ""
                content = msg.content or ""

                # Format assistant turn: <think> + <tool_call>
                assistant_parts = []
                if reasoning:
                    assistant_parts.append(f"<think>{reasoning}</think>")
                if content:
                    assistant_parts.append(content)

                tool_call_texts = []
                for tc in msg.tool_calls:
                    fn_name = tc.function.name
                    fn_args = tc.function.arguments
                    tool_call_texts.append(
                        f"<tool_call>{json.dumps({'name': fn_name, 'arguments': json.loads(fn_args) if fn_args else {}}, ensure_ascii=False)}</tool_call>"
                    )
                assistant_parts.extend(tool_call_texts)

                assistant_content = "\n".join(assistant_parts)
                trajectory_messages.append({
                    "role": "assistant",
                    "content": assistant_content,
                })

                # API-format assistant dict for continuing the conversation
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

                # Execute tools, capture observations
                for tc in msg.tool_calls:
                    fn_name = tc.function.name
                    try:
                        fn_args = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        fn_args = {"raw": tc.function.arguments}

                    logger.info("  Teacher tool call: %s", fn_name)
                    result = tool_executor(fn_name, fn_args)
                    result_str = json.dumps(result, ensure_ascii=False) if isinstance(result, (dict, list)) else str(result)
                    tool_call_count += 1

                    # Trajectory gets full tool output
                    trajectory_messages.append({
                        "role": "tool",
                        "content": result_str[:_MAX_TOOL_RESULT_CHARS * 2],
                    })

                    # API messages get truncated output
                    api_content = result_str
                    if len(api_content) > _MAX_TOOL_RESULT_CHARS:
                        api_content = api_content[:_MAX_TOOL_RESULT_CHARS] + "..."
                    msgs.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": api_content,
                    })

                logger.info(
                    "  Teacher round %d/%d: %d tool calls",
                    round_num + 1, self._max_tool_rounds, len(msg.tool_calls),
                )
            else:
                # Model finished — capture final answer
                reasoning = getattr(msg, "reasoning_content", None) or ""
                content = msg.content or ""

                final_parts = []
                if reasoning:
                    final_parts.append(f"<think>{reasoning}</think>")
                if content:
                    final_parts.append(content)

                final_content = "\n".join(final_parts)
                trajectory_messages.append({
                    "role": "assistant",
                    "content": final_content,
                })

                final_answer = _extract_final_answer(content)

                trajectory = Trajectory(
                    messages=trajectory_messages,
                    final_answer=final_answer,
                    tool_call_count=tool_call_count,
                )

                # Rejection sampling: verify(τ.final_answer, A)
                verified = verify_answer(final_answer, reference_answer)
                trajectory.verified = verified

                logger.info(
                    "Teacher rollout done: %d tool calls, verified=%s",
                    tool_call_count, verified,
                )

                return RolloutResult(
                    question=question,
                    reference_answer=reference_answer,
                    trajectory=trajectory,
                    verified=verified,
                )

        # Max rounds reached — extract whatever we have
        logger.warning("Teacher max rounds (%d) reached", self._max_tool_rounds)
        last = msgs[-1]
        last_content = last.get("content", "") if isinstance(last, dict) else getattr(last, "content", "") or ""
        final_answer = _extract_final_answer(last_content)

        trajectory = Trajectory(
            messages=trajectory_messages,
            final_answer=final_answer,
            tool_call_count=tool_call_count,
            verified=False,
        )

        verified = verify_answer(final_answer, reference_answer)
        trajectory.verified = verified

        return RolloutResult(
            question=question,
            reference_answer=reference_answer,
            trajectory=trajectory,
            verified=verified,
        )
