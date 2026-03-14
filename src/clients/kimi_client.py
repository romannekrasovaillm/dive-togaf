from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from src.tools.orchestrator import ToolOrchestrator
from src.tools.wrappers import WrapperExecutor


@dataclass
class KimiClient:
    config_path: str = "config/tool_pool.yaml"

    def __post_init__(self) -> None:
        self.executor = WrapperExecutor(config_path=self.config_path)
        self.orchestrator = ToolOrchestrator(executor=self.executor)

    @staticmethod
    def build_prompt() -> str:
        return (
            "Исследуй Banking Core Modernization в домене TOGAF. "
            "Используй разные инструменты для сбора верифицируемой информации."
        )

    def run_research(self, country_code: str = "POL") -> Dict[str, Any]:
        scenario = {
            "steps": [
                {
                    "wrapper": "wb_get_gdp_growth",
                    "params": {"country_code": country_code, "date_range": "2019:2023"},
                    "store_as": "series_payload",
                },
                {
                    "wrapper": "wb_process_trend_summary",
                    "params": {},
                    "store_as": "trend_summary",
                },
                {
                    "wrapper": "wb_process_risk_flags",
                    "params": {"thresholds": {"high": -1.0, "medium": 0.5}},
                    "store_as": "macro_risk",
                },
                {
                    "wrapper": "fx_get_timeseries",
                    "params": {
                        "base": "EUR",
                        "symbols": "USD,PLN",
                        "start_date": "2024-01-01",
                        "end_date": "2024-01-10",
                    },
                    "store_as": "timeseries_payload",
                },
                {
                    "wrapper": "fx_process_volatility",
                    "params": {},
                    "store_as": "fx_volatility",
                },
            ]
        }

        run_result = self.orchestrator.run(scenario)
        return {
            "prompt": self.build_prompt(),
            "tool_pool": self.executor.config,
            "evidence": run_result["evidence"],
            "trace": run_result["trace"],
            "summary": self._build_summary(run_result["context"]),
        }

    @staticmethod
    def _build_summary(context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "macro_risk": context.get("macro_risk", {}),
            "fx_volatility": context.get("fx_volatility", {}),
            "next_adm_focus": [
                "ADM E: Migration Planning (prioritize low-volatility windows)",
                "ADM G: Compliance assessment for identified macro/fx risks",
            ],
        }


def main() -> None:
    client = KimiClient()
    result = client.run_research()
    print(result["prompt"])
    print(f"Collected evidence items: {len(result['evidence'])}")


if __name__ == "__main__":
    main()
