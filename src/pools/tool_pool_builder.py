"""Builder for the TOGAF Tool Pool.

Generates ~373 tool definitions across 5 domains (ADM, ArchiMate, Repository,
Governance, General), classified as Retrieval or Processing.
"""

from __future__ import annotations

from pathlib import Path

from .models import (
    ToolDefinition,
    ToolParameter,
    ToolType,
    ToolDomain,
    save_pool,
)


def _retrieval_tools_adm() -> list[ToolDefinition]:
    """ADM-related retrieval tools."""
    tools = []

    # --- Phase details ---
    phases = [
        ("A", "Architecture Vision"),
        ("B", "Business Architecture"),
        ("C", "Information Systems Architecture"),
        ("D", "Technology Architecture"),
        ("E", "Opportunities and Solutions"),
        ("F", "Migration Planning"),
        ("G", "Implementation Governance"),
        ("H", "Architecture Change Management"),
        ("Preliminary", "Preliminary Phase"),
        ("Requirements", "Requirements Management"),
    ]
    for code, label in phases:
        tools.append(ToolDefinition(
            id=f"adm_get_phase_details_{code.lower()}",
            name="adm_get_phase_details",
            description=f"Returns deliverables, inputs, outputs, techniques and stakeholders for ADM Phase {code} ({label}).",
            tool_type=ToolType.RETRIEVAL,
            domain=ToolDomain.ADM,
            parameters=[
                ToolParameter("phase", "string", f"ADM phase identifier", enum=[code]),
                ToolParameter("include_techniques", "boolean", "Include recommended techniques", required=False, default=True),
                ToolParameter("include_stakeholders", "boolean", "Include stakeholder list", required=False, default=False),
            ],
            return_schema={
                "type": "object",
                "properties": {
                    "phase": {"type": "string"},
                    "deliverables": {"type": "array", "items": {"type": "string"}},
                    "inputs": {"type": "array", "items": {"type": "string"}},
                    "outputs": {"type": "array", "items": {"type": "string"}},
                    "techniques": {"type": "array", "items": {"type": "string"}},
                    "stakeholders": {"type": "array", "items": {"type": "string"}},
                },
            },
            examples=[{
                "call": {"phase": code, "include_techniques": True},
                "response": {"phase": code, "deliverables": [f"{label} Document"], "inputs": ["Request for Architecture Work"], "outputs": [f"Approved {label}"], "techniques": ["Stakeholder Analysis"]},
            }],
            tags=["adm", "phase", code.lower()],
        ))

    # --- ADM iteration tools ---
    tools.append(ToolDefinition(
        id="adm_get_iteration_cycle",
        name="adm_get_iteration_cycle",
        description="Returns the iteration cycle details for a given ADM scope (architecture landscape, capability, or foundation).",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.ADM,
        parameters=[
            ToolParameter("cycle_type", "string", "Type of iteration cycle", enum=["architecture_landscape", "capability_increment", "foundation"]),
        ],
        return_schema={"type": "object", "properties": {"cycle_type": {"type": "string"}, "phases_included": {"type": "array"}, "description": {"type": "string"}}},
        examples=[],
        tags=["adm", "iteration"],
    ))

    # --- Deliverable queries ---
    for deliverable_type in [
        "architecture_vision", "statement_of_architecture_work",
        "architecture_definition_document", "architecture_requirements_specification",
        "architecture_roadmap", "transition_architecture",
        "implementation_governance_model", "architecture_contract",
        "compliance_assessment", "change_request",
        "business_architecture_document", "data_architecture_document",
        "application_architecture_document", "technology_architecture_document",
        "stakeholder_map", "value_chain_diagram",
        "organization_map", "business_interaction_matrix",
        "business_footprint_diagram", "business_service_catalog",
        "functional_decomposition_diagram", "goal_objective_service_diagram",
        "business_use_case_diagram", "process_flow_diagram",
    ]:
        tools.append(ToolDefinition(
            id=f"adm_get_deliverable_{deliverable_type}",
            name="adm_get_deliverable",
            description=f"Retrieves the template, structure and content guidelines for the {deliverable_type.replace('_', ' ').title()} deliverable.",
            tool_type=ToolType.RETRIEVAL,
            domain=ToolDomain.ADM,
            parameters=[
                ToolParameter("deliverable_type", "string", "Deliverable type identifier", enum=[deliverable_type]),
                ToolParameter("format", "string", "Output format", required=False, enum=["summary", "full", "template"], default="summary"),
            ],
            return_schema={"type": "object", "properties": {"deliverable_type": {"type": "string"}, "content": {"type": "object"}, "phase": {"type": "string"}}},
            examples=[],
            tags=["adm", "deliverable", deliverable_type],
        ))

    # --- Technique queries ---
    for technique in [
        "stakeholder_analysis", "business_transformation_readiness",
        "gap_analysis", "migration_planning", "interoperability_requirements",
        "business_scenarios", "architecture_principles",
        "risk_management", "capability_based_planning",
        "architecture_patterns", "business_models",
    ]:
        tools.append(ToolDefinition(
            id=f"adm_get_technique_{technique}",
            name="adm_get_technique",
            description=f"Returns methodology and steps for the {technique.replace('_', ' ').title()} technique.",
            tool_type=ToolType.RETRIEVAL,
            domain=ToolDomain.ADM,
            parameters=[
                ToolParameter("technique", "string", "Technique identifier", enum=[technique]),
            ],
            return_schema={"type": "object", "properties": {"technique": {"type": "string"}, "steps": {"type": "array"}, "inputs": {"type": "array"}, "outputs": {"type": "array"}}},
            examples=[],
            tags=["adm", "technique", technique],
        ))

    # --- Viewpoint queries ---
    tools.append(ToolDefinition(
        id="adm_get_viewpoint",
        name="adm_get_viewpoint",
        description="Returns viewpoint details including stakeholder concerns, model kinds, and correspondence rules.",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.ADM,
        parameters=[
            ToolParameter("viewpoint_name", "string", "Name of the architecture viewpoint"),
            ToolParameter("include_examples", "boolean", "Include example views", required=False, default=False),
        ],
        return_schema={"type": "object", "properties": {"viewpoint_name": {"type": "string"}, "stakeholders": {"type": "array"}, "concerns": {"type": "array"}, "model_kinds": {"type": "array"}}},
        examples=[],
        tags=["adm", "viewpoint"],
    ))

    return tools


def _retrieval_tools_archimate() -> list[ToolDefinition]:
    """ArchiMate-related retrieval tools."""
    tools = []

    # --- Element queries ---
    for layer in ["business", "application", "technology", "motivation", "strategy", "implementation_migration"]:
        tools.append(ToolDefinition(
            id=f"archimate_get_elements_{layer}",
            name="archimate_get_elements",
            description=f"Retrieves all ArchiMate elements defined in the {layer.replace('_', ' ')} layer.",
            tool_type=ToolType.RETRIEVAL,
            domain=ToolDomain.ARCHIMATE,
            parameters=[
                ToolParameter("layer", "string", "ArchiMate layer", enum=[layer]),
                ToolParameter("element_type", "string", "Filter by element type (e.g., 'service', 'process')", required=False),
            ],
            return_schema={"type": "object", "properties": {"layer": {"type": "string"}, "elements": {"type": "array", "items": {"type": "object"}}}},
            examples=[],
            tags=["archimate", "element", layer],
        ))

    # --- Relationship queries ---
    tools.append(ToolDefinition(
        id="archimate_get_relationships",
        name="archimate_get_relationships",
        description="Returns all relationships (serving, composition, aggregation, realization, etc.) for a given ArchiMate element.",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.ARCHIMATE,
        parameters=[
            ToolParameter("element", "string", "Element name or ID"),
            ToolParameter("relationship_type", "string", "Filter by relationship type", required=False,
                         enum=["serving", "composition", "aggregation", "realization", "assignment",
                               "access", "influence", "triggering", "flow", "specialization", "association"]),
            ToolParameter("direction", "string", "Relationship direction", required=False, enum=["incoming", "outgoing", "both"], default="both"),
        ],
        return_schema={"type": "object", "properties": {"element": {"type": "string"}, "relationships": {"type": "array"}}},
        examples=[{"call": {"element": "Legacy COBOL LOS"}, "response": {"element": "Legacy COBOL LOS", "relationships": [{"type": "serving", "target": "Loan Processing Service"}]}}],
        tags=["archimate", "relationship"],
    ))

    # --- Viewpoint queries ---
    for vp in [
        "organization", "business_process_cooperation", "product",
        "application_cooperation", "application_usage", "technology_usage",
        "technology", "information_structure", "service_realization",
        "implementation_deployment", "layered", "landscape_map",
        "goal_realization", "requirements_realization", "motivation",
        "strategy", "capability_map", "outcome_realization",
        "resource_map", "value_stream", "migration", "project",
        "stakeholder", "physical",
    ]:
        tools.append(ToolDefinition(
            id=f"archimate_get_viewpoint_{vp}",
            name="archimate_get_viewpoint",
            description=f"Returns the {vp.replace('_', ' ').title()} viewpoint definition, allowed elements, and relationships.",
            tool_type=ToolType.RETRIEVAL,
            domain=ToolDomain.ARCHIMATE,
            parameters=[
                ToolParameter("viewpoint", "string", "Viewpoint name", enum=[vp]),
            ],
            return_schema={"type": "object", "properties": {"viewpoint": {"type": "string"}, "allowed_elements": {"type": "array"}, "allowed_relationships": {"type": "array"}, "purpose": {"type": "string"}}},
            examples=[],
            tags=["archimate", "viewpoint", vp],
        ))

    # --- Model queries ---
    tools.append(ToolDefinition(
        id="archimate_query_model",
        name="archimate_query_model",
        description="Queries an ArchiMate model with filters for elements, relationships, and properties.",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.ARCHIMATE,
        parameters=[
            ToolParameter("model_id", "string", "Model identifier"),
            ToolParameter("query", "string", "Search query or filter expression"),
            ToolParameter("max_depth", "integer", "Maximum traversal depth", required=False, default=2),
        ],
        return_schema={"type": "object", "properties": {"results": {"type": "array"}, "total": {"type": "integer"}}},
        examples=[],
        tags=["archimate", "model", "query"],
    ))

    # --- Metamodel queries ---
    tools.append(ToolDefinition(
        id="archimate_get_metamodel",
        name="archimate_get_metamodel",
        description="Returns ArchiMate metamodel constraints: valid element-relationship combinations.",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.ARCHIMATE,
        parameters=[
            ToolParameter("scope", "string", "Scope of metamodel query", enum=["full", "layer", "cross_layer"], default="full"),
        ],
        return_schema={"type": "object", "properties": {"constraints": {"type": "array"}}},
        examples=[],
        tags=["archimate", "metamodel"],
    ))

    return tools


def _retrieval_tools_repository() -> list[ToolDefinition]:
    """Architecture Repository retrieval tools."""
    tools = []

    # --- Search ---
    tools.append(ToolDefinition(
        id="repo_search_artifacts",
        name="repo_search_artifacts",
        description="Searches the Architecture Repository for artifacts matching a query across all categories.",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.REPOSITORY,
        parameters=[
            ToolParameter("query", "string", "Search query"),
            ToolParameter("category", "string", "Artifact category filter", required=False,
                         enum=["architecture_metamodel", "architecture_capability", "architecture_landscape",
                               "standards_information_base", "reference_library", "governance_log"]),
            ToolParameter("limit", "integer", "Max results", required=False, default=20),
        ],
        return_schema={"type": "object", "properties": {"artifacts": {"type": "array"}, "total": {"type": "integer"}}},
        examples=[{"call": {"query": "loan origination"}, "response": {"artifacts": [{"name": "Loan Origination System", "category": "architecture_landscape"}], "total": 1}}],
        tags=["repository", "search"],
    ))

    # --- Building Block queries ---
    for bb_type in ["architecture_building_block", "solution_building_block"]:
        tools.append(ToolDefinition(
            id=f"repo_get_building_block_{bb_type}",
            name="repo_get_building_block",
            description=f"Retrieves details for a {bb_type.replace('_', ' ').upper()} including status, interfaces, and dependencies.",
            tool_type=ToolType.RETRIEVAL,
            domain=ToolDomain.REPOSITORY,
            parameters=[
                ToolParameter("block_name", "string", "Building block name"),
                ToolParameter("block_type", "string", "ABB or SBB", enum=[bb_type]),
                ToolParameter("include_dependencies", "boolean", "Include dependency tree", required=False, default=True),
            ],
            return_schema={"type": "object", "properties": {"name": {"type": "string"}, "type": {"type": "string"}, "status": {"type": "string"}, "interfaces": {"type": "array"}, "dependencies": {"type": "array"}}},
            examples=[],
            tags=["repository", "building_block", bb_type],
        ))

    # --- Reference model queries ---
    for ref_model in [
        "trm", "iii_rm", "soa_ra", "cloud_ra",
        "security_ra", "integration_ra", "data_ra",
        "bian", "tmforum_oda", "acord", "hl7_fhir",
    ]:
        tools.append(ToolDefinition(
            id=f"repo_get_reference_model_{ref_model}",
            name="repo_get_reference_model",
            description=f"Retrieves the {ref_model.upper().replace('_', ' ')} reference model taxonomy, components and mappings.",
            tool_type=ToolType.RETRIEVAL,
            domain=ToolDomain.REPOSITORY,
            parameters=[
                ToolParameter("model_name", "string", "Reference model identifier", enum=[ref_model]),
                ToolParameter("detail_level", "string", "Level of detail", required=False, enum=["summary", "detailed", "full"], default="summary"),
            ],
            return_schema={"type": "object", "properties": {"model_name": {"type": "string"}, "components": {"type": "array"}, "mappings": {"type": "array"}}},
            examples=[],
            tags=["repository", "reference_model", ref_model],
        ))

    # --- Standards Information Base ---
    for standard_domain in [
        "security", "integration", "data", "infrastructure",
        "application", "regulatory", "industry",
    ]:
        tools.append(ToolDefinition(
            id=f"repo_get_standards_{standard_domain}",
            name="repo_get_standards",
            description=f"Retrieves standards from the Standards Information Base for the {standard_domain} domain.",
            tool_type=ToolType.RETRIEVAL,
            domain=ToolDomain.REPOSITORY,
            parameters=[
                ToolParameter("domain", "string", "Standards domain", enum=[standard_domain]),
                ToolParameter("status", "string", "Standard status filter", required=False, enum=["current", "deprecated", "emerging", "all"], default="current"),
            ],
            return_schema={"type": "object", "properties": {"standards": {"type": "array"}, "domain": {"type": "string"}}},
            examples=[],
            tags=["repository", "standards", standard_domain],
        ))

    # --- Capability catalog ---
    tools.append(ToolDefinition(
        id="capability_catalog_search",
        name="capability_catalog_search",
        description="Searches the capability catalog for business capabilities matching a query.",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.REPOSITORY,
        parameters=[
            ToolParameter("domain", "string", "Business domain"),
            ToolParameter("query", "string", "Search query"),
            ToolParameter("maturity_filter", "string", "Filter by maturity level", required=False, enum=["all", "low", "medium", "high"], default="all"),
        ],
        return_schema={"type": "object", "properties": {"capabilities": {"type": "array"}, "total": {"type": "integer"}}},
        examples=[{"call": {"domain": "banking", "query": "core systems"}, "response": {"capabilities": [{"name": "Payment Processing", "maturity": 2}], "total": 3}}],
        tags=["repository", "capability"],
    ))

    # --- Stakeholder catalog ---
    tools.append(ToolDefinition(
        id="stakeholder_catalog_search",
        name="stakeholder_catalog_search",
        description="Searches the stakeholder catalog and returns stakeholders with their concerns, influence and power levels.",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.REPOSITORY,
        parameters=[
            ToolParameter("query", "string", "Search query or project context"),
            ToolParameter("role_filter", "string", "Filter by role type", required=False,
                         enum=["executive", "business", "technical", "regulatory", "all"], default="all"),
        ],
        return_schema={"type": "object", "properties": {"stakeholders": {"type": "array"}, "total": {"type": "integer"}}},
        examples=[],
        tags=["repository", "stakeholder"],
    ))

    # --- Governance log ---
    tools.append(ToolDefinition(
        id="governance_log_query",
        name="governance_log_query",
        description="Queries the governance log for architecture decisions, dispensations, and compliance records.",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.REPOSITORY,
        parameters=[
            ToolParameter("query", "string", "Search query"),
            ToolParameter("record_type", "string", "Record type filter", required=False,
                         enum=["decision", "dispensation", "compliance", "review", "all"], default="all"),
            ToolParameter("date_from", "string", "Start date (ISO format)", required=False),
            ToolParameter("date_to", "string", "End date (ISO format)", required=False),
        ],
        return_schema={"type": "object", "properties": {"records": {"type": "array"}, "total": {"type": "integer"}}},
        examples=[],
        tags=["repository", "governance"],
    ))

    # --- Current state queries ---
    tools.append(ToolDefinition(
        id="current_state_query",
        name="current_state_query",
        description="Queries the current/baseline architecture state for a system, including technology stack, age, interfaces, and known issues.",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.REPOSITORY,
        parameters=[
            ToolParameter("system_name", "string", "System to query"),
            ToolParameter("include_interfaces", "boolean", "Include interface details", required=False, default=True),
            ToolParameter("include_issues", "boolean", "Include known issues", required=False, default=True),
        ],
        return_schema={"type": "object", "properties": {"system": {"type": "string"}, "technology": {"type": "string"}, "age_years": {"type": "integer"}, "interfaces": {"type": "array"}, "issues": {"type": "array"}}},
        examples=[{"call": {"system_name": "Legacy COBOL LOS"}, "response": {"system": "Legacy COBOL LOS", "technology": "COBOL", "age_years": 23, "interfaces": 4}}],
        tags=["repository", "current_state"],
    ))

    # --- Target state queries ---
    tools.append(ToolDefinition(
        id="target_state_query",
        name="target_state_query",
        description="Queries the target architecture state for a system or domain.",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.REPOSITORY,
        parameters=[
            ToolParameter("domain", "string", "Target architecture domain"),
            ToolParameter("time_horizon", "string", "Planning horizon", required=False, enum=["short", "medium", "long"], default="medium"),
        ],
        return_schema={"type": "object", "properties": {"domain": {"type": "string"}, "target_components": {"type": "array"}, "principles": {"type": "array"}}},
        examples=[],
        tags=["repository", "target_state"],
    ))

    # --- Architecture principles ---
    tools.append(ToolDefinition(
        id="repo_get_principles",
        name="repo_get_principles",
        description="Retrieves architecture principles with rationale, implications, and priority.",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.REPOSITORY,
        parameters=[
            ToolParameter("category", "string", "Principle category", required=False,
                         enum=["business", "data", "application", "technology", "security", "all"], default="all"),
        ],
        return_schema={"type": "object", "properties": {"principles": {"type": "array"}}},
        examples=[],
        tags=["repository", "principles"],
    ))

    # --- Pattern library ---
    tools.append(ToolDefinition(
        id="repo_get_patterns",
        name="repo_get_patterns",
        description="Retrieves architecture patterns from the pattern library.",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.REPOSITORY,
        parameters=[
            ToolParameter("pattern_type", "string", "Pattern type", enum=["integration", "security", "data", "deployment", "messaging", "scalability"]),
            ToolParameter("query", "string", "Search query", required=False),
        ],
        return_schema={"type": "object", "properties": {"patterns": {"type": "array"}}},
        examples=[],
        tags=["repository", "patterns"],
    ))

    return tools


def _retrieval_tools_governance() -> list[ToolDefinition]:
    """Governance retrieval tools."""
    tools = []

    # --- Compliance standards ---
    for standard in [
        "pci_dss", "sox", "gdpr", "hipaa", "basel_iii",
        "iso_27001", "cobit", "itil", "nist_csf",
        "togaf_compliance", "fedramp", "ccpa",
        "dora", "nis2", "mifid2", "psd2",
    ]:
        tools.append(ToolDefinition(
            id=f"compliance_get_requirements_{standard}",
            name="compliance_get_requirements",
            description=f"Retrieves compliance requirements for {standard.upper().replace('_', ' ')} standard.",
            tool_type=ToolType.RETRIEVAL,
            domain=ToolDomain.GOVERNANCE,
            parameters=[
                ToolParameter("standard", "string", "Compliance standard", enum=[standard]),
                ToolParameter("category", "string", "Requirement category filter", required=False),
            ],
            return_schema={"type": "object", "properties": {"standard": {"type": "string"}, "requirements": {"type": "array"}}},
            examples=[],
            tags=["governance", "compliance", standard],
        ))

    # --- Architecture board ---
    tools.append(ToolDefinition(
        id="governance_get_board_decisions",
        name="governance_get_board_decisions",
        description="Retrieves architecture board decisions, including rationale and impact assessment.",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.GOVERNANCE,
        parameters=[
            ToolParameter("project", "string", "Project or initiative name", required=False),
            ToolParameter("status", "string", "Decision status", required=False, enum=["pending", "approved", "rejected", "deferred", "all"], default="all"),
        ],
        return_schema={"type": "object", "properties": {"decisions": {"type": "array"}}},
        examples=[],
        tags=["governance", "board"],
    ))

    # --- Architecture contract ---
    tools.append(ToolDefinition(
        id="governance_get_contracts",
        name="governance_get_contracts",
        description="Retrieves architecture contracts for projects, including SLAs, constraints, and acceptance criteria.",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.GOVERNANCE,
        parameters=[
            ToolParameter("project", "string", "Project name"),
            ToolParameter("contract_type", "string", "Contract type", required=False, enum=["development", "service", "operational", "all"], default="all"),
        ],
        return_schema={"type": "object", "properties": {"contracts": {"type": "array"}}},
        examples=[],
        tags=["governance", "contract"],
    ))

    # --- Dispensation queries ---
    tools.append(ToolDefinition(
        id="governance_get_dispensations",
        name="governance_get_dispensations",
        description="Retrieves architecture dispensations (approved deviations from standards).",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.GOVERNANCE,
        parameters=[
            ToolParameter("project", "string", "Project name", required=False),
            ToolParameter("status", "string", "Dispensation status", required=False, enum=["active", "expired", "revoked", "all"], default="all"),
        ],
        return_schema={"type": "object", "properties": {"dispensations": {"type": "array"}}},
        examples=[],
        tags=["governance", "dispensation"],
    ))

    return tools


def _retrieval_tools_general() -> list[ToolDefinition]:
    """General/cross-cutting retrieval tools."""
    tools = []

    # --- Maturity assessment ---
    tools.append(ToolDefinition(
        id="maturity_assessment_query",
        name="maturity_assessment_query",
        description="Queries maturity assessment scores for capabilities, processes, or technology components.",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.GENERAL,
        parameters=[
            ToolParameter("entity_name", "string", "Name of entity to assess"),
            ToolParameter("entity_type", "string", "Type of entity", enum=["capability", "process", "technology", "organization"]),
            ToolParameter("framework", "string", "Maturity framework", required=False, enum=["cmmi", "togaf_amm", "custom"], default="togaf_amm"),
        ],
        return_schema={"type": "object", "properties": {"entity": {"type": "string"}, "score": {"type": "number"}, "level": {"type": "string"}, "details": {"type": "object"}}},
        examples=[],
        tags=["general", "maturity"],
    ))

    # --- Technology radar ---
    tools.append(ToolDefinition(
        id="technology_radar_query",
        name="technology_radar_query",
        description="Queries the technology radar for adoption status and recommendations.",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.GENERAL,
        parameters=[
            ToolParameter("technology", "string", "Technology name"),
            ToolParameter("category", "string", "Technology category", required=False,
                         enum=["languages", "frameworks", "platforms", "tools", "techniques", "all"], default="all"),
        ],
        return_schema={"type": "object", "properties": {"technology": {"type": "string"}, "ring": {"type": "string"}, "quadrant": {"type": "string"}}},
        examples=[],
        tags=["general", "technology_radar"],
    ))

    # --- Project portfolio ---
    tools.append(ToolDefinition(
        id="portfolio_query_projects",
        name="portfolio_query_projects",
        description="Queries the project portfolio for active, planned, or completed projects.",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.GENERAL,
        parameters=[
            ToolParameter("query", "string", "Search query"),
            ToolParameter("status", "string", "Project status filter", required=False,
                         enum=["active", "planned", "completed", "on_hold", "all"], default="all"),
        ],
        return_schema={"type": "object", "properties": {"projects": {"type": "array"}, "total": {"type": "integer"}}},
        examples=[],
        tags=["general", "portfolio"],
    ))

    # --- Business capability model ---
    tools.append(ToolDefinition(
        id="business_capability_model_query",
        name="business_capability_model_query",
        description="Queries the business capability model for capabilities at specified levels.",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.GENERAL,
        parameters=[
            ToolParameter("domain", "string", "Business domain"),
            ToolParameter("level", "integer", "Capability hierarchy level (1-4)", required=False, default=2),
        ],
        return_schema={"type": "object", "properties": {"capabilities": {"type": "array"}}},
        examples=[],
        tags=["general", "capability_model"],
    ))

    # --- Value stream ---
    tools.append(ToolDefinition(
        id="value_stream_query",
        name="value_stream_query",
        description="Queries value stream definitions including stages, capabilities, and enabling elements.",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.GENERAL,
        parameters=[
            ToolParameter("value_stream_name", "string", "Value stream name"),
            ToolParameter("include_capabilities", "boolean", "Include mapped capabilities", required=False, default=True),
        ],
        return_schema={"type": "object", "properties": {"value_stream": {"type": "string"}, "stages": {"type": "array"}, "capabilities": {"type": "array"}}},
        examples=[],
        tags=["general", "value_stream"],
    ))

    # --- Integration catalog ---
    tools.append(ToolDefinition(
        id="integration_catalog_query",
        name="integration_catalog_query",
        description="Queries the integration catalog for system interfaces, APIs, and data flows.",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.GENERAL,
        parameters=[
            ToolParameter("system", "string", "System name"),
            ToolParameter("interface_type", "string", "Interface type filter", required=False,
                         enum=["api", "file", "messaging", "database", "all"], default="all"),
        ],
        return_schema={"type": "object", "properties": {"interfaces": {"type": "array"}, "total": {"type": "integer"}}},
        examples=[],
        tags=["general", "integration"],
    ))

    # --- Data catalog ---
    tools.append(ToolDefinition(
        id="data_catalog_query",
        name="data_catalog_query",
        description="Queries the data catalog for data entities, ownership, quality metrics, and lineage.",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.GENERAL,
        parameters=[
            ToolParameter("query", "string", "Search query"),
            ToolParameter("classification", "string", "Data classification filter", required=False,
                         enum=["public", "internal", "confidential", "restricted", "all"], default="all"),
        ],
        return_schema={"type": "object", "properties": {"entities": {"type": "array"}, "total": {"type": "integer"}}},
        examples=[],
        tags=["general", "data_catalog"],
    ))

    # --- Application portfolio ---
    tools.append(ToolDefinition(
        id="application_portfolio_query",
        name="application_portfolio_query",
        description="Queries the application portfolio for TIME classification (Tolerate, Invest, Migrate, Eliminate).",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.GENERAL,
        parameters=[
            ToolParameter("query", "string", "Search query or domain"),
            ToolParameter("time_classification", "string", "TIME filter", required=False,
                         enum=["tolerate", "invest", "migrate", "eliminate", "all"], default="all"),
        ],
        return_schema={"type": "object", "properties": {"applications": {"type": "array"}, "total": {"type": "integer"}}},
        examples=[],
        tags=["general", "application_portfolio"],
    ))

    return tools


def _processing_tools() -> list[ToolDefinition]:
    """All processing (computation/transformation) tools."""
    tools = []

    # --- Gap Analysis ---
    tools.append(ToolDefinition(
        id="gap_analysis_compute",
        name="gap_analysis_compute",
        description="Computes gap analysis between baseline and target architecture states, identifying new, eliminated, and changed elements.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.ADM,
        parameters=[
            ToolParameter("baseline", "object", "Baseline architecture state (elements and relationships)"),
            ToolParameter("target", "object", "Target architecture state (elements and relationships)"),
            ToolParameter("analysis_type", "string", "Type of gap analysis", required=False,
                         enum=["element", "relationship", "capability", "full"], default="full"),
        ],
        return_schema={"type": "object", "properties": {"gaps": {"type": "array"}, "summary": {"type": "object"}}},
        examples=[{"call": {"baseline": {"elements": ["Batch Processing"]}, "target": {"elements": ["API Gateway"]}},
                   "response": {"gaps": [{"type": "new", "element": "API Gateway"}, {"type": "eliminated", "element": "Batch Processing"}]}}],
        tags=["processing", "gap_analysis"],
    ))

    # --- Risk Score ---
    tools.append(ToolDefinition(
        id="risk_score_compute",
        name="risk_score_compute",
        description="Computes a risk score for a system or architecture element based on weighted factors.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.GOVERNANCE,
        parameters=[
            ToolParameter("system", "string", "System or element name"),
            ToolParameter("factors", "array", "Risk factors with weights and values"),
            ToolParameter("methodology", "string", "Risk methodology", required=False, enum=["qualitative", "quantitative", "semi_quantitative"], default="semi_quantitative"),
        ],
        return_schema={"type": "object", "properties": {"system": {"type": "string"}, "risk_score": {"type": "number"}, "risk_level": {"type": "string"}, "breakdown": {"type": "array"}}},
        examples=[],
        tags=["processing", "risk"],
    ))

    # --- Compliance Check ---
    tools.append(ToolDefinition(
        id="compliance_check_execute",
        name="compliance_check_execute",
        description="Executes a compliance check for an architecture building block against specified standards.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.GOVERNANCE,
        parameters=[
            ToolParameter("block", "object", "Building block definition"),
            ToolParameter("standards", "array", "List of standard identifiers to check against"),
            ToolParameter("severity_threshold", "string", "Minimum severity to report", required=False, enum=["info", "warning", "error", "critical"], default="warning"),
        ],
        return_schema={"type": "object", "properties": {"compliant": {"type": "boolean"}, "violations": {"type": "array"}, "warnings": {"type": "array"}}},
        examples=[],
        tags=["processing", "compliance"],
    ))

    # --- Cost-Benefit Analysis ---
    tools.append(ToolDefinition(
        id="cost_benefit_analyze",
        name="cost_benefit_analyze",
        description="Performs cost-benefit analysis for an architecture initiative, calculating ROI, payback period, and NPV.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.GENERAL,
        parameters=[
            ToolParameter("initiative", "string", "Initiative name"),
            ToolParameter("costs", "object", "Cost breakdown (capex, opex, by year)"),
            ToolParameter("benefits", "object", "Benefit projections (revenue, savings, by year)"),
            ToolParameter("discount_rate", "number", "Discount rate for NPV", required=False, default=0.08),
            ToolParameter("time_horizon_years", "integer", "Analysis time horizon", required=False, default=5),
        ],
        return_schema={"type": "object", "properties": {"roi_percent": {"type": "number"}, "payback_months": {"type": "integer"}, "npv": {"type": "number"}, "irr": {"type": "number"}}},
        examples=[],
        tags=["processing", "cost_benefit"],
    ))

    # --- Roadmap Generation ---
    tools.append(ToolDefinition(
        id="roadmap_generate",
        name="roadmap_generate",
        description="Generates a migration roadmap with waves/phases based on dependencies, priorities, and constraints.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.ADM,
        parameters=[
            ToolParameter("work_packages", "array", "List of work packages with dependencies and priorities"),
            ToolParameter("constraints", "object", "Constraints (budget, resources, time)", required=False),
            ToolParameter("strategy", "string", "Migration strategy", required=False,
                         enum=["big_bang", "phased", "parallel", "incremental"], default="phased"),
        ],
        return_schema={"type": "object", "properties": {"waves": {"type": "array"}, "timeline": {"type": "object"}, "critical_path": {"type": "array"}}},
        examples=[],
        tags=["processing", "roadmap"],
    ))

    # --- Stakeholder Impact ---
    tools.append(ToolDefinition(
        id="stakeholder_impact_analyze",
        name="stakeholder_impact_analyze",
        description="Analyzes the impact of architecture changes on stakeholders, mapping concerns to changes.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.ADM,
        parameters=[
            ToolParameter("stakeholders", "array", "List of stakeholders with concerns"),
            ToolParameter("changes", "array", "Proposed architecture changes"),
            ToolParameter("include_communication_plan", "boolean", "Generate communication plan", required=False, default=False),
        ],
        return_schema={"type": "object", "properties": {"impact_matrix": {"type": "array"}, "high_impact_stakeholders": {"type": "array"}}},
        examples=[],
        tags=["processing", "stakeholder"],
    ))

    # --- Dependency Analysis ---
    tools.append(ToolDefinition(
        id="dependency_analysis_compute",
        name="dependency_analysis_compute",
        description="Computes dependency analysis including circular dependencies, critical paths, and coupling metrics.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.GENERAL,
        parameters=[
            ToolParameter("elements", "array", "Architecture elements with their relationships"),
            ToolParameter("analysis_type", "string", "Type of analysis", required=False,
                         enum=["circular", "critical_path", "coupling", "full"], default="full"),
        ],
        return_schema={"type": "object", "properties": {"circular_dependencies": {"type": "array"}, "critical_path": {"type": "array"}, "coupling_metrics": {"type": "object"}}},
        examples=[],
        tags=["processing", "dependency"],
    ))

    # --- Architecture Scoring ---
    tools.append(ToolDefinition(
        id="architecture_score_compute",
        name="architecture_score_compute",
        description="Computes an architecture quality score based on multiple dimensions (modularity, reusability, scalability, etc.).",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.GENERAL,
        parameters=[
            ToolParameter("architecture", "object", "Architecture description with components and relationships"),
            ToolParameter("dimensions", "array", "Quality dimensions to evaluate", required=False),
            ToolParameter("weights", "object", "Dimension weights", required=False),
        ],
        return_schema={"type": "object", "properties": {"overall_score": {"type": "number"}, "dimension_scores": {"type": "object"}, "recommendations": {"type": "array"}}},
        examples=[],
        tags=["processing", "scoring"],
    ))

    # --- Reuse Analysis ---
    tools.append(ToolDefinition(
        id="reuse_analysis_compute",
        name="reuse_analysis_compute",
        description="Computes building block reuse percentage across domains, identifying reuse opportunities and redundancies.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.REPOSITORY,
        parameters=[
            ToolParameter("building_blocks", "array", "Building blocks to analyze"),
            ToolParameter("domains", "array", "Domains to check for reuse"),
            ToolParameter("threshold", "number", "Similarity threshold for reuse detection", required=False, default=0.8),
        ],
        return_schema={"type": "object", "properties": {"reuse_percent": {"type": "number"}, "opportunities": {"type": "array"}, "redundancies": {"type": "array"}}},
        examples=[],
        tags=["processing", "reuse"],
    ))

    # --- Capability Heat Map ---
    tools.append(ToolDefinition(
        id="capability_heatmap_compute",
        name="capability_heatmap_compute",
        description="Computes a capability heat map showing investment vs. business value vs. technical fitness.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.GENERAL,
        parameters=[
            ToolParameter("capabilities", "array", "Capabilities with metrics"),
            ToolParameter("axes", "object", "Heat map axes configuration", required=False),
        ],
        return_schema={"type": "object", "properties": {"heatmap": {"type": "array"}, "quadrant_summary": {"type": "object"}}},
        examples=[],
        tags=["processing", "heatmap", "capability"],
    ))

    # --- Migration Complexity ---
    tools.append(ToolDefinition(
        id="migration_complexity_compute",
        name="migration_complexity_compute",
        description="Computes migration complexity score based on system characteristics, data volume, integrations, and organizational factors.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.ADM,
        parameters=[
            ToolParameter("source_system", "object", "Source system characteristics"),
            ToolParameter("target_system", "object", "Target system characteristics"),
            ToolParameter("data_volume_gb", "number", "Data volume in GB"),
            ToolParameter("integration_count", "integer", "Number of integrations affected"),
        ],
        return_schema={"type": "object", "properties": {"complexity_score": {"type": "number"}, "complexity_level": {"type": "string"}, "risk_factors": {"type": "array"}}},
        examples=[],
        tags=["processing", "migration"],
    ))

    # --- Business Transformation Readiness ---
    tools.append(ToolDefinition(
        id="transformation_readiness_assess",
        name="transformation_readiness_assess",
        description="Assesses business transformation readiness across organizational, technical, and cultural dimensions.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.ADM,
        parameters=[
            ToolParameter("organization", "object", "Organization characteristics"),
            ToolParameter("proposed_changes", "array", "Proposed transformation changes"),
            ToolParameter("dimensions", "array", "Assessment dimensions", required=False),
        ],
        return_schema={"type": "object", "properties": {"readiness_score": {"type": "number"}, "dimension_scores": {"type": "object"}, "blockers": {"type": "array"}, "enablers": {"type": "array"}}},
        examples=[],
        tags=["processing", "transformation"],
    ))

    # --- Interoperability Matrix ---
    tools.append(ToolDefinition(
        id="interoperability_matrix_compute",
        name="interoperability_matrix_compute",
        description="Computes an interoperability matrix between systems, assessing technical, semantic, and organizational interoperability.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.GENERAL,
        parameters=[
            ToolParameter("systems", "array", "List of systems to analyze"),
            ToolParameter("interop_dimensions", "array", "Interoperability dimensions", required=False,
                         enum=["technical", "semantic", "organizational", "legal"]),
        ],
        return_schema={"type": "object", "properties": {"matrix": {"type": "array"}, "overall_score": {"type": "number"}, "gaps": {"type": "array"}}},
        examples=[],
        tags=["processing", "interoperability"],
    ))

    # --- Architecture Decision Evaluation ---
    tools.append(ToolDefinition(
        id="decision_evaluation_compute",
        name="decision_evaluation_compute",
        description="Evaluates architecture decisions using weighted criteria, trade-off analysis, and sensitivity analysis.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.GOVERNANCE,
        parameters=[
            ToolParameter("alternatives", "array", "Decision alternatives with criteria scores"),
            ToolParameter("criteria", "array", "Evaluation criteria with weights"),
            ToolParameter("method", "string", "Evaluation method", required=False, enum=["weighted_sum", "ahp", "topsis"], default="weighted_sum"),
        ],
        return_schema={"type": "object", "properties": {"ranking": {"type": "array"}, "sensitivity": {"type": "object"}, "trade_offs": {"type": "array"}}},
        examples=[],
        tags=["processing", "decision"],
    ))

    # --- SLA Validation ---
    tools.append(ToolDefinition(
        id="sla_validation_compute",
        name="sla_validation_compute",
        description="Validates architecture design against SLA requirements (availability, performance, recovery).",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.GOVERNANCE,
        parameters=[
            ToolParameter("architecture", "object", "Architecture design"),
            ToolParameter("sla_requirements", "array", "SLA requirements to validate against"),
        ],
        return_schema={"type": "object", "properties": {"valid": {"type": "boolean"}, "violations": {"type": "array"}, "margin_analysis": {"type": "object"}}},
        examples=[],
        tags=["processing", "sla"],
    ))

    # --- Data Flow Analysis ---
    tools.append(ToolDefinition(
        id="data_flow_analysis_compute",
        name="data_flow_analysis_compute",
        description="Analyzes data flows between systems, identifying bottlenecks, privacy concerns, and optimization opportunities.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.GENERAL,
        parameters=[
            ToolParameter("data_flows", "array", "Data flow definitions"),
            ToolParameter("analysis_focus", "string", "Focus of analysis", required=False,
                         enum=["performance", "privacy", "security", "optimization", "full"], default="full"),
        ],
        return_schema={"type": "object", "properties": {"bottlenecks": {"type": "array"}, "privacy_concerns": {"type": "array"}, "optimization_suggestions": {"type": "array"}}},
        examples=[],
        tags=["processing", "data_flow"],
    ))

    # --- Technical Debt Assessment ---
    tools.append(ToolDefinition(
        id="technical_debt_compute",
        name="technical_debt_compute",
        description="Computes technical debt assessment including debt principal, interest rate, and remediation priorities.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.GENERAL,
        parameters=[
            ToolParameter("systems", "array", "Systems to assess"),
            ToolParameter("factors", "array", "Technical debt factors (code quality, documentation, testing, etc.)"),
        ],
        return_schema={"type": "object", "properties": {"total_debt": {"type": "object"}, "by_system": {"type": "array"}, "remediation_priority": {"type": "array"}}},
        examples=[],
        tags=["processing", "technical_debt"],
    ))

    # --- Capacity Planning ---
    tools.append(ToolDefinition(
        id="capacity_planning_compute",
        name="capacity_planning_compute",
        description="Computes capacity planning projections based on growth rates, current utilization, and thresholds.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.GENERAL,
        parameters=[
            ToolParameter("resources", "array", "Current resource utilization"),
            ToolParameter("growth_rate", "number", "Expected annual growth rate"),
            ToolParameter("threshold", "number", "Capacity threshold for alerting", required=False, default=0.8),
            ToolParameter("horizon_months", "integer", "Planning horizon in months", required=False, default=24),
        ],
        return_schema={"type": "object", "properties": {"projections": {"type": "array"}, "alerts": {"type": "array"}, "recommendations": {"type": "array"}}},
        examples=[],
        tags=["processing", "capacity"],
    ))

    # --- Architecture Comparison ---
    tools.append(ToolDefinition(
        id="architecture_comparison_compute",
        name="architecture_comparison_compute",
        description="Compares two architecture alternatives across multiple dimensions and produces a decision matrix.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.GENERAL,
        parameters=[
            ToolParameter("architecture_a", "object", "First architecture alternative"),
            ToolParameter("architecture_b", "object", "Second architecture alternative"),
            ToolParameter("criteria", "array", "Comparison criteria with weights"),
        ],
        return_schema={"type": "object", "properties": {"comparison_matrix": {"type": "array"}, "winner": {"type": "string"}, "trade_offs": {"type": "array"}}},
        examples=[],
        tags=["processing", "comparison"],
    ))

    # --- Viewpoint Consistency Check ---
    tools.append(ToolDefinition(
        id="viewpoint_consistency_check",
        name="viewpoint_consistency_check",
        description="Checks consistency across multiple architecture viewpoints, identifying conflicts and overlaps.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.ARCHIMATE,
        parameters=[
            ToolParameter("viewpoints", "array", "Viewpoints to check for consistency"),
            ToolParameter("check_type", "string", "Type of consistency check", required=False,
                         enum=["element", "relationship", "naming", "full"], default="full"),
        ],
        return_schema={"type": "object", "properties": {"consistent": {"type": "boolean"}, "conflicts": {"type": "array"}, "overlaps": {"type": "array"}}},
        examples=[],
        tags=["processing", "consistency", "viewpoint"],
    ))

    return tools


# =====================================================================
# Analysis Tools — architecture metrics, DSM, gap analysis, tech radar
# =====================================================================

def _analysis_tools() -> list[ToolDefinition]:
    """Architecture analysis and comparison tools."""
    tools = []

    # --- Martin Metrics (coupling/cohesion/instability/abstractness) ---
    tools.append(ToolDefinition(
        id="compute_coupling_metrics",
        name="compute_coupling_metrics",
        description="Computes afferent coupling (Ca) and efferent coupling (Ce) for architecture components. "
                    "Ca = number of components that depend on this component. Ce = number of components this component depends on.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.ANALYSIS,
        parameters=[
            ToolParameter("components", "array", "List of component objects with their dependency relationships"),
            ToolParameter("scope", "string", "Analysis scope", required=False,
                         enum=["component", "layer", "domain"], default="component"),
        ],
        return_schema={"type": "object", "properties": {
            "metrics": {"type": "array", "items": {"type": "object", "properties": {
                "component": {"type": "string"}, "Ca": {"type": "integer"}, "Ce": {"type": "integer"}}}},
            "summary": {"type": "object", "properties": {
                "avg_Ca": {"type": "number"}, "avg_Ce": {"type": "number"}, "max_Ca_component": {"type": "string"}}}}},
        examples=[{"call": {"components": [{"id": "OrderService", "depends_on": ["PaymentService", "InventoryService"]}], "scope": "component"},
                   "response": {"metrics": [{"component": "OrderService", "Ca": 0, "Ce": 2}]}}],
        tags=["analysis", "metrics", "coupling", "martin"],
    ))

    tools.append(ToolDefinition(
        id="compute_instability_abstractness",
        name="compute_instability_abstractness",
        description="Computes Robert C. Martin's Instability (I = Ce/(Ca+Ce)) and Abstractness (A = abstract_types/total_types) "
                    "for each component. Plots position on the Main Sequence (D = |A + I - 1|). "
                    "Zone of Pain: high stability + low abstraction. Zone of Uselessness: high instability + high abstraction.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.ANALYSIS,
        parameters=[
            ToolParameter("components", "array", "Components with Ca, Ce, abstract_count, total_count"),
            ToolParameter("threshold_d", "number", "Distance-from-main-sequence threshold for flagging", required=False, default=0.3),
        ],
        return_schema={"type": "object", "properties": {
            "metrics": {"type": "array", "items": {"type": "object", "properties": {
                "component": {"type": "string"}, "I": {"type": "number"}, "A": {"type": "number"},
                "D": {"type": "number"}, "zone": {"type": "string"}}}},
            "flagged": {"type": "array"}, "main_sequence_chart": {"type": "string"}}},
        examples=[],
        tags=["analysis", "metrics", "instability", "abstractness", "martin"],
    ))

    tools.append(ToolDefinition(
        id="compute_cohesion_metrics",
        name="compute_cohesion_metrics",
        description="Computes Lack of Cohesion (LCOM) metrics for architecture components. "
                    "Measures how well the internal elements of a component belong together. "
                    "High LCOM suggests the component should be split.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.ANALYSIS,
        parameters=[
            ToolParameter("components", "array", "Components with internal elements and their interactions"),
            ToolParameter("method", "string", "Cohesion measurement method", required=False,
                         enum=["lcom1", "lcom4", "connectivity"], default="lcom4"),
        ],
        return_schema={"type": "object", "properties": {
            "metrics": {"type": "array", "items": {"type": "object", "properties": {
                "component": {"type": "string"}, "lcom": {"type": "number"}, "connected_components": {"type": "integer"},
                "should_split": {"type": "boolean"}}}},
            "split_recommendations": {"type": "array"}}},
        examples=[],
        tags=["analysis", "metrics", "cohesion", "lcom"],
    ))

    # --- Dependency Structure Matrix (DSM) ---
    tools.append(ToolDefinition(
        id="build_dependency_structure_matrix",
        name="build_dependency_structure_matrix",
        description="Builds a Dependency Structure Matrix (DSM) from architecture components and their relationships. "
                    "Rows and columns are components; cells indicate dependency type and strength. "
                    "Supports reordering algorithms (partitioning, clustering) to reveal architectural layers and cycles.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.ANALYSIS,
        parameters=[
            ToolParameter("elements", "array", "Architecture elements (components, services, modules)"),
            ToolParameter("relationships", "array", "Relationships between elements with type and direction"),
            ToolParameter("ordering", "string", "Matrix ordering algorithm", required=False,
                         enum=["original", "partition", "cluster", "band_optimize"], default="partition"),
            ToolParameter("relationship_filter", "array", "Relationship types to include", required=False),
        ],
        return_schema={"type": "object", "properties": {
            "matrix": {"type": "array", "items": {"type": "array"}},
            "element_order": {"type": "array"},
            "cycles": {"type": "array", "items": {"type": "array"}},
            "layers": {"type": "array", "items": {"type": "object", "properties": {
                "layer": {"type": "integer"}, "elements": {"type": "array"}}}},
            "density": {"type": "number"},
            "propagation_cost": {"type": "number"}}},
        examples=[],
        tags=["analysis", "dsm", "dependency", "matrix", "visualization"],
    ))

    tools.append(ToolDefinition(
        id="detect_architecture_cycles",
        name="detect_architecture_cycles",
        description="Detects dependency cycles in the architecture graph using Tarjan's algorithm. "
                    "Cycles indicate architectural debt and potential deployment issues.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.ANALYSIS,
        parameters=[
            ToolParameter("elements", "array", "Architecture elements"),
            ToolParameter("relationships", "array", "Directed relationships between elements"),
            ToolParameter("max_cycle_length", "integer", "Maximum cycle length to report", required=False, default=10),
        ],
        return_schema={"type": "object", "properties": {
            "cycles": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
            "strongly_connected_components": {"type": "array"},
            "cycle_count": {"type": "integer"},
            "acyclic": {"type": "boolean"}}},
        examples=[],
        tags=["analysis", "cycles", "dependency", "tarjan"],
    ))

    # --- Architecture Gap Analysis ---
    tools.append(ToolDefinition(
        id="gap_analysis_asis_tobe",
        name="gap_analysis_asis_tobe",
        description="Performs structured gap analysis between as-is and to-be architecture states. "
                    "Identifies elements that are: (1) unchanged, (2) modified, (3) removed in to-be, (4) new in to-be. "
                    "Maps each gap to required transition activities.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.ANALYSIS,
        parameters=[
            ToolParameter("as_is", "object", "As-is architecture state with elements and relationships"),
            ToolParameter("to_be", "object", "To-be architecture state with elements and relationships"),
            ToolParameter("comparison_keys", "array", "Attributes to compare for change detection", required=False),
            ToolParameter("include_transition", "boolean", "Generate transition architecture recommendations", required=False, default=True),
        ],
        return_schema={"type": "object", "properties": {
            "unchanged": {"type": "array"}, "modified": {"type": "array"},
            "removed": {"type": "array"}, "new": {"type": "array"},
            "gap_count": {"type": "integer"},
            "transition_activities": {"type": "array", "items": {"type": "object", "properties": {
                "gap": {"type": "string"}, "activity": {"type": "string"},
                "effort": {"type": "string"}, "risk": {"type": "string"}}}},
            "impact_matrix": {"type": "object"}}},
        examples=[],
        tags=["analysis", "gap_analysis", "as_is", "to_be", "transition"],
    ))

    tools.append(ToolDefinition(
        id="capability_gap_heatmap",
        name="capability_gap_heatmap",
        description="Generates a capability-based gap heatmap. Scores current capabilities against target maturity, "
                    "producing a visual heatmap showing investment priorities. Uses TOGAF capability-based planning.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.ANALYSIS,
        parameters=[
            ToolParameter("capabilities", "array", "Capabilities with current and target maturity scores (1-5)"),
            ToolParameter("dimensions", "array", "Assessment dimensions", required=False,
                         enum=["process", "people", "technology", "information"], default=None),
            ToolParameter("weighting", "string", "Capability weighting scheme", required=False,
                         enum=["equal", "strategic_value", "risk"], default="strategic_value"),
        ],
        return_schema={"type": "object", "properties": {
            "heatmap": {"type": "array", "items": {"type": "object", "properties": {
                "capability": {"type": "string"}, "current": {"type": "number"},
                "target": {"type": "number"}, "gap": {"type": "number"}, "priority": {"type": "string"}}}},
            "investment_priorities": {"type": "array"},
            "total_gap_score": {"type": "number"}}},
        examples=[],
        tags=["analysis", "capability", "gap", "heatmap", "maturity"],
    ))

    # --- Architecture Health & Complexity ---
    tools.append(ToolDefinition(
        id="compute_architecture_complexity",
        name="compute_architecture_complexity",
        description="Computes architecture complexity metrics: total elements, total relationships, "
                    "connectivity ratio, depth of inheritance, fan-in/fan-out distribution, "
                    "and overall complexity score using graph-theoretic measures.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.ANALYSIS,
        parameters=[
            ToolParameter("elements", "array", "All architecture elements"),
            ToolParameter("relationships", "array", "All relationships between elements"),
            ToolParameter("include_distribution", "boolean", "Include statistical distributions", required=False, default=True),
        ],
        return_schema={"type": "object", "properties": {
            "element_count": {"type": "integer"}, "relationship_count": {"type": "integer"},
            "connectivity_ratio": {"type": "number"}, "avg_fan_in": {"type": "number"},
            "avg_fan_out": {"type": "number"}, "max_fan_in": {"type": "object"},
            "max_fan_out": {"type": "object"}, "depth_distribution": {"type": "array"},
            "complexity_score": {"type": "number"}, "complexity_rating": {"type": "string"}}},
        examples=[],
        tags=["analysis", "complexity", "health", "graph"],
    ))

    tools.append(ToolDefinition(
        id="detect_architecture_smells",
        name="detect_architecture_smells",
        description="Detects common architecture smells: god components (too many responsibilities), "
                    "hub-and-spoke (single point of failure), cyclic dependencies, dead components, "
                    "ambiguous interfaces, and scattered functionality.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.ANALYSIS,
        parameters=[
            ToolParameter("elements", "array", "Architecture elements with types and properties"),
            ToolParameter("relationships", "array", "Relationships between elements"),
            ToolParameter("thresholds", "object", "Custom thresholds for smell detection", required=False),
        ],
        return_schema={"type": "object", "properties": {
            "smells": {"type": "array", "items": {"type": "object", "properties": {
                "type": {"type": "string"}, "severity": {"type": "string"},
                "elements": {"type": "array"}, "description": {"type": "string"},
                "recommendation": {"type": "string"}}}},
            "smell_count": {"type": "integer"}, "health_score": {"type": "number"}}},
        examples=[],
        tags=["analysis", "smells", "health", "quality"],
    ))

    tools.append(ToolDefinition(
        id="compute_modularity_score",
        name="compute_modularity_score",
        description="Computes the modularity score (Q) of an architecture using Newman's modularity metric. "
                    "Q measures how well the architecture decomposes into loosely coupled, highly cohesive modules. "
                    "Scores range from -0.5 to 1.0; values above 0.3 indicate meaningful modular structure.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.ANALYSIS,
        parameters=[
            ToolParameter("elements", "array", "Architecture elements with module/domain assignments"),
            ToolParameter("relationships", "array", "Relationships between elements"),
            ToolParameter("module_field", "string", "Field name identifying module membership", required=False, default="domain"),
        ],
        return_schema={"type": "object", "properties": {
            "Q": {"type": "number"}, "modules": {"type": "array", "items": {"type": "object", "properties": {
                "module": {"type": "string"}, "internal_edges": {"type": "integer"},
                "external_edges": {"type": "integer"}, "cohesion": {"type": "number"}}}},
            "inter_module_coupling": {"type": "array"}}},
        examples=[],
        tags=["analysis", "modularity", "newman", "graph"],
    ))

    # --- Technology Radar ---
    tools.append(ToolDefinition(
        id="get_technology_radar",
        name="get_technology_radar",
        description="Retrieves technology radar data with ring classifications (Adopt, Trial, Assess, Hold) "
                    "for technologies across quadrants (Techniques, Platforms, Tools, Languages & Frameworks). "
                    "Based on ThoughtWorks Technology Radar methodology.",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.TECHNOLOGY_RADAR,
        parameters=[
            ToolParameter("quadrant", "string", "Radar quadrant to query", required=False,
                         enum=["techniques", "platforms", "tools", "languages_frameworks"]),
            ToolParameter("ring", "string", "Radar ring to filter", required=False,
                         enum=["adopt", "trial", "assess", "hold"]),
            ToolParameter("tags", "array", "Technology tags to filter by", required=False),
        ],
        return_schema={"type": "object", "properties": {
            "entries": {"type": "array", "items": {"type": "object", "properties": {
                "name": {"type": "string"}, "quadrant": {"type": "string"}, "ring": {"type": "string"},
                "description": {"type": "string"}, "moved": {"type": "string"}}}},
            "total": {"type": "integer"}}},
        examples=[{"call": {"quadrant": "platforms", "ring": "adopt"},
                   "response": {"entries": [{"name": "Kubernetes", "quadrant": "platforms", "ring": "adopt",
                                            "description": "Container orchestration standard", "moved": "stable"}]}}],
        tags=["radar", "technology", "assessment"],
    ))

    tools.append(ToolDefinition(
        id="assess_technology_fitness",
        name="assess_technology_fitness",
        description="Assesses the fitness of a technology choice against architectural quality attributes "
                    "(scalability, reliability, security, operability, cost). Cross-references technology radar position "
                    "and community momentum to produce an adoption recommendation.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.TECHNOLOGY_RADAR,
        parameters=[
            ToolParameter("technology", "string", "Technology name to assess"),
            ToolParameter("quality_attributes", "array", "Required quality attributes with priorities"),
            ToolParameter("context", "object", "Deployment context (scale, team_size, budget, timeline)", required=False),
        ],
        return_schema={"type": "object", "properties": {
            "technology": {"type": "string"}, "radar_position": {"type": "string"},
            "fitness_scores": {"type": "object"}, "overall_fitness": {"type": "number"},
            "recommendation": {"type": "string"}, "risks": {"type": "array"},
            "alternatives": {"type": "array"}}},
        examples=[],
        tags=["radar", "technology", "fitness", "assessment"],
    ))

    tools.append(ToolDefinition(
        id="compare_technology_stacks",
        name="compare_technology_stacks",
        description="Compares two or more technology stack alternatives across dimensions: "
                    "maturity, community size, learning curve, operational complexity, licensing cost, "
                    "ecosystem breadth, and alignment with architecture principles.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.TECHNOLOGY_RADAR,
        parameters=[
            ToolParameter("stacks", "array", "Technology stack alternatives to compare"),
            ToolParameter("criteria", "array", "Comparison criteria with weights", required=False),
            ToolParameter("context", "object", "Organizational context for evaluation", required=False),
        ],
        return_schema={"type": "object", "properties": {
            "comparison_matrix": {"type": "array"}, "winner": {"type": "string"},
            "trade_offs": {"type": "array"}, "migration_complexity": {"type": "object"}}},
        examples=[],
        tags=["radar", "technology", "comparison", "stack"],
    ))

    # --- Cross-domain reference architecture retrieval ---
    tools.append(ToolDefinition(
        id="get_bian_service_domain",
        name="get_bian_service_domain",
        description="Retrieves BIAN Service Landscape service domain details including business area, "
                    "service operations, asset types, and behavioral qualifiers.",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.GENERAL,
        parameters=[
            ToolParameter("domain_name", "string", "BIAN service domain name or partial match"),
            ToolParameter("business_area", "string", "Filter by business area", required=False),
        ],
        return_schema={"type": "object", "properties": {
            "domain": {"type": "string"}, "business_area": {"type": "string"},
            "description": {"type": "string"}, "service_operations": {"type": "array"},
            "asset_type": {"type": "string"}, "behavioral_qualifiers": {"type": "array"}}},
        examples=[],
        tags=["bian", "banking", "reference_architecture"],
    ))

    tools.append(ToolDefinition(
        id="get_tmforum_functional_block",
        name="get_tmforum_functional_block",
        description="Retrieves TMForum ODA functional block details including capabilities, "
                    "exposed APIs (Open APIs), and integration points.",
        tool_type=ToolType.RETRIEVAL,
        domain=ToolDomain.GENERAL,
        parameters=[
            ToolParameter("block_name", "string", "ODA functional block name or partial match"),
            ToolParameter("area", "string", "Filter by ODA area", required=False,
                         enum=["core_commerce", "production", "engagement", "intelligence", "security", "integration", "enterprise"]),
        ],
        return_schema={"type": "object", "properties": {
            "block": {"type": "string"}, "area": {"type": "string"},
            "description": {"type": "string"}, "capabilities": {"type": "array"},
            "open_apis": {"type": "array"}, "integration_points": {"type": "array"}}},
        examples=[],
        tags=["tmforum", "oda", "telecom", "reference_architecture"],
    ))

    tools.append(ToolDefinition(
        id="map_team_topology",
        name="map_team_topology",
        description="Maps architecture components to Team Topologies patterns. Analyzes component boundaries, "
                    "interaction patterns, and cognitive load to recommend team structures "
                    "(stream-aligned, platform, enabling, complicated-subsystem) and interaction modes.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.ANALYSIS,
        parameters=[
            ToolParameter("components", "array", "Architecture components with domain and dependency info"),
            ToolParameter("current_teams", "array", "Current team structures", required=False),
            ToolParameter("max_cognitive_load", "integer", "Max services per team before splitting", required=False, default=8),
        ],
        return_schema={"type": "object", "properties": {
            "recommended_teams": {"type": "array", "items": {"type": "object", "properties": {
                "name": {"type": "string"}, "type": {"type": "string"},
                "components": {"type": "array"}, "interaction_mode": {"type": "string"}}}},
            "cognitive_load_analysis": {"type": "object"},
            "fracture_planes": {"type": "array"}}},
        examples=[],
        tags=["analysis", "team_topologies", "organizational"],
    ))

    # --- Architecture Fitness Functions ---
    tools.append(ToolDefinition(
        id="evaluate_fitness_functions",
        name="evaluate_fitness_functions",
        description="Evaluates architecture fitness functions — automated tests for architecture characteristics. "
                    "Checks quantifiable quality attributes against defined thresholds: "
                    "response time, availability, deployment frequency, coupling metrics, security posture.",
        tool_type=ToolType.PROCESSING,
        domain=ToolDomain.ANALYSIS,
        parameters=[
            ToolParameter("fitness_functions", "array", "Fitness function definitions with thresholds"),
            ToolParameter("measurements", "object", "Current measurement values"),
            ToolParameter("trend_window", "integer", "Number of historical data points for trend analysis", required=False, default=10),
        ],
        return_schema={"type": "object", "properties": {
            "results": {"type": "array", "items": {"type": "object", "properties": {
                "function": {"type": "string"}, "passed": {"type": "boolean"},
                "current": {"type": "number"}, "threshold": {"type": "number"},
                "trend": {"type": "string"}}}},
            "overall_fitness": {"type": "number"}, "failing_count": {"type": "integer"}}},
        examples=[],
        tags=["analysis", "fitness_functions", "evolutionary", "quality"],
    ))

    return tools


def build_tool_pool() -> list[ToolDefinition]:
    """Builds the complete tool pool."""
    tools = []
    tools.extend(_retrieval_tools_adm())
    tools.extend(_retrieval_tools_archimate())
    tools.extend(_retrieval_tools_repository())
    tools.extend(_retrieval_tools_governance())
    tools.extend(_retrieval_tools_general())
    tools.extend(_processing_tools())
    tools.extend(_analysis_tools())
    return tools


def save_tool_pool(output_path: Path | None = None) -> tuple[Path, int]:
    """Builds and saves the tool pool. Returns (path, count)."""
    tools = build_tool_pool()
    path = output_path or Path("pools/tools/tool_pool.json")
    save_pool(tools, path)
    return path, len(tools)


if __name__ == "__main__":
    path, count = save_tool_pool()
    retrieval = sum(1 for t in build_tool_pool() if t.tool_type == ToolType.RETRIEVAL)
    processing = count - retrieval
    print(f"Tool pool saved to {path}: {count} tools ({retrieval} retrieval, {processing} processing)")
