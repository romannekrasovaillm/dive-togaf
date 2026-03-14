"""TOGAF ADM reference tools — live implementations backed by static knowledge base."""
from __future__ import annotations
from typing import Any

_ADM_PHASES: dict[str, dict] = {
    "Preliminary": {
        "name": "Preliminary Phase", "objective": "Prepare the organization for TOGAF ADM",
        "deliverables": ["Organizational Model for Enterprise Architecture", "Tailored Architecture Framework", "Architecture Principles", "Architecture Repository (initial)", "Architecture Governance Framework", "Request for Architecture Work (draft)"],
        "inputs": ["TOGAF Standard", "Other Architecture Frameworks", "Board strategy and business plans", "Architecture Governance Strategy", "Existing Organizational Model"],
        "outputs": ["Organizational Model for EA", "Tailored Architecture Framework", "Initial Architecture Repository", "Restatement of business principles, goals, drivers", "Architecture Principles", "Request for Architecture Work"],
        "techniques": ["Architecture Principles development", "Stakeholder Management", "Business Transformation Readiness Assessment", "Enterprise Architecture Maturity Assessment"],
        "stakeholders": ["CIO", "Chief Architect", "Enterprise Architecture Board", "Program Sponsors", "IT Strategy Committee"],
    },
    "A": {
        "name": "Phase A: Architecture Vision", "objective": "Develop a high-level aspirational vision of capabilities and business value",
        "deliverables": ["Architecture Vision Document", "Statement of Architecture Work", "Architecture Communication Plan", "Stakeholder Map Matrix", "Value Chain Diagram"],
        "inputs": ["Request for Architecture Work", "Architecture Principles", "Enterprise Continuum", "Architecture Repository", "Business principles, goals, and drivers"],
        "outputs": ["Approved Statement of Architecture Work", "Architecture Vision", "Refined key goals and drivers", "Architecture Work Plan", "Communication Plan"],
        "techniques": ["Stakeholder Analysis", "Business Scenarios", "Capability-Based Planning", "Architecture Vision Development"],
        "stakeholders": ["CIO", "Business Executives", "Architecture Board", "Project Sponsors", "Business Domain Experts"],
    },
    "B": {
        "name": "Phase B: Business Architecture", "objective": "Develop the Target Business Architecture describing how the enterprise needs to operate",
        "deliverables": ["Business Architecture Document", "Business Capability Map", "Organization Map", "Business Process Models", "Value Stream Map", "Business Interaction Matrix", "Business Footprint Diagram", "Business Service/Function Catalog", "Functional Decomposition Diagram", "Goal/Objective/Service Diagram", "Business Use-Case Diagram"],
        "inputs": ["Architecture Vision", "Architecture Repository", "Architecture Principles", "Gap Analysis Results (if any)", "Stakeholder concerns"],
        "outputs": ["Refined Business Architecture", "Business Architecture components of Architecture Roadmap", "Impact Analysis of Business Architecture", "Gap Analysis Results (Baseline vs Target)", "Candidate Architecture Roadmap components"],
        "techniques": ["Business Process Modeling (BPMN)", "Value Stream Mapping", "Capability-Based Planning", "Business Scenarios", "Gap Analysis", "Organization Mapping"],
        "stakeholders": ["Business Process Owners", "Business Domain Experts", "Chief Operating Officer", "HR Director", "Business Analysts", "Architecture Board"],
    },
    "C": {
        "name": "Phase C: Information Systems Architectures", "objective": "Develop Target Data and Application Architectures",
        "deliverables": ["Data Architecture Document", "Application Architecture Document", "Data Entity/Data Component Catalog", "Data Dissemination Diagram", "Application Portfolio Catalog", "Application/Data Matrix", "Application Interaction Matrix", "Application Communication Diagram"],
        "inputs": ["Architecture Vision", "Business Architecture", "Architecture Repository", "Architecture Principles", "Gap Analysis Results from Phase B"],
        "outputs": ["Data Architecture", "Application Architecture", "Data and Application Architecture components of Architecture Roadmap", "Impact Analysis of Data and Application Architectures", "Gap Analysis Results (Baseline vs Target)"],
        "techniques": ["Data Modeling", "Application Portfolio Analysis", "Data Flow Analysis", "Application Interaction Analysis", "Gap Analysis", "Data Migration Planning"],
        "stakeholders": ["Application Architects", "Data Architects", "Database Administrators", "Chief Data Officer", "Application Development Managers", "Integration Architects"],
    },
    "D": {
        "name": "Phase D: Technology Architecture", "objective": "Develop the Target Technology Architecture enabling the logical and physical application/data components",
        "deliverables": ["Technology Architecture Document", "Technology Standards Catalog", "Technology Portfolio Catalog", "Environments and Locations Diagram", "Platform Decomposition Diagram", "Processing Diagram", "Networked Computing/Hardware Diagram"],
        "inputs": ["Architecture Vision", "Business Architecture", "Data Architecture", "Application Architecture", "Architecture Principles", "Architecture Repository"],
        "outputs": ["Technology Architecture", "Technology Architecture components of Architecture Roadmap", "Impact Analysis of Technology Architecture", "Gap Analysis Results (Baseline vs Target)", "Technology Standards Catalog"],
        "techniques": ["Technology Portfolio Analysis", "Platform Decomposition", "Environment and Location Analysis", "Gap Analysis", "Technology Standards Review"],
        "stakeholders": ["Infrastructure Architects", "Network Architects", "Security Architects", "IT Operations Managers", "CTO", "Platform Engineers"],
    },
    "E": {
        "name": "Phase E: Opportunities and Solutions", "objective": "Generate the initial implementation and migration plan; identify major work packages",
        "deliverables": ["Implementation and Migration Strategy", "Architecture Roadmap (consolidated)", "Transition Architectures", "Implementation Factor Assessment and Deduction Matrix", "Consolidated Gaps, Solutions, and Dependencies Matrix"],
        "inputs": ["Architecture Vision", "Target Architectures (Business, Data, Application, Technology)", "Architecture Roadmap (draft components)", "Architecture Repository", "Gap Analysis Results from Phases B-D"],
        "outputs": ["Implementation and Migration Strategy", "Transition Architectures", "Architecture Roadmap (consolidated)", "Prioritized list of projects/work packages", "Solution Building Blocks"],
        "techniques": ["Gap Analysis (consolidated)", "Migration Planning", "Interoperability Analysis", "Risk Assessment", "Cost/Benefit Analysis", "Business Value Assessment", "Transition Architecture Planning"],
        "stakeholders": ["Project Managers", "Portfolio Managers", "Architecture Board", "Business Planners", "Solution Architects", "Enterprise Architect"],
    },
    "F": {
        "name": "Phase F: Migration Planning", "objective": "Finalize detailed implementation and migration plan addressing how to move from Baseline to Target Architectures",
        "deliverables": ["Implementation and Migration Plan", "Finalized Architecture Roadmap", "Architecture Implementation Governance Model", "Change Requests for Architecture Capability", "Implementation and Migration Plan (detailed work packages)"],
        "inputs": ["Implementation and Migration Strategy", "Transition Architectures", "Architecture Roadmap", "Architecture Repository", "Gap/Solution/Dependencies Matrix"],
        "outputs": ["Finalized Implementation and Migration Plan", "Finalized Architecture Roadmap", "Finalized Transition Architectures", "Architecture Contracts (initial)", "Reusable Architecture Building Blocks"],
        "techniques": ["Business Value Assessment", "Risk Assessment", "Migration Planning", "Work Package Definition", "Resource Estimation", "Project Prioritization", "Dependency Analysis"],
        "stakeholders": ["Program Managers", "Project Managers", "Architecture Board", "Budget Officers", "Resource Managers", "Change Management Team"],
    },
    "G": {
        "name": "Phase G: Implementation Governance", "objective": "Ensure conformance of implementation projects with the Target Architecture",
        "deliverables": ["Architecture Contract", "Compliance Assessment", "Change Requests", "Architecture-compliant implemented system", "Implementation Governance Model", "Architecture Compliance Review Reports"],
        "inputs": ["Implementation and Migration Plan", "Architecture Contract", "Architecture Repository", "Architecture Roadmap", "Implementation projects"],
        "outputs": ["Architecture Compliance Reviews", "Change Requests", "Compliance Assessments", "Impact Analysis of implementation changes", "Updated Architecture Repository", "Governance Recommendations"],
        "techniques": ["Architecture Compliance Review", "Implementation Review", "Change Management", "Risk Monitoring", "Quality Assurance"],
        "stakeholders": ["Implementation Project Managers", "Architecture Board", "Solution Architects", "QA Team", "Operations Team", "Enterprise Architect"],
    },
    "H": {
        "name": "Phase H: Architecture Change Management", "objective": "Ensure the architecture lifecycle is maintained and architecture governance framework is executed",
        "deliverables": ["Architecture Updates", "Change Requests", "Updated Architecture Requirements", "New Request for Architecture Work (for significant changes)", "Architecture Change Impact Assessment"],
        "inputs": ["Architecture Repository", "Change Requests", "Technology Changes", "Business Changes", "Lessons Learned", "Architecture Compliance Reviews"],
        "outputs": ["Architecture Updates", "Changes to Architecture Framework and Principles", "New Request for Architecture Work (if needed)", "Updated Architecture Repository", "Architecture Change Impact Assessment"],
        "techniques": ["Business and IT Environment Monitoring", "Technology Monitoring", "Architecture Change Impact Analysis", "Enterprise Architecture Maturity Assessment", "Lessons Learned Analysis"],
        "stakeholders": ["Enterprise Architect", "Architecture Board", "CIO", "Business Change Managers", "IT Governance Team", "Technology Scouts"],
    },
    "Requirements": {
        "name": "Requirements Management", "objective": "Manage architecture requirements identified during ADM execution across all phases",
        "deliverables": ["Requirements Repository", "Requirements Impact Assessment", "Updated Requirements Specification", "Requirements Traceability Matrix"],
        "inputs": ["Architecture Requirements Specification (from any phase)", "Change Requests", "Stakeholder Concerns", "Gap Analysis Results", "Architecture Repository"],
        "outputs": ["Updated Requirements Repository", "Requirements Impact Assessment", "Requirements prioritization", "Requirements for upcoming ADM phases", "Requirements Traceability Matrix"],
        "techniques": ["Requirements Prioritization (MoSCoW)", "Impact Analysis", "Requirements Traceability", "Requirements Validation", "Requirements Change Management"],
        "stakeholders": ["Enterprise Architect", "Business Analysts", "Solution Architects", "Architecture Board", "Project Managers", "Requirements Engineers"],
    },
}

_ADM_DELIVERABLES: dict[str, dict] = {
    "architecture_vision": {"name": "Architecture Vision", "phase": "A", "description": "High-level description of the Baseline and Target Architectures, providing a summary view of the gap between them, identifying the key stakeholders, their concerns, and the business scenarios to be addressed.", "sections": ["Problem Description", "Objective of Architecture Vision", "Summary Views of Baseline and Target", "Gap Analysis Overview", "Key Stakeholder Requirements", "Architecture Model (high-level)"], "purpose": "Provide strategic direction for architecture work and secure stakeholder buy-in"},
    "statement_of_architecture_work": {"name": "Statement of Architecture Work", "phase": "A", "description": "Defines the scope and approach that will be used to complete an architecture development cycle.", "sections": ["Architecture project scope", "Architecture Vision Summary", "Specific Change of Scope", "Roles and Responsibilities", "Acceptance Criteria", "Architecture Project Plan", "Timeline and Milestones"], "purpose": "Formal agreement between developing organization and sponsor on deliverables, quality, and fitness-for-purpose"},
    "architecture_definition_document": {"name": "Architecture Definition Document", "phase": "B-D", "description": "Spans all architecture domains and contains the core architectural artifacts created during a phase.", "sections": ["Scope", "Goals and Objectives", "Architecture Principles", "Baseline Architecture", "Target Architecture", "Gap Analysis", "Impact Assessment", "Architecture Models and Views"], "purpose": "Provide a qualitative view of the solution to enable understanding and communication"},
    "architecture_requirements_specification": {"name": "Architecture Requirements Specification", "phase": "B-D", "description": "Set of quantitative statements specifying what a solution must implement.", "sections": ["Success Measures", "Architecture Requirements", "Service Contracts", "Implementation Guidelines", "Implementation Specifications", "Standards Compliance Requirements", "Interoperability Requirements"], "purpose": "Provide a quantitative view of the solution — measurable characteristics of the architecture"},
    "architecture_roadmap": {"name": "Architecture Roadmap", "phase": "E-F", "description": "Lists individual work packages that will realize the Target Architecture.", "sections": ["Work Package Portfolio", "Implementation Factor Assessment", "Deduction Matrix", "Transition Architectures", "Project Dependencies", "Consolidated Gap/Solution Matrix", "Timeline and Resource Summary"], "purpose": "Provide a time-based list of all projects and activities needed to realize the Target Architecture"},
    "transition_architecture": {"name": "Transition Architecture", "phase": "E", "description": "Formal description of an architecture state at an architecturally significant point in the migration from Baseline to Target.", "sections": ["Transition State Description", "Business Architecture (transition)", "Data Architecture (transition)", "Application Architecture (transition)", "Technology Architecture (transition)", "Gap Analysis for Transition", "Residual Risks"], "purpose": "Allow the organization to achieve incremental business value through manageable transition states"},
    "implementation_governance_model": {"name": "Implementation Governance Model", "phase": "F-G", "description": "Framework for governing the implementation of architecture, including compliance review processes.", "sections": ["Governance Organization", "Governance Processes", "Compliance Review Schedule", "Architecture Contract Template", "Dispensation Process", "Escalation Procedures", "Key Performance Indicators"], "purpose": "Ensure implementation projects conform to the defined architecture"},
    "architecture_contract": {"name": "Architecture Contract", "phase": "G", "description": "Joint agreement between development partners and sponsors on deliverables, quality, and fitness-for-purpose.", "sections": ["Architecture Design and Development", "Business Users", "Operations", "Architecture Compliance and Reviews", "Target Architecture Measures", "Service Architecture Requirements", "Conformance Requirements"], "purpose": "Formal agreement governing the delivery and quality of architecture implementation"},
    "compliance_assessment": {"name": "Compliance Assessment", "phase": "G", "description": "Assessment of project compliance with the defined architecture.", "sections": ["Project Overview", "Architecture Requirements", "Compliance Review Results", "Non-conformances", "Dispensation Requests", "Recommendations", "Risk Assessment"], "purpose": "Assess adherence to the architecture and identify compliance issues"},
    "change_request": {"name": "Change Request", "phase": "H", "description": "Request for modification to the architecture or architecture deliverables.", "sections": ["Change Description", "Reason for Change", "Impact Analysis", "Affected Architecture Components", "Proposed Solution", "Priority Assessment", "Approval Status"], "purpose": "Formally propose and track changes to the architecture"},
    "business_architecture_document": {"name": "Business Architecture Document", "phase": "B", "description": "Comprehensive Business Architecture covering organization, functions, services, processes, and information.", "sections": ["Organization Structure", "Business Functions", "Business Services", "Business Processes", "Business Information", "Business Events", "Business Roles and Actors"], "purpose": "Define the business strategy, governance, organization, and key business processes"},
    "data_architecture_document": {"name": "Data Architecture Document", "phase": "C", "description": "Describes the structure of an organization's logical and physical data assets.", "sections": ["Data Entities", "Data Components", "Data Flow Diagrams", "Data Lifecycle", "Data Quality Requirements", "Data Governance", "Data Migration Strategy"], "purpose": "Define how data is stored, managed, and used across the enterprise"},
    "application_architecture_document": {"name": "Application Architecture Document", "phase": "C", "description": "Provides a blueprint for individual applications to be deployed and their interactions.", "sections": ["Application Portfolio", "Application Components", "Application Interfaces", "Application Integration", "Application Migration", "Application Standards", "Application Data Mapping"], "purpose": "Define the kinds of application systems relevant and how they relate to core business processes"},
    "technology_architecture_document": {"name": "Technology Architecture Document", "phase": "D", "description": "Describes the logical software and hardware capabilities required to support business, data, and application services.", "sections": ["Technology Standards", "Platform Services", "Infrastructure Components", "Network Architecture", "Security Architecture", "Technology Lifecycle", "Environment Strategy"], "purpose": "Define the technology infrastructure needed to support the application and data architectures"},
    "stakeholder_map": {"name": "Stakeholder Map Matrix", "phase": "A", "description": "Identifies stakeholders and maps them against architecture views and concerns.", "sections": ["Stakeholder Identification", "Stakeholder Concerns", "Stakeholder Influence/Impact", "Communication Requirements", "View Requirements"], "purpose": "Ensure all stakeholder concerns are addressed in architecture development"},
    "value_chain_diagram": {"name": "Value Chain Diagram", "phase": "B", "description": "Provides a high-level orientation view of the enterprise and how it interacts with the outside world.", "sections": ["Primary Activities", "Support Activities", "Value Propositions", "External Interactions", "Key Linkages"], "purpose": "Document and communicate high-level business value creation"},
    "organization_map": {"name": "Organization Map", "phase": "B", "description": "Depicts the key organizational entities and their relationships.", "sections": ["Business Units", "Reporting Lines", "Shared Services", "External Partners", "Key Roles"], "purpose": "Identify organizational units involved in and affected by the architecture"},
    "business_interaction_matrix": {"name": "Business Interaction Matrix", "phase": "B", "description": "Depicts the relationship interactions between organizations/actors.", "sections": ["Actor-to-Actor Interactions", "Organization-to-Organization Dependencies", "Information Exchange", "Service Dependencies", "Interaction Frequency"], "purpose": "Identify and document key business interactions and dependencies"},
    "business_footprint_diagram": {"name": "Business Footprint Diagram", "phase": "B", "description": "Describes the links between business goals, organizational units, business functions, and services.", "sections": ["Business Goals", "Organizational Units", "Business Functions", "Delivered Services", "Traceability Links"], "purpose": "Trace business goals to the functions and services that support them"},
    "business_service_catalog": {"name": "Business Service/Function Catalog", "phase": "B", "description": "A catalog listing all business services and functions.", "sections": ["Service Name and ID", "Service Description", "Service Owner", "Consumers", "Service Level", "Supporting Applications"], "purpose": "Provide a comprehensive inventory of business services and functions"},
    "functional_decomposition_diagram": {"name": "Functional Decomposition Diagram", "phase": "B", "description": "Shows capabilities of an organization relevant to the architecture.", "sections": ["Top-level Capabilities", "Capability Decomposition", "Capability Dependencies", "Capability Owners", "Technology Enablers"], "purpose": "Show the functional capabilities of an organization in a hierarchical view"},
    "goal_objective_service_diagram": {"name": "Goal/Objective/Service Diagram", "phase": "B", "description": "Defines the ways in which a service contributes to the achievement of a business vision or strategy.", "sections": ["Strategic Goals", "Tactical Objectives", "Contributing Services", "Goal-Service Mappings", "Measurement Criteria"], "purpose": "Link business goals and objectives to the services that fulfill them"},
    "business_use_case_diagram": {"name": "Business Use-Case Diagram", "phase": "B", "description": "Depicts the relationships between consumers and providers of business services.", "sections": ["Actors", "Use Cases", "System Boundaries", "Relationships", "Pre/Post-conditions"], "purpose": "Describe how the business uses and interacts with business services"},
    "process_flow_diagram": {"name": "Process Flow Diagram", "phase": "B", "description": "Depicts how processes interact, including sequencing and control flow.", "sections": ["Process Steps", "Decision Points", "Swimlanes", "Data Objects", "Events and Triggers", "Exception Flows"], "purpose": "Document business process flows including interactions between processes"},
}

_ADM_TECHNIQUES: dict[str, dict] = {
    "stakeholder_analysis": {"name": "Stakeholder Analysis", "description": "Technique for identifying and classifying stakeholders, understanding their key concerns, and ensuring proper communication.", "steps": ["Identify stakeholders", "Classify stakeholders by power/interest", "Determine key concerns for each stakeholder", "Define communication approach", "Map stakeholders to architecture views", "Plan engagement strategy"], "inputs": ["Organizational chart", "Business strategy", "Project charter", "Architecture scope"], "outputs": ["Stakeholder Map Matrix", "Communication Plan", "View/Viewpoint selection"], "applicable_phases": ["Preliminary", "A", "B", "C", "D"]},
    "business_transformation_readiness": {"name": "Business Transformation Readiness Assessment", "description": "Evaluate the organization's readiness to accept change, identify risks, and determine mitigation activities.", "steps": ["Define readiness factors", "Rate current maturity", "Identify readiness risks", "Assess impact of transformation", "Define mitigation actions", "Create transformation roadmap"], "inputs": ["Architecture Vision", "Business scenarios", "Organizational assessments", "Current capabilities"], "outputs": ["Readiness Assessment Report", "Readiness Factor Ratings", "Risk-mitigation plan", "Transformation Readiness Score"], "applicable_phases": ["Preliminary", "A", "E", "F"]},
    "gap_analysis": {"name": "Gap Analysis", "description": "Compare Baseline and Target Architectures to identify gaps, overlaps, and impacts.", "steps": ["Document Baseline Architecture", "Document Target Architecture", "Create gap matrix", "Identify new elements (in target, not in baseline)", "Identify eliminated elements (in baseline, not in target)", "Identify changed elements", "Prioritize gaps"], "inputs": ["Baseline Architecture", "Target Architecture", "Architecture models"], "outputs": ["Gap Analysis Report", "Gap Matrix", "Change impact assessment", "Prioritized gap list"], "applicable_phases": ["B", "C", "D", "E"]},
    "migration_planning": {"name": "Migration Planning", "description": "Plan the migration from Baseline to Target Architecture through incremental transition states.", "steps": ["Identify transition architectures", "Define work packages", "Assess dependencies", "Evaluate implementation factors", "Prioritize migration activities", "Define implementation timeline", "Assign resources"], "inputs": ["Architecture Roadmap", "Gap Analysis", "Transition Architectures", "Implementation factors"], "outputs": ["Migration Plan", "Work package definitions", "Dependency matrix", "Resource plan"], "applicable_phases": ["E", "F"]},
    "interoperability_requirements": {"name": "Interoperability Requirements", "description": "Define the degree to which information and services can be shared across the enterprise.", "steps": ["Define interoperability needs", "Identify standards and protocols", "Assess current interoperability", "Define interoperability requirements", "Map requirements to architecture components"], "inputs": ["Business requirements", "Technology standards", "Current integration landscape", "Service contracts"], "outputs": ["Interoperability requirements", "Standards catalog", "Integration patterns", "Service contracts"], "applicable_phases": ["C", "D", "E"]},
    "business_scenarios": {"name": "Business Scenarios", "description": "Identify and document business requirements through scenario-based analysis.", "steps": ["Identify the problem or opportunity", "Define the business and technical environment", "Describe desired outcome objectives", "Identify human actors and computing actors", "Identify roles and responsibilities", "Refine and document scenarios"], "inputs": ["Business goals", "Architecture Vision", "Stakeholder concerns", "Environmental factors"], "outputs": ["Business scenario documentation", "Refined business requirements", "Architecture requirements", "Risk factors"], "applicable_phases": ["A", "B"]},
    "architecture_principles": {"name": "Architecture Principles", "description": "Define and manage the architecture principles that guide architecture decisions.", "steps": ["Review existing principles", "Draft new principles", "Validate against business strategy", "Gain stakeholder consensus", "Document with rationale and implications", "Establish governance for principles"], "inputs": ["Business strategy", "IT strategy", "Industry standards", "Best practices"], "outputs": ["Architecture Principles catalog", "Principle rationale", "Implications of each principle"], "applicable_phases": ["Preliminary", "A"]},
    "risk_management": {"name": "Risk Management", "description": "Identify, classify, and mitigate risks associated with architecture transformation.", "steps": ["Identify risks", "Classify risks (initial level of risk)", "Determine mitigation approach", "Assign risk ownership", "Monitor and review risks", "Document residual risks"], "inputs": ["Architecture gap analysis", "Change impact assessment", "Stakeholder concerns", "Environmental factors"], "outputs": ["Risk register", "Risk mitigation plan", "Residual risk assessment", "Risk monitoring framework"], "applicable_phases": ["A", "B", "C", "D", "E", "F"]},
    "capability_based_planning": {"name": "Capability-Based Planning", "description": "Plan enterprise change based on business capabilities rather than organizational structure.", "steps": ["Identify required capabilities", "Assess current capability maturity", "Define target capability levels", "Map capabilities to business outcomes", "Plan capability improvement roadmap", "Align with investment portfolio"], "inputs": ["Business strategy", "Capability map", "Maturity assessments", "Investment portfolio"], "outputs": ["Capability assessment report", "Capability improvement roadmap", "Investment recommendations", "Capability heat map"], "applicable_phases": ["Preliminary", "A", "B", "E"]},
    "architecture_patterns": {"name": "Architecture Patterns", "description": "Apply reusable architecture patterns to solve recurring design problems.", "steps": ["Identify recurring design problems", "Search pattern repository", "Evaluate pattern applicability", "Adapt pattern to context", "Apply pattern", "Document pattern usage and adaptations"], "inputs": ["Architecture requirements", "Pattern repository", "Design constraints", "Technology standards"], "outputs": ["Applied architecture patterns", "Pattern adaptation documentation", "Updated pattern repository"], "applicable_phases": ["B", "C", "D"]},
    "business_models": {"name": "Business Models", "description": "Develop and analyze business models to understand value creation, delivery, and capture.", "steps": ["Define value proposition", "Identify customer segments", "Map value streams", "Analyze revenue model", "Identify key resources and activities", "Map partner network"], "inputs": ["Business strategy", "Market analysis", "Customer insights", "Competitive landscape"], "outputs": ["Business Model Canvas", "Value proposition map", "Revenue model analysis", "Key activity inventory"], "applicable_phases": ["Preliminary", "A", "B"]},
}


def adm_get_phase_details(phase: str = "", include_techniques: bool = True, include_stakeholders: bool = True, **kwargs) -> dict:
    data = _ADM_PHASES.get(phase, _ADM_PHASES.get(phase.upper(), {}))
    if not data:
        for key, val in _ADM_PHASES.items():
            if phase.lower() in key.lower() or phase.lower() in val.get("name", "").lower():
                data = val
                break
    if not data:
        return {"phase": phase, "error": f"Unknown phase: {phase}", "available_phases": list(_ADM_PHASES.keys())}
    result = {"phase": data["name"], "deliverables": data["deliverables"], "inputs": data["inputs"], "outputs": data["outputs"]}
    if include_techniques:
        result["techniques"] = data["techniques"]
    if include_stakeholders:
        result["stakeholders"] = data["stakeholders"]
    return result


def adm_get_deliverable(deliverable_type: str = "", format: str = "summary", **kwargs) -> dict:
    data = _ADM_DELIVERABLES.get(deliverable_type, {})
    if not data:
        for key, val in _ADM_DELIVERABLES.items():
            if deliverable_type.lower() in key.lower():
                data = val
                break
    if not data:
        return {"deliverable_type": deliverable_type, "error": f"Unknown deliverable: {deliverable_type}"}
    result = {"deliverable_type": deliverable_type, "phase": data["phase"], "content": {"name": data["name"], "description": data["description"], "purpose": data["purpose"]}}
    if format in ("full", "template"):
        result["content"]["sections"] = data["sections"]
    return result


def adm_get_technique(technique_type: str = "", context: str = "", **kwargs) -> dict:
    data = _ADM_TECHNIQUES.get(technique_type, {})
    if not data:
        for key, val in _ADM_TECHNIQUES.items():
            if technique_type.lower() in key.lower():
                data = val
                break
    if not data:
        return {"technique": technique_type, "error": f"Unknown technique: {technique_type}"}
    return {"technique": data["name"], "description": data["description"], "steps": data["steps"], "inputs": data["inputs"], "outputs": data["outputs"], "applicable_phases": data["applicable_phases"]}


def adm_get_iteration_cycle(cycle_type: str = "standard", **kwargs) -> dict:
    return {
        "cycle_type": cycle_type,
        "description": "The ADM is an iterative method — within each phase, between phases, and around the entire cycle.",
        "iteration_types": [
            {"type": "Architecture Development Iteration", "description": "Full cycle through ADM phases for initial architecture development", "phases": ["Preliminary", "A", "B", "C", "D", "E", "F", "G", "H"]},
            {"type": "Transition Planning Iteration", "description": "Phases E and F to create implementation and migration plans", "phases": ["E", "F"]},
            {"type": "Architecture Governance Iteration", "description": "Phases G and H for ongoing governance and change management", "phases": ["G", "H"]},
            {"type": "Architecture Capability Iteration", "description": "Focus on establishing or improving architecture capability", "phases": ["Preliminary", "A", "H"]},
        ],
        "key_principles": ["Each iteration establishes content scope, resources, scheduling", "Architecture development is continuous and cyclical", "Scope, detail, and deliverables adapt to the iteration context"],
    }


def adm_get_viewpoint(viewpoint_name: str = "", **kwargs) -> dict:
    viewpoints = {
        "stakeholder": {"name": "Stakeholder Viewpoint", "purpose": "Show key stakeholders and their concerns", "concerns": ["Power/Interest classification", "Communication needs", "Architecture views required"]},
        "architecture_overview": {"name": "Architecture Overview Viewpoint", "purpose": "Provide a summary view of the entire architecture", "concerns": ["Architecture scope", "Key design decisions", "Architecture principles"]},
        "business_capability": {"name": "Business Capability Viewpoint", "purpose": "Show business capabilities and their maturity", "concerns": ["Capability gaps", "Maturity levels", "Strategic alignment"]},
    }
    data = viewpoints.get(viewpoint_name, viewpoints.get("architecture_overview"))
    return {"viewpoint": data["name"], "purpose": data["purpose"], "concerns": data["concerns"]}


def _make_phase_handler(phase_key: str):
    def handler(**kwargs):
        kwargs.pop("phase", None)
        return adm_get_phase_details(phase=phase_key, **kwargs)
    return handler


def _make_deliverable_handler(deliverable_key: str):
    def handler(**kwargs):
        kwargs.pop("deliverable_type", None)
        return adm_get_deliverable(deliverable_type=deliverable_key, **kwargs)
    return handler


def _make_technique_handler(technique_key: str):
    def handler(**kwargs):
        kwargs.pop("technique_type", None)
        return adm_get_technique(technique_type=technique_key, **kwargs)
    return handler


TOOL_REGISTRY: dict[str, Any] = {}

# Phase variants
for _phase_key, _phase_suffix in [("Preliminary", "preliminary"), ("A", "a"), ("B", "b"), ("C", "c"), ("D", "d"), ("E", "e"), ("F", "f"), ("G", "g"), ("H", "h"), ("Requirements", "requirements")]:
    TOOL_REGISTRY[f"adm_get_phase_details_{_phase_suffix}"] = _make_phase_handler(_phase_key)

# Deliverable variants
for _deliv_key in _ADM_DELIVERABLES:
    TOOL_REGISTRY[f"adm_get_deliverable_{_deliv_key}"] = _make_deliverable_handler(_deliv_key)

# Technique variants
for _tech_key in _ADM_TECHNIQUES:
    TOOL_REGISTRY[f"adm_get_technique_{_tech_key}"] = _make_technique_handler(_tech_key)

# 1:1 tools
TOOL_REGISTRY["adm_get_iteration_cycle"] = adm_get_iteration_cycle
TOOL_REGISTRY["adm_get_viewpoint"] = adm_get_viewpoint
