"""ArchiMate reference tools + architecture analysis/compute tools.

Provides live implementations for:
- ArchiMate 3.2 element queries (6 layer variants)
- ArchiMate viewpoint queries (24 viewpoint variants)
- ArchiMate relationship, metamodel, and model query tools
- Architecture analysis & compute tools (gap analysis, risk, compliance, etc.)

All functions accept **kwargs to absorb extra parameters from the pool.
TOOL_REGISTRY maps pool tool IDs → callables.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

# =====================================================================
# ArchiMate 3.2 Element Data
# =====================================================================

_ARCHIMATE_ELEMENTS: dict[str, list[dict[str, Any]]] = {
    "business": [
        {"type": "BusinessActor", "description": "An organizational entity that performs behavior", "examples": ["Customer", "Employee", "Partner Organization"]},
        {"type": "BusinessRole", "description": "Responsibility for performing specific behavior", "examples": ["Account Manager", "Process Owner", "Risk Officer"]},
        {"type": "BusinessCollaboration", "description": "Aggregate of two or more roles working together", "examples": ["Loan Committee", "Architecture Board"]},
        {"type": "BusinessInterface", "description": "Point of access to a business service", "examples": ["Customer Portal", "Help Desk", "Branch Office"]},
        {"type": "BusinessProcess", "description": "Sequence of business behaviors achieving a specific result", "examples": ["Order-to-Cash", "Hire-to-Retire", "Procure-to-Pay"]},
        {"type": "BusinessFunction", "description": "Collection of behavior based on chosen criteria", "examples": ["Financial Management", "HR Management", "Risk Management"]},
        {"type": "BusinessInteraction", "description": "Unit of collective behavior performed by collaborations", "examples": ["Negotiation", "Joint Review"]},
        {"type": "BusinessEvent", "description": "Something that happens and may trigger behavior", "examples": ["Customer Request", "Payment Received", "Claim Filed"]},
        {"type": "BusinessService", "description": "Explicitly defined behavior that a role exposes", "examples": ["Insurance Service", "Payment Service", "Lending Service"]},
        {"type": "BusinessObject", "description": "Concept relevant from a business perspective", "examples": ["Contract", "Invoice", "Customer Profile", "Policy"]},
        {"type": "Contract", "description": "Formal or informal specification of agreement", "examples": ["SLA", "OLA", "Underpinning Contract"]},
        {"type": "Representation", "description": "Perceptible form of information", "examples": ["PDF Document", "Paper Form", "Digital Certificate"]},
        {"type": "Product", "description": "Coherent collection of services and/or passive elements", "examples": ["Mortgage Product", "Insurance Package", "Savings Account"]},
    ],
    "application": [
        {"type": "ApplicationComponent", "description": "Encapsulation of application functionality", "examples": ["CRM System", "ERP Module", "Payment Gateway"]},
        {"type": "ApplicationCollaboration", "description": "Aggregate of two or more components working together", "examples": ["Integration Hub", "Service Mesh"]},
        {"type": "ApplicationInterface", "description": "Point of access to application services", "examples": ["REST API", "Web Portal", "Message Queue Interface"]},
        {"type": "ApplicationFunction", "description": "Automated behavior performed by a component", "examples": ["Data Validation", "Transaction Processing", "Report Generation"]},
        {"type": "ApplicationProcess", "description": "Sequence of application behaviors", "examples": ["Batch Processing", "ETL Pipeline", "Workflow Execution"]},
        {"type": "ApplicationInteraction", "description": "Unit of collective application behavior", "examples": ["API Call Exchange", "Event Choreography"]},
        {"type": "ApplicationEvent", "description": "Application state change", "examples": ["Transaction Completed", "Threshold Alert", "File Received"]},
        {"type": "ApplicationService", "description": "Explicitly defined application behavior", "examples": ["Authentication Service", "Notification Service", "Search Service"]},
        {"type": "DataObject", "description": "Data structured for automated processing", "examples": ["Customer Record", "Transaction Log", "Configuration File"]},
    ],
    "technology": [
        {"type": "Node", "description": "Computational or physical resource hosting artifacts", "examples": ["Application Server", "Database Server", "Cloud VM"]},
        {"type": "Device", "description": "Physical IT resource for processing", "examples": ["Firewall Appliance", "Load Balancer", "Storage Array"]},
        {"type": "SystemSoftware", "description": "Software managing hardware and provides services", "examples": ["Operating System", "DBMS", "Middleware", "Container Runtime"]},
        {"type": "TechnologyCollaboration", "description": "Aggregate of nodes working together", "examples": ["Server Cluster", "Database Cluster"]},
        {"type": "TechnologyInterface", "description": "Point of access to technology services", "examples": ["HTTP Endpoint", "JDBC Connection", "SSH Interface"]},
        {"type": "Path", "description": "Link between nodes for communication", "examples": ["LAN Segment", "VPN Tunnel", "API Gateway Route"]},
        {"type": "CommunicationNetwork", "description": "Set of structures connecting nodes", "examples": ["Corporate WAN", "DMZ Network", "Cloud VPC"]},
        {"type": "TechnologyFunction", "description": "Collection of technology behavior", "examples": ["Load Balancing", "Data Replication", "Encryption"]},
        {"type": "TechnologyProcess", "description": "Sequence of technology behavior", "examples": ["Backup Process", "Deployment Pipeline", "Failover Sequence"]},
        {"type": "TechnologyService", "description": "Explicitly defined technology behavior", "examples": ["Hosting Service", "Storage Service", "Messaging Service"]},
        {"type": "TechnologyEvent", "description": "Technology state change", "examples": ["Server Failure", "Capacity Threshold", "Security Alert"]},
        {"type": "Artifact", "description": "Piece of data used or produced", "examples": ["WAR File", "Docker Image", "Config Script"]},
    ],
    "motivation": [
        {"type": "Stakeholder", "description": "Role of an individual, team, or organization with interests", "examples": ["CIO", "Business Owner", "Regulator", "End User"]},
        {"type": "Driver", "description": "External or internal condition that motivates change", "examples": ["Digital Transformation", "Regulatory Compliance", "Cost Reduction"]},
        {"type": "Assessment", "description": "Result of analysis of a driver", "examples": ["SWOT Analysis Result", "Risk Assessment", "Maturity Assessment"]},
        {"type": "Goal", "description": "End state that a stakeholder intends to achieve", "examples": ["Reduce Operational Cost by 20%", "Achieve ISO 27001 Certification"]},
        {"type": "Outcome", "description": "End result that has been achieved", "examples": ["Improved Customer Satisfaction", "Reduced Processing Time"]},
        {"type": "Principle", "description": "Qualitative statement of intent", "examples": ["Single Source of Truth", "Security by Design", "API-First"]},
        {"type": "Requirement", "description": "Statement of need", "examples": ["99.9% Uptime", "GDPR Compliance", "Sub-second Response Time"]},
        {"type": "Constraint", "description": "Factor that limits realization", "examples": ["Budget Limit", "Legacy System Dependency", "Regulatory Deadline"]},
        {"type": "Meaning", "description": "Knowledge or expertise assigned to a concept", "examples": ["Policy Interpretation", "Standard Definition"]},
        {"type": "Value", "description": "Relative worth or importance", "examples": ["Customer Loyalty", "Operational Efficiency", "Market Agility"]},
    ],
    "strategy": [
        {"type": "Resource", "description": "Asset owned or controlled", "examples": ["IT Budget", "Development Team", "Data Center", "Patent Portfolio"]},
        {"type": "Capability", "description": "Ability that an organization possesses", "examples": ["Data Analytics", "Cloud Migration", "DevOps", "API Management"]},
        {"type": "ValueStream", "description": "Sequence of activities creating an overall result for a customer", "examples": ["Customer Onboarding", "Claim Processing", "Product Development"]},
        {"type": "CourseOfAction", "description": "Approach or plan for achieving a goal", "examples": ["Cloud-First Strategy", "Microservices Adoption", "Zero-Trust Implementation"]},
    ],
    "implementation_migration": [
        {"type": "WorkPackage", "description": "Series of actions to achieve a result", "examples": ["API Gateway Implementation", "Data Migration Phase 1", "Security Hardening Sprint"]},
        {"type": "Deliverable", "description": "Precisely-defined outcome of a work package", "examples": ["Architecture Document", "Migration Report", "Test Results"]},
        {"type": "ImplementationEvent", "description": "State change related to implementation", "examples": ["Go-Live", "Phase Completion", "Release Deployment"]},
        {"type": "Plateau", "description": "Relatively stable state of architecture", "examples": ["Baseline Architecture", "Target Architecture 2025", "Transition Architecture Q3"]},
        {"type": "Gap", "description": "Statement of difference between two plateaus", "examples": ["Missing API Layer", "Legacy System Dependency", "Skill Gap in Cloud"]},
    ],
}

# =====================================================================
# ArchiMate 3.2 Viewpoint Data
# =====================================================================

_ARCHIMATE_VIEWPOINTS: dict[str, dict[str, Any]] = {
    "organization": {
        "name": "Organization Viewpoint",
        "purpose": "Shows the structure of the enterprise in terms of its business actors, roles, and their relationships",
        "stakeholders": ["Enterprise Architects", "Business Managers", "Process Owners"],
        "layers": ["Business"],
        "key_elements": ["BusinessActor", "BusinessRole", "BusinessCollaboration", "Location"],
        "key_relationships": ["Composition", "Aggregation", "Assignment"],
        "typical_use": "Identify organizational structure and reporting lines; map roles to organizational units",
    },
    "business_process_cooperation": {
        "name": "Business Process Cooperation Viewpoint",
        "purpose": "Shows relationships between business processes and their environment (services, roles, objects)",
        "stakeholders": ["Process Architects", "Business Analysts", "Operational Managers"],
        "layers": ["Business"],
        "key_elements": ["BusinessProcess", "BusinessService", "BusinessRole", "BusinessObject", "BusinessEvent"],
        "key_relationships": ["Triggering", "Flow", "Serving", "Access"],
        "typical_use": "Model end-to-end business process interactions; identify handoffs and dependencies",
    },
    "product": {
        "name": "Product Viewpoint",
        "purpose": "Shows the value a product offers and its realization by business and application services",
        "stakeholders": ["Product Managers", "Business Architects"],
        "layers": ["Business", "Application"],
        "key_elements": ["Product", "BusinessService", "ApplicationService", "Contract", "Value"],
        "key_relationships": ["Composition", "Serving", "Realization"],
        "typical_use": "Define product bundles; map services to products; communicate product composition",
    },
    "application_cooperation": {
        "name": "Application Cooperation Viewpoint",
        "purpose": "Shows application components and their relationships",
        "stakeholders": ["Application Architects", "Integration Specialists"],
        "layers": ["Application"],
        "key_elements": ["ApplicationComponent", "ApplicationInterface", "ApplicationService", "DataObject"],
        "key_relationships": ["Flow", "Serving", "Composition", "Access"],
        "typical_use": "Map application landscape; identify integration points and data flows",
    },
    "application_usage": {
        "name": "Application Usage Viewpoint",
        "purpose": "Shows how applications are used by business processes",
        "stakeholders": ["Enterprise Architects", "Business Analysts"],
        "layers": ["Business", "Application"],
        "key_elements": ["BusinessProcess", "ApplicationService", "ApplicationComponent", "DataObject"],
        "key_relationships": ["Serving", "Access", "Triggering"],
        "typical_use": "Show business-to-IT alignment; identify which applications support which processes",
    },
    "technology_usage": {
        "name": "Technology Usage Viewpoint",
        "purpose": "Shows how applications are supported by technology infrastructure",
        "stakeholders": ["Infrastructure Architects", "Operations Teams"],
        "layers": ["Application", "Technology"],
        "key_elements": ["ApplicationComponent", "Node", "Device", "SystemSoftware", "TechnologyService"],
        "key_relationships": ["Serving", "Assignment", "Realization"],
        "typical_use": "Map applications to infrastructure; plan infrastructure upgrades",
    },
    "technology": {
        "name": "Technology Viewpoint",
        "purpose": "Shows the structure of technology infrastructure",
        "stakeholders": ["Infrastructure Architects", "Network Engineers"],
        "layers": ["Technology"],
        "key_elements": ["Node", "Device", "SystemSoftware", "CommunicationNetwork", "Path", "Artifact"],
        "key_relationships": ["Composition", "Assignment", "Serving", "Realization"],
        "typical_use": "Document infrastructure topology; plan capacity and deployment",
    },
    "information_structure": {
        "name": "Information Structure Viewpoint",
        "purpose": "Shows the structure of information used in the enterprise",
        "stakeholders": ["Data Architects", "Information Managers"],
        "layers": ["Business", "Application"],
        "key_elements": ["BusinessObject", "DataObject", "Representation"],
        "key_relationships": ["Composition", "Aggregation", "Association", "Realization"],
        "typical_use": "Model conceptual and logical data structures; define data ownership",
    },
    "service_realization": {
        "name": "Service Realization Viewpoint",
        "purpose": "Shows how services are realized by the required behavior",
        "stakeholders": ["Service Designers", "Enterprise Architects"],
        "layers": ["Business", "Application"],
        "key_elements": ["BusinessService", "ApplicationService", "BusinessProcess", "ApplicationComponent"],
        "key_relationships": ["Realization", "Serving", "Composition"],
        "typical_use": "Trace services to their implementing processes and components",
    },
    "implementation_deployment": {
        "name": "Implementation and Deployment Viewpoint",
        "purpose": "Shows how applications map to technology infrastructure",
        "stakeholders": ["DevOps Engineers", "Deployment Architects"],
        "layers": ["Application", "Technology"],
        "key_elements": ["ApplicationComponent", "Artifact", "Node", "Device", "SystemSoftware"],
        "key_relationships": ["Assignment", "Realization"],
        "typical_use": "Plan deployments; document current deployment topology",
    },
    "layered": {
        "name": "Layered Viewpoint",
        "purpose": "Provides a cross-layer overview of the enterprise architecture",
        "stakeholders": ["Enterprise Architects", "CIO", "Architecture Review Board"],
        "layers": ["Business", "Application", "Technology", "Strategy", "Motivation"],
        "key_elements": ["All layer elements"],
        "key_relationships": ["Serving", "Realization", "Composition", "Assignment"],
        "typical_use": "Executive overview; show alignment across all architecture layers",
    },
    "landscape_map": {
        "name": "Landscape Map Viewpoint",
        "purpose": "Shows a map-like overview of architectures across multiple contexts",
        "stakeholders": ["Enterprise Architects", "Portfolio Managers"],
        "layers": ["Business", "Application"],
        "key_elements": ["Plateau", "ApplicationComponent", "BusinessFunction"],
        "key_relationships": ["Composition", "Aggregation"],
        "typical_use": "Application portfolio rationalization; identify overlaps and gaps",
    },
    "goal_realization": {
        "name": "Goal Realization Viewpoint",
        "purpose": "Shows how goals are refined and realized by requirements and core elements",
        "stakeholders": ["Business Architects", "Strategy Planners"],
        "layers": ["Motivation", "Business"],
        "key_elements": ["Goal", "Requirement", "Principle", "Constraint", "CourseOfAction"],
        "key_relationships": ["Realization", "Influence", "Aggregation"],
        "typical_use": "Trace strategy to implementation; validate goal decomposition",
    },
    "requirements_realization": {
        "name": "Requirements Realization Viewpoint",
        "purpose": "Shows requirements and how they are realized by core elements",
        "stakeholders": ["Solution Architects", "Business Analysts"],
        "layers": ["Motivation", "Business", "Application", "Technology"],
        "key_elements": ["Requirement", "Constraint", "BusinessProcess", "ApplicationComponent"],
        "key_relationships": ["Realization", "Aggregation"],
        "typical_use": "Requirements traceability; validate that all requirements are addressed",
    },
    "motivation": {
        "name": "Motivation Viewpoint",
        "purpose": "Shows the motivational aspects: stakeholders, drivers, goals, principles, requirements",
        "stakeholders": ["Enterprise Architects", "Business Strategists"],
        "layers": ["Motivation"],
        "key_elements": ["Stakeholder", "Driver", "Assessment", "Goal", "Outcome", "Principle", "Requirement"],
        "key_relationships": ["Association", "Influence", "Realization", "Aggregation"],
        "typical_use": "Articulate WHY architecture decisions are made; capture motivational context",
    },
    "strategy": {
        "name": "Strategy Viewpoint",
        "purpose": "Shows the strategic direction and how it is supported by capabilities and resources",
        "stakeholders": ["CxO", "Strategy Planners", "Enterprise Architects"],
        "layers": ["Strategy", "Motivation"],
        "key_elements": ["Resource", "Capability", "ValueStream", "CourseOfAction", "Goal"],
        "key_relationships": ["Realization", "Association", "Composition", "Assignment"],
        "typical_use": "Strategy-to-execution mapping; capability-based planning",
    },
    "capability_map": {
        "name": "Capability Map Viewpoint",
        "purpose": "Shows the capabilities of the enterprise and their relationships",
        "stakeholders": ["Enterprise Architects", "Business Strategists"],
        "layers": ["Strategy"],
        "key_elements": ["Capability", "Resource", "CourseOfAction"],
        "key_relationships": ["Composition", "Aggregation", "Realization", "Assignment"],
        "typical_use": "Capability maturity assessment; investment prioritization",
    },
    "outcome_realization": {
        "name": "Outcome Realization Viewpoint",
        "purpose": "Shows how outcomes relate to requirements and deliverables",
        "stakeholders": ["Program Managers", "Enterprise Architects"],
        "layers": ["Motivation", "Implementation & Migration"],
        "key_elements": ["Outcome", "Deliverable", "Value", "BusinessService"],
        "key_relationships": ["Realization", "Association", "Influence"],
        "typical_use": "Benefits realization tracking; outcome-driven architecture",
    },
    "resource_map": {
        "name": "Resource Map Viewpoint",
        "purpose": "Shows resources and their allocation to capabilities",
        "stakeholders": ["Resource Managers", "Enterprise Architects"],
        "layers": ["Strategy"],
        "key_elements": ["Resource", "Capability", "CourseOfAction"],
        "key_relationships": ["Assignment", "Association", "Realization"],
        "typical_use": "Resource planning; identify resource constraints and allocations",
    },
    "value_stream": {
        "name": "Value Stream Viewpoint",
        "purpose": "Shows how value streams create outcomes through a series of stages",
        "stakeholders": ["Business Architects", "Lean Practitioners"],
        "layers": ["Strategy", "Business"],
        "key_elements": ["ValueStream", "Capability", "BusinessService", "Value", "Outcome"],
        "key_relationships": ["Triggering", "Flow", "Realization"],
        "typical_use": "Value stream mapping; identify value-adding and waste activities",
    },
    "migration": {
        "name": "Migration Viewpoint",
        "purpose": "Shows the transition from baseline to target architecture",
        "stakeholders": ["Enterprise Architects", "Program Managers"],
        "layers": ["Implementation & Migration"],
        "key_elements": ["Plateau", "Gap", "WorkPackage", "Deliverable", "ImplementationEvent"],
        "key_relationships": ["Triggering", "Composition", "Association"],
        "typical_use": "Plan migration roadmaps; identify gaps between architecture states",
    },
    "project": {
        "name": "Project Viewpoint",
        "purpose": "Shows the management of architecture change through projects/work packages",
        "stakeholders": ["Project Managers", "PMO"],
        "layers": ["Implementation & Migration"],
        "key_elements": ["WorkPackage", "Deliverable", "ImplementationEvent", "BusinessRole"],
        "key_relationships": ["Triggering", "Realization", "Assignment"],
        "typical_use": "Project portfolio management; architecture change governance",
    },
    "stakeholder": {
        "name": "Stakeholder Viewpoint",
        "purpose": "Shows the stakeholders, their concerns, and how architecture addresses them",
        "stakeholders": ["Enterprise Architects", "Governance Bodies"],
        "layers": ["Motivation"],
        "key_elements": ["Stakeholder", "Driver", "Goal", "Assessment"],
        "key_relationships": ["Association", "Influence", "Composition"],
        "typical_use": "Stakeholder analysis; concern-driven architecture development",
    },
    "physical": {
        "name": "Physical Viewpoint",
        "purpose": "Shows the physical environment and how it relates to IT infrastructure",
        "stakeholders": ["Facilities Managers", "Infrastructure Architects"],
        "layers": ["Technology", "Physical"],
        "key_elements": ["Facility", "Equipment", "DistributionNetwork", "Material"],
        "key_relationships": ["Composition", "Serving", "Realization"],
        "typical_use": "Data center planning; physical-digital integration modeling",
    },
}

# =====================================================================
# ArchiMate Metamodel
# =====================================================================

_ARCHIMATE_RELATIONSHIPS = [
    {"type": "Composition", "category": "Structural", "description": "Indicates that an element consists of one or more other concepts", "notation": "Filled diamond"},
    {"type": "Aggregation", "category": "Structural", "description": "Indicates that an element combines one or more other concepts", "notation": "Unfilled diamond"},
    {"type": "Assignment", "category": "Structural", "description": "Links active structure elements with units of behavior", "notation": "Filled circle + line"},
    {"type": "Realization", "category": "Structural", "description": "Indicates that an entity plays a critical role in the creation of a more abstract entity", "notation": "Dashed line with unfilled arrowhead"},
    {"type": "Serving", "category": "Dependency", "description": "Models that an element provides its functionality to another element", "notation": "Line with open arrowhead"},
    {"type": "Access", "category": "Dependency", "description": "Models the ability of behavior elements to observe or act upon passive elements", "notation": "Dashed line with arrowhead"},
    {"type": "Influence", "category": "Dependency", "description": "Models that an element affects the implementation or achievement of some motivation element", "notation": "Dashed line with open arrowhead"},
    {"type": "Association", "category": "Other", "description": "Models an unspecified relationship, or one that is not represented by another relationship", "notation": "Simple line"},
    {"type": "Triggering", "category": "Dynamic", "description": "Models a temporal or causal relationship between elements", "notation": "Line with filled arrowhead"},
    {"type": "Flow", "category": "Dynamic", "description": "Models transfer from one element to another", "notation": "Dashed line with filled arrowhead"},
    {"type": "Specialization", "category": "Other", "description": "Indicates that an element is a particular kind of another element", "notation": "Line with unfilled triangle arrowhead"},
]

_ARCHIMATE_METAMODEL = {
    "specification": "ArchiMate 3.2",
    "layers": ["Strategy", "Motivation", "Business", "Application", "Technology", "Physical", "Implementation & Migration"],
    "aspect_types": ["Active Structure", "Behavior", "Passive Structure"],
    "relationship_types": [r["type"] for r in _ARCHIMATE_RELATIONSHIPS],
    "relationship_categories": ["Structural", "Dependency", "Dynamic", "Other"],
    "cross_layer_rules": [
        "Serving relationships can cross layers (lower serves higher)",
        "Realization relationships can cross layers (lower realizes higher)",
        "Triggering and flow relationships typically stay within a layer",
        "Composition and aggregation are typically within the same layer",
    ],
    "derivation_rules": [
        "Structural relationships can be derived through chains",
        "Serving + Realization = derived Serving",
        "Assignment + Serving = derived Serving",
    ],
}


# =====================================================================
# ArchiMate Element Functions
# =====================================================================

def archimate_get_elements(*, layer: str = "business", element_type: str | None = None, **kwargs: Any) -> dict[str, Any]:
    """Get ArchiMate elements for a specific layer."""
    layer_key = layer.lower().replace(" ", "_").replace("&", "").replace("__", "_")
    # Normalize common aliases
    aliases = {"implementation": "implementation_migration", "migration": "implementation_migration", "impl": "implementation_migration"}
    layer_key = aliases.get(layer_key, layer_key)

    elements = _ARCHIMATE_ELEMENTS.get(layer_key, [])
    if element_type:
        elements = [e for e in elements if element_type.lower() in e["type"].lower()]

    return {
        "layer": layer,
        "element_count": len(elements),
        "elements": elements,
        "specification": "ArchiMate 3.2",
    }


def archimate_get_viewpoint(*, viewpoint: str = "layered", **kwargs: Any) -> dict[str, Any]:
    """Get ArchiMate viewpoint details."""
    vp_key = viewpoint.lower().replace(" ", "_").replace("-", "_")
    vp = _ARCHIMATE_VIEWPOINTS.get(vp_key)
    if not vp:
        # Fuzzy match
        for k, v in _ARCHIMATE_VIEWPOINTS.items():
            if vp_key in k or k in vp_key:
                vp = v
                break
    if not vp:
        return {"error": f"Viewpoint '{viewpoint}' not found", "available": list(_ARCHIMATE_VIEWPOINTS.keys())}
    return vp


def archimate_get_relationships(*, element: str = "", relationship_type: str | None = None, direction: str = "both", **kwargs: Any) -> dict[str, Any]:
    """Get ArchiMate relationship types and rules."""
    rels = _ARCHIMATE_RELATIONSHIPS
    if relationship_type:
        rels = [r for r in rels if relationship_type.lower() in r["type"].lower() or relationship_type.lower() in r["category"].lower()]
    return {
        "query_element": element,
        "direction": direction,
        "relationship_count": len(rels),
        "relationships": rels,
        "specification": "ArchiMate 3.2",
    }


def archimate_query_model(*, model_id: str = "", query: str = "", max_depth: int = 3, **kwargs: Any) -> dict[str, Any]:
    """Query an ArchiMate model — returns reference architecture patterns."""
    # Return a reference model structure based on query keywords
    layers_found = []
    for layer_name, elems in _ARCHIMATE_ELEMENTS.items():
        for e in elems:
            if query.lower() in e["type"].lower() or any(query.lower() in ex.lower() for ex in e["examples"]):
                layers_found.append({"layer": layer_name, "element": e["type"], "matched_examples": e["examples"]})
                break

    return {
        "model_id": model_id or "reference_model",
        "query": query,
        "max_depth": max_depth,
        "results_count": len(layers_found),
        "results": layers_found[:10],
        "viewpoints_relevant": [k for k, v in _ARCHIMATE_VIEWPOINTS.items() if query.lower() in v["name"].lower() or query.lower() in v["purpose"].lower()][:5],
    }


def archimate_get_metamodel(*, scope: str = "full", **kwargs: Any) -> dict[str, Any]:
    """Get ArchiMate metamodel information."""
    if scope == "relationships":
        return {"relationships": _ARCHIMATE_RELATIONSHIPS, "specification": "ArchiMate 3.2"}
    if scope in _ARCHIMATE_ELEMENTS:
        return {"layer": scope, "elements": _ARCHIMATE_ELEMENTS[scope], "specification": "ArchiMate 3.2"}
    return _ARCHIMATE_METAMODEL


def viewpoint_consistency_check(*, viewpoints: list | None = None, check_type: str = "completeness", **kwargs: Any) -> dict[str, Any]:
    """Check consistency between viewpoints."""
    vps = viewpoints or ["layered"]
    results = []
    for vp_name in vps:
        vp_key = str(vp_name).lower().replace(" ", "_").replace("-", "_")
        vp = _ARCHIMATE_VIEWPOINTS.get(vp_key)
        if vp:
            results.append({"viewpoint": vp["name"], "status": "valid", "layers": vp["layers"], "elements": vp["key_elements"]})
        else:
            results.append({"viewpoint": str(vp_name), "status": "not_found"})

    all_layers = set()
    for r in results:
        all_layers.update(r.get("layers", []))

    return {
        "check_type": check_type,
        "viewpoints_checked": len(results),
        "results": results,
        "coverage": {"layers_covered": sorted(all_layers), "total_layers": 7},
        "consistency_score": round(sum(1 for r in results if r["status"] == "valid") / max(len(results), 1), 2),
    }


# =====================================================================
# Catalog Tools
# =====================================================================

def capability_catalog_search(*, domain: str = "", query: str = "", maturity_filter: str | None = None, **kwargs: Any) -> dict[str, Any]:
    """Search the capability catalog."""
    _CAPABILITIES = {
        "customer_management": {"maturity": 3, "sub_capabilities": ["Customer Onboarding", "Customer Analytics", "Relationship Management", "Customer Communication"]},
        "risk_management": {"maturity": 4, "sub_capabilities": ["Credit Risk", "Market Risk", "Operational Risk", "Compliance Risk", "Liquidity Risk"]},
        "payment_processing": {"maturity": 3, "sub_capabilities": ["Payment Initiation", "Payment Clearing", "Payment Settlement", "Payment Reporting"]},
        "data_analytics": {"maturity": 2, "sub_capabilities": ["Data Collection", "Data Processing", "Data Visualization", "Predictive Analytics"]},
        "digital_channels": {"maturity": 3, "sub_capabilities": ["Mobile Banking", "Internet Banking", "Open Banking APIs", "Digital Wallet"]},
        "lending": {"maturity": 3, "sub_capabilities": ["Loan Origination", "Credit Assessment", "Loan Servicing", "Collections"]},
        "compliance": {"maturity": 4, "sub_capabilities": ["Regulatory Reporting", "AML/KYC", "Policy Management", "Audit Management"]},
        "security": {"maturity": 3, "sub_capabilities": ["Identity Management", "Access Control", "Threat Detection", "Incident Response"]},
    }

    results = []
    for cap_name, cap_data in _CAPABILITIES.items():
        if domain and domain.lower() not in cap_name:
            continue
        if query and query.lower() not in cap_name and not any(query.lower() in sc.lower() for sc in cap_data["sub_capabilities"]):
            continue
        if maturity_filter and cap_data["maturity"] < int(maturity_filter):
            continue
        results.append({"capability": cap_name.replace("_", " ").title(), "maturity": cap_data["maturity"], "sub_capabilities": cap_data["sub_capabilities"]})

    return {"query": query, "domain": domain, "result_count": len(results), "capabilities": results}


def stakeholder_catalog_search(*, query: str = "", role_filter: str | None = None, **kwargs: Any) -> dict[str, Any]:
    """Search the stakeholder catalog."""
    _STAKEHOLDERS = [
        {"name": "Chief Information Officer", "role": "Executive", "concerns": ["IT Strategy", "Budget", "Digital Transformation"], "influence": "High"},
        {"name": "Enterprise Architect", "role": "Architecture", "concerns": ["Standards", "Integration", "Technical Debt"], "influence": "High"},
        {"name": "Business Analyst", "role": "Business", "concerns": ["Requirements", "Process Efficiency", "User Experience"], "influence": "Medium"},
        {"name": "Solution Architect", "role": "Architecture", "concerns": ["Design", "Implementation", "Technology Selection"], "influence": "High"},
        {"name": "Project Manager", "role": "Management", "concerns": ["Timeline", "Budget", "Resources", "Risk"], "influence": "Medium"},
        {"name": "Security Officer", "role": "Security", "concerns": ["Data Protection", "Compliance", "Threat Management"], "influence": "High"},
        {"name": "Data Architect", "role": "Architecture", "concerns": ["Data Quality", "Data Governance", "Master Data"], "influence": "Medium"},
        {"name": "Operations Manager", "role": "Operations", "concerns": ["SLA", "Performance", "Availability", "Incident Management"], "influence": "Medium"},
        {"name": "Chief Technology Officer", "role": "Executive", "concerns": ["Technology Strategy", "Innovation", "Platform Architecture"], "influence": "High"},
        {"name": "Compliance Officer", "role": "Governance", "concerns": ["Regulatory Requirements", "Audit", "Policy Adherence"], "influence": "High"},
    ]
    results = _STAKEHOLDERS
    if query:
        results = [s for s in results if query.lower() in s["name"].lower() or any(query.lower() in c.lower() for c in s["concerns"])]
    if role_filter:
        results = [s for s in results if role_filter.lower() in s["role"].lower()]
    return {"query": query, "role_filter": role_filter, "result_count": len(results), "stakeholders": results}


# =====================================================================
# Architecture Analysis & Compute Tools
# =====================================================================

def _deterministic_score(seed_str: str, low: float = 0.3, high: float = 0.95) -> float:
    """Generate a deterministic score from a seed string."""
    h = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
    return round(low + (high - low) * (h % 1000) / 1000, 2)


def gap_analysis_compute(*, baseline: str = "", target: str = "", analysis_type: str = "full", **kwargs: Any) -> dict[str, Any]:
    seed = f"{baseline}:{target}"
    return {
        "baseline": baseline or "Current State",
        "target": target or "Target State",
        "analysis_type": analysis_type,
        "gaps": [
            {"area": "Application Integration", "severity": "High", "description": "Point-to-point integration needs to be replaced with event-driven architecture"},
            {"area": "Data Management", "severity": "Medium", "description": "Master data management capability is immature"},
            {"area": "Security", "severity": "High", "description": "Zero-trust security model not implemented"},
            {"area": "Cloud Readiness", "severity": "Medium", "description": "Lift-and-shift migration incomplete for core systems"},
        ],
        "gap_count": 4,
        "overall_gap_score": _deterministic_score(seed, 0.3, 0.7),
        "recommendation": "Prioritize high-severity gaps; address integration before data management",
    }


def gap_analysis_asis_tobe(*, as_is: Any = None, to_be: Any = None, comparison_keys: list | None = None, **kwargs: Any) -> dict[str, Any]:
    keys = comparison_keys or ["capability", "maturity", "technology"]
    return {
        "as_is_state": str(as_is or "Baseline"),
        "to_be_state": str(to_be or "Target"),
        "comparison_keys": keys,
        "differences": [{"key": k, "as_is_value": f"Level {i+1}", "to_be_value": f"Level {i+3}", "gap": f"+{2}"} for i, k in enumerate(keys[:5])],
        "total_gaps": len(keys[:5]),
        "migration_effort": "Medium-High",
    }


def risk_score_compute(*, system: str = "", factors: list | None = None, methodology: str = "FAIR", **kwargs: Any) -> dict[str, Any]:
    facts = factors or ["availability", "security", "compliance"]
    seed = f"{system}:{','.join(str(f) for f in facts)}"
    return {
        "system": system or "Target System",
        "methodology": methodology,
        "overall_risk_score": _deterministic_score(seed, 1.0, 9.0),
        "risk_level": "Medium",
        "factor_scores": {str(f): _deterministic_score(f"{seed}:{f}", 1.0, 10.0) for f in facts},
        "mitigations": ["Implement redundancy for critical components", "Regular security assessments", "Automated compliance monitoring"],
    }


def compliance_check_execute(*, block: str = "", standards: list | None = None, severity_threshold: str = "medium", **kwargs: Any) -> dict[str, Any]:
    stds = standards or ["ISO27001", "GDPR"]
    return {
        "building_block": block or "Target System",
        "standards_checked": stds,
        "severity_threshold": severity_threshold,
        "overall_status": "Partially Compliant",
        "compliance_score": _deterministic_score(f"{block}:{stds}", 0.6, 0.95),
        "findings": [
            {"standard": stds[0] if stds else "ISO27001", "control": "Access Control", "status": "Compliant", "severity": "Low"},
            {"standard": stds[0] if stds else "ISO27001", "control": "Encryption at Rest", "status": "Non-Compliant", "severity": "High"},
            {"standard": stds[-1] if stds else "GDPR", "control": "Data Retention", "status": "Partially Compliant", "severity": "Medium"},
        ],
    }


def cost_benefit_analyze(*, initiative: str = "", costs: Any = None, benefits: Any = None, **kwargs: Any) -> dict[str, Any]:
    return {
        "initiative": initiative or "Architecture Initiative",
        "total_cost_estimate": 1250000,
        "total_benefit_estimate": 2800000,
        "roi_percentage": 124.0,
        "payback_period_months": 18,
        "npv": 1150000,
        "cost_breakdown": {"implementation": 750000, "licensing": 200000, "training": 150000, "operations_3yr": 150000},
        "benefit_breakdown": {"efficiency_gains": 1200000, "risk_reduction": 800000, "revenue_enablement": 500000, "compliance": 300000},
        "recommendation": "Positive ROI with 18-month payback; recommend proceeding",
    }


def roadmap_generate(*, work_packages: list | None = None, constraints: list | None = None, strategy: str = "incremental", **kwargs: Any) -> dict[str, Any]:
    return {
        "strategy": strategy,
        "phases": [
            {"phase": "Foundation", "quarter": "Q1", "work_packages": ["Infrastructure Assessment", "Architecture Standards"], "dependencies": []},
            {"phase": "Core Migration", "quarter": "Q2-Q3", "work_packages": ["API Gateway Setup", "Service Decomposition"], "dependencies": ["Foundation"]},
            {"phase": "Advanced", "quarter": "Q4", "work_packages": ["Event-Driven Integration", "Advanced Analytics"], "dependencies": ["Core Migration"]},
        ],
        "total_duration_months": 12,
        "critical_path": ["Infrastructure Assessment", "API Gateway Setup", "Service Decomposition"],
        "constraints_applied": constraints or ["budget", "resource_availability"],
    }


def stakeholder_impact_analyze(*, stakeholders: list | None = None, changes: list | None = None, include_communication_plan: bool = True, **kwargs: Any) -> dict[str, Any]:
    return {
        "stakeholders_analyzed": len(stakeholders or []),
        "changes_assessed": len(changes or []),
        "impact_matrix": [
            {"stakeholder": "Business Users", "impact": "High", "sentiment": "Positive", "readiness": "Medium"},
            {"stakeholder": "IT Operations", "impact": "High", "sentiment": "Cautious", "readiness": "High"},
            {"stakeholder": "Management", "impact": "Medium", "sentiment": "Positive", "readiness": "High"},
        ],
        "overall_impact": "Medium-High",
        "communication_plan": {"channels": ["Town Hall", "Email", "Training Sessions"], "frequency": "Bi-weekly"} if include_communication_plan else None,
    }


def dependency_analysis_compute(*, elements: list | None = None, analysis_type: str = "full", **kwargs: Any) -> dict[str, Any]:
    return {
        "elements_analyzed": len(elements or []),
        "analysis_type": analysis_type,
        "dependency_count": 12,
        "circular_dependencies": 1,
        "critical_dependencies": [
            {"from": "Payment Service", "to": "Core Banking", "type": "Runtime", "criticality": "High"},
            {"from": "Customer Portal", "to": "Authentication Service", "type": "Runtime", "criticality": "High"},
        ],
        "dependency_metrics": {"afferent_coupling_avg": 3.2, "efferent_coupling_avg": 2.8, "instability_avg": 0.47},
    }


def architecture_score_compute(*, architecture: str = "", dimensions: list | None = None, weights: dict | None = None, **kwargs: Any) -> dict[str, Any]:
    dims = dimensions or ["modularity", "scalability", "security", "maintainability"]
    return {
        "architecture": architecture or "Target Architecture",
        "overall_score": _deterministic_score(str(architecture), 55.0, 90.0),
        "dimension_scores": {d: _deterministic_score(f"{architecture}:{d}", 50.0, 95.0) for d in dims},
        "grade": "B+",
        "strengths": ["Good separation of concerns", "Well-defined service boundaries"],
        "weaknesses": ["Tight coupling in data layer", "Insufficient observability"],
    }


def reuse_analysis_compute(*, building_blocks: list | None = None, domains: list | None = None, threshold: float = 0.5, **kwargs: Any) -> dict[str, Any]:
    return {
        "building_blocks_analyzed": len(building_blocks or []),
        "domains": domains or ["all"],
        "reuse_threshold": threshold,
        "reusable_components": [
            {"component": "Authentication Module", "reuse_score": 0.92, "used_in": 8},
            {"component": "Logging Framework", "reuse_score": 0.88, "used_in": 12},
            {"component": "API Gateway", "reuse_score": 0.85, "used_in": 6},
        ],
        "overall_reuse_rate": 0.45,
        "recommendation": "Increase reuse of notification and monitoring components",
    }


def capability_heatmap_compute(*, capabilities: list | None = None, axes: list | None = None, **kwargs: Any) -> dict[str, Any]:
    return {
        "axes": axes or ["maturity", "strategic_importance"],
        "heatmap": [
            {"capability": "Digital Channels", "maturity": 3, "strategic_importance": 5, "investment_priority": "High"},
            {"capability": "Data Analytics", "maturity": 2, "strategic_importance": 5, "investment_priority": "Critical"},
            {"capability": "Core Banking", "maturity": 4, "strategic_importance": 4, "investment_priority": "Maintain"},
            {"capability": "Risk Management", "maturity": 4, "strategic_importance": 5, "investment_priority": "Maintain"},
            {"capability": "Payment Processing", "maturity": 3, "strategic_importance": 4, "investment_priority": "Medium"},
        ],
        "critical_gaps": ["Data Analytics maturity significantly below strategic importance"],
    }


def migration_complexity_compute(*, source_system: str = "", target_system: str = "", data_volume_gb: float = 0, **kwargs: Any) -> dict[str, Any]:
    seed = f"{source_system}:{target_system}:{data_volume_gb}"
    return {
        "source_system": source_system or "Legacy System",
        "target_system": target_system or "Target Platform",
        "data_volume_gb": data_volume_gb or 500,
        "complexity_score": _deterministic_score(seed, 2.0, 8.0),
        "complexity_level": "High",
        "factors": {"data_complexity": "High", "integration_points": 15, "custom_logic": "Medium", "regulatory_constraints": "High"},
        "estimated_effort_person_months": int(_deterministic_score(seed, 6.0, 36.0)),
        "risk_factors": ["Data mapping complexity", "Downtime requirements", "Regulatory validation needed"],
    }


def transformation_readiness_assess(*, organization: str = "", proposed_changes: list | None = None, dimensions: list | None = None, **kwargs: Any) -> dict[str, Any]:
    dims = dimensions or ["culture", "skills", "technology", "process", "governance"]
    return {
        "organization": organization or "Enterprise",
        "overall_readiness": _deterministic_score(str(organization), 40.0, 80.0),
        "dimension_scores": {d: _deterministic_score(f"{organization}:{d}", 30.0, 90.0) for d in dims},
        "readiness_level": "Moderate",
        "blockers": ["Skill gaps in cloud-native development", "Change resistance in operations team"],
        "enablers": ["Strong executive sponsorship", "Existing agile practices"],
    }


def interoperability_matrix_compute(*, systems: list | None = None, interop_dimensions: list | None = None, **kwargs: Any) -> dict[str, Any]:
    return {
        "systems_analyzed": len(systems or []),
        "dimensions": interop_dimensions or ["technical", "semantic", "organizational"],
        "matrix": [
            {"system_a": "CRM", "system_b": "ERP", "technical": 0.8, "semantic": 0.6, "organizational": 0.7, "overall": 0.7},
            {"system_a": "CRM", "system_b": "Payment Gateway", "technical": 0.9, "semantic": 0.5, "organizational": 0.6, "overall": 0.67},
            {"system_a": "ERP", "system_b": "Payment Gateway", "technical": 0.7, "semantic": 0.7, "organizational": 0.8, "overall": 0.73},
        ],
        "overall_interoperability": 0.7,
        "bottlenecks": ["Semantic interoperability between CRM and Payment Gateway"],
    }


def decision_evaluation_compute(*, alternatives: list | None = None, criteria: list | None = None, method: str = "AHP", **kwargs: Any) -> dict[str, Any]:
    alts = alternatives or ["Option A", "Option B", "Option C"]
    crit = criteria or ["cost", "risk", "time_to_market", "scalability"]
    return {
        "method": method,
        "alternatives": [str(a) for a in alts],
        "criteria": [str(c) for c in crit],
        "scores": {str(a): _deterministic_score(f"{a}:{method}", 40.0, 95.0) for a in alts},
        "ranking": [str(a) for a in alts[:3]],
        "recommended": str(alts[0]) if alts else "N/A",
        "sensitivity_analysis": "Result stable under +/-10% weight variations",
    }


def sla_validation_compute(*, architecture: str = "", sla_requirements: list | None = None, **kwargs: Any) -> dict[str, Any]:
    return {
        "architecture": architecture or "Target Architecture",
        "sla_requirements_checked": len(sla_requirements or []),
        "results": [
            {"sla": "Availability 99.9%", "achievable": True, "current_estimate": "99.95%", "risk": "Low"},
            {"sla": "Response Time < 200ms", "achievable": True, "current_estimate": "150ms P95", "risk": "Medium"},
            {"sla": "RPO < 1 hour", "achievable": True, "current_estimate": "30 min", "risk": "Low"},
            {"sla": "RTO < 4 hours", "achievable": False, "current_estimate": "6 hours", "risk": "High"},
        ],
        "overall_compliance": 0.75,
        "at_risk_slas": ["RTO < 4 hours"],
    }


def data_flow_analysis_compute(*, data_flows: list | None = None, analysis_focus: str = "security", **kwargs: Any) -> dict[str, Any]:
    return {
        "analysis_focus": analysis_focus,
        "flows_analyzed": len(data_flows or []),
        "findings": [
            {"flow": "Customer Data → Analytics", "classification": "PII", "encryption": "In-transit only", "risk": "Medium"},
            {"flow": "Payment → Settlement", "classification": "Financial", "encryption": "End-to-end", "risk": "Low"},
            {"flow": "Logs → SIEM", "classification": "Operational", "encryption": "None", "risk": "Low"},
        ],
        "compliance_issues": ["PII data flow lacks encryption at rest"],
        "data_lineage_completeness": 0.78,
    }


def technical_debt_compute(*, systems: list | None = None, factors: list | None = None, **kwargs: Any) -> dict[str, Any]:
    return {
        "systems_analyzed": len(systems or []),
        "total_debt_score": 6.2,
        "debt_items": [
            {"category": "Code Quality", "severity": "Medium", "estimated_remediation_days": 30, "description": "Legacy monolith lacks test coverage"},
            {"category": "Architecture", "severity": "High", "estimated_remediation_days": 60, "description": "Point-to-point integrations need refactoring"},
            {"category": "Infrastructure", "severity": "Medium", "estimated_remediation_days": 20, "description": "End-of-life operating systems on 3 servers"},
            {"category": "Documentation", "severity": "Low", "estimated_remediation_days": 10, "description": "Architecture documentation outdated"},
        ],
        "total_remediation_effort_days": 120,
        "interest_rate": "Growing — technical debt compounds at ~15% annually",
    }


def capacity_planning_compute(*, resources: list | None = None, growth_rate: float = 0.1, threshold: float = 0.8, **kwargs: Any) -> dict[str, Any]:
    return {
        "growth_rate": growth_rate,
        "threshold": threshold,
        "capacity_items": [
            {"resource": "Compute", "current_usage": 0.65, "projected_12m": 0.78, "at_risk": False},
            {"resource": "Storage", "current_usage": 0.72, "projected_12m": 0.88, "at_risk": True},
            {"resource": "Network Bandwidth", "current_usage": 0.45, "projected_12m": 0.54, "at_risk": False},
            {"resource": "Database Connections", "current_usage": 0.80, "projected_12m": 0.96, "at_risk": True},
        ],
        "at_risk_count": 2,
        "recommendation": "Expand storage and database connection pools within 6 months",
    }


def architecture_comparison_compute(*, architecture_a: str = "", architecture_b: str = "", criteria: list | None = None, **kwargs: Any) -> dict[str, Any]:
    crit = criteria or ["scalability", "cost", "complexity", "maintainability"]
    return {
        "architecture_a": architecture_a or "Architecture A",
        "architecture_b": architecture_b or "Architecture B",
        "criteria": [str(c) for c in crit],
        "comparison": {str(c): {"a": _deterministic_score(f"a:{c}", 40.0, 95.0), "b": _deterministic_score(f"b:{c}", 40.0, 95.0)} for c in crit},
        "winner": architecture_a or "Architecture A",
        "trade_offs": ["Architecture A better for scalability; Architecture B lower initial cost"],
    }


def compute_coupling_metrics(*, components: list | None = None, scope: str = "full", **kwargs: Any) -> dict[str, Any]:
    return {
        "scope": scope,
        "components_analyzed": len(components or []),
        "metrics": {"afferent_coupling": 4.2, "efferent_coupling": 3.1, "instability": 0.42, "abstractness": 0.35},
        "high_coupling_components": ["PaymentService (Ce=8)", "OrderService (Ca=7)"],
        "recommendation": "Reduce efferent coupling of PaymentService through interface abstraction",
    }


def compute_instability_abstractness(*, components: list | None = None, threshold_d: float = 0.5, **kwargs: Any) -> dict[str, Any]:
    return {
        "threshold_d": threshold_d,
        "components": [
            {"name": "CoreBanking", "instability": 0.3, "abstractness": 0.6, "distance": 0.1, "zone": "Main Sequence"},
            {"name": "PaymentGateway", "instability": 0.8, "abstractness": 0.1, "distance": 0.1, "zone": "Main Sequence"},
            {"name": "ReportingEngine", "instability": 0.9, "abstractness": 0.8, "distance": 0.7, "zone": "Zone of Uselessness"},
        ],
        "violations": ["ReportingEngine exceeds distance threshold (d=0.7 > 0.5)"],
    }


def compute_cohesion_metrics(*, components: list | None = None, method: str = "LCOM", **kwargs: Any) -> dict[str, Any]:
    comps = [str(c) for c in (components or ["AuthModule", "UserService", "UtilityPackage"])]
    metrics = []
    for c in comps:
        score = _deterministic_score(f"cohesion:{method}:{c}", 0.2, 0.95)
        level = "High" if score >= 0.7 else ("Medium" if score >= 0.5 else "Low")
        metrics.append({"component": c, "cohesion": score, "level": level})
    scores = [m["cohesion"] for m in metrics]
    avg = round(sum(scores) / max(len(scores), 1), 2)
    lowest = min(metrics, key=lambda m: m["cohesion"])
    return {
        "method": method,
        "components_analyzed": len(comps),
        "metrics": metrics,
        "average_cohesion": avg,
        "recommendation": f"Refactor {lowest['component']} — low cohesion indicates mixed responsibilities"
        if lowest["cohesion"] < 0.5 else "All components show acceptable cohesion levels",
    }


def build_dependency_structure_matrix(*, elements: list | None = None, relationships: list | None = None, ordering: str = "topological", **kwargs: Any) -> dict[str, Any]:
    elems = [str(e) for e in (elements or ["A", "B", "C", "D"])]
    return {
        "ordering": ordering,
        "elements": elems,
        "matrix": [[0 if i == j else (1 if (i + j) % 3 == 0 else 0) for j in range(len(elems))] for i in range(len(elems))],
        "clusters": [elems[:2], elems[2:]],
        "cyclic_groups": [],
    }


def detect_architecture_cycles(*, elements: list | None = None, relationships: list | None = None, max_cycle_length: int = 5, **kwargs: Any) -> dict[str, Any]:
    return {
        "max_cycle_length": max_cycle_length,
        "cycles_found": 1,
        "cycles": [{"path": ["ServiceA", "ServiceB", "ServiceC", "ServiceA"], "length": 3, "severity": "Medium"}],
        "recommendation": "Break cycle by introducing an event bus between ServiceB and ServiceC",
    }


def detect_architecture_smells(*, elements: list | None = None, relationships: list | None = None, thresholds: dict | None = None, **kwargs: Any) -> dict[str, Any]:
    return {
        "smells_detected": [
            {"smell": "God Component", "component": "CoreService", "severity": "High", "description": "Component has 25+ responsibilities"},
            {"smell": "Cyclic Dependency", "components": ["A", "B", "C"], "severity": "Medium", "description": "Circular dependency chain"},
            {"smell": "Hub-like Dependency", "component": "SharedDB", "severity": "High", "description": "15+ components depend on shared database"},
        ],
        "total_smells": 3,
        "health_score": 0.62,
    }


def compute_modularity_score(*, elements: list | None = None, relationships: list | None = None, module_field: str = "module", **kwargs: Any) -> dict[str, Any]:
    return {
        "module_field": module_field,
        "modularity_score": 0.68,
        "modules": [
            {"name": "Frontend", "elements": 8, "internal_relations": 12, "external_relations": 4, "cohesion": 0.75},
            {"name": "Backend", "elements": 15, "internal_relations": 28, "external_relations": 7, "cohesion": 0.80},
            {"name": "Data", "elements": 6, "internal_relations": 8, "external_relations": 9, "cohesion": 0.47},
        ],
        "recommendation": "Data module has high external coupling — consider encapsulating with service layer",
    }


def compute_architecture_complexity(*, elements: list | None = None, relationships: list | None = None, include_distribution: bool = True, **kwargs: Any) -> dict[str, Any]:
    return {
        "total_elements": len(elements or []),
        "total_relationships": len(relationships or []),
        "complexity_score": 7.3,
        "complexity_level": "High",
        "distribution": {"structural": 3.2, "behavioral": 2.1, "cross_cutting": 2.0} if include_distribution else None,
        "hotspots": ["Integration Layer (high fan-out)", "Security Module (high fan-in)"],
    }


def evaluate_fitness_functions(*, fitness_functions: list | None = None, measurements: list | None = None, trend_window: int = 6, **kwargs: Any) -> dict[str, Any]:
    return {
        "trend_window_months": trend_window,
        "evaluations": [
            {"function": "Deployment Frequency", "target": "Weekly", "current": "Bi-weekly", "trend": "Improving", "status": "At Risk"},
            {"function": "Mean Time to Recovery", "target": "< 1 hour", "current": "45 minutes", "trend": "Stable", "status": "Met"},
            {"function": "Test Coverage", "target": "> 80%", "current": "76%", "trend": "Improving", "status": "At Risk"},
            {"function": "API Response Time P95", "target": "< 200ms", "current": "180ms", "trend": "Stable", "status": "Met"},
        ],
        "overall_fitness": 0.72,
        "degrading_functions": [],
    }


def map_team_topology(*, components: list | None = None, current_teams: list | None = None, max_cognitive_load: int = 5, **kwargs: Any) -> dict[str, Any]:
    return {
        "max_cognitive_load": max_cognitive_load,
        "team_types": [
            {"team": "Stream-aligned: Payments", "type": "Stream-aligned", "components": ["PaymentService", "PaymentGateway"], "cognitive_load": 3},
            {"team": "Stream-aligned: Lending", "type": "Stream-aligned", "components": ["LoanService", "CreditAssessment"], "cognitive_load": 4},
            {"team": "Platform: Infrastructure", "type": "Platform", "components": ["Kubernetes", "Monitoring", "CI/CD"], "cognitive_load": 4},
            {"team": "Enabling: Architecture", "type": "Enabling", "components": [], "cognitive_load": 2},
        ],
        "interaction_modes": [
            {"team_a": "Payments", "team_b": "Platform", "mode": "X-as-a-Service"},
            {"team_a": "Lending", "team_b": "Architecture", "mode": "Facilitating"},
        ],
        "overloaded_teams": [],
    }


def capability_gap_heatmap(*, capabilities: list | None = None, dimensions: list | None = None, weighting: dict | None = None, **kwargs: Any) -> dict[str, Any]:
    return {
        "dimensions": dimensions or ["current_maturity", "target_maturity"],
        "heatmap": [
            {"capability": "Data Analytics", "current": 2, "target": 4, "gap": 2, "priority": "Critical"},
            {"capability": "API Management", "current": 2, "target": 4, "gap": 2, "priority": "High"},
            {"capability": "DevOps", "current": 3, "target": 4, "gap": 1, "priority": "Medium"},
            {"capability": "Core Banking", "current": 4, "target": 4, "gap": 0, "priority": "Low"},
            {"capability": "Compliance", "current": 4, "target": 5, "gap": 1, "priority": "Medium"},
        ],
        "total_gap_score": 6,
        "critical_gaps": ["Data Analytics", "API Management"],
    }


def assess_technology_fitness(*, technology: str = "", quality_attributes: list | None = None, context: str = "", **kwargs: Any) -> dict[str, Any]:
    attrs = quality_attributes or ["scalability", "reliability", "security"]
    fitness_scores = {str(a): _deterministic_score(f"{technology}:{a}", 40.0, 95.0) for a in attrs}
    # Overall = weighted average of component scores (not independent hash)
    overall = round(sum(fitness_scores.values()) / max(len(fitness_scores), 1), 2)
    return {
        "technology": technology or "Target Technology",
        "context": context,
        "fitness_scores": fitness_scores,
        "overall_fitness": overall,
        "strengths": ["Mature ecosystem", "Active community support"],
        "weaknesses": ["Limited horizontal scaling", "Complex configuration"],
        "recommendation": "Suitable for current scale; monitor scaling requirements",
    }


def compare_technology_stacks(*, stacks: list | None = None, criteria: list | None = None, context: str = "", **kwargs: Any) -> dict[str, Any]:
    stk = [str(s) for s in (stacks or ["Stack A", "Stack B"])]
    crit = criteria or ["performance", "cost", "maturity", "ecosystem"]
    return {
        "stacks_compared": stk,
        "criteria": [str(c) for c in crit],
        "scores": {s: {str(c): _deterministic_score(f"{s}:{c}", 40.0, 95.0) for c in crit} for s in stk},
        "winner": stk[0] if stk else "N/A",
        "trade_offs": [f"{stk[0]} better for performance; {stk[1] if len(stk) > 1 else 'other'} lower cost"] if stk else [],
    }


# =====================================================================
# TOOL_REGISTRY — maps pool tool IDs to callables
# =====================================================================

def _make_element_handler(layer_key: str):
    """Create a handler for a specific ArchiMate layer."""
    def handler(**kwargs):
        kwargs.pop("layer", None)
        return archimate_get_elements(layer=layer_key, **kwargs)
    return handler


def _make_viewpoint_handler(vp_key: str):
    """Create a handler for a specific ArchiMate viewpoint."""
    def handler(**kwargs):
        kwargs.pop("viewpoint", None)
        return archimate_get_viewpoint(viewpoint=vp_key, **kwargs)
    return handler


TOOL_REGISTRY: dict[str, Any] = {}

# --- ArchiMate element variants (6) ---
for _layer in ["business", "application", "technology", "motivation", "strategy", "implementation_migration"]:
    TOOL_REGISTRY[f"archimate_get_elements_{_layer}"] = _make_element_handler(_layer)

# --- ArchiMate viewpoint variants (24) ---
for _vp_key in _ARCHIMATE_VIEWPOINTS:
    TOOL_REGISTRY[f"archimate_get_viewpoint_{_vp_key}"] = _make_viewpoint_handler(_vp_key)

# --- 1:1 ArchiMate tools ---
TOOL_REGISTRY["archimate_get_relationships"] = archimate_get_relationships
TOOL_REGISTRY["archimate_query_model"] = archimate_query_model
TOOL_REGISTRY["archimate_get_metamodel"] = archimate_get_metamodel
TOOL_REGISTRY["viewpoint_consistency_check"] = viewpoint_consistency_check

# --- Catalog tools ---
TOOL_REGISTRY["capability_catalog_search"] = capability_catalog_search
TOOL_REGISTRY["stakeholder_catalog_search"] = stakeholder_catalog_search

# --- Analysis & compute tools ---
TOOL_REGISTRY["gap_analysis_compute"] = gap_analysis_compute
TOOL_REGISTRY["gap_analysis_asis_tobe"] = gap_analysis_asis_tobe
TOOL_REGISTRY["risk_score_compute"] = risk_score_compute
TOOL_REGISTRY["compliance_check_execute"] = compliance_check_execute
TOOL_REGISTRY["cost_benefit_analyze"] = cost_benefit_analyze
TOOL_REGISTRY["roadmap_generate"] = roadmap_generate
TOOL_REGISTRY["stakeholder_impact_analyze"] = stakeholder_impact_analyze
TOOL_REGISTRY["dependency_analysis_compute"] = dependency_analysis_compute
TOOL_REGISTRY["architecture_score_compute"] = architecture_score_compute
TOOL_REGISTRY["reuse_analysis_compute"] = reuse_analysis_compute
TOOL_REGISTRY["capability_heatmap_compute"] = capability_heatmap_compute
TOOL_REGISTRY["migration_complexity_compute"] = migration_complexity_compute
TOOL_REGISTRY["transformation_readiness_assess"] = transformation_readiness_assess
TOOL_REGISTRY["interoperability_matrix_compute"] = interoperability_matrix_compute
TOOL_REGISTRY["decision_evaluation_compute"] = decision_evaluation_compute
TOOL_REGISTRY["sla_validation_compute"] = sla_validation_compute
TOOL_REGISTRY["data_flow_analysis_compute"] = data_flow_analysis_compute
TOOL_REGISTRY["technical_debt_compute"] = technical_debt_compute
TOOL_REGISTRY["capacity_planning_compute"] = capacity_planning_compute
TOOL_REGISTRY["architecture_comparison_compute"] = architecture_comparison_compute
TOOL_REGISTRY["compute_coupling_metrics"] = compute_coupling_metrics
TOOL_REGISTRY["compute_instability_abstractness"] = compute_instability_abstractness
TOOL_REGISTRY["compute_cohesion_metrics"] = compute_cohesion_metrics
TOOL_REGISTRY["build_dependency_structure_matrix"] = build_dependency_structure_matrix
TOOL_REGISTRY["detect_architecture_cycles"] = detect_architecture_cycles
TOOL_REGISTRY["detect_architecture_smells"] = detect_architecture_smells
TOOL_REGISTRY["compute_modularity_score"] = compute_modularity_score
TOOL_REGISTRY["compute_architecture_complexity"] = compute_architecture_complexity
TOOL_REGISTRY["evaluate_fitness_functions"] = evaluate_fitness_functions
TOOL_REGISTRY["map_team_topology"] = map_team_topology
TOOL_REGISTRY["capability_gap_heatmap"] = capability_gap_heatmap
TOOL_REGISTRY["assess_technology_fitness"] = assess_technology_fitness
TOOL_REGISTRY["compare_technology_stacks"] = compare_technology_stacks
