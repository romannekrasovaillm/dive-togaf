"""Tool executor: dispatches tool calls to real or LLM-simulated implementations.

Live tools (NetworkX graph analysis, ArchiMate parser, Wikipedia, Wikidata)
execute against real libraries. All other tools from the pool are simulated
by the LLM using the tool's definition, parameters, and seed context to
produce domain-realistic structured outputs.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


# =====================================================================
# Live tool registry — maps tool names to real implementations
# =====================================================================

_LIVE_TOOLS: dict[str, Callable[..., Any]] = {}


def _register_live_tools() -> None:
    """Import and register available live tool implementations."""
    global _LIVE_TOOLS
    if _LIVE_TOOLS:
        return

    # NetworkX graph tools
    try:
        from src.pools.live_tools.networkx_tools import (
            graph_get_node_info,
            graph_get_neighbors,
            graph_get_subgraph,
            graph_get_paths,
            graph_get_layer_nodes,
            graph_list_relationship_types,
            graph_get_elements_by_type,
            graph_search_nodes,
            graph_compute_centrality,
            graph_compute_coupling,
            graph_compute_layer_metrics,
            graph_detect_cycles,
            graph_compute_impact_analysis,
            graph_compute_critical_path,
            graph_compute_clustering,
            graph_compute_dependency_matrix,
            graph_compute_component_health,
            graph_compute_complexity_metrics,
            graph_compute_change_impact_score,
            graph_detect_architecture_smells,
        )
        _LIVE_TOOLS.update({
            "graph_get_node_info": graph_get_node_info,
            "graph_get_neighbors": graph_get_neighbors,
            "graph_get_subgraph": graph_get_subgraph,
            "graph_get_paths": graph_get_paths,
            "graph_get_layer_nodes": graph_get_layer_nodes,
            "graph_list_relationship_types": graph_list_relationship_types,
            "graph_get_elements_by_type": graph_get_elements_by_type,
            "graph_search_nodes": graph_search_nodes,
            "graph_compute_centrality": graph_compute_centrality,
            "graph_compute_coupling": graph_compute_coupling,
            "graph_compute_layer_metrics": graph_compute_layer_metrics,
            "graph_detect_cycles": graph_detect_cycles,
            "graph_compute_impact_analysis": graph_compute_impact_analysis,
            "graph_compute_critical_path": graph_compute_critical_path,
            "graph_compute_clustering": graph_compute_clustering,
            "graph_compute_dependency_matrix": graph_compute_dependency_matrix,
            "graph_compute_component_health": graph_compute_component_health,
            "graph_compute_complexity_metrics": graph_compute_complexity_metrics,
            "graph_compute_change_impact_score": graph_compute_change_impact_score,
            "graph_detect_architecture_smells": graph_detect_architecture_smells,
        })
        logger.info("Registered %d NetworkX live tools", 20)
    except ImportError as e:
        logger.warning("NetworkX tools unavailable: %s", e)

    # ArchiMate parser tools
    try:
        from src.pools.live_tools.archimate_parser_tools import (
            archimate_parse_model,
            archimate_list_elements,
            archimate_get_element,
            archimate_list_relationships,
            archimate_get_relationships_for,
            archimate_list_views,
            archimate_get_view_elements,
            archimate_get_properties,
            archimate_search,
            archimate_model_stats,
        )
        _LIVE_TOOLS.update({
            "archimate_parse_model": archimate_parse_model,
            "archimate_list_elements": archimate_list_elements,
            "archimate_get_element": archimate_get_element,
            "archimate_list_relationships": archimate_list_relationships,
            "archimate_get_relationships_for": archimate_get_relationships_for,
            "archimate_list_views": archimate_list_views,
            "archimate_get_view_elements": archimate_get_view_elements,
            "archimate_get_properties": archimate_get_properties,
            "archimate_search": archimate_search,
            "archimate_model_stats": archimate_model_stats,
        })
        logger.info("Registered %d ArchiMate parser live tools", 10)
    except ImportError as e:
        logger.warning("ArchiMate tools unavailable: %s", e)

    # Wikipedia / Wikidata tools
    try:
        from src.pools.live_tools.wikipedia_tools import (
            wikipedia_search,
            wikipedia_get_summary,
            wikipedia_get_sections,
            wikipedia_get_links,
            wikipedia_get_categories,
            github_search_repos,
            github_get_repo_info,
            github_get_repo_languages,
            github_get_repo_topics,
            github_search_code,
        )
        _LIVE_TOOLS.update({
            "wikipedia_search": wikipedia_search,
            "wikipedia_get_summary": wikipedia_get_summary,
            "wikipedia_get_sections": wikipedia_get_sections,
            "wikipedia_get_links": wikipedia_get_links,
            "wikipedia_get_categories": wikipedia_get_categories,
            "github_search_repos": github_search_repos,
            "github_get_repo_info": github_get_repo_info,
            "github_get_repo_languages": github_get_repo_languages,
            "github_get_repo_topics": github_get_repo_topics,
            "github_search_code": github_search_code,
        })
        logger.info("Registered %d Wikipedia/GitHub live tools", 10)
    except ImportError as e:
        logger.warning("Wikipedia/GitHub tools unavailable: %s", e)


def _build_tool_index(tool_pool: list[dict]) -> dict[str, dict]:
    """Build a lookup from tool id to tool definition."""
    index: dict[str, dict] = {}
    for tool in tool_pool:
        index[tool["id"]] = tool
        # Also index by name for fuzzy matching
        index[tool["name"]] = tool
    return index


class ToolExecutor:
    """Executes tool calls — real implementations when available, LLM-simulated otherwise."""

    def __init__(
        self,
        tool_pool: list[dict],
        kimi_client: Any,
        seed_context: str = "",
    ):
        """
        Args:
            tool_pool: List of tool definition dicts from the pool.
            kimi_client: KimiClient instance for simulating tool outputs.
            seed_context: Description of the current seed for context.
        """
        _register_live_tools()
        self._tool_index = _build_tool_index(tool_pool)
        self._kimi = kimi_client
        self._seed_context = seed_context
        self._call_count = 0

    def __call__(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Execute a tool call. Returns structured result."""
        self._call_count += 1

        # Try live execution first
        if tool_name in _LIVE_TOOLS:
            try:
                result = _LIVE_TOOLS[tool_name](**arguments)
                logger.info("Live tool '%s' executed successfully", tool_name)
                return result
            except Exception as e:
                logger.warning("Live tool '%s' failed: %s, falling back to simulation", tool_name, e)

        # LLM-simulated execution
        return self._simulate_tool(tool_name, arguments)

    def _simulate_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Use LLM to generate realistic tool output based on definition."""
        tool_def = self._tool_index.get(tool_name, {})
        tool_desc = tool_def.get("description", f"Tool: {tool_name}")
        return_schema = tool_def.get("return_schema", {})
        examples = tool_def.get("examples", [])

        example_str = ""
        if examples:
            example_str = f"\n\nExample output:\n{json.dumps(examples[0].get('response', {}), indent=2, ensure_ascii=False)}"

        prompt = f"""You are a TOGAF/ArchiMate architecture tool simulator. Generate a realistic, detailed JSON output for the following tool call.

CONTEXT: {self._seed_context}

TOOL: {tool_name}
DESCRIPTION: {tool_desc}
ARGUMENTS: {json.dumps(arguments, ensure_ascii=False)}
RETURN SCHEMA: {json.dumps(return_schema, ensure_ascii=False)}{example_str}

RULES:
- Return ONLY valid JSON matching the return schema
- Generate realistic, domain-accurate data (use real TOGAF/ArchiMate terminology)
- Include specific names, numbers, and concrete details — not placeholders
- Data should be internally consistent and plausible for the given context
- Do NOT wrap in markdown code blocks — return raw JSON only"""

        response = self._kimi.chat_text(
            messages=[
                {"role": "system", "content": "You are a precise architecture data generator. Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=2048,
        )

        # Parse JSON from response
        try:
            # Strip any markdown code fences
            text = response.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse simulated tool output as JSON for '%s'", tool_name)
            return {"raw_output": response, "tool_name": tool_name, "parse_error": True}

    @property
    def call_count(self) -> int:
        return self._call_count

    def get_openai_tool_schemas(self, tool_subset: list[dict]) -> list[dict]:
        """Convert pool tool definitions to OpenAI-format tool schemas."""
        schemas = []
        for tool in tool_subset:
            params_props = {}
            required = []
            for p in tool.get("parameters", []):
                prop: dict[str, Any] = {"type": p["type"], "description": p["description"]}
                if p.get("enum"):
                    prop["enum"] = p["enum"]
                params_props[p["name"]] = prop
                if p.get("required", True):
                    required.append(p["name"])

            schemas.append({
                "type": "function",
                "function": {
                    "name": tool["id"],
                    "description": tool["description"],
                    "parameters": {
                        "type": "object",
                        "properties": params_props,
                        "required": required,
                    },
                },
            })
        return schemas
