"""Kimi/Moonshot API client using OpenAI-compatible SDK.

Env var: KIMI_API_KEY (or MOONSHOT_API_KEY)
Base URL: https://api.moonshot.ai/v1
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from typing import Any

from openai import OpenAI
from openai.types.chat import ChatCompletion

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.moonshot.ai/v1"
DEFAULT_MODEL = "kimi-k2.5"

# Models where temperature/top_p/n/presence_penalty/frequency_penalty cannot be modified
_FIXED_TEMP_MODELS = {"kimi-k2.5"}

# Thinking models require max_tokens >= 16000 (reasoning_content + content)
_THINKING_MIN_TOKENS = 32768


def _get_api_key() -> str:
    key = os.environ.get("KIMI_API_KEY") or os.environ.get("MOONSHOT_API_KEY")
    if not key:
        raise EnvironmentError(
            "Set KIMI_API_KEY or MOONSHOT_API_KEY environment variable. "
            "Get your key at https://platform.moonshot.ai/"
        )
    return key


class KimiClient:
    """Thin wrapper around OpenAI SDK configured for Moonshot/Kimi API."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
        temperature: float = 0.6,
        max_retries: int = 5,
    ):
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries
        self._client = OpenAI(
            api_key=_get_api_key(),
            base_url=base_url,
            timeout=120.0,
        )
        # Session-level cache key for prompt caching (per Moonshot docs)
        self._cache_key = f"dive-togaf-{uuid.uuid4().hex[:12]}"

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | None = None,
        temperature: float | None = None,
        max_tokens: int = 32768,
        stream: bool = False,
    ) -> ChatCompletion:
        """Send a chat completion request, with optional tool definitions.

        Returns the raw ChatCompletion object.
        """
        # Thinking models need >= 16000 tokens for reasoning_content + content
        if self.model in _FIXED_TEMP_MODELS or "thinking" in self.model:
            max_tokens = max(max_tokens, _THINKING_MIN_TOKENS)

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_completion_tokens": max_tokens,
            "prompt_cache_key": self._cache_key,
        }
        # kimi-k2.5 does not allow temperature to be set
        if self.model not in _FIXED_TEMP_MODELS:
            kwargs["temperature"] = temperature if temperature is not None else self.temperature
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice or "auto"
        if stream:
            kwargs["stream"] = True

        last_err = None
        for attempt in range(1, self.max_retries + 1):
            try:
                if stream:
                    return self._handle_stream(kwargs)
                response = self._client.chat.completions.create(**kwargs)
                return response
            except Exception as e:
                last_err = e
                # Don't retry client errors (400, 401, 403) — they won't self-heal
                status = getattr(e, "status_code", None)
                if status and 400 <= status < 500 and status != 429:
                    logger.error("Kimi API fatal error (HTTP %d): %s", status, e)
                    raise
                if attempt < self.max_retries:
                    wait = 2 ** attempt
                    logger.warning("Kimi API attempt %d/%d failed: %s. Retry in %ds", attempt, self.max_retries, e, wait)
                    time.sleep(wait)
        raise RuntimeError(f"Kimi API failed after {self.max_retries} attempts: {last_err}") from last_err

    def _handle_stream(self, kwargs: dict[str, Any]) -> ChatCompletion:
        """Consume a streaming response and reconstruct a ChatCompletion-like object.

        Streaming avoids connection timeouts for long-running thinking responses.
        """
        kwargs["stream_options"] = {"include_usage": True}
        stream = self._client.chat.completions.create(**kwargs)

        content_parts: list[str] = []
        reasoning_parts: list[str] = []
        tool_calls_map: dict[int, dict[str, Any]] = {}
        finish_reason = None
        model = ""
        completion_id = ""
        usage = None

        for chunk in stream:
            if not chunk.choices:
                # Final usage-only chunk
                if chunk.usage:
                    usage = chunk.usage
                continue

            delta = chunk.choices[0].delta
            completion_id = chunk.id or completion_id
            model = chunk.model or model

            if chunk.choices[0].finish_reason:
                finish_reason = chunk.choices[0].finish_reason

            # Content
            if delta.content:
                content_parts.append(delta.content)

            # Reasoning content (thinking)
            rc = getattr(delta, "reasoning_content", None)
            if rc:
                reasoning_parts.append(rc)

            # Tool calls (accumulated by index)
            if delta.tool_calls:
                for tc_delta in delta.tool_calls:
                    idx = tc_delta.index
                    if idx not in tool_calls_map:
                        tool_calls_map[idx] = {
                            "id": tc_delta.id or "",
                            "type": "function",
                            "function": {"name": "", "arguments": ""},
                        }
                    entry = tool_calls_map[idx]
                    if tc_delta.id:
                        entry["id"] = tc_delta.id
                    if tc_delta.function:
                        if tc_delta.function.name:
                            entry["function"]["name"] += tc_delta.function.name
                        if tc_delta.function.arguments:
                            entry["function"]["arguments"] += tc_delta.function.arguments

        # Build a mock ChatCompletion-like object
        from types import SimpleNamespace

        tool_calls_list = None
        if tool_calls_map:
            tool_calls_list = []
            for idx in sorted(tool_calls_map):
                tc = tool_calls_map[idx]
                tool_calls_list.append(SimpleNamespace(
                    id=tc["id"],
                    type="function",
                    function=SimpleNamespace(
                        name=tc["function"]["name"],
                        arguments=tc["function"]["arguments"],
                    ),
                ))

        message = SimpleNamespace(
            role="assistant",
            content="".join(content_parts) or None,
            tool_calls=tool_calls_list,
            reasoning_content="".join(reasoning_parts) or None,
        )

        choice = SimpleNamespace(
            index=0,
            message=message,
            finish_reason=finish_reason,
        )

        return SimpleNamespace(
            id=completion_id,
            model=model,
            choices=[choice],
            usage=usage,
        )

    def chat_text(
        self,
        messages: list[dict[str, Any]],
        temperature: float | None = None,
        max_tokens: int = 32768,
    ) -> str:
        """Simple text-only chat completion. Returns assistant content string."""
        resp = self.chat(messages, temperature=temperature, max_tokens=max_tokens)
        return resp.choices[0].message.content or ""

    def chat_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        tool_executor: Any,
        max_rounds: int = 10,
        temperature: float | None = None,
        max_tokens: int = 32768,
    ) -> tuple[str, list[dict[str, Any]]]:
        """Run a tool-calling loop until the model finishes or max_rounds reached.

        Uses streaming to avoid connection timeouts on long-running thinking
        responses. Per Moonshot docs for thinking models:
        - Append the assistant message object directly (preserves reasoning_content)
        - max_tokens >= 16000 for reasoning_content + content
        - stream = true to avoid timeouts

        Args:
            messages: Conversation history.
            tools: OpenAI-format tool definitions.
            tool_executor: Callable(name, arguments) -> str that executes a tool.
            max_rounds: Maximum tool-call rounds.
            temperature: Override temperature.
            max_tokens: Max tokens per response.

        Returns:
            (final_text, tool_call_log) where tool_call_log is a list of
            {tool_name, arguments, result} dicts.
        """
        tool_call_log: list[dict[str, Any]] = []
        msgs = list(messages)

        for round_num in range(max_rounds):
            # Use streaming to prevent connection timeouts during long thinking
            resp = self.chat(
                msgs, tools=tools, temperature=temperature,
                max_tokens=max_tokens, stream=True,
            )
            choice = resp.choices[0]
            msg = choice.message

            # If model returned tool calls
            if msg.tool_calls:
                # Append the assistant message directly (per Moonshot docs).
                # This preserves reasoning_content intact — "the model will
                # decide which parts are necessary and forward them."
                msgs.append(msg)

                # Execute each tool call and append results
                for tc in msg.tool_calls:
                    fn_name = tc.function.name
                    try:
                        fn_args = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        fn_args = {"raw": tc.function.arguments}

                    logger.info("Tool call: %s(%s)", fn_name, json.dumps(fn_args, ensure_ascii=False)[:200])
                    result = tool_executor(fn_name, fn_args)
                    result_str = json.dumps(result, ensure_ascii=False) if isinstance(result, (dict, list)) else str(result)

                    tool_call_log.append({
                        "tool_name": fn_name,
                        "arguments": fn_args,
                        "result": result,
                    })

                    msgs.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result_str,
                    })

                logger.info(
                    "Round %d/%d: %d tool calls, message count: %d",
                    round_num + 1, max_rounds, len(msg.tool_calls), len(msgs),
                )
            else:
                # Model finished — return final text
                return msg.content or "", tool_call_log

        # Max rounds reached — return whatever we have
        logger.warning("Max tool-call rounds (%d) reached", max_rounds)
        last = msgs[-1]
        final = last.get("content", "") if isinstance(last, dict) else getattr(last, "content", "") or ""
        return final, tool_call_log
