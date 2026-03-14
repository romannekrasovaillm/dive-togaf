"""Kimi/Moonshot API client using OpenAI-compatible SDK.

Env var: KIMI_API_KEY (or MOONSHOT_API_KEY)
Base URL: https://api.moonshot.cn/v1
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

from openai import OpenAI
from openai.types.chat import ChatCompletion

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.moonshot.cn/v1"
DEFAULT_MODEL = "kimi-k2.5"


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
        max_retries: int = 3,
    ):
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries
        self._client = OpenAI(
            api_key=_get_api_key(),
            base_url=base_url,
        )

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | None = None,
        temperature: float | None = None,
        max_tokens: int = 4096,
    ) -> ChatCompletion:
        """Send a chat completion request, with optional tool definitions.

        Returns the raw ChatCompletion object.
        """
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice or "auto"

        last_err = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self._client.chat.completions.create(**kwargs)
                return response
            except Exception as e:
                last_err = e
                if attempt < self.max_retries:
                    wait = 2 ** attempt
                    logger.warning("Kimi API attempt %d failed: %s. Retry in %ds", attempt, e, wait)
                    time.sleep(wait)
        raise RuntimeError(f"Kimi API failed after {self.max_retries} attempts: {last_err}") from last_err

    def chat_text(
        self,
        messages: list[dict[str, Any]],
        temperature: float | None = None,
        max_tokens: int = 4096,
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
        max_tokens: int = 4096,
    ) -> tuple[str, list[dict[str, Any]]]:
        """Run a tool-calling loop until the model finishes or max_rounds reached.

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

        for _ in range(max_rounds):
            resp = self.chat(msgs, tools=tools, temperature=temperature, max_tokens=max_tokens)
            choice = resp.choices[0]
            msg = choice.message

            # If model returned tool calls
            if msg.tool_calls:
                # Append assistant message with tool calls
                msgs.append({
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
                })

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
            else:
                # Model finished — return final text
                return msg.content or "", tool_call_log

        # Max rounds reached — return whatever we have
        logger.warning("Max tool-call rounds (%d) reached", max_rounds)
        return msgs[-1].get("content", "") if isinstance(msgs[-1], dict) else "", tool_call_log
