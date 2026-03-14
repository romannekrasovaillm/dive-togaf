from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field
from statistics import mean, pstdev
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlencode
from urllib.request import urlopen



TransportFn = Callable[[str, Dict[str, Any]], Dict[str, Any]]


@dataclass
class WrapperExecutor:
    """Executes retrieval and processing wrappers from tool_pool config."""

    config_path: str = "config/tool_pool.yaml"
    transport: Optional[TransportFn] = None
    timeout: int = 20
    _config: Dict[str, Any] = field(init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def __post_init__(self) -> None:
        with open(self.config_path, "r", encoding="utf-8") as file:
            self._config = json.load(file)

    @property
    def config(self) -> Dict[str, Any]:
        return self._config

    def execute(self, wrapper_name: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        method_name = f"_run_{wrapper_name}"
        if not hasattr(self, method_name):
            raise ValueError(f"Wrapper '{wrapper_name}' is not implemented")
        method = getattr(self, method_name)
        result = method(params, context)
        return {"wrapper": wrapper_name, "result": result}

    def _request_json(self, base_url: str, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if self.transport:
            return self.transport(f"{base_url}{endpoint}", params)

        query = urlencode(params)
        url = f"{base_url}{endpoint}?{query}" if query else f"{base_url}{endpoint}"
        with urlopen(url, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    # --- World Bank wrappers ---
    def _run_wb_get_gdp_growth(self, params: Dict[str, Any], _: Dict[str, Any]) -> Any:
        return self._world_bank_indicator(params["country_code"], "NY.GDP.MKTP.KD.ZG", params["date_range"])

    def _run_wb_get_financial_access(self, params: Dict[str, Any], _: Dict[str, Any]) -> Any:
        return self._world_bank_indicator(params["country_code"], "FB.ATM.TOTL.P5", params["date_range"])

    def _run_wb_get_regulatory_quality(self, params: Dict[str, Any], _: Dict[str, Any]) -> Any:
        return self._world_bank_indicator(params["country_code"], "IQ.CPA.REGQ.XQ", params["date_range"])

    def _world_bank_indicator(self, country_code: str, indicator: str, date_range: str) -> Any:
        return self._request_json(
            "https://api.worldbank.org/v2",
            f"/country/{country_code}/indicator/{indicator}",
            {"format": "json", "date": date_range},
        )

    def _run_wb_process_trend_summary(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        payload = params.get("series_payload") or context.get("series_payload")
        records = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
        cleaned = [r for r in records if r.get("value") is not None]
        if len(cleaned) < 2:
            return {"latest": None, "previous": None, "delta": None, "trend": "insufficient_data"}

        latest = float(cleaned[0]["value"])
        previous = float(cleaned[1]["value"])
        delta = latest - previous
        trend = "up" if delta > 0 else "down" if delta < 0 else "flat"
        return {"latest": latest, "previous": previous, "delta": delta, "trend": trend}

    def _run_wb_process_risk_flags(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        summary = params.get("trend_summary") or context.get("trend_summary", {})
        thresholds = params.get("thresholds", {"high": -2.0, "medium": 0.0})
        delta = summary.get("delta")

        if delta is None:
            return {"risk_level": "unknown", "flags": ["no_data"], "recommendation": "collect_more_data"}

        if delta <= thresholds["high"]:
            return {"risk_level": "high", "flags": ["negative_macro_shift"], "recommendation": "increase_governance_controls"}
        if delta <= thresholds["medium"]:
            return {"risk_level": "medium", "flags": ["slowdown"], "recommendation": "monitor_quarterly"}
        return {"risk_level": "low", "flags": ["stable_or_improving"], "recommendation": "proceed_with_transition"}

    # --- FX wrappers ---
    def _run_fx_get_latest(self, params: Dict[str, Any], _: Dict[str, Any]) -> Any:
        return self._request_json(
            "https://api.exchangerate.host",
            "/latest",
            {"base": params["base"], "symbols": params["symbols"]},
        )

    def _run_fx_get_timeseries(self, params: Dict[str, Any], _: Dict[str, Any]) -> Any:
        return self._request_json(
            "https://api.exchangerate.host",
            "/timeframe",
            {
                "base": params["base"],
                "symbols": params["symbols"],
                "start_date": params["start_date"],
                "end_date": params["end_date"],
            },
        )

    def _run_fx_get_convert(self, params: Dict[str, Any], _: Dict[str, Any]) -> Any:
        return self._request_json(
            "https://api.exchangerate.host",
            "/convert",
            {"from": params["from_currency"], "to": params["to_currency"], "amount": params["amount"]},
        )

    def _run_fx_process_volatility(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        payload = params.get("timeseries_payload") or context.get("timeseries_payload", {})
        rates = payload.get("rates", {})
        if not rates:
            return {"pair": None, "avg": None, "stdev": None, "volatility_bucket": "unknown"}

        first_day = next(iter(rates.values()))
        pair = next(iter(first_day.keys()))
        points: List[float] = [float(day[pair]) for day in rates.values() if pair in day]
        avg = mean(points)
        deviation = pstdev(points) if len(points) > 1 else 0.0
        bucket = "high" if deviation > 0.03 else "medium" if deviation > 0.01 else "low"
        return {"pair": pair, "avg": round(avg, 6), "stdev": round(deviation, 6), "volatility_bucket": bucket}

    def _run_fx_process_compliance_exposure(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        payload = params.get("latest_payload") or context.get("latest_payload", {})
        limits = params.get("policy_limits", {})
        rates = payload.get("rates", {})

        breaches = []
        for symbol, rate in rates.items():
            max_rate = limits.get(symbol)
            if max_rate is not None and float(rate) > float(max_rate):
                breaches.append({"symbol": symbol, "rate": rate, "limit": max_rate})

        score = min(100, len(breaches) * 20)
        action = "escalate_to_architecture_board" if breaches else "within_limits"
        return {"exposure_score": score, "breaches": breaches, "action": action}
