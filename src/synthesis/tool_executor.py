"""Tool executor: dispatches tool calls to real or LLM-simulated implementations.

Live tools include:
- TOGAF ADM reference tools (phases, deliverables, techniques)
- Repository, Governance, General domain reference tools (BIAN, compliance, etc.)
- ArchiMate reference tools (elements, viewpoints, analysis)
- NetworkX graph analysis tools
- ArchiMate XML parser tools (lxml)
- GitHub API tools

All other tools from the pool are simulated by the LLM using the tool's
definition, parameters, and seed context to produce domain-realistic
structured outputs. Simulated results are marked with `_simulated: true`.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Callable

logger = logging.getLogger(__name__)


# =====================================================================
# Live tool registry — maps tool IDs to real implementations
# =====================================================================

_LIVE_TOOLS: dict[str, Callable[..., Any]] = {}


def _register_live_tools() -> None:
    """Import and register available live tool implementations."""
    global _LIVE_TOOLS
    if _LIVE_TOOLS:
        return

    # --- TOGAF ADM reference tools (phases, deliverables, techniques) ---
    try:
        from src.pools.live_tools.togaf_adm_tools import TOOL_REGISTRY as adm_registry
        _LIVE_TOOLS.update(adm_registry)
        logger.info("Registered %d TOGAF ADM live tools", len(adm_registry))
    except ImportError as e:
        logger.warning("TOGAF ADM tools unavailable: %s", e)

    # --- Repository, Governance, General reference tools ---
    try:
        from src.pools.live_tools.repository_reference_tools import TOOL_REGISTRY as repo_registry
        _LIVE_TOOLS.update(repo_registry)
        logger.info("Registered %d Repository/Governance/General live tools", len(repo_registry))
    except ImportError as e:
        logger.warning("Repository/Governance tools unavailable: %s", e)

    # --- ArchiMate reference tools (elements, viewpoints, analysis) ---
    try:
        from src.pools.live_tools.archimate_reference_tools import TOOL_REGISTRY as archimate_ref_registry
        _LIVE_TOOLS.update(archimate_ref_registry)
        logger.info("Registered %d ArchiMate reference live tools", len(archimate_ref_registry))
    except ImportError as e:
        logger.warning("ArchiMate reference tools unavailable: %s", e)

    # --- NetworkX graph tools ---
    try:
        from src.pools.live_tools.networkx_tools import (
            graph_get_node_info,
            graph_find_neighbors,
            graph_find_paths,
            graph_get_components,
            graph_find_cycles,
            graph_get_leaf_nodes,
            graph_get_bridges,
            graph_get_subgraph,
            graph_compute_centrality,
            graph_compute_coupling,
            graph_compute_critical_path,
            graph_compute_impact_score,
            graph_compute_modularity,
            graph_compute_topology_metrics,
            graph_compute_dependency_depth,
            graph_compute_similarity,
            graph_compute_topological_sort,
            graph_compute_clustering,
            graph_compute_gap_analysis,
            graph_compute_layer_crossing,
        )
        _LIVE_TOOLS.update({
            "graph_get_node_info": graph_get_node_info,
            "graph_find_neighbors": graph_find_neighbors,
            "graph_find_paths": graph_find_paths,
            "graph_get_components": graph_get_components,
            "graph_find_cycles": graph_find_cycles,
            "graph_get_leaf_nodes": graph_get_leaf_nodes,
            "graph_get_bridges": graph_get_bridges,
            "graph_get_subgraph": graph_get_subgraph,
            "graph_compute_centrality": graph_compute_centrality,
            "graph_compute_coupling": graph_compute_coupling,
            "graph_compute_critical_path": graph_compute_critical_path,
            "graph_compute_impact_score": graph_compute_impact_score,
            "graph_compute_modularity": graph_compute_modularity,
            "graph_compute_topology_metrics": graph_compute_topology_metrics,
            "graph_compute_dependency_depth": graph_compute_dependency_depth,
            "graph_compute_similarity": graph_compute_similarity,
            "graph_compute_topological_sort": graph_compute_topological_sort,
            "graph_compute_clustering": graph_compute_clustering,
            "graph_compute_gap_analysis": graph_compute_gap_analysis,
            "graph_compute_layer_crossing": graph_compute_layer_crossing,
        })
        logger.info("Registered %d NetworkX live tools", 20)
    except ImportError as e:
        logger.warning("NetworkX tools unavailable: %s", e)

    # --- ArchiMate XML parser tools ---
    try:
        from src.pools.live_tools.archimate_parser_tools import (
            archimate_parse_model_info,
            archimate_list_elements,
            archimate_list_relationships,
            archimate_get_element_relationships,
            archimate_list_views,
            archimate_get_properties,
            archimate_compute_model_metrics,
            archimate_compute_element_usage,
            archimate_validate_relationships,
            archimate_extract_to_graph,
        )
        _LIVE_TOOLS.update({
            "archimate_parse_model_info": archimate_parse_model_info,
            "archimate_list_elements": archimate_list_elements,
            "archimate_list_relationships": archimate_list_relationships,
            "archimate_get_element_relationships": archimate_get_element_relationships,
            "archimate_list_views": archimate_list_views,
            "archimate_get_properties": archimate_get_properties,
            "archimate_compute_model_metrics": archimate_compute_model_metrics,
            "archimate_compute_element_usage": archimate_compute_element_usage,
            "archimate_validate_relationships": archimate_validate_relationships,
            "archimate_extract_to_graph": archimate_extract_to_graph,
        })
        logger.info("Registered %d ArchiMate parser live tools", 10)
    except ImportError as e:
        logger.warning("ArchiMate parser tools unavailable: %s", e)

    # --- GitHub tools ---
    try:
        from src.pools.live_tools.wikipedia_tools import (
            github_search_repositories,
            github_get_repository,
            github_get_repo_languages,
            github_get_repo_topics,
            github_list_repo_contents,
        )
        _LIVE_TOOLS.update({
            "github_search_repositories": github_search_repositories,
            "github_get_repository": github_get_repository,
            "github_get_repo_languages": github_get_repo_languages,
            "github_get_repo_topics": github_get_repo_topics,
            "github_list_repo_contents": github_list_repo_contents,
        })
        logger.info("Registered %d GitHub live tools", 5)
    except ImportError as e:
        logger.warning("GitHub tools unavailable: %s", e)


def _build_tool_index(tool_pool: list[dict]) -> dict[str, dict]:
    """Build a lookup from tool id to tool definition."""
    index: dict[str, dict] = {}
    for tool in tool_pool:
        index[tool["id"]] = tool
        # Also index by name for fuzzy matching
        index[tool["name"]] = tool
    return index


def _extract_json(text: str) -> dict | list | None:
    """Robustly extract JSON from LLM response text.

    Handles: code fences, leading/trailing text, nested objects.
    """
    text = text.strip()

    # Strip markdown code fences
    if text.startswith("```"):
        lines = text.split("\n", 1)
        text = lines[1] if len(lines) > 1 else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON object/array
    for start_char, end_char in [("{", "}"), ("[", "]")]:
        start = text.find(start_char)
        if start < 0:
            continue
        # Find matching closing bracket (handle nesting)
        depth = 0
        for i in range(start, len(text)):
            if text[i] == start_char:
                depth += 1
            elif text[i] == end_char:
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except json.JSONDecodeError:
                        break

    return None


class ToolExecutor:
    """Executes tool calls — real implementations when available, LLM-simulated otherwise.

    Results from simulated tools include `_simulated: true`.
    Results with JSON parse errors include `_parse_failed: true`.
    """

    def __init__(
        self,
        tool_pool: list[dict],
        kimi_client: Any,
        seed_context: str = "",
    ):
        _register_live_tools()
        self._tool_index = _build_tool_index(tool_pool)
        self._kimi = kimi_client
        self._seed_context = seed_context
        self._call_count = 0
        self._live_count = 0
        self._simulated_count = 0

    def __call__(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Execute a tool call. Returns structured result."""
        self._call_count += 1

        # Try live execution first
        if tool_name in _LIVE_TOOLS:
            try:
                result = _LIVE_TOOLS[tool_name](**arguments)
                self._live_count += 1
                logger.info("Live tool '%s' executed successfully", tool_name)
                return result
            except Exception as e:
                logger.warning("Live tool '%s' failed: %s, falling back to simulation", tool_name, e)

        # LLM-simulated execution
        self._simulated_count += 1
        return self._simulate_tool(tool_name, arguments)

    def _simulate_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Use LLM to generate realistic tool output based on definition.

        Results are marked with `_simulated: true`. If JSON parsing fails,
        `_parse_failed: true` is also set.
        """
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

        # Parse JSON from response with robust extraction
        parsed = _extract_json(response)
        if parsed is not None:
            if isinstance(parsed, dict):
                parsed["_simulated"] = True
            return parsed
        else:
            logger.warning("Failed to parse simulated tool output as JSON for '%s'", tool_name)
            return {
                "raw_output": response,
                "tool_name": tool_name,
                "_simulated": True,
                "_parse_failed": True,
            }

    @property
    def call_count(self) -> int:
        return self._call_count

    @property
    def live_count(self) -> int:
        return self._live_count

    @property
    def simulated_count(self) -> int:
        return self._simulated_count

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
