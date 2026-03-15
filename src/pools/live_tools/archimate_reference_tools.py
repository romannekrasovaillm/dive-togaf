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
    wps = [str(w) for w in (work_packages or ["Infrastructure Assessment", "Architecture Standards", "API Gateway Setup", "Service Decomposition"])]
    cons = [str(c) for c in (constraints or ["budget", "resource_availability"])]
    phase_names = ["Foundation", "Core Migration", "Advanced", "Optimization"]
    n_phases = min(max(2, (len(wps) + 1) // 2), 4)
    phases = []
    quarters = ["Q1", "Q2", "Q2-Q3", "Q3-Q4", "Q4"]
    for i in range(n_phases):
        chunk = wps[i * len(wps) // n_phases:(i + 1) * len(wps) // n_phases]
        deps = [phase_names[i - 1]] if i > 0 else []
        phases.append({"phase": phase_names[i], "quarter": quarters[min(i, len(quarters) - 1)], "work_packages": chunk, "dependencies": deps})
    return {
        "strategy": strategy,
        "phases": phases,
        "total_duration_months": n_phases * 3,
        "critical_path": wps[:min(3, len(wps))],
        "constraints_applied": cons,
    }


def stakeholder_impact_analyze(*, stakeholders: list | None = None, changes: list | None = None, include_communication_plan: bool = True, **kwargs: Any) -> dict[str, Any]:
    shs = [str(s) for s in (stakeholders or ["Business Users", "IT Operations", "Management"])]
    chs = [str(c) for c in (changes or [])]
    impacts = ["High", "Medium", "Low"]
    sentiments = ["Positive", "Cautious", "Resistant"]
    readiness_levels = ["High", "Medium", "Low"]
    matrix = []
    for s in shs:
        h = int(hashlib.md5(f"stakeholder:{s}".encode()).hexdigest()[:6], 16)
        matrix.append({
            "stakeholder": s,
            "impact": impacts[h % 3],
            "sentiment": sentiments[(h >> 4) % 3],
            "readiness": readiness_levels[(h >> 8) % 3],
        })
    high_count = sum(1 for m in matrix if m["impact"] == "High")
    overall = "High" if high_count > len(matrix) // 2 else ("Medium-High" if high_count > 0 else "Medium")
    return {
        "stakeholders_analyzed": len(shs),
        "changes_assessed": len(chs),
        "impact_matrix": matrix,
        "overall_impact": overall,
        "communication_plan": {"channels": ["Town Hall", "Email", "Training Sessions"], "frequency": "Bi-weekly"} if include_communication_plan else None,
    }


def dependency_analysis_compute(*, elements: list | None = None, analysis_type: str = "full", **kwargs: Any) -> dict[str, Any]:
    elems = [str(e) for e in (elements or ["Payment Service", "Core Banking", "Customer Portal"])]
    dep_types = ["Runtime", "Build", "Data", "API"]
    criticalities = ["High", "Medium", "Low"]
    critical_deps = []
    for i in range(min(len(elems) - 1, 4)):
        h = int(hashlib.md5(f"dep:{elems[i]}:{elems[(i+1) % len(elems)]}".encode()).hexdigest()[:4], 16)
        critical_deps.append({
            "from": elems[i], "to": elems[(i + 1) % len(elems)],
            "type": dep_types[h % len(dep_types)],
            "criticality": criticalities[h % len(criticalities)],
        })
    n = len(elems)
    dep_count = int(_deterministic_score(f"depcount:{n}", float(n), float(n * 3)))
    circular = 1 if n >= 3 and int(hashlib.md5(":".join(elems).encode()).hexdigest()[:4], 16) % 3 == 0 else 0
    return {
        "elements_analyzed": n,
        "analysis_type": analysis_type,
        "dependency_count": dep_count,
        "circular_dependencies": circular,
        "critical_dependencies": critical_deps,
        "dependency_metrics": {
            "afferent_coupling_avg": _deterministic_score(f"dep:ca:{n}", 1.5, 6.0),
            "efferent_coupling_avg": _deterministic_score(f"dep:ce:{n}", 1.5, 6.0),
            "instability_avg": _deterministic_score(f"dep:inst:{n}", 0.2, 0.8),
        },
    }


def architecture_score_compute(*, architecture: str = "", dimensions: list | None = None, weights: dict | None = None, **kwargs: Any) -> dict[str, Any]:
    dims = [str(d) for d in (dimensions or ["modularity", "scalability", "security", "maintainability"])]
    arch = architecture or "Target Architecture"
    dim_scores = {d: _deterministic_score(f"{arch}:{d}", 50.0, 95.0) for d in dims}
    overall = round(sum(dim_scores.values()) / max(len(dim_scores), 1), 2)
    grades = ["A", "A-", "B+", "B", "B-", "C+", "C"]
    grade = grades[min(int((95 - overall) / 7), len(grades) - 1)]
    sorted_dims = sorted(dim_scores.items(), key=lambda x: x[1], reverse=True)
    return {
        "architecture": arch,
        "overall_score": overall,
        "dimension_scores": dim_scores,
        "grade": grade,
        "strengths": [f"Strong {d}" for d, s in sorted_dims[:2]],
        "weaknesses": [f"Improve {d}" for d, s in sorted_dims[-2:]],
    }


def reuse_analysis_compute(*, building_blocks: list | None = None, domains: list | None = None, threshold: float = 0.5, **kwargs: Any) -> dict[str, Any]:
    bbs = [str(b) for b in (building_blocks or ["Authentication Module", "Logging Framework", "API Gateway"])]
    doms = [str(d) for d in (domains or ["all"])]
    reusable = []
    for b in bbs:
        score = _deterministic_score(f"reuse:{b}", 0.2, 0.98)
        used_in = int(_deterministic_score(f"reuse:usage:{b}", 1.0, 15.0))
        if score >= threshold:
            reusable.append({"component": b, "reuse_score": score, "used_in": used_in})
    overall = round(sum(r["reuse_score"] for r in reusable) / max(len(bbs), 1), 2)
    low_reuse = [b for b in bbs if _deterministic_score(f"reuse:{b}", 0.2, 0.98) < threshold]
    return {
        "building_blocks_analyzed": len(bbs),
        "domains": doms,
        "reuse_threshold": threshold,
        "reusable_components": reusable,
        "overall_reuse_rate": overall,
        "recommendation": f"Increase reuse of {', '.join(low_reuse)}" if low_reuse else "All components meet reuse threshold",
    }


def capability_heatmap_compute(*, capabilities: list | None = None, axes: list | None = None, **kwargs: Any) -> dict[str, Any]:
    caps = [str(c) for c in (capabilities or ["Digital Channels", "Data Analytics", "Core Banking", "Risk Management", "Payment Processing"])]
    ax = axes or ["maturity", "strategic_importance"]
    heatmap = []
    critical = []
    for c in caps:
        maturity = int(_deterministic_score(f"caphm:mat:{c}", 1.0, 5.0))
        importance = int(_deterministic_score(f"caphm:imp:{c}", 2.0, 5.0))
        gap = importance - maturity
        priority = "Critical" if gap >= 2 else ("High" if gap == 1 and importance >= 4 else ("Maintain" if gap <= 0 else "Medium"))
        heatmap.append({"capability": c, "maturity": maturity, "strategic_importance": importance, "investment_priority": priority})
        if priority == "Critical":
            critical.append(f"{c} maturity significantly below strategic importance")
    return {
        "axes": ax,
        "heatmap": heatmap,
        "critical_gaps": critical,
    }


def migration_complexity_compute(*, source_system: str = "", target_system: str = "", data_volume_gb: float = 0, **kwargs: Any) -> dict[str, Any]:
    src = source_system or "Legacy System"
    tgt = target_system or "Target Platform"
    vol = data_volume_gb or 500
    seed = f"{src}:{tgt}:{vol}"
    score = _deterministic_score(seed, 2.0, 8.0)
    level = "Low" if score < 4.0 else ("Medium" if score < 6.0 else "High")
    complexity_levels = ["Low", "Medium", "High"]
    h = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16)
    return {
        "source_system": src,
        "target_system": tgt,
        "data_volume_gb": vol,
        "complexity_score": score,
        "complexity_level": level,
        "factors": {
            "data_complexity": complexity_levels[h % 3],
            "integration_points": int(_deterministic_score(f"{seed}:intpts", 3.0, 25.0)),
            "custom_logic": complexity_levels[(h >> 4) % 3],
            "regulatory_constraints": complexity_levels[(h >> 8) % 3],
        },
        "estimated_effort_person_months": int(_deterministic_score(seed, 6.0, 36.0)),
        "risk_factors": [f"Data mapping complexity ({src} → {tgt})", "Downtime requirements", "Regulatory validation needed"],
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
    syss = [str(s) for s in (systems or ["CRM", "ERP", "Payment Gateway"])]
    dims = [str(d) for d in (interop_dimensions or ["technical", "semantic", "organizational"])]
    matrix = []
    all_scores = []
    bottlenecks = []
    for i in range(len(syss)):
        for j in range(i + 1, len(syss)):
            row = {"system_a": syss[i], "system_b": syss[j]}
            dim_scores = []
            for d in dims:
                s = _deterministic_score(f"interop:{syss[i]}:{syss[j]}:{d}", 0.3, 0.95)
                row[d] = s
                dim_scores.append(s)
                if s < 0.5:
                    bottlenecks.append(f"{d.capitalize()} interoperability between {syss[i]} and {syss[j]}")
            row["overall"] = round(sum(dim_scores) / max(len(dim_scores), 1), 2)
            all_scores.append(row["overall"])
            matrix.append(row)
    return {
        "systems_analyzed": len(syss),
        "dimensions": dims,
        "matrix": matrix,
        "overall_interoperability": round(sum(all_scores) / max(len(all_scores), 1), 2) if all_scores else 0.0,
        "bottlenecks": bottlenecks[:3],
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
    arch = architecture or "Target Architecture"
    slas = [str(s) for s in (sla_requirements or ["Availability 99.9%", "Response Time < 200ms", "RPO < 1 hour", "RTO < 4 hours"])]
    risks = ["Low", "Medium", "High"]
    results = []
    at_risk = []
    for s in slas:
        h = int(hashlib.md5(f"sla:{arch}:{s}".encode()).hexdigest()[:6], 16)
        achievable = h % 4 != 0  # ~75% achievable
        risk = risks[h % 3]
        results.append({"sla": s, "achievable": achievable, "risk": risk})
        if not achievable or risk == "High":
            at_risk.append(s)
    compliance = round(sum(1 for r in results if r["achievable"]) / max(len(results), 1), 2)
    return {
        "architecture": arch,
        "sla_requirements_checked": len(slas),
        "results": results,
        "overall_compliance": compliance,
        "at_risk_slas": at_risk,
    }


def data_flow_analysis_compute(*, data_flows: list | None = None, analysis_focus: str = "security", **kwargs: Any) -> dict[str, Any]:
    flows = [str(f) for f in (data_flows or ["Customer Data → Analytics", "Payment → Settlement", "Logs → SIEM"])]
    classifications = ["PII", "Financial", "Operational", "Confidential"]
    encryptions = ["End-to-end", "In-transit only", "At-rest only", "None"]
    risk_levels = ["Low", "Medium", "High"]
    findings = []
    compliance_issues = []
    for f in flows:
        h = int(hashlib.md5(f"dataflow:{analysis_focus}:{f}".encode()).hexdigest()[:6], 16)
        cls = classifications[h % len(classifications)]
        enc = encryptions[(h >> 4) % len(encryptions)]
        risk = risk_levels[(h >> 8) % len(risk_levels)]
        findings.append({"flow": f, "classification": cls, "encryption": enc, "risk": risk})
        if cls in ("PII", "Financial") and enc in ("None", "In-transit only"):
            compliance_issues.append(f"{cls} data flow '{f}' lacks encryption at rest")
    return {
        "analysis_focus": analysis_focus,
        "flows_analyzed": len(flows),
        "findings": findings,
        "compliance_issues": compliance_issues,
        "data_lineage_completeness": _deterministic_score(f"lineage:{analysis_focus}:{len(flows)}", 0.5, 0.95),
    }


def technical_debt_compute(*, systems: list | None = None, factors: list | None = None, **kwargs: Any) -> dict[str, Any]:
    syss = [str(s) for s in (systems or ["Legacy System"])]
    facts = [str(f) for f in (factors or ["Code Quality", "Architecture", "Infrastructure", "Documentation"])]
    severities = ["Low", "Medium", "High"]
    debt_items = []
    total_days = 0
    for s in syss:
        for f in facts:
            h = int(hashlib.md5(f"debt:{s}:{f}".encode()).hexdigest()[:6], 16)
            severity = severities[h % 3]
            days = int(_deterministic_score(f"debt:days:{s}:{f}", 5.0, 60.0))
            total_days += days
            debt_items.append({
                "system": s, "category": f, "severity": severity,
                "estimated_remediation_days": days,
                "description": f"{s}: {f.lower()} improvement needed",
            })
    total_score = round(_deterministic_score(f"debtscore:{len(syss)}:{len(facts)}", 2.0, 9.0), 1)
    return {
        "systems_analyzed": len(syss),
        "total_debt_score": total_score,
        "debt_items": debt_items,
        "total_remediation_effort_days": total_days,
        "interest_rate": "Growing — technical debt compounds at ~15% annually",
    }


def capacity_planning_compute(*, resources: list | None = None, growth_rate: float = 0.1, threshold: float = 0.8, **kwargs: Any) -> dict[str, Any]:
    res = [str(r) for r in (resources or ["Compute", "Storage", "Network Bandwidth", "Database Connections"])]
    items = []
    at_risk_names = []
    for r in res:
        current = _deterministic_score(f"cap:cur:{r}", 0.3, 0.9)
        projected = round(min(current * (1 + growth_rate) ** 1, 1.0), 2)  # 12-month projection
        risk = projected >= threshold
        items.append({"resource": r, "current_usage": current, "projected_12m": projected, "at_risk": risk})
        if risk:
            at_risk_names.append(r)
    return {
        "growth_rate": growth_rate,
        "threshold": threshold,
        "capacity_items": items,
        "at_risk_count": len(at_risk_names),
        "recommendation": f"Expand {' and '.join(at_risk_names)} within 6 months" if at_risk_names else "All resources within capacity limits",
    }


def architecture_comparison_compute(*, architecture_a: str = "", architecture_b: str = "", criteria: list | None = None, **kwargs: Any) -> dict[str, Any]:
    a = architecture_a or "Architecture A"
    b = architecture_b or "Architecture B"
    crit = [str(c) for c in (criteria or ["scalability", "cost", "complexity", "maintainability"])]
    comparison = {}
    a_total, b_total = 0.0, 0.0
    for c in crit:
        sa = _deterministic_score(f"{a}:{c}", 40.0, 95.0)
        sb = _deterministic_score(f"{b}:{c}", 40.0, 95.0)
        comparison[c] = {"a": sa, "b": sb}
        a_total += sa
        b_total += sb
    winner = a if a_total >= b_total else b
    a_strengths = [c for c in crit if comparison[c]["a"] > comparison[c]["b"]]
    b_strengths = [c for c in crit if comparison[c]["b"] > comparison[c]["a"]]
    trade_offs = []
    if a_strengths:
        trade_offs.append(f"{a} stronger in {', '.join(a_strengths)}")
    if b_strengths:
        trade_offs.append(f"{b} stronger in {', '.join(b_strengths)}")
    return {
        "architecture_a": a,
        "architecture_b": b,
        "criteria": crit,
        "comparison": comparison,
        "winner": winner,
        "trade_offs": trade_offs or ["Both architectures score similarly across criteria"],
    }


def compute_coupling_metrics(*, components: list | None = None, scope: str = "full", **kwargs: Any) -> dict[str, Any]:
    comps = [str(c) for c in (components or ["ComponentA", "ComponentB", "ComponentC"])]
    metrics = []
    for c in comps:
        ca = _deterministic_score(f"coupling:ca:{c}", 1.0, 10.0)
        ce = _deterministic_score(f"coupling:ce:{c}", 1.0, 10.0)
        inst = round(ce / (ca + ce) if (ca + ce) > 0 else 0.5, 2)
        abst = _deterministic_score(f"coupling:abst:{c}", 0.1, 0.9)
        metrics.append({"component": c, "afferent_coupling": ca, "efferent_coupling": ce, "instability": inst, "abstractness": abst})
    avg_ca = round(sum(m["afferent_coupling"] for m in metrics) / max(len(metrics), 1), 2)
    avg_ce = round(sum(m["efferent_coupling"] for m in metrics) / max(len(metrics), 1), 2)
    avg_inst = round(sum(m["instability"] for m in metrics) / max(len(metrics), 1), 2)
    highest_ce = max(metrics, key=lambda m: m["efferent_coupling"])
    return {
        "scope": scope,
        "components_analyzed": len(comps),
        "component_metrics": metrics,
        "averages": {"afferent_coupling": avg_ca, "efferent_coupling": avg_ce, "instability": avg_inst},
        "high_coupling_components": [f"{m['component']} (Ce={m['efferent_coupling']})" for m in metrics if m["efferent_coupling"] > 6],
        "recommendation": f"Reduce efferent coupling of {highest_ce['component']} through interface abstraction",
    }


def compute_instability_abstractness(*, components: list | None = None, threshold_d: float = 0.5, **kwargs: Any) -> dict[str, Any]:
    comps = [str(c) for c in (components or ["ComponentA", "ComponentB", "ComponentC"])]
    results = []
    violations = []
    for c in comps:
        inst = _deterministic_score(f"ia:inst:{c}", 0.1, 0.95)
        abst = _deterministic_score(f"ia:abst:{c}", 0.05, 0.9)
        dist = round(abs(inst + abst - 1.0), 2)
        zone = "Zone of Pain" if inst < 0.3 and abst < 0.3 else (
            "Zone of Uselessness" if inst > 0.7 and abst > 0.7 else "Main Sequence"
        )
        results.append({"name": c, "instability": inst, "abstractness": abst, "distance": dist, "zone": zone})
        if dist > threshold_d:
            violations.append(f"{c} exceeds distance threshold (d={dist} > {threshold_d})")
    return {
        "threshold_d": threshold_d,
        "components": results,
        "violations": violations,
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
    elems = [str(e) for e in (elements or ["ServiceA", "ServiceB", "ServiceC"])]
    # Deterministically pick a subset to form a cycle based on input
    cycles = []
    if len(elems) >= 3:
        seed_val = int(hashlib.md5(":".join(elems).encode()).hexdigest()[:4], 16)
        cycle_len = min(3 + seed_val % 2, len(elems), max_cycle_length)
        cycle_path = elems[:cycle_len] + [elems[0]]
        severity = "High" if cycle_len >= 4 else "Medium"
        cycles.append({"path": cycle_path, "length": cycle_len, "severity": severity})
    return {
        "max_cycle_length": max_cycle_length,
        "elements_analyzed": len(elems),
        "cycles_found": len(cycles),
        "cycles": cycles,
        "recommendation": f"Break cycle by introducing an event bus between {elems[1]} and {elems[-1]}" if cycles else "No cycles detected",
    }


def detect_architecture_smells(*, elements: list | None = None, relationships: list | None = None, thresholds: dict | None = None, **kwargs: Any) -> dict[str, Any]:
    elems = [str(e) for e in (elements or ["CoreService", "SharedDB", "ServiceX"])]
    smell_types = ["God Component", "Cyclic Dependency", "Hub-like Dependency", "Shotgun Surgery", "Feature Envy"]
    smells = []
    for i, e in enumerate(elems):
        seed_val = int(hashlib.md5(f"smell:{e}".encode()).hexdigest()[:4], 16)
        if seed_val % 3 == 0:  # ~1/3 of elements have a smell
            smell = smell_types[seed_val % len(smell_types)]
            severity = "High" if seed_val % 5 < 2 else "Medium"
            smells.append({"smell": smell, "component": e, "severity": severity, "description": f"{e} — detected {smell.lower()}"})
    if not smells and elems:
        smells.append({"smell": "Hub-like Dependency", "component": elems[0], "severity": "Medium", "description": f"{elems[0]} has high fan-in"})
    health = round(max(0.3, 1.0 - len(smells) * 0.12), 2)
    return {
        "elements_analyzed": len(elems),
        "smells_detected": smells,
        "total_smells": len(smells),
        "health_score": health,
    }


def compute_modularity_score(*, elements: list | None = None, relationships: list | None = None, module_field: str = "module", **kwargs: Any) -> dict[str, Any]:
    elems = [str(e) for e in (elements or ["Frontend", "Backend", "Data"])]
    rels = relationships or []
    modules = []
    for e in elems:
        n_elem = int(_deterministic_score(f"mod:elem:{e}", 3.0, 20.0))
        internal = int(_deterministic_score(f"mod:int:{e}", 5.0, 30.0))
        external = int(_deterministic_score(f"mod:ext:{e}", 2.0, 15.0))
        cohesion = round(internal / max(internal + external, 1), 2)
        modules.append({"name": e, "elements": n_elem, "internal_relations": internal, "external_relations": external, "cohesion": cohesion})
    avg_cohesion = round(sum(m["cohesion"] for m in modules) / max(len(modules), 1), 2)
    lowest = min(modules, key=lambda m: m["cohesion"])
    return {
        "module_field": module_field,
        "elements_analyzed": len(elems),
        "relationships_analyzed": len(rels),
        "modularity_score": avg_cohesion,
        "modules": modules,
        "recommendation": f"{lowest['name']} has high external coupling — consider encapsulating with service layer"
        if lowest["cohesion"] < 0.6 else "All modules show acceptable cohesion",
    }


def compute_architecture_complexity(*, elements: list | None = None, relationships: list | None = None, include_distribution: bool = True, **kwargs: Any) -> dict[str, Any]:
    elems = [str(e) for e in (elements or [])]
    rels = relationships or []
    n_e, n_r = len(elems), len(rels)
    # Complexity scales with element count and relationship density
    base = _deterministic_score(f"complexity:{n_e}:{n_r}", 2.0, 9.5)
    density_factor = min(n_r / max(n_e, 1), 3.0) / 3.0  # normalize
    score = round(base * (0.7 + 0.3 * density_factor), 1)
    level = "Low" if score < 4.0 else ("Medium" if score < 6.5 else "High")
    dist = None
    if include_distribution:
        structural = round(score * _deterministic_score(f"cx:s:{n_e}", 0.3, 0.5), 1)
        behavioral = round(score * _deterministic_score(f"cx:b:{n_e}", 0.2, 0.4), 1)
        cross_cutting = round(score - structural - behavioral, 1)
        dist = {"structural": structural, "behavioral": behavioral, "cross_cutting": max(cross_cutting, 0.1)}
    # Hotspots from actual elements
    hotspots = []
    for e in elems:
        h = int(hashlib.md5(f"hotspot:{e}".encode()).hexdigest()[:4], 16)
        if h % 4 == 0:
            hotspots.append(f"{e} (high fan-out)" if h % 2 == 0 else f"{e} (high fan-in)")
    return {
        "total_elements": n_e,
        "total_relationships": n_r,
        "complexity_score": score,
        "complexity_level": level,
        "distribution": dist,
        "hotspots": hotspots or ([f"{elems[0]} (high connectivity)"] if elems else []),
    }


def evaluate_fitness_functions(*, fitness_functions: list | None = None, measurements: list | None = None, trend_window: int = 6, **kwargs: Any) -> dict[str, Any]:
    ffs = [str(f) for f in (fitness_functions or ["Deployment Frequency", "Mean Time to Recovery", "Test Coverage", "API Response Time P95"])]
    trends = ["Improving", "Stable", "Degrading"]
    evaluations = []
    degrading = []
    for ff in ffs:
        score = _deterministic_score(f"ff:{ff}", 0.4, 1.0)
        trend_idx = int(hashlib.md5(f"fftrend:{ff}".encode()).hexdigest()[:4], 16) % 3
        trend = trends[trend_idx]
        status = "Met" if score >= 0.8 else "At Risk"
        evaluations.append({"function": ff, "score": score, "trend": trend, "status": status})
        if trend == "Degrading":
            degrading.append(ff)
    overall = round(sum(e["score"] for e in evaluations) / max(len(evaluations), 1), 2)
    return {
        "trend_window_months": trend_window,
        "evaluations": evaluations,
        "overall_fitness": overall,
        "degrading_functions": degrading,
    }


def map_team_topology(*, components: list | None = None, current_teams: list | None = None, max_cognitive_load: int = 5, **kwargs: Any) -> dict[str, Any]:
    comps = [str(c) for c in (components or ["ServiceA", "ServiceB", "ServiceC"])]
    teams_input = [str(t) for t in (current_teams or [])]
    team_types_list = ["Stream-aligned", "Platform", "Enabling", "Complicated-subsystem"]
    interaction_modes = ["Collaboration", "X-as-a-Service", "Facilitating"]
    # Distribute components across teams
    n_teams = max(len(teams_input), max(2, len(comps) // 2))
    team_names = teams_input + [f"Team-{i+1}" for i in range(len(teams_input), n_teams)]
    teams = []
    overloaded = []
    for i, t in enumerate(team_names):
        t_type = team_types_list[int(hashlib.md5(f"ttype:{t}".encode()).hexdigest()[:4], 16) % len(team_types_list)]
        assigned = [c for j, c in enumerate(comps) if j % n_teams == i]
        cog_load = int(_deterministic_score(f"cogload:{t}", 1.0, float(max_cognitive_load + 2)))
        teams.append({"team": f"{t_type}: {t}", "type": t_type, "components": assigned, "cognitive_load": cog_load})
        if cog_load > max_cognitive_load:
            overloaded.append(t)
    interactions = []
    for i in range(min(len(team_names) - 1, 3)):
        mode = interaction_modes[i % len(interaction_modes)]
        interactions.append({"team_a": team_names[i], "team_b": team_names[i + 1], "mode": mode})
    return {
        "max_cognitive_load": max_cognitive_load,
        "team_types": teams,
        "interaction_modes": interactions,
        "overloaded_teams": overloaded,
    }


def capability_gap_heatmap(*, capabilities: list | None = None, dimensions: list | None = None, weighting: dict | None = None, **kwargs: Any) -> dict[str, Any]:
    caps = [str(c) for c in (capabilities or ["Data Analytics", "API Management", "DevOps", "Core Banking", "Compliance"])]
    dims = dimensions or ["current_maturity", "target_maturity"]
    heatmap = []
    total_gap = 0
    critical = []
    for c in caps:
        current = int(_deterministic_score(f"capheat:cur:{c}", 1.0, 5.0))
        target = int(_deterministic_score(f"capheat:tgt:{c}", max(float(current), 3.0), 5.0))
        gap = target - current
        total_gap += gap
        priority = "Critical" if gap >= 2 else ("High" if gap == 1 and target >= 4 else ("Medium" if gap == 1 else "Low"))
        heatmap.append({"capability": c, "current": current, "target": target, "gap": gap, "priority": priority})
        if priority == "Critical":
            critical.append(c)
    return {
        "dimensions": dims,
        "heatmap": heatmap,
        "total_gap_score": total_gap,
        "critical_gaps": critical,
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
# Security Architecture Tools
# =====================================================================

def security_threat_model(*, system: str = "", assets: list | None = None, threat_framework: str = "STRIDE", **kwargs: Any) -> dict[str, Any]:
    """Analyze security threats for an architecture component."""
    sys_name = system or "Target System"
    asset_list = [str(a) for a in (assets or ["User Data", "API Keys", "Session Tokens"])]
    stride = ["Spoofing", "Tampering", "Repudiation", "Information Disclosure", "Denial of Service", "Elevation of Privilege"]
    threats = []
    for a in asset_list:
        for t in stride:
            h = int(hashlib.md5(f"threat:{sys_name}:{a}:{t}".encode()).hexdigest()[:4], 16)
            if h % 3 == 0:
                risk = _deterministic_score(f"risk:{sys_name}:{a}:{t}", 2.0, 9.0)
                threats.append({"asset": a, "threat_type": t, "risk_score": risk,
                                "likelihood": "High" if risk > 7 else ("Medium" if risk > 4 else "Low"),
                                "mitigation": f"Apply {t.lower()} controls for {a}"})
    return {
        "system": sys_name, "framework": threat_framework,
        "assets_analyzed": len(asset_list), "threats": threats,
        "overall_risk": round(sum(t["risk_score"] for t in threats) / max(len(threats), 1), 2),
        "priority_mitigations": [t["mitigation"] for t in sorted(threats, key=lambda x: x["risk_score"], reverse=True)[:3]],
    }


def security_control_assessment(*, controls: list | None = None, compliance_framework: str = "ISO27001", scope: str = "", **kwargs: Any) -> dict[str, Any]:
    """Assess effectiveness of security controls against a compliance framework."""
    ctrl_list = [str(c) for c in (controls or ["Access Control", "Encryption", "Monitoring", "Backup"])]
    statuses = ["Implemented", "Partial", "Planned", "Not Implemented"]
    results = []
    for c in ctrl_list:
        h = int(hashlib.md5(f"ctrl:{compliance_framework}:{c}".encode()).hexdigest()[:4], 16)
        eff = _deterministic_score(f"ctrl:eff:{c}", 0.3, 1.0)
        results.append({"control": c, "status": statuses[h % len(statuses)],
                        "effectiveness": eff, "gaps": [] if eff > 0.7 else [f"{c}: coverage gap identified"]})
    compliance_rate = round(sum(1 for r in results if r["status"] == "Implemented") / max(len(results), 1), 2)
    return {
        "framework": compliance_framework, "scope": scope or "Full",
        "controls_assessed": len(ctrl_list), "results": results,
        "compliance_rate": compliance_rate,
        "critical_gaps": [r["gaps"][0] for r in results if r["gaps"]],
    }


# =====================================================================
# Data Architecture Tools
# =====================================================================

def data_quality_assessment(*, datasets: list | None = None, dimensions: list | None = None, **kwargs: Any) -> dict[str, Any]:
    """Assess data quality across multiple dimensions for given datasets."""
    ds_list = [str(d) for d in (datasets or ["Customer Master", "Transaction Log", "Product Catalog"])]
    dim_list = [str(d) for d in (dimensions or ["completeness", "accuracy", "timeliness", "consistency"])]
    assessments = []
    for ds in ds_list:
        dim_scores = {}
        for dim in dim_list:
            dim_scores[dim] = _deterministic_score(f"dq:{ds}:{dim}", 0.4, 0.99)
        overall = round(sum(dim_scores.values()) / max(len(dim_scores), 1), 2)
        assessments.append({"dataset": ds, "dimension_scores": dim_scores, "overall_quality": overall,
                            "issues": [f"{dim}: below threshold" for dim, s in dim_scores.items() if s < 0.7]})
    return {
        "datasets_analyzed": len(ds_list), "dimensions": dim_list,
        "assessments": assessments,
        "overall_quality": round(sum(a["overall_quality"] for a in assessments) / max(len(assessments), 1), 2),
        "priority_issues": [i for a in assessments for i in a["issues"]][:5],
    }


def data_lineage_trace(*, entity: str = "", direction: str = "both", max_depth: int = 5, **kwargs: Any) -> dict[str, Any]:
    """Trace data lineage upstream/downstream for a data entity."""
    ent = entity or "CustomerRecord"
    upstream = [f"Source_{i}_{ent[:4]}" for i in range(int(_deterministic_score(f"lineage:up:{ent}", 1.0, 5.0)))]
    downstream = [f"Consumer_{i}_{ent[:4]}" for i in range(int(_deterministic_score(f"lineage:down:{ent}", 1.0, 6.0)))]
    transformations = []
    for i, src in enumerate(upstream):
        h = int(hashlib.md5(f"transform:{src}:{ent}".encode()).hexdigest()[:4], 16)
        transformations.append({"from": src, "to": ent, "type": ["ETL", "CDC", "API", "Batch"][h % 4],
                                "quality_impact": ["None", "Minor", "Significant"][h % 3]})
    return {
        "entity": ent, "direction": direction,
        "upstream": upstream, "downstream": downstream,
        "transformations": transformations,
        "lineage_depth": max(len(upstream), len(downstream)),
        "data_quality_risks": [t for t in transformations if t["quality_impact"] == "Significant"],
    }


def data_classification_scan(*, data_stores: list | None = None, classification_scheme: str = "sensitivity", **kwargs: Any) -> dict[str, Any]:
    """Classify data stores by sensitivity, regulatory requirements, and retention."""
    stores = [str(s) for s in (data_stores or ["UserDB", "LogStore", "AnalyticsWarehouse"])]
    levels = ["Public", "Internal", "Confidential", "Restricted"]
    regulations = ["GDPR", "PCI-DSS", "HIPAA", "SOX", "None"]
    results = []
    for s in stores:
        h = int(hashlib.md5(f"classify:{s}".encode()).hexdigest()[:6], 16)
        lvl = levels[h % len(levels)]
        reg = [regulations[h % len(regulations)]]
        if lvl in ("Confidential", "Restricted"):
            reg.append(regulations[(h >> 4) % (len(regulations) - 1)])
        retention_months = int(_deterministic_score(f"retain:{s}", 6.0, 120.0))
        results.append({"data_store": s, "classification": lvl, "regulations": list(set(reg)),
                        "retention_months": retention_months, "encryption_required": lvl in ("Confidential", "Restricted")})
    return {
        "scheme": classification_scheme, "stores_scanned": len(stores),
        "results": results,
        "high_sensitivity_count": sum(1 for r in results if r["classification"] in ("Confidential", "Restricted")),
        "regulatory_summary": list({reg for r in results for reg in r["regulations"] if reg != "None"}),
    }


# =====================================================================
# Integration & API Architecture Tools
# =====================================================================

def integration_pattern_analyze(*, source_system: str = "", target_system: str = "", data_volume: str = "medium", latency_requirement: str = "seconds", **kwargs: Any) -> dict[str, Any]:
    """Recommend integration patterns based on system characteristics."""
    src = source_system or "System A"
    tgt = target_system or "System B"
    patterns = ["REST API", "Event-Driven (Kafka)", "GraphQL", "gRPC", "File Transfer", "ESB", "CDC"]
    h = int(hashlib.md5(f"intpat:{src}:{tgt}:{data_volume}:{latency_requirement}".encode()).hexdigest()[:8], 16)
    recommended = patterns[h % len(patterns)]
    alternatives = [patterns[(h >> 4) % len(patterns)], patterns[(h >> 8) % len(patterns)]]
    return {
        "source": src, "target": tgt, "data_volume": data_volume, "latency_requirement": latency_requirement,
        "recommended_pattern": recommended,
        "alternatives": [a for a in alternatives if a != recommended],
        "evaluation": {
            recommended: {"fit_score": _deterministic_score(f"intfit:{src}:{tgt}:{recommended}", 0.7, 0.98),
                          "complexity": "Low" if h % 3 == 0 else ("Medium" if h % 3 == 1 else "High")},
        },
        "anti_patterns": [f"Avoid point-to-point between {src} and {tgt} at {data_volume} volume"],
    }


def api_maturity_assess(*, apis: list | None = None, model: str = "Richardson", **kwargs: Any) -> dict[str, Any]:
    """Assess API maturity level for a set of APIs."""
    api_list = [str(a) for a in (apis or ["Customer API", "Payment API", "Notification API"])]
    levels = {"Richardson": ["Level 0: Swamp of POX", "Level 1: Resources", "Level 2: HTTP Verbs", "Level 3: Hypermedia"],
              "custom": ["Basic", "Managed", "Defined", "Optimized"]}
    maturity_levels = levels.get(model, levels["Richardson"])
    results = []
    for api in api_list:
        h = int(hashlib.md5(f"apimat:{api}".encode()).hexdigest()[:4], 16)
        lvl = h % len(maturity_levels)
        results.append({"api": api, "maturity_level": lvl, "maturity_label": maturity_levels[lvl],
                        "versioning": h % 2 == 0, "documentation": _deterministic_score(f"apidoc:{api}", 0.3, 1.0),
                        "deprecation_policy": h % 3 != 0})
    avg_level = round(sum(r["maturity_level"] for r in results) / max(len(results), 1), 1)
    return {
        "model": model, "apis_assessed": len(api_list), "results": results,
        "average_maturity": avg_level,
        "recommendations": [f"Upgrade {r['api']} to {maturity_levels[min(r['maturity_level']+1, len(maturity_levels)-1)]}"
                            for r in results if r["maturity_level"] < len(maturity_levels) - 1][:3],
    }


# =====================================================================
# Cloud & Infrastructure Architecture Tools
# =====================================================================

def cloud_readiness_assess(*, workloads: list | None = None, target_cloud: str = "hybrid", strategy: str = "6R", **kwargs: Any) -> dict[str, Any]:
    """Assess workload readiness for cloud migration using 6R framework."""
    wl_list = [str(w) for w in (workloads or ["ERP", "CRM", "Email", "Analytics Platform"])]
    strategies_6r = ["Rehost", "Replatform", "Refactor", "Repurchase", "Retire", "Retain"]
    results = []
    for w in wl_list:
        h = int(hashlib.md5(f"cloud:{w}:{target_cloud}".encode()).hexdigest()[:6], 16)
        rec_strategy = strategies_6r[h % len(strategies_6r)]
        readiness = _deterministic_score(f"cloudready:{w}", 0.2, 0.95)
        effort = int(_deterministic_score(f"cloudeffort:{w}", 1.0, 12.0))
        results.append({"workload": w, "recommended_strategy": rec_strategy,
                        "readiness_score": readiness, "migration_effort_months": effort,
                        "blockers": [f"{w}: {['licensing', 'latency', 'compliance', 'data gravity'][h % 4]} concern"]
                        if readiness < 0.5 else []})
    return {
        "target_cloud": target_cloud, "strategy_framework": strategy,
        "workloads_assessed": len(wl_list), "results": results,
        "overall_readiness": round(sum(r["readiness_score"] for r in results) / max(len(results), 1), 2),
        "total_effort_months": sum(r["migration_effort_months"] for r in results),
        "blockers": [b for r in results for b in r["blockers"]],
    }


def infrastructure_cost_model(*, services: list | None = None, period_months: int = 12, growth_rate: float = 0.1, **kwargs: Any) -> dict[str, Any]:
    """Model infrastructure costs across services with growth projections."""
    svc_list = [str(s) for s in (services or ["Compute", "Storage", "Database", "Network", "Monitoring"])]
    items = []
    total_current = 0.0
    total_projected = 0.0
    for s in svc_list:
        monthly = _deterministic_score(f"cost:monthly:{s}", 500.0, 15000.0)
        projected = round(monthly * ((1 + growth_rate) ** (period_months / 12)), 2)
        total_current += monthly
        total_projected += projected
        items.append({"service": s, "monthly_cost": monthly, "projected_monthly": projected,
                      "annual_cost": round(monthly * 12, 2),
                      "optimization_potential": _deterministic_score(f"costopt:{s}", 0.05, 0.35)})
    return {
        "period_months": period_months, "growth_rate": growth_rate,
        "cost_items": items,
        "total_monthly": round(total_current, 2), "total_annual": round(total_current * 12, 2),
        "projected_monthly": round(total_projected, 2),
        "savings_opportunity": round(sum(i["monthly_cost"] * i["optimization_potential"] for i in items), 2),
    }


# =====================================================================
# Organization & Governance Tools
# =====================================================================

def raci_matrix_generate(*, activities: list | None = None, roles: list | None = None, **kwargs: Any) -> dict[str, Any]:
    """Generate a RACI responsibility matrix for activities and roles."""
    acts = [str(a) for a in (activities or ["Design", "Review", "Approve", "Implement", "Test"])]
    role_list = [str(r) for r in (roles or ["Architect", "Developer", "Manager", "QA", "Stakeholder"])]
    raci_vals = ["R", "A", "C", "I"]
    matrix = []
    for act in acts:
        row = {"activity": act}
        for role in role_list:
            h = int(hashlib.md5(f"raci:{act}:{role}".encode()).hexdigest()[:4], 16)
            row[role] = raci_vals[h % len(raci_vals)]
        matrix.append(row)
    # Validate: each activity should have exactly one A
    issues = []
    for row in matrix:
        a_count = sum(1 for r in role_list if row[r] == "A")
        if a_count != 1:
            issues.append(f"{row['activity']}: {a_count} accountable roles (should be 1)")
    return {
        "activities": acts, "roles": role_list, "matrix": matrix,
        "validation_issues": issues,
        "coverage": round(1.0 - len(issues) / max(len(matrix), 1), 2),
    }


def architecture_decision_record(*, decision: str = "", options: list | None = None, context: str = "", **kwargs: Any) -> dict[str, Any]:
    """Generate and evaluate an Architecture Decision Record (ADR)."""
    dec = decision or "Select integration pattern"
    opts = [str(o) for o in (options or ["Option A", "Option B", "Option C"])]
    criteria = ["cost", "complexity", "scalability", "time_to_market"]
    evaluations = {}
    for o in opts:
        evaluations[o] = {c: _deterministic_score(f"adr:{dec}:{o}:{c}", 30.0, 95.0) for c in criteria}
    scores = {o: round(sum(evaluations[o].values()) / len(criteria), 2) for o in opts}
    recommended = max(scores, key=scores.get)
    return {
        "decision": dec, "context": context, "status": "Proposed",
        "options_evaluated": opts, "criteria": criteria,
        "evaluations": evaluations, "scores": scores,
        "recommended": recommended,
        "consequences": [f"Adopting {recommended} requires {criteria[int(hashlib.md5(recommended.encode()).hexdigest()[:2], 16) % len(criteria)]} investment"],
    }


def compliance_regulation_check(*, regulations: list | None = None, architecture_elements: list | None = None, **kwargs: Any) -> dict[str, Any]:
    """Check architecture elements against regulatory requirements."""
    regs = [str(r) for r in (regulations or ["GDPR", "PCI-DSS", "SOC2"])]
    elements = [str(e) for e in (architecture_elements or ["Database", "API Gateway", "Auth Service"])]
    checks = []
    for reg in regs:
        for elem in elements:
            h = int(hashlib.md5(f"regcheck:{reg}:{elem}".encode()).hexdigest()[:4], 16)
            compliant = h % 4 != 0  # ~75% compliant
            checks.append({"regulation": reg, "element": elem, "compliant": compliant,
                           "finding": f"{elem}: {'compliant' if compliant else 'non-compliant'} with {reg}",
                           "remediation": None if compliant else f"Apply {reg} controls to {elem}"})
    non_compliant = [c for c in checks if not c["compliant"]]
    return {
        "regulations_checked": regs, "elements_checked": elements,
        "total_checks": len(checks), "checks": checks,
        "compliance_rate": round(1.0 - len(non_compliant) / max(len(checks), 1), 2),
        "critical_findings": [c["finding"] for c in non_compliant],
        "remediations": [c["remediation"] for c in non_compliant if c["remediation"]],
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

# --- Security Architecture tools ---
TOOL_REGISTRY["security_threat_model"] = security_threat_model
TOOL_REGISTRY["security_control_assessment"] = security_control_assessment

# --- Data Architecture tools ---
TOOL_REGISTRY["data_quality_assessment"] = data_quality_assessment
TOOL_REGISTRY["data_lineage_trace"] = data_lineage_trace
TOOL_REGISTRY["data_classification_scan"] = data_classification_scan

# --- Integration & API tools ---
TOOL_REGISTRY["integration_pattern_analyze"] = integration_pattern_analyze
TOOL_REGISTRY["api_maturity_assess"] = api_maturity_assess

# --- Cloud & Infrastructure tools ---
TOOL_REGISTRY["cloud_readiness_assess"] = cloud_readiness_assess
TOOL_REGISTRY["infrastructure_cost_model"] = infrastructure_cost_model

# --- Organization & Governance tools ---
TOOL_REGISTRY["raci_matrix_generate"] = raci_matrix_generate
TOOL_REGISTRY["architecture_decision_record"] = architecture_decision_record
TOOL_REGISTRY["compliance_regulation_check"] = compliance_regulation_check
