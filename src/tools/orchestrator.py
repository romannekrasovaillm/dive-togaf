from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from src.tools.wrappers import WrapperExecutor


@dataclass
class ToolOrchestrator:
    executor: WrapperExecutor
    trace: List[Dict[str, Any]] = field(default_factory=list)

    def run(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        context: Dict[str, Any] = {}
        evidence: List[Dict[str, Any]] = []

        for step in scenario.get("steps", []):
            wrapper = step["wrapper"]
            params = step.get("params", {})
            output = self.executor.execute(wrapper, params, context=context)
            key = step.get("store_as")
            if key:
                context[key] = output["result"]
            evidence.append(output)
            self.trace.append(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "wrapper": wrapper,
                    "store_as": key,
                    "result_shape": self._describe_shape(output["result"]),
                }
            )

        return {"context": context, "evidence": evidence, "trace": self.trace}

    @staticmethod
    def _describe_shape(payload: Any) -> str:
        if isinstance(payload, dict):
            return f"dict:{','.join(sorted(payload.keys()))}"
        if isinstance(payload, list):
            return f"list:{len(payload)}"
        return type(payload).__name__
