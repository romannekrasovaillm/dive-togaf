from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from typing import Any, Dict

from src.tools.orchestrator import ToolOrchestrator
from src.tools.wrappers import WrapperExecutor


def fake_transport(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    if "worldbank.org" in url:
        return [
            {"page": 1, "pages": 1, "per_page": "50", "total": 3},
            [
                {"date": "2023", "value": 3.2, "country": {"id": params.get("country_code", "POL")}},
                {"date": "2022", "value": 1.1, "country": {"id": params.get("country_code", "POL")}},
                {"date": "2021", "value": 0.9, "country": {"id": params.get("country_code", "POL")}},
            ],
        ]

    if "timeframe" in url:
        return {
            "base": params["base"],
            "rates": {
                "2024-01-01": {"USD": 1.1},
                "2024-01-02": {"USD": 1.13},
                "2024-01-03": {"USD": 1.11},
            },
            "start_date": params["start_date"],
            "end_date": params["end_date"],
        }

    if "latest" in url:
        return {"date": "2024-01-03", "base": params["base"], "rates": {"USD": 1.12, "PLN": 4.4}}

    if "convert" in url:
        return {"query": params, "result": 112.0, "info": {"rate": 1.12}}

    raise ValueError(f"Unsupported URL in fake transport: {url}")


def build_executor() -> WrapperExecutor:
    return WrapperExecutor(config_path="config/tool_pool.yaml", transport=fake_transport)


def test_response_schema_shapes_are_correct() -> None:
    executor = build_executor()

    gdp = executor.execute("wb_get_gdp_growth", {"country_code": "POL", "date_range": "2021:2023"})["result"]
    assert isinstance(gdp, list)
    assert isinstance(gdp[1], list)
    assert {"date", "value"}.issubset(gdp[1][0].keys())

    trend = executor.execute("wb_process_trend_summary", {"series_payload": gdp})["result"]
    assert {"latest", "previous", "delta", "trend"}.issubset(trend.keys())

    fx = executor.execute(
        "fx_get_timeseries",
        {"base": "EUR", "symbols": "USD", "start_date": "2024-01-01", "end_date": "2024-01-03"},
    )["result"]
    assert {"base", "rates", "start_date", "end_date"}.issubset(fx.keys())

    vol = executor.execute("fx_process_volatility", {"timeseries_payload": fx})["result"]
    assert {"pair", "avg", "stdev", "volatility_bucket"}.issubset(vol.keys())


def test_repeat_calls_are_consistent() -> None:
    executor = build_executor()
    payload = {"base": "EUR", "symbols": "USD", "start_date": "2024-01-01", "end_date": "2024-01-03"}

    first = executor.execute("fx_get_timeseries", deepcopy(payload))["result"]
    second = executor.execute("fx_get_timeseries", deepcopy(payload))["result"]
    assert first == second

    first_vol = executor.execute("fx_process_volatility", {"timeseries_payload": first})["result"]
    second_vol = executor.execute("fx_process_volatility", {"timeseries_payload": second})["result"]
    assert first_vol == second_vol


def test_parallel_calls_are_session_isolated() -> None:
    executor = build_executor()
    def run_for_country(country: str) -> Dict[str, Any]:
        orchestrator = ToolOrchestrator(executor=executor)
        scenario = {
            "steps": [
                {
                    "wrapper": "wb_get_gdp_growth",
                    "params": {"country_code": country, "date_range": "2021:2023"},
                    "store_as": "series_payload",
                },
                {"wrapper": "wb_process_trend_summary", "params": {}, "store_as": "trend_summary"},
            ]
        }
        return orchestrator.run(scenario)

    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(run_for_country, ["POL", "KAZ", "CZE"]))

    for result in results:
        trend_summary = result["context"]["trend_summary"]
        assert trend_summary["trend"] in {"up", "down", "flat", "insufficient_data"}
        assert "series_payload" in result["context"]
