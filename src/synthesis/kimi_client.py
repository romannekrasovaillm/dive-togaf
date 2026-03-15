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
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
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

# Max chars for tool result in API messages (context management).
# Full results are preserved in tool_call_log for evidence.
_MAX_TOOL_RESULT_CHARS = 800

# Max chars for prompt/response debug logging (truncation limit).
_LOG_TRUNCATE_CHARS = 500


def _truncate_for_log(text: str, max_chars: int = _LOG_TRUNCATE_CHARS) -> str:
    """Truncate text for logging, preserving start and end."""
    if not text or len(text) <= max_chars:
        return text or ""
    half = max_chars // 2
    return f"{text[:half]}...({len(text)} chars total)...{text[-half:]}"


def _format_message_for_log(msg: dict | Any) -> str:
    """Format a single message for debug logging."""
    if isinstance(msg, dict):
        role = msg.get("role", "?")
        content = msg.get("content", "")
        tool_calls = msg.get("tool_calls")
    else:
        role = getattr(msg, "role", "?")
        content = getattr(msg, "content", "") or ""
        tool_calls = getattr(msg, "tool_calls", None)

    parts = [f"  [{role}]"]
    if content:
        parts.append(f" {_truncate_for_log(str(content))}")
    if tool_calls:
        tc_count = len(tool_calls) if isinstance(tool_calls, list) else 1
        parts.append(f" (tool_calls={tc_count})")
    return "".join(parts)


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
        verbose: bool = False,
    ):
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries
        self.verbose = verbose
        self._client = OpenAI(
            api_key=_get_api_key(),
            base_url=base_url,
            timeout=120.0,
        )
        # Session-level cache key for prompt caching (per Moonshot docs)
        self._cache_key = f"dive-togaf-{uuid.uuid4().hex[:12]}"
        self._call_seq = 0

    # ------------------------------------------------------------------
    # Prompt dump (verbose mode only)
    # ------------------------------------------------------------------

    def _dump_prompt(
        self,
        messages: list[dict[str, Any] | Any],
        tools: list[dict[str, Any]] | None,
        call_id: str,
    ) -> None:
        """Save full prompt to file for post-mortem analysis."""
        if not self.verbose:
            return

        dump_dir = Path("output/prompt_dumps")
        dump_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%H%M%S")
        filename = dump_dir / f"{timestamp}_{call_id}.json"

        # Serialize messages — handle both dicts and SDK objects
        serializable_msgs = []
        for m in messages:
            if isinstance(m, dict):
                serializable_msgs.append(m)
            else:
                # SDK object — extract fields
                serializable_msgs.append({
                    "role": getattr(m, "role", "unknown"),
                    "content": getattr(m, "content", None),
                    "reasoning_content_length": len(getattr(m, "reasoning_content", "") or ""),
                    "has_tool_calls": bool(getattr(m, "tool_calls", None)),
                })

        payload_json = json.dumps(serializable_msgs, ensure_ascii=False, default=str)
        payload_bytes = len(payload_json.encode("utf-8"))

        dump = {
            "timestamp": datetime.now().isoformat(),
            "call_id": call_id,
            "message_count": len(messages),
            "messages_summary": [
                {
                    "role": m.get("role") if isinstance(m, dict) else getattr(m, "role", "?"),
                    "content_length": len(str(m.get("content", "") if isinstance(m, dict) else getattr(m, "content", "") or "")),
                    "has_tool_calls": ("tool_calls" in m) if isinstance(m, dict) else bool(getattr(m, "tool_calls", None)),
                    "has_reasoning": bool(m.get("reasoning_content") if isinstance(m, dict) else getattr(m, "reasoning_content", None)),
                }
                for m in messages
            ],
            "full_messages": serializable_msgs,
            "tool_count": len(tools) if tools else 0,
            "total_payload_bytes": payload_bytes,
            "token_estimate": payload_bytes // 4,
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(dump, f, ensure_ascii=False, indent=2, default=str)

        logger.debug("Prompt dumped to %s", filename)

    # ------------------------------------------------------------------
    # Core API call
    # ------------------------------------------------------------------

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | None = None,
        temperature: float | None = None,
        max_tokens: int = 32768,
        stream: bool = False,
    ) -> ChatCompletion:
        """Send a chat completion request, with optional tool definitions."""
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

        # --- Payload size logging ---
        self._call_seq += 1
        payload_json = json.dumps(messages, ensure_ascii=False, default=str)
        payload_bytes = len(payload_json.encode("utf-8"))
        token_est = payload_bytes // 4
        logger.info(
            "API call #%d: %d messages, %d bytes (~%dk tokens est.), tools: %d",
            self._call_seq, len(messages), payload_bytes, token_est // 1000,
            len(tools) if tools else 0,
        )

        # --- Detailed prompt content logging (always, with truncation) ---
        for idx, m in enumerate(messages):
            logger.debug("  prompt[%d]: %s", idx, _format_message_for_log(m))

        # --- Prompt dump (verbose only) ---
        call_id = f"call{self._call_seq}"
        self._dump_prompt(messages, tools, call_id)

        last_err = None
        for attempt in range(1, self.max_retries + 1):
            try:
                start = time.monotonic()
                if stream:
                    result = self._handle_stream(kwargs)
                else:
                    result = self._client.chat.completions.create(**kwargs)
                elapsed = time.monotonic() - start

                # --- Response logging ---
                usage = getattr(result, "usage", None)
                finish = result.choices[0].finish_reason if result.choices else "?"
                if usage:
                    logger.info(
                        "API response #%d: %.1fs, finish=%s, prompt_tokens=%s, completion_tokens=%s, total=%s, cached=%s",
                        self._call_seq, elapsed, finish,
                        getattr(usage, "prompt_tokens", "?"),
                        getattr(usage, "completion_tokens", "?"),
                        getattr(usage, "total_tokens", "?"),
                        getattr(usage, "cached_tokens", "?"),
                    )
                else:
                    logger.info(
                        "API response #%d: %.1fs, finish=%s (no usage data)",
                        self._call_seq, elapsed, finish,
                    )

                # --- Detailed response content logging ---
                if result.choices:
                    resp_msg = result.choices[0].message
                    resp_content = getattr(resp_msg, "content", None) or ""
                    resp_tc = getattr(resp_msg, "tool_calls", None)
                    resp_reasoning = getattr(resp_msg, "reasoning_content", None)
                    logger.debug(
                        "  response content: %s", _truncate_for_log(resp_content),
                    )
                    if resp_tc:
                        for tc_idx, tc in enumerate(resp_tc):
                            fn = getattr(tc, "function", None) or tc.get("function", {}) if isinstance(tc, dict) else getattr(tc, "function", None)
                            fn_name = getattr(fn, "name", "?") if fn else "?"
                            fn_args = getattr(fn, "arguments", "") if fn else ""
                            logger.debug(
                                "  response tool_call[%d]: %s(%s)",
                                tc_idx, fn_name, _truncate_for_log(fn_args, 200),
                            )
                    if resp_reasoning:
                        logger.debug(
                            "  response reasoning: %s",
                            _truncate_for_log(resp_reasoning),
                        )
                return result
            except Exception as e:
                last_err = e
                elapsed = time.monotonic() - start

                # --- Enhanced error logging ---
                error_info: dict[str, Any] = {
                    "type": type(e).__name__,
                    "message": str(e)[:300],
                    "elapsed": f"{elapsed:.1f}s",
                    "payload_bytes": payload_bytes,
                    "message_count": len(messages),
                }
                status = getattr(e, "status_code", None)
                if status:
                    error_info["status_code"] = status
                resp = getattr(e, "response", None)
                if resp is not None:
                    error_info["response_status"] = getattr(resp, "status_code", None)
                    error_info["response_headers"] = {
                        k: v for k, v in getattr(resp, "headers", {}).items()
                        if k.lower() in ("retry-after", "x-ratelimit-remaining", "x-ratelimit-reset", "content-type")
                    }
                req = getattr(e, "request", None)
                if req is not None:
                    error_info["request_content_length"] = len(getattr(req, "content", b"") or b"")

                # Don't retry client errors (400, 401, 403) — they won't self-heal
                if status and 400 <= status < 500 and status != 429:
                    logger.error("Kimi API fatal error: %s", json.dumps(error_info, ensure_ascii=False, default=str))
                    raise
                if attempt < self.max_retries:
                    wait = 2 ** attempt
                    logger.warning(
                        "Kimi API attempt %d/%d failed: %s. Retry in %ds",
                        attempt, self.max_retries,
                        json.dumps(error_info, ensure_ascii=False, default=str),
                        wait,
                    )
                    time.sleep(wait)
        raise RuntimeError(f"Kimi API failed after {self.max_retries} attempts: {last_err}") from last_err

    # ------------------------------------------------------------------
    # Streaming handler
    # ------------------------------------------------------------------

    def _handle_stream(self, kwargs: dict[str, Any]) -> Any:
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
                if chunk.usage:
                    usage = chunk.usage
                continue

            delta = chunk.choices[0].delta
            completion_id = chunk.id or completion_id
            model = chunk.model or model

            if chunk.choices[0].finish_reason:
                finish_reason = chunk.choices[0].finish_reason

            if delta.content:
                content_parts.append(delta.content)

            rc = getattr(delta, "reasoning_content", None)
            if rc:
                reasoning_parts.append(rc)

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

    # ------------------------------------------------------------------
    # Convenience methods
    # ------------------------------------------------------------------

    def chat_text(
        self,
        messages: list[dict[str, Any]],
        temperature: float | None = None,
        max_tokens: int = 32768,
    ) -> str:
        """Simple text-only chat completion. Returns assistant content string.

        Uses streaming for thinking models (kimi-k2.5) to avoid
        connection timeouts on long reasoning responses.
        """
        use_stream = self.model in _FIXED_TEMP_MODELS or "thinking" in self.model
        resp = self.chat(
            messages, temperature=temperature,
            max_tokens=max_tokens, stream=use_stream,
        )
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
        - Preserve full reasoning_content
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
            resp = self.chat(
                msgs, tools=tools, temperature=temperature,
                max_tokens=max_tokens, stream=True,
            )
            choice = resp.choices[0]
            msg = choice.message

            if msg.tool_calls:
                # Convert to plain dict for JSON serialization (SimpleNamespace
                # from streaming is not serializable). Preserve full
                # reasoning_content per Moonshot thinking model docs.
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
                reasoning = getattr(msg, "reasoning_content", None)
                if reasoning:
                    assistant_dict["reasoning_content"] = reasoning
                msgs.append(assistant_dict)

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

                    # Log tool result with truncation
                    logger.debug(
                        "  tool result [%s]: %s",
                        fn_name, _truncate_for_log(result_str, 300),
                    )

                    # Full result → tool_call_log (evidence, never truncated)
                    tool_call_log.append({
                        "tool_name": fn_name,
                        "arguments": fn_args,
                        "result": result,
                    })

                    # Truncated result → API messages (context management)
                    api_content = result_str
                    if len(api_content) > _MAX_TOOL_RESULT_CHARS:
                        api_content = api_content[:_MAX_TOOL_RESULT_CHARS] + "..."
                    msgs.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": api_content,
                    })

                logger.info(
                    "Round %d/%d: %d tool calls, message count: %d",
                    round_num + 1, max_rounds, len(msg.tool_calls), len(msgs),
                )

                # Rate limit pacing — avoid hitting RPM/TPM limits
                time.sleep(2)
            else:
                # Model finished — return final text
                return msg.content or "", tool_call_log

        # Max rounds reached — return whatever we have
        logger.warning("Max tool-call rounds (%d) reached", max_rounds)
        last = msgs[-1]
        final = last.get("content", "") if isinstance(last, dict) else getattr(last, "content", "") or ""
        return final, tool_call_log
