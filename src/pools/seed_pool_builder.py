"""Builder for the TOGAF/ArchiMate Seed Pool.

All entities are grounded in the TOGAF Standard 10th Edition and
ArchiMate 3.2 specifications. Names, deliverables, metamodel entities,
and viewpoints use EXACT spec terminology.

Sources:
- TOGAF Standard, 10th Edition (The Open Group, 2022)
- ArchiMate 3.2 Specification (The Open Group, 2023)
"""

from __future__ import annotations

from pathlib import Path

from .models import SeedConcept, SeedCategory, save_pool


# =====================================================================
# TOGAF ADM Phases — exact per spec
# =====================================================================

def _togaf_phase_seeds() -> list[SeedConcept]:
    """ADM phases with exact inputs/outputs/steps per TOGAF Standard."""
    phases = [
        # Preliminary Phase
        ("preliminary", "Preliminary Phase",
         "Define Architecture Capability, establish Architecture Principles, select tools, define frameworks and methods",
         {"inputs": ["TOGAF Library", "Other architecture frameworks", "Board strategies and board business plans",
                     "Architecture governance and support strategies", "IT strategy", "Business principles, goals, and drivers"],
          "outputs": ["Organizational Model for Enterprise Architecture", "Tailored Architecture Framework",
                      "Architecture Principles", "Architecture Repository (initial)", "Request for Architecture Work (optional)",
                      "Architecture Governance Framework"],
          "steps": ["Define the enterprise", "Identify key drivers and elements", "Define architecture principles",
                    "Define the framework and methodology", "Evaluate EA maturity", "Define architecture team and organization",
                    "Identify and establish architecture governance"]}),

        # Phase A
        ("phase_A", "Phase A: Architecture Vision",
         "Develop high-level aspirational vision, obtain approval for Statement of Architecture Work",
         {"inputs": ["Request for Architecture Work", "Business principles, goals, and drivers",
                     "Architecture Principles", "Enterprise Continuum", "Architecture Repository"],
          "outputs": ["Approved Statement of Architecture Work", "Architecture Vision", "Refined statements of business principles, goals, and drivers",
                      "Draft Architecture Definition Document", "Communications Plan", "Capability Assessment"],
          "steps": ["Establish the architecture project", "Identify stakeholders, concerns, and business requirements",
                    "Confirm and elaborate business goals, drivers, and constraints", "Evaluate business capabilities",
                    "Assess readiness for transformation", "Define scope", "Confirm and elaborate Architecture Principles",
                    "Develop Architecture Vision", "Define Target Architecture value propositions and KPIs",
                    "Identify risks and mitigation activities", "Develop Statement of Architecture Work"]}),

        # Phase B
        ("phase_B", "Phase B: Business Architecture",
         "Develop the Business Architecture that supports the Architecture Vision",
         {"inputs": ["Request for Architecture Work", "Architecture Vision", "Architecture Principles",
                     "Enterprise Continuum", "Architecture Repository", "Draft Architecture Definition Document"],
          "outputs": ["Draft Architecture Definition Document (updated with Business Architecture)",
                      "Draft Architecture Requirements Specification (Business)",
                      "Business Architecture components of Architecture Roadmap"],
          "steps": ["Select reference models, viewpoints, and tools", "Develop Baseline Business Architecture Description",
                    "Develop Target Business Architecture Description", "Perform gap analysis",
                    "Define candidate roadmap components", "Resolve impacts across the Architecture Landscape",
                    "Conduct formal stakeholder review", "Finalize the Business Architecture",
                    "Create Architecture Definition Document"]}),

        # Phase C
        ("phase_C", "Phase C: Information Systems Architectures",
         "Develop Data Architecture and Application Architecture to support Business Architecture",
         {"inputs": ["Request for Architecture Work", "Capability Assessment", "Architecture Vision",
                     "Architecture Definition Document (with Business Architecture)", "Architecture Repository"],
          "outputs": ["Draft Architecture Definition Document (updated with Data and Application Architectures)",
                      "Draft Architecture Requirements Specification (IS)",
                      "Data Architecture components of Architecture Roadmap",
                      "Application Architecture components of Architecture Roadmap"],
          "steps": ["Develop Data Architecture (select models/viewpoints, baseline, target, gap analysis)",
                    "Develop Application Architecture (select models/viewpoints, baseline, target, gap analysis)",
                    "Resolve impacts across the Architecture Landscape",
                    "Conduct formal stakeholder review", "Finalize Information Systems Architectures",
                    "Create/update Architecture Definition Document"]}),

        # Phase D
        ("phase_D", "Phase D: Technology Architecture",
         "Develop the Technology Architecture that enables the IS Architectures",
         {"inputs": ["Architecture Vision", "Architecture Definition Document (B, C)", "Architecture Requirements Specification",
                     "Architecture Repository"],
          "outputs": ["Draft Architecture Definition Document (updated with Technology Architecture)",
                      "Draft Architecture Requirements Specification (Technology)",
                      "Technology Architecture components of Architecture Roadmap"],
          "steps": ["Select reference models, viewpoints, and tools", "Develop Baseline Technology Architecture Description",
                    "Develop Target Technology Architecture Description", "Perform gap analysis",
                    "Define candidate roadmap components", "Resolve impacts across the Architecture Landscape",
                    "Conduct formal stakeholder review", "Finalize the Technology Architecture",
                    "Create/update Architecture Definition Document"]}),

        # Phase E
        ("phase_E", "Phase E: Opportunities and Solutions",
         "Generate the initial complete version of the Architecture Roadmap, based on gap analysis and candidate roadmap components from B-D",
         {"inputs": ["Architecture Vision", "Architecture Definition Document (B, C, D)",
                     "Architecture Requirements Specification", "Architecture Repository",
                     "Candidate Architecture Roadmap components from B-D"],
          "outputs": ["Architecture Roadmap (initial complete version)", "Transition Architectures",
                      "Implementation and Migration Strategy"],
          "steps": ["Determine/confirm key corporate change attributes", "Determine business constraints for implementation",
                    "Review and consolidate gap analysis results from B-D", "Review consolidated requirements across functions",
                    "Consolidate and reconcile interoperability requirements",
                    "Refine and validate dependencies", "Confirm readiness and risk for transformation",
                    "Formulate Implementation and Migration Strategy", "Identify and group major work packages",
                    "Identify Transition Architectures", "Create the Architecture Roadmap and Implementation and Migration Plan"]}),

        # Phase F
        ("phase_F", "Phase F: Migration Planning",
         "Finalize the Architecture Roadmap and the Implementation and Migration Plan",
         {"inputs": ["Implementation and Migration Strategy", "Architecture Roadmap (from E)",
                     "Architecture Definition Document", "Architecture Requirements Specification",
                     "Transition Architectures", "Implementation Factor Assessment and Deduction Matrix"],
          "outputs": ["Implementation and Migration Plan (finalized)", "Architecture Roadmap (finalized)",
                      "Transition Architectures (finalized)", "Architecture contracts (in preparation)",
                      "Implementation governance model"],
          "steps": ["Confirm management framework interactions for Implementation and Migration Plan",
                    "Assign a business value to each work package", "Estimate resource requirements, project timings, and availability",
                    "Prioritize the migration projects through a cost/benefit assessment and risk validation",
                    "Confirm Architecture Roadmap and update Architecture Definition Document",
                    "Complete the Implementation and Migration Plan",
                    "Complete the architecture development cycle and document lessons learned"]}),

        # Phase G
        ("phase_G", "Phase G: Implementation Governance",
         "Provide architecture oversight of the implementation, ensure conformance with Target Architecture",
         {"inputs": ["Implementation and Migration Plan", "Architecture contracts",
                     "Architecture Definition Document", "Architecture Requirements Specification",
                     "Architecture Roadmap", "Implementation governance model"],
          "outputs": ["Architecture Contract (signed)", "Compliance Assessments",
                      "Change Requests", "Architecture-compliant implemented system"],
          "steps": ["Confirm scope and priorities for deployment with development management",
                    "Identify deployment resources and skills", "Guide development of solutions deployment",
                    "Perform enterprise architecture compliance reviews",
                    "Implement business and IT operations", "Perform post-implementation review and close the implementation"]}),

        # Phase H
        ("phase_H", "Phase H: Architecture Change Management",
         "Establish and support the implemented architecture, manage changes in an orderly fashion",
         {"inputs": ["Implementation Governance phase outputs", "Architecture Definition Document",
                     "Architecture Requirements Specification", "Architecture Roadmap",
                     "Change Requests from lessons learned"],
          "outputs": ["Architecture updates", "Changes to Architecture Framework and Principles",
                      "New Request for Architecture Work (to initiate another ADM cycle)"],
          "steps": ["Establish value realization process", "Deploy monitoring tools",
                    "Manage risks", "Provide analysis for architecture change management",
                    "Develop change requirements to meet performance targets",
                    "Manage governance process", "Activate the process to implement change"]}),

        # Requirements Management
        ("requirements_mgmt", "Requirements Management",
         "Continuous process of managing architecture requirements throughout all ADM phases",
         {"inputs": ["Architecture requirements from any ADM phase"],
          "outputs": ["Requirements Impact Assessment", "Updated Architecture Requirements Specification"],
          "steps": ["Identify/document requirements", "Baseline requirements",
                    "Monitor baseline requirements", "Identify changed requirements and record priorities",
                    "Assess impact of changed requirements on current and previous ADM phases",
                    "Implement requirements arising from Phase H",
                    "Update the requirements repository", "Implement change in current phase",
                    "Assess and revise gap analysis for changed requirements"]}),
    ]

    seeds = []
    for key, name, desc, meta in phases:
        seeds.append(SeedConcept(
            id=f"phase_{key}", name=name, category=SeedCategory.TOGAF_PHASE,
            description=desc, domain="adm", tags=["phase", key], metadata=meta,
        ))
    return seeds


# =====================================================================
# TOGAF Deliverables — exact spec names (Section 20.3)
# =====================================================================

def _togaf_deliverable_seeds() -> list[SeedConcept]:
    """TOGAF deliverables as defined in the spec."""
    deliverables = [
        ("architecture_building_blocks", "Architecture Building Blocks", "Reusable architecture components: ABBs capture architecture requirements and direct SBBs"),
        ("architecture_contract", "Architecture Contract", "Joint agreements between development partners and sponsors on deliverables, quality, and fitness-for-purpose of an architecture"),
        ("architecture_definition_document", "Architecture Definition Document", "The deliverable container for the core architectural artifacts. Spans all domains: Business, Data, Application, Technology"),
        ("architecture_principles", "Architecture Principles", "General rules and guidelines that inform and support how an organization fulfills its mission"),
        ("architecture_repository", "Architecture Repository", "The holding area for all architecture-related materials: Architecture Metamodel, Architecture Capability, Architecture Landscape, Standards Information Base, Reference Library, Governance Log"),
        ("architecture_requirements_spec", "Architecture Requirements Specification", "Set of quantitative statements that outline what an implementation project must do to comply with the architecture"),
        ("architecture_roadmap", "Architecture Roadmap", "List of individual work packages showing a timeline of the changes, including Transition Architectures"),
        ("architecture_vision", "Architecture Vision", "High-level summary of the changes to the enterprise that will accrue from successful deployment of the Target Architecture"),
        ("business_principles_goals_drivers", "Business Principles, Business Goals, and Business Drivers", "Business principles, goals, and strategic drivers that provide context for architecture work"),
        ("capability_assessment", "Capability Assessment", "Assessment of the capabilities and maturity levels of the enterprise, identifying areas of change"),
        ("change_request", "Change Request", "Request for modification, raised through governance as a result of changes to the baseline or target architecture"),
        ("communications_plan", "Communications Plan", "Plan to communicate architecture deliverables to the right stakeholders at the right time"),
        ("compliance_assessment", "Compliance Assessment", "Assessment of architecture compliance of projects, identifying any architecture gaps"),
        ("implementation_governance_model", "Implementation Governance Model", "Governance procedures and organization for managing the architecture implementation"),
        ("implementation_migration_plan", "Implementation and Migration Plan", "Schedule of projects, resource allocations, and detailed migration approach for realizing Transition Architectures"),
        ("org_model_for_ea", "Organizational Model for Enterprise Architecture", "Governance model, maturity assessments, budget, and roles/responsibilities for EA capability"),
        ("request_for_architecture_work", "Request for Architecture Work", "Trigger document for architecture development, from sponsor to architecture organization"),
        ("requirements_impact_assessment", "Requirements Impact Assessment", "Assessment of the impact of new/changed requirements on the current architecture"),
        ("solution_building_blocks", "Solution Building Blocks", "Candidate solutions: implementations of ABBs that map to specific products or technologies"),
        ("statement_of_architecture_work", "Statement of Architecture Work", "Defines scope and approach of the architecture project; a deliverable of Phase A"),
        ("tailored_architecture_framework", "Tailored Architecture Framework", "Organization-specific version of the TOGAF framework"),
        ("transition_architecture", "Transition Architecture", "Description of the enterprise at an architecturally significant state between the Baseline and Target Architectures"),
    ]

    seeds = []
    for key, name, desc in deliverables:
        seeds.append(SeedConcept(
            id=f"deliverable_{key}", name=name, category=SeedCategory.TOGAF_DELIVERABLE,
            description=desc, domain="togaf", tags=["deliverable"],
        ))
    return seeds


# =====================================================================
# TOGAF Artifacts — catalogs, matrices, diagrams (Section 20.4)
# =====================================================================

def _togaf_artifact_seeds() -> list[SeedConcept]:
    """TOGAF artifacts: catalogs, matrices, diagrams per spec."""
    artifacts = [
        # Catalogs
        ("principles_catalog", "Principles Catalog", "catalog", "Catalog of architecture principles with rationale and implications"),
        ("stakeholder_map_catalog", "Stakeholder Map", "catalog", "Matrix of stakeholders against architecture viewpoints"),
        ("role_catalog", "Role Catalog", "catalog", "Catalog of governance/process roles"),
        ("business_service_function_catalog", "Business Service/Function Catalog", "catalog", "Functional decomposition of services/functions"),
        ("location_catalog", "Location Catalog", "catalog", "List of all enterprise locations"),
        ("process_event_catalog", "Process/Event/Control/Product Catalog", "catalog", "List of processes, events, controls, and products"),
        ("contract_measure_catalog", "Contract/Measure Catalog", "catalog", "Catalog of contracts and SLAs"),
        ("data_entity_catalog", "Data Entity/Data Component Catalog", "catalog", "Listing of data entities and data components"),
        ("application_portfolio_catalog", "Application Portfolio Catalog", "catalog", "Full inventory of applications"),
        ("interface_catalog", "Interface Catalog", "catalog", "Catalog of application-to-application interfaces"),
        ("technology_standards_catalog", "Technology Standards Catalog", "catalog", "Approved technology standards list"),
        ("technology_portfolio_catalog", "Technology Portfolio Catalog", "catalog", "Technology components with lifecycle status"),

        # Matrices
        ("stakeholder_role_matrix", "Stakeholder Map/Role Matrix", "matrix", "Mapping of stakeholders to their roles"),
        ("business_interaction_matrix", "Business Interaction Matrix", "matrix", "Dependencies between business functions/organizations"),
        ("actor_role_matrix", "Actor/Role Matrix", "matrix", "Mapping of actors to roles"),
        ("application_data_matrix", "Application/Data Matrix", "matrix", "Mapping of applications to data entities"),
        ("app_function_matrix", "Application/Function Matrix", "matrix", "Mapping of applications to business functions"),
        ("app_org_matrix", "Application/Organization Matrix", "matrix", "Mapping of applications to organizational units"),
        ("app_role_matrix", "Application/Role Matrix", "matrix", "Mapping of applications to user roles"),
        ("app_technology_matrix", "Application/Technology Matrix", "matrix", "Mapping of applications to technology platforms"),
        ("system_data_matrix", "System/Data Matrix", "matrix", "Mapping of systems to data flows"),
        ("system_technology_matrix", "System/Technology Matrix", "matrix", "Mapping of systems to technology components"),

        # Diagrams
        ("value_chain_diagram", "Value Chain Diagram", "diagram", "High-level view of the enterprise value chain"),
        ("solution_concept_diagram", "Solution Concept Diagram", "diagram", "High-level graphical view of the solution"),
        ("business_footprint_diagram", "Business Footprint Diagram", "diagram", "Links between business goals, organizational units, business functions, and services"),
        ("business_service_info_diagram", "Business Service/Information Diagram", "diagram", "Mapping of business services to information"),
        ("functional_decomposition_diagram", "Functional Decomposition Diagram", "diagram", "Hierarchical decomposition of business functions"),
        ("product_lifecycle_diagram", "Product Lifecycle Diagram", "diagram", "Lifecycle stages of products/services"),
        ("goal_objective_service_diagram", "Goal/Objective/Service Diagram", "diagram", "Mapping of business goals to architecture services"),
        ("business_use_case_diagram", "Business Use-Case Diagram", "diagram", "Business processes with actors"),
        ("organization_decomposition_diagram", "Organization Decomposition Diagram", "diagram", "Organizational hierarchy"),
        ("process_flow_diagram", "Process Flow Diagram", "diagram", "Business process flow sequences"),
        ("event_diagram", "Event Diagram", "diagram", "Business events and their relationships"),
        ("data_dissemination_diagram", "Data Dissemination Diagram", "diagram", "Data movement between systems"),
        ("data_lifecycle_diagram", "Data Lifecycle Diagram", "diagram", "Data entity lifecycle"),
        ("data_security_diagram", "Data Security Diagram", "diagram", "Data classification and access controls"),
        ("class_hierarchy_diagram", "Class Hierarchy Diagram", "diagram", "Data entity class hierarchy"),
        ("data_migration_diagram", "Data Migration Diagram", "diagram", "Data migration approach"),
        ("application_communication_diagram", "Application Communication Diagram", "diagram", "Inter-application data flows"),
        ("application_and_user_location_diagram", "Application and User Location Diagram", "diagram", "Geographic deployment of applications"),
        ("application_use_case_diagram", "Application Use-Case Diagram", "diagram", "Application use cases"),
        ("enterprise_manageability_diagram", "Enterprise Manageability Diagram", "diagram", "How systems are managed"),
        ("process_application_realization_diagram", "Process/Application Realization Diagram", "diagram", "How applications realize business processes"),
        ("software_engineering_diagram", "Software Engineering Diagram", "diagram", "Software engineering artifacts"),
        ("application_migration_diagram", "Application Migration Diagram", "diagram", "Application migration steps"),
        ("software_distribution_diagram", "Software Distribution Diagram", "diagram", "Software deployment topology"),
        ("environments_locations_diagram", "Environments and Locations Diagram", "diagram", "Technology environments and physical locations"),
        ("platform_decomposition_diagram", "Platform Decomposition Diagram", "diagram", "Platform component breakdown"),
        ("processing_diagram", "Processing Diagram", "diagram", "Processing flows and nodes"),
        ("network_computing_hw_diagram", "Networked Computing/Hardware Diagram", "diagram", "Network and compute infrastructure"),
        ("communications_engineering_diagram", "Communications Engineering Diagram", "diagram", "Communication infrastructure detail"),
    ]

    seeds = []
    for key, name, artifact_type, desc in artifacts:
        seeds.append(SeedConcept(
            id=f"artifact_{key}", name=name, category=SeedCategory.TOGAF_ARTIFACT,
            description=desc, domain="togaf", tags=["artifact", artifact_type],
            metadata={"artifact_type": artifact_type},
        ))
    return seeds


# =====================================================================
# TOGAF Content Metamodel Entities (Section 20.2)
# =====================================================================

def _togaf_metamodel_seeds() -> list[SeedConcept]:
    """TOGAF Content Metamodel entity types — exact spec names."""
    entities = [
        # Architecture Core entities
        ("cm_principle", "Principle", "core", "A qualitative statement of intent that should be met by the architecture"),
        ("cm_constraint", "Constraint", "core", "An external factor that prevents the organization from pursuing approaches"),
        ("cm_assumption", "Assumption", "core", "A statement of probable fact that has not been fully validated"),
        ("cm_requirement", "Requirement", "core", "A quantitative statement of business need that must be met by architecture"),
        ("cm_gap", "Gap", "core", "A statement of difference between two states. Used in gap analysis for each domain"),
        ("cm_work_package", "Work Package", "core", "A set of actions identified to realize one or more objectives of the architecture"),
        ("cm_capability", "Capability", "core", "A particular ability that a business may possess or exchange to achieve a purpose"),
        ("cm_course_of_action", "Course of Action", "core", "Direction and focus for how the architecture contributes to achieving goals"),
        ("cm_location", "Location", "core", "A place where business activity takes place and can be hierarchically decomposed"),

        # Business Architecture entities
        ("cm_organization_unit", "Organization Unit", "business", "Self-contained unit of resources with goals, objectives, and measures"),
        ("cm_actor", "Actor", "business", "A person, organization, or system that is outside the consideration of the architecture model"),
        ("cm_role", "Role", "business", "An actor assumes a role to perform a task. Multiple actors can assume same role"),
        ("cm_business_service", "Business Service", "business", "Supports business capabilities through an explicitly defined interface"),
        ("cm_business_function", "Function", "business", "Delivers business capabilities closely aligned to an organization"),
        ("cm_business_process", "Process", "business", "A process that is a flow of activities. Orchestrated through business events"),
        ("cm_business_event", "Event", "business", "An organizational state change that triggers further processing"),
        ("cm_control", "Control", "business", "Ensures that a process produces the correct outcome"),
        ("cm_product", "Product", "business", "Output generated by the business that provides value to a customer"),
        ("cm_measure", "Measure", "business", "Indicator or factor that can be tracked, usually against a target or objective"),
        ("cm_objective", "Objective", "business", "A time-bounded milestone for an organization"),
        ("cm_contract", "Contract", "business", "An agreement between a service consumer and provider"),
        ("cm_service_quality", "Service Quality", "business", "A preset/agreed-to QoS level: availability, service hours, etc."),

        # Data Architecture entities
        ("cm_data_entity", "Data Entity", "data", "An encapsulation of data managed/owned by the enterprise"),
        ("cm_logical_data_component", "Logical Data Component", "data", "A boundary zone that encapsulates related data entities"),
        ("cm_physical_data_component", "Physical Data Component", "data", "A physical implementation of a logical data component"),

        # Application Architecture entities
        ("cm_logical_application_component", "Logical Application Component", "application", "An encapsulation of application functionality independently deployable, reusable"),
        ("cm_physical_application_component", "Physical Application Component", "application", "An application, module, sub-system, or object that realizes logical components"),
        ("cm_information_system_service", "Information System Service", "application", "An automated service that provides a specific business interface"),

        # Technology Architecture entities
        ("cm_platform_service", "Platform Service", "technology", "A technical capability required to provide infrastructure for the architecture"),
        ("cm_logical_technology_component", "Logical Technology Component", "technology", "A technology infrastructure component independent of specific products"),
        ("cm_physical_technology_component", "Physical Technology Component", "technology", "A specific technology infrastructure product/component"),
    ]

    seeds = []
    for key, name, domain, desc in entities:
        seeds.append(SeedConcept(
            id=f"metamodel_{key}", name=name, category=SeedCategory.TOGAF_METAMODEL_ENTITY,
            description=desc, domain=domain, tags=["metamodel", domain],
        ))
    return seeds


# =====================================================================
# TOGAF Techniques (Section 21)
# =====================================================================

def _togaf_technique_seeds() -> list[SeedConcept]:
    """TOGAF techniques — exact names from the spec."""
    techniques = [
        ("principles_definition", "Architecture Principles", "Defining and cataloging architecture principles with name, statement, rationale, and implications"),
        ("stakeholder_management", "Stakeholder Management", "Identifying, classifying, and managing stakeholder engagement using power/interest grids"),
        ("architecture_patterns", "Architecture Patterns", "Reusable forms describing context, problem, and solution for recurring architectural challenges"),
        ("gap_analysis", "Gap Analysis", "Systematic comparison of baseline and target architectures to identify gaps (new, modified, eliminated, retained)"),
        ("migration_planning", "Migration Planning Techniques", "Implementation Factor Assessment, Deduction Matrix, business value assessment, and risk assessment for sequencing"),
        ("interoperability", "Interoperability Requirements", "Determining interoperability requirements and classifying them on the Enterprise/ISA Interoperability spectrum"),
        ("business_transformation_readiness", "Business Transformation Readiness Assessment", "Evaluating organizational readiness for change across maturity factors and readiness factors"),
        ("risk_management", "Risk Management", "Classification and mitigation of risks: initial level of risk, residual level of risk, and risk mitigation activities"),
        ("capability_based_planning", "Capability-Based Planning", "Planning based on business capabilities: capability increments, capability dimensions, and heat maps"),
        ("business_scenarios", "Business Scenarios", "Technique for identifying and articulating business requirements using problem-goal-solution narrative"),
        ("business_value_assessment", "Value Realization/Business Value Assessment", "Quantifying the business value of architecture work: financial metrics, KPIs, and value streams"),
        ("architecture_compliance_review", "Architecture Compliance Reviews", "Formal reviews ensuring implementation conforms to architecture: tailored checklists per project type"),
        ("maturity_models", "Architecture Maturity Models", "ACMM (Architecture Capability Maturity Model) levels 0-5 for assessing EA practice maturity"),
        ("implementation_factor_assessment", "Implementation Factor Assessment and Deduction Matrix", "Assessing factors (risks, issues, dependencies, actions) and using deduction matrix to determine project sequencing"),
    ]

    seeds = []
    for key, name, desc in techniques:
        seeds.append(SeedConcept(
            id=f"technique_{key}", name=name, category=SeedCategory.TOGAF_TECHNIQUE,
            description=desc, domain="togaf", tags=["technique"],
        ))
    return seeds


# =====================================================================
# TOGAF Architecture Viewpoints (Section 20.5, Architecture Views)
# =====================================================================

def _togaf_viewpoint_seeds() -> list[SeedConcept]:
    """TOGAF architecture viewpoints — per spec guidance."""
    viewpoints = [
        ("vp_business_arch_view", "Business Architecture View", "Addresses concerns of business management: services, processes, organization, functions, events"),
        ("vp_data_arch_view", "Data Architecture View", "Addresses concerns of data management: entities, components, flows, governance"),
        ("vp_application_arch_view", "Application Architecture View", "Addresses concerns of application development: components, interfaces, services, portfolios"),
        ("vp_technology_arch_view", "Technology Architecture View", "Addresses concerns of IT operations: platforms, infrastructure, networks, middleware"),
        ("vp_security_view", "Security Architecture View", "Addresses security aspects across all architecture domains"),
        ("vp_performance_view", "Performance and Capacity Architecture View", "Addresses performance and capacity engineering across all domains"),
        ("vp_interoperability_view", "System/Service Interoperability View", "Addresses interoperability concerns between systems and services"),
        ("vp_governance_view", "Governance Architecture View", "Addresses concerns of architecture governance: compliance, decision-making, standards"),
        ("vp_migration_view", "Migration Architecture View", "Addresses concerns of transition from baseline to target architecture"),
        ("vp_requirements_view", "Requirements View", "Addresses traceability from requirements to architecture artifacts"),
    ]

    seeds = []
    for key, name, desc in viewpoints:
        seeds.append(SeedConcept(
            id=f"togaf_{key}", name=name, category=SeedCategory.TOGAF_VIEWPOINT,
            description=desc, domain="togaf", tags=["viewpoint", "togaf"],
        ))
    return seeds


# =====================================================================
# ArchiMate 3.2 Elements — complete per spec
# =====================================================================

def _archimate_element_seeds() -> list[SeedConcept]:
    """ArchiMate 3.2 element types — exact names per spec."""
    elements = [
        # Strategy Layer (Chapter 7)
        ("resource", "Resource", "strategy", "active_structure", "An asset owned or controlled by an individual or organization"),
        ("capability", "Capability", "strategy", "behavior", "An ability that an active structure element possesses"),
        ("value_stream", "Value Stream", "strategy", "behavior", "A sequence of activities that creates an overall result for a customer, stakeholder, or end user"),
        ("course_of_action", "Course of Action", "strategy", "behavior", "An approach or plan for configuring capabilities and resources to achieve a goal"),

        # Business Layer (Chapter 8)
        ("business_actor", "Business Actor", "business", "active_structure", "A business entity that is capable of performing behavior"),
        ("business_role", "Business Role", "business", "active_structure", "The responsibility for performing specific behavior, to which an actor can be assigned"),
        ("business_collaboration", "Business Collaboration", "business", "active_structure", "An aggregate of two or more business internal active structure elements that work together"),
        ("business_interface", "Business Interface", "business", "active_structure", "A point of access where a business service is made available to the environment"),
        ("business_process", "Business Process", "business", "behavior", "A sequence of business behaviors that achieves a specific result"),
        ("business_function", "Business Function", "business", "behavior", "A collection of business behavior based on a chosen set of criteria"),
        ("business_interaction", "Business Interaction", "business", "behavior", "A unit of collective business behavior performed by a collaboration"),
        ("business_event", "Business Event", "business", "behavior", "A business behavior element that denotes an organizational state change"),
        ("business_service", "Business Service", "business", "behavior", "An explicitly defined exposed business behavior"),
        ("business_object", "Business Object", "business", "passive_structure", "A concept used within a particular business domain"),
        ("contract", "Contract", "business", "passive_structure", "A formal or informal specification of an agreement between a provider and a consumer"),
        ("representation", "Representation", "business", "passive_structure", "A perceptible form of the information carried by a business object"),
        ("product", "Product", "business", "composite", "A coherent collection of services and/or passive structure elements, accompanied by a contract/agreement"),

        # Application Layer (Chapter 9)
        ("application_component", "Application Component", "application", "active_structure", "An encapsulation of application functionality aligned to implementation structure"),
        ("application_collaboration", "Application Collaboration", "application", "active_structure", "An aggregate of two or more application components that work together"),
        ("application_interface", "Application Interface", "application", "active_structure", "A point of access where application services are made available"),
        ("application_function", "Application Function", "application", "behavior", "Automated behavior that can be performed by an application component"),
        ("application_interaction", "Application Interaction", "application", "behavior", "A unit of collective application behavior performed by a collaboration"),
        ("application_process", "Application Process", "application", "behavior", "A sequence of application behaviors that achieves a specific result"),
        ("application_event", "Application Event", "application", "behavior", "An application behavior element that denotes a state change"),
        ("application_service", "Application Service", "application", "behavior", "An explicitly defined exposed application behavior"),
        ("data_object", "Data Object", "application", "passive_structure", "Data structured for automated processing"),

        # Technology Layer (Chapter 10)
        ("node", "Node", "technology", "active_structure", "A computational or physical resource that hosts, manipulates, or interacts with other computational or physical resources"),
        ("device", "Device", "technology", "active_structure", "A physical IT resource upon which system software and artifacts may be stored or deployed"),
        ("system_software", "System Software", "technology", "active_structure", "Software that provides or contributes to an environment for storing, executing, and using software or data"),
        ("technology_collaboration", "Technology Collaboration", "technology", "active_structure", "An aggregate of two or more technology internal active structure elements that work together"),
        ("technology_interface", "Technology Interface", "technology", "active_structure", "A point of access where technology services are made available"),
        ("path", "Path", "technology", "active_structure", "A link between two or more nodes, through which these nodes can exchange data, energy, or material"),
        ("communication_network", "Communication Network", "technology", "active_structure", "A set of structures that connects nodes for transmission, routing, and reception"),
        ("technology_function", "Technology Function", "technology", "behavior", "A collection of technology behavior that can be performed by a node"),
        ("technology_process", "Technology Process", "technology", "behavior", "A sequence of technology behaviors that achieves a specific result"),
        ("technology_interaction", "Technology Interaction", "technology", "behavior", "A unit of collective technology behavior performed by a collaboration"),
        ("technology_event", "Technology Event", "technology", "behavior", "A technology behavior element that denotes a state change"),
        ("technology_service", "Technology Service", "technology", "behavior", "An explicitly defined exposed technology behavior"),
        ("artifact", "Artifact", "technology", "passive_structure", "A piece of data that is used or produced in a software development process, or by deployment and operation of an IT system"),

        # Physical Elements (Chapter 11)
        ("equipment", "Equipment", "physical", "active_structure", "One or more physical machines, tools, or instruments that can create, use, store, move, or transform materials"),
        ("facility", "Facility", "physical", "active_structure", "A physical structure or environment"),
        ("distribution_network", "Distribution Network", "physical", "active_structure", "A physical medium used to transport materials or energy"),
        ("material", "Material", "physical", "passive_structure", "Tangible physical matter or energy"),

        # Motivation Elements (Chapter 12)
        ("stakeholder", "Stakeholder", "motivation", "active_structure", "The role of an individual, team, or organization that represents their interests in the architecture"),
        ("driver", "Driver", "motivation", "passive_structure", "An external or internal condition that motivates an organization to define its goals and implement changes"),
        ("assessment", "Assessment", "motivation", "passive_structure", "The result of an analysis of the state of affairs of the enterprise with respect to some driver"),
        ("goal", "Goal", "motivation", "passive_structure", "A high-level statement of intent, direction, or desired end state"),
        ("outcome", "Outcome", "motivation", "passive_structure", "An end result"),
        ("principle", "Principle", "motivation", "passive_structure", "A qualitative statement of intent that should be met by the architecture"),
        ("requirement", "Requirement", "motivation", "passive_structure", "A statement of need that must be realized by a system"),
        ("constraint", "Constraint", "motivation", "passive_structure", "A factor that prevents or obstructs the realization of goals"),
        ("meaning", "Meaning", "motivation", "passive_structure", "The knowledge or expertise present in, or the interpretation given to, a concept"),
        ("value", "Value", "motivation", "passive_structure", "The relative worth, utility, or importance of a concept"),

        # Implementation & Migration (Chapter 13)
        ("work_package", "Work Package", "implementation_migration", "behavior", "A series of actions identified and designed to achieve specific results within specified time and resource constraints"),
        ("deliverable", "Deliverable", "implementation_migration", "passive_structure", "A precisely-defined outcome of a work package"),
        ("implementation_event", "Implementation Event", "implementation_migration", "behavior", "A state change related to implementation or migration"),
        ("plateau", "Plateau", "implementation_migration", "composite", "A relatively stable state of the architecture that exists during a limited period of time"),
        ("gap", "Gap", "implementation_migration", "passive_structure", "A statement of difference between two plateaus"),

        # Composite Elements (Chapter 14)
        ("grouping", "Grouping", "composite", "composite", "Aggregates or composes concepts that belong together based on some common characteristic"),
        ("location", "Location", "composite", "composite", "A place or position where structure elements can be located or behavior can be performed"),
    ]

    seeds = []
    for key, name, layer, aspect, desc in elements:
        seeds.append(SeedConcept(
            id=f"am_element_{key}", name=name, category=SeedCategory.ARCHIMATE_ELEMENT,
            description=desc, domain=f"archimate_{layer}",
            tags=["archimate", "element", layer, aspect],
            metadata={"layer": layer, "aspect": aspect},
        ))
    return seeds


# =====================================================================
# ArchiMate 3.2 Relationships — complete per spec (Chapter 5)
# =====================================================================

def _archimate_relationship_seeds() -> list[SeedConcept]:
    """ArchiMate 3.2 relationship types — exact per spec."""
    relationships = [
        # Structural relationships
        ("composition", "Composition Relationship", "structural",
         "Indicates that an element consists of one or more other concepts. The part is integral to the whole"),
        ("aggregation", "Aggregation Relationship", "structural",
         "Indicates that an element combines one or more other concepts. Parts can exist independently"),
        ("assignment", "Assignment Relationship", "structural",
         "Expresses the allocation of responsibility, performance of behavior, storage, or execution"),
        ("realization", "Realization Relationship", "structural",
         "Indicates that an entity plays a critical role in the creation, achievement, sustenance, or operation of a more abstract entity"),

        # Dependency relationships
        ("serving", "Serving Relationship", "dependency",
         "Models that an element provides its functionality to another element. Previously called 'Used By'"),
        ("access", "Access Relationship", "dependency",
         "Models the ability of behavior and active structure elements to observe or act upon passive structure elements"),
        ("influence", "Influence Relationship", "dependency",
         "Models that an element affects the implementation or achievement of some motivation element. Can be positive or negative"),

        # Dynamic relationships
        ("triggering", "Triggering Relationship", "dynamic",
         "Describes a temporal or causal relationship between elements. The source triggers the target"),
        ("flow", "Flow Relationship", "dynamic",
         "Describes the exchange or transfer of, for example, information or value between processes, function, interactions, and events"),

        # Other relationships
        ("specialization", "Specialization Relationship", "other",
         "Indicates that an element is a particular kind of another element"),
        ("association", "Association Relationship", "other",
         "Models an unspecified relationship, or one that is not represented by another ArchiMate relationship"),

        # Connectors
        ("junction_and", "Junction (AND)", "connector",
         "Used to connect relationships of the same type. AND junction: all paths are followed"),
        ("junction_or", "Junction (OR)", "connector",
         "Used to connect relationships of the same type. OR junction: one or more paths are followed"),
    ]

    seeds = []
    for key, name, rel_category, desc in relationships:
        seeds.append(SeedConcept(
            id=f"am_rel_{key}", name=name, category=SeedCategory.ARCHIMATE_RELATIONSHIP,
            description=desc, domain="archimate",
            tags=["archimate", "relationship", rel_category],
            metadata={"relationship_category": rel_category},
        ))
    return seeds


# =====================================================================
# ArchiMate 3.2 Viewpoints — complete per spec (Appendix C)
# =====================================================================

def _archimate_viewpoint_seeds() -> list[SeedConcept]:
    """ArchiMate 3.2 example viewpoints — exact names from Appendix C."""
    viewpoints = [
        ("organization_vp", "Organization Viewpoint", "Shows the structure of the organization: actors, roles, and their relationships"),
        ("business_process_cooperation_vp", "Business Process Cooperation Viewpoint", "Shows relationships and dependencies between business processes"),
        ("product_vp", "Product Viewpoint", "Shows the value a product offers to customers, including the constituting services and contracts"),
        ("application_cooperation_vp", "Application Cooperation Viewpoint", "Shows application components and their cooperation through information flows or services"),
        ("application_usage_vp", "Application Usage Viewpoint", "Relates applications to their use by business processes"),
        ("implementation_deployment_vp", "Implementation and Deployment Viewpoint", "Shows how applications are mapped onto the underlying technology"),
        ("technology_vp", "Technology Viewpoint", "Shows the structure and connectivity of the technology infrastructure"),
        ("technology_usage_vp", "Technology Usage Viewpoint", "Shows how applications are supported by the technology infrastructure"),
        ("information_structure_vp", "Information Structure Viewpoint", "Shows the structure of the information used, including data types and relationships"),
        ("service_realization_vp", "Service Realization Viewpoint", "Shows how services are realized by required behavior, performed by active structure elements"),
        ("physical_vp", "Physical Viewpoint", "Shows the physical environment and how it relates to IT infrastructure"),
        ("layered_vp", "Layered Viewpoint", "Provides an overview across two or more layers of the ArchiMate framework"),
        ("landscape_map_vp", "Landscape Map Viewpoint", "Represents architecture elements as a map (matrix/grid) showing relationships between dimensions"),
        ("goal_realization_vp", "Goal Realization Viewpoint", "Shows how goals are refined into requirements, and realized by core elements"),
        ("requirements_realization_vp", "Requirements Realization Viewpoint", "Shows how requirements are realized by core elements such as actors, services, processes, applications"),
        ("motivation_vp", "Motivation Viewpoint", "Shows motivational elements and their relationships: stakeholders, drivers, goals, principles, requirements"),
        ("strategy_vp", "Strategy Viewpoint", "Shows strategic course of action, capabilities, and resources"),
        ("capability_map_vp", "Capability Map Viewpoint", "Shows a structured overview of capabilities, typically as a heat map"),
        ("outcome_realization_vp", "Outcome Realization Viewpoint", "Shows how outcomes contribute to value creation and how core elements realize outcomes"),
        ("resource_map_vp", "Resource Map Viewpoint", "Shows structured overview of resources required to realize capabilities"),
        ("value_stream_vp", "Value Stream Viewpoint", "Shows value stream stages and their relationships to capabilities, value, and stakeholders"),
        ("project_vp", "Project Viewpoint", "Shows management of the change: work packages, deliverables, and migration from plateau to plateau"),
        ("migration_vp", "Migration Viewpoint", "Shows transition from existing plateaus to target plateaus through transition architectures"),
        ("implementation_migration_vp", "Implementation and Migration Viewpoint", "Shows how the implementation of projects relates to migration from current to future state"),
    ]

    seeds = []
    for key, name, desc in viewpoints:
        seeds.append(SeedConcept(
            id=f"am_{key}", name=name, category=SeedCategory.ARCHIMATE_VIEWPOINT,
            description=desc, domain="archimate", tags=["archimate", "viewpoint"],
        ))
    return seeds


# =====================================================================
# Industry Cases
# =====================================================================

def _industry_case_seeds() -> list[SeedConcept]:
    """Industry-specific case seeds across domains."""
    cases = [
        # Banking & Finance
        ("banking_core_modernization", "Banking Core Modernization", "banking", "Modernizing legacy core banking systems to cloud-native architecture"),
        ("payment_hub_transformation", "Payment Hub Transformation", "banking", "Centralizing payment processing across channels"),
        ("open_banking_api", "Open Banking API Ecosystem", "banking", "PSD2/open banking API infrastructure"),
        ("aml_kyc_platform", "AML/KYC Platform Modernization", "banking", "Anti-money laundering and KYC platform overhaul"),
        ("loan_origination_modernization", "Loan Origination System Modernization", "banking", "Modernizing end-to-end loan origination"),
        ("real_time_payments", "Real-Time Payments Infrastructure", "banking", "Instant payment capabilities (ISO 20022)"),
        ("regulatory_reporting", "Regulatory Reporting Platform", "banking", "Automated regulatory reporting (Basel III, BCBS 239)"),

        # Healthcare
        ("healthcare_fhir", "Healthcare FHIR Integration", "healthcare", "HL7 FHIR-based healthcare data interoperability"),
        ("ehr_modernization", "EHR System Modernization", "healthcare", "Electronic health record system modernization"),
        ("clinical_data_lake", "Clinical Data Lake", "healthcare", "Enterprise clinical data lake for analytics"),
        ("telemedicine_platform", "Telemedicine Platform Architecture", "healthcare", "Scalable telemedicine platform design"),

        # Telecom
        ("telecom_5g_slicing", "5G Network Slicing Architecture", "telecom", "5G network slicing for multi-tenant services"),
        ("bss_transformation", "BSS Transformation", "telecom", "Business support system transformation (TM Forum ODA)"),
        ("oss_modernization", "OSS Modernization", "telecom", "Operations support system cloud migration"),

        # Manufacturing
        ("smart_factory", "Smart Factory Architecture", "manufacturing", "Industry 4.0 smart factory implementation"),
        ("supply_chain_control_tower", "Supply Chain Control Tower", "manufacturing", "End-to-end supply chain visibility"),
        ("digital_twin_manufacturing", "Manufacturing Digital Twin", "manufacturing", "Digital twin for manufacturing processes"),

        # Government
        ("gov_digital_services", "Government Digital Services", "government", "Citizen-facing digital government services"),
        ("cross_agency_data_sharing", "Cross-Agency Data Sharing", "government", "Secure inter-agency data sharing"),
        ("gov_legacy_modernization", "Government IT Modernization", "government", "Modernizing decades-old government systems"),

        # Cross-industry
        ("cloud_migration_enterprise", "Enterprise Cloud Migration", "cross_industry", "Comprehensive cloud migration program"),
        ("microservices_decomposition", "Monolith to Microservices", "cross_industry", "Monolith decomposition transformation"),
        ("data_mesh", "Data Mesh Implementation", "cross_industry", "Data mesh architecture paradigm"),
        ("zero_trust", "Zero Trust Architecture", "cross_industry", "Zero trust network architecture implementation"),
        ("api_platform", "Enterprise API Platform", "cross_industry", "Organization-wide API management"),
        ("event_driven", "Event-Driven Architecture", "cross_industry", "Enterprise EDA transformation"),
        ("erp_cloud_migration", "ERP Cloud Migration", "cross_industry", "Migrating ERP to cloud platform"),
        ("observability_platform", "Observability Platform", "cross_industry", "Unified monitoring and observability"),
        ("iam_modernization", "IAM Modernization", "cross_industry", "Identity and access management overhaul"),
    ]

    seeds = []
    for key, name, industry, desc in cases:
        seeds.append(SeedConcept(
            id=f"case_{key}", name=name, category=SeedCategory.INDUSTRY_CASE,
            description=desc, domain=industry, tags=["industry_case", industry],
        ))
    return seeds


# =====================================================================
# Standards
# =====================================================================

def _standard_seeds() -> list[SeedConcept]:
    """Compliance standards relevant to architecture."""
    standards = [
        ("togaf_10", "TOGAF Standard 10th Edition", "The Open Group Architecture Framework version 10"),
        ("archimate_3_2", "ArchiMate 3.2 Specification", "ArchiMate modeling language specification"),
        ("it4it", "IT4IT Reference Architecture", "IT value chain reference architecture"),
        ("iso_42010", "ISO/IEC/IEEE 42010:2022", "Systems and software engineering — Architecture description"),
        ("pci_dss_4", "PCI DSS v4.0", "Payment Card Industry Data Security Standard"),
        ("sox", "SOX (Sarbanes-Oxley Act)", "Financial reporting and internal controls"),
        ("gdpr", "GDPR", "General Data Protection Regulation"),
        ("hipaa", "HIPAA", "Health Insurance Portability and Accountability Act"),
        ("basel_iii", "Basel III/IV", "Banking regulatory capital framework"),
        ("dora", "DORA", "Digital Operational Resilience Act"),
        ("nis2", "NIS2 Directive", "Network and Information Security Directive 2"),
        ("iso_27001", "ISO 27001:2022", "Information security management system"),
        ("nist_csf", "NIST Cybersecurity Framework 2.0", "Cybersecurity risk management framework"),
        ("cobit_2019", "COBIT 2019", "IT governance and management framework"),
        ("itil_4", "ITIL 4", "IT service management framework"),
        ("safe_6", "SAFe 6.0", "Scaled Agile Framework"),
        ("bian", "BIAN", "Banking Industry Architecture Network"),
        ("tmforum_oda", "TM Forum ODA", "Open Digital Architecture for telecom"),
        ("hl7_fhir", "HL7 FHIR R4", "Healthcare interoperability standard"),
    ]

    seeds = []
    for key, name, desc in standards:
        seeds.append(SeedConcept(
            id=f"standard_{key}", name=name, category=SeedCategory.STANDARD,
            description=desc, domain="standards", tags=["standard"],
        ))
    return seeds


# =====================================================================
# Capabilities, Building Blocks, Stakeholders
# =====================================================================

def _capability_seeds() -> list[SeedConcept]:
    """Business capabilities across industries."""
    capabilities = [
        # Banking
        ("payment_processing", "Payment Processing", "banking"), ("customer_onboarding", "Customer Onboarding", "banking"),
        ("loan_origination", "Loan Origination", "banking"), ("risk_management_banking", "Financial Risk Management", "banking"),
        ("fraud_detection", "Fraud Detection", "banking"), ("regulatory_compliance_banking", "Regulatory Compliance", "banking"),
        ("credit_decisioning", "Credit Decisioning", "banking"), ("treasury_management", "Treasury Management", "banking"),
        # Healthcare
        ("patient_registration", "Patient Registration", "healthcare"), ("clinical_documentation", "Clinical Documentation", "healthcare"),
        ("medication_management", "Medication Management", "healthcare"), ("medical_billing", "Medical Billing", "healthcare"),
        # Telecom
        ("network_planning", "Network Planning", "telecom"), ("service_provisioning", "Service Provisioning", "telecom"),
        ("billing_rating", "Billing and Rating", "telecom"), ("network_monitoring", "Network Monitoring", "telecom"),
        # Cross-industry
        ("identity_access_mgmt", "Identity and Access Management", "cross_industry"), ("data_governance", "Data Governance", "cross_industry"),
        ("api_management", "API Management", "cross_industry"), ("master_data_mgmt", "Master Data Management", "cross_industry"),
        ("analytics_bi", "Analytics and BI", "cross_industry"), ("workflow_automation", "Workflow Automation", "cross_industry"),
    ]

    seeds = []
    for key, name, domain in capabilities:
        seeds.append(SeedConcept(
            id=f"cap_{key}", name=name, category=SeedCategory.CAPABILITY,
            description=f"Business capability: {name}", domain=domain, tags=["capability", domain],
        ))
    return seeds


def _building_block_seeds() -> list[SeedConcept]:
    """ABB and SBB seeds."""
    blocks = [
        # ABBs
        ("abb_api_gateway", "API Gateway ABB", "abb"), ("abb_message_broker", "Message Broker ABB", "abb"),
        ("abb_identity_provider", "Identity Provider ABB", "abb"), ("abb_data_store", "Data Store ABB", "abb"),
        ("abb_event_bus", "Event Bus ABB", "abb"), ("abb_service_mesh", "Service Mesh ABB", "abb"),
        ("abb_etl_pipeline", "ETL/ELT Pipeline ABB", "abb"), ("abb_monitoring", "Observability ABB", "abb"),
        ("abb_cache_layer", "Cache Layer ABB", "abb"), ("abb_container_platform", "Container Platform ABB", "abb"),
        ("abb_ci_cd", "CI/CD Pipeline ABB", "abb"), ("abb_secret_mgmt", "Secret Management ABB", "abb"),
        # SBBs
        ("sbb_kong", "Kong API Gateway", "sbb"), ("sbb_kafka", "Apache Kafka", "sbb"),
        ("sbb_keycloak", "Keycloak", "sbb"), ("sbb_postgresql", "PostgreSQL", "sbb"),
        ("sbb_elasticsearch", "Elasticsearch", "sbb"), ("sbb_kubernetes", "Kubernetes", "sbb"),
        ("sbb_istio", "Istio Service Mesh", "sbb"), ("sbb_prometheus", "Prometheus/Grafana", "sbb"),
        ("sbb_vault", "HashiCorp Vault", "sbb"), ("sbb_terraform", "Terraform", "sbb"),
    ]

    seeds = []
    for key, name, bb_type in blocks:
        seeds.append(SeedConcept(
            id=f"bb_{key}", name=name, category=SeedCategory.BUILDING_BLOCK,
            description=f"{'Architecture' if bb_type == 'abb' else 'Solution'} Building Block: {name}",
            domain="architecture", tags=["building_block", bb_type],
        ))
    return seeds


def _stakeholder_seeds() -> list[SeedConcept]:
    """Stakeholder roles per TOGAF."""
    stakeholders = [
        # Per TOGAF stakeholder taxonomy
        ("ceo", "CEO", "executive"), ("cto", "CTO", "executive"), ("cio", "CIO", "executive"),
        ("cfo", "CFO", "executive"), ("ciso", "CISO", "executive"), ("cdo", "CDO", "executive"),
        ("chief_architect", "Chief Enterprise Architect", "architecture"),
        ("business_arch", "Business Domain Architect", "architecture"),
        ("data_arch", "Data Architect", "architecture"),
        ("app_arch", "Application Architect", "architecture"),
        ("tech_arch", "Technology/Infrastructure Architect", "architecture"),
        ("solution_arch", "Solution Architect", "architecture"),
        ("security_arch", "Security Architect", "architecture"),
        ("product_manager", "Product Manager", "business"),
        ("business_analyst", "Business Analyst", "business"),
        ("process_owner", "Business Process Owner", "business"),
        ("head_of_compliance", "Head of Compliance", "business"),
        ("dev_lead", "Development Team Lead", "technical"),
        ("sre", "Site Reliability Engineer", "technical"),
        ("arch_board_chair", "Architecture Board Chair", "governance"),
        ("program_manager", "Program Manager", "governance"),
        ("regulator", "Regulatory Authority", "external"),
        ("external_auditor", "External Auditor", "external"),
    ]

    seeds = []
    for key, name, role_type in stakeholders:
        seeds.append(SeedConcept(
            id=f"stakeholder_{key}", name=name, category=SeedCategory.STAKEHOLDER,
            description=f"Stakeholder: {name}", domain=role_type, tags=["stakeholder", role_type],
        ))
    return seeds


# =====================================================================
# BIAN Service Landscape — banking industry reference architecture
# Based on BIAN Service Landscape v12
# =====================================================================

def _bian_service_domain_seeds() -> list[SeedConcept]:
    """BIAN service domains — banking industry reference architecture."""
    # Representative set from BIAN Service Landscape v12 across all business areas
    domains = [
        # Customer Management
        ("party_reference_data", "Party Reference Data Directory", "customer_management",
         "Maintain a directory of party reference information (individuals, organizations) used across services"),
        ("customer_relationship", "Customer Relationship Management", "customer_management",
         "Manage the relationship with customers including lifecycle, preferences, and engagement history"),
        ("customer_offer", "Customer Offer", "customer_management",
         "Manage the presentation and negotiation of product/service offers to customers"),
        ("customer_onboarding", "Customer Onboarding", "customer_management",
         "Orchestrate the activities involved in enrolling a new customer"),
        ("customer_profile", "Customer Profile", "customer_management",
         "Maintain consolidated customer profile data aggregating behavior and preferences"),
        ("customer_access_entitlement", "Customer Access Entitlement", "customer_management",
         "Manage customer authentication and access entitlements across channels"),
        ("customer_agreement", "Customer Agreement", "customer_management",
         "Maintain customer agreements covering products, terms, and conditions"),
        ("customer_case_management", "Customer Case Management", "customer_management",
         "Track and resolve customer cases, complaints, and service requests"),
        ("customer_campaign_mgmt", "Customer Campaign Management", "customer_management",
         "Design, execute, and track marketing campaigns targeting customer segments"),
        ("customer_behavioral_insights", "Customer Behavioral Insights", "customer_management",
         "Develop behavioral analysis and insights from customer activity patterns"),

        # Sales & Service
        ("sales_product_agreement", "Sales Product Agreement", "sales_service",
         "Manage product agreements as part of the sales process"),
        ("servicing_mandate", "Servicing Mandate", "sales_service",
         "Maintain servicing mandates defining the scope and constraints of customer servicing"),
        ("customer_servicing", "Customer Servicing", "sales_service",
         "Orchestrate customer service delivery across products and channels"),
        ("contact_center_mgmt", "Contact Center Management", "sales_service",
         "Manage contact center operations including routing, queuing, and workforce scheduling"),
        ("branch_network_mgmt", "Branch/Location Management", "sales_service",
         "Manage physical branch network operations and logistics"),

        # Products — Deposits & Lending
        ("current_account", "Current Account", "products",
         "Fulfill current/checking account facilities covering payments, balances, and statements"),
        ("savings_account", "Savings Account", "products",
         "Fulfill savings account facilities including interest calculations and withdrawal rules"),
        ("deposit_account", "Deposit Account", "products",
         "Fulfill term deposit and fixed deposit facilities"),
        ("loan", "Loan", "products",
         "Fulfill loan product facilities including disbursement, repayment, and interest management"),
        ("mortgage", "Mortgage", "products",
         "Fulfill mortgage product facilities covering property-secured lending"),
        ("credit_facility", "Credit Facility", "products",
         "Manage credit facility offerings including revolving credit and overdraft"),
        ("credit_card", "Credit Card", "products",
         "Fulfill credit card facilities including transactions, billing, and rewards"),
        ("leasing", "Leasing", "products",
         "Fulfill leasing arrangements for assets (vehicles, equipment)"),

        # Products — Investment & Treasury
        ("investment_portfolio", "Investment Portfolio Management", "products",
         "Manage investment portfolios including asset allocation and rebalancing"),
        ("securities_trading", "Securities Trading", "products",
         "Execute securities trading across equities, bonds, and derivatives"),
        ("market_making", "Market Making", "products",
         "Provide market making services maintaining bid/ask quotes"),
        ("treasury", "Treasury Management", "products",
         "Manage treasury operations including liquidity, funding, and ALM"),
        ("custody_services", "Custody Services", "products",
         "Provide custody and safekeeping of securities and assets"),
        ("wealth_management", "Wealth Management", "products",
         "Deliver wealth management advisory and portfolio services"),
        ("fund_management", "Fund Management", "products",
         "Manage investment fund operations including NAV calculation and distribution"),

        # Payments
        ("payment_initiation", "Payment Initiation", "payments",
         "Initiate payment transactions across domestic and international schemes"),
        ("payment_execution", "Payment Execution", "payments",
         "Execute and settle payment transactions through clearing networks"),
        ("payment_order", "Payment Order", "payments",
         "Process payment orders including validation, routing, and confirmation"),
        ("card_transaction_switch", "Card Transaction Switch", "payments",
         "Route and switch card transactions between acquirers and issuers"),
        ("correspondent_banking", "Correspondent Banking", "payments",
         "Manage correspondent banking relationships and nostro/vostro accounts"),
        ("direct_debit", "Direct Debit", "payments",
         "Process direct debit mandates and collections"),

        # Risk & Compliance
        ("credit_risk_assessment", "Credit Risk Assessment", "risk_compliance",
         "Assess credit risk for counterparties and exposures"),
        ("market_risk", "Market Risk", "risk_compliance",
         "Measure and monitor market risk (VaR, stress testing, sensitivity)"),
        ("operational_risk", "Operational Risk", "risk_compliance",
         "Identify, assess, and monitor operational risk events and controls"),
        ("fraud_detection", "Fraud Detection", "risk_compliance",
         "Detect and investigate fraudulent activities using pattern analysis"),
        ("aml_kyc", "AML/KYC", "risk_compliance",
         "Perform anti-money-laundering checks and know-your-customer due diligence"),
        ("regulatory_compliance", "Regulatory Compliance", "risk_compliance",
         "Monitor and ensure compliance with regulatory requirements"),
        ("regulatory_reporting", "Regulatory Reporting", "risk_compliance",
         "Generate and submit regulatory reports (Basel, IFRS, local regulations)"),
        ("counterparty_risk", "Counterparty Risk", "risk_compliance",
         "Assess and monitor counterparty credit and settlement risk"),

        # Operations & Technology
        ("transaction_engine", "Transaction Engine", "operations",
         "Core transaction processing engine for booking and posting"),
        ("general_ledger", "General Ledger", "operations",
         "Maintain the general ledger and chart of accounts"),
        ("financial_accounting", "Financial Accounting", "operations",
         "Manage financial accounting, reporting, and reconciliation"),
        ("reconciliation", "Reconciliation", "operations",
         "Perform automated reconciliation of transactions across systems"),
        ("document_management", "Document Management", "operations",
         "Manage documents, content, and digital records across the enterprise"),
        ("data_management", "Enterprise Data Management", "operations",
         "Govern enterprise data quality, lineage, and master data"),
        ("it_operations", "IT Operations Administration", "operations",
         "Manage IT infrastructure operations, monitoring, and incident response"),
        ("system_administration", "System Administration", "operations",
         "Administer core banking systems and middleware"),
        ("business_continuity", "Business Continuity Management", "operations",
         "Plan and manage business continuity and disaster recovery"),

        # Corporate Services
        ("trade_finance", "Trade Finance", "corporate",
         "Fulfill trade finance instruments (letters of credit, guarantees, documentary collections)"),
        ("corporate_lending", "Corporate Lending", "corporate",
         "Manage corporate and syndicated lending facilities"),
        ("cash_management", "Cash Management", "corporate",
         "Provide corporate cash management including pooling and sweeping"),
        ("supply_chain_finance", "Supply Chain Finance", "corporate",
         "Facilitate supply chain financing (factoring, reverse factoring)"),
    ]

    seeds = []
    for key, name, area, desc in domains:
        seeds.append(SeedConcept(
            id=f"bian_{key}", name=f"BIAN: {name}",
            category=SeedCategory.BIAN_SERVICE_DOMAIN,
            description=desc, domain="banking",
            tags=["bian", "banking", area, "service_domain"],
            metadata={"bian_business_area": area, "reference": "BIAN Service Landscape v12"},
        ))
    return seeds


# =====================================================================
# TMForum Open Digital Architecture — telco/digital industry
# Based on TMForum ODA Functional Architecture v5
# =====================================================================

def _tmforum_oda_seeds() -> list[SeedConcept]:
    """TMForum Open Digital Architecture functional blocks."""
    blocks = [
        # Core Commerce Management
        ("party_mgmt", "Party Management", "core_commerce",
         "Manage parties (individuals, organizations) and their roles across the enterprise"),
        ("product_catalog", "Product Catalog Management", "core_commerce",
         "Design, manage, and publish product and service catalogs"),
        ("product_ordering", "Product Ordering", "core_commerce",
         "Capture, validate, and orchestrate product orders through fulfillment"),
        ("product_inventory", "Product Inventory", "core_commerce",
         "Track and manage the inventory of active product instances"),
        ("customer_mgmt", "Customer Management", "core_commerce",
         "Manage customer lifecycle, profiles, and interaction history"),
        ("customer_bill_mgmt", "Customer Bill Management", "core_commerce",
         "Generate, present, and manage customer billing and invoicing"),
        ("revenue_mgmt", "Revenue Management", "core_commerce",
         "Rate usage, apply charges, manage revenue assurance and settlements"),
        ("loyalty_mgmt", "Loyalty Management", "core_commerce",
         "Manage loyalty programs, points, tiers, and rewards"),
        ("partner_mgmt", "Partner Management", "core_commerce",
         "Manage partner relationships, agreements, and settlement"),
        ("sales_mgmt", "Sales Management", "core_commerce",
         "Manage sales pipeline, opportunities, and quoting processes"),
        ("agreement_mgmt", "Agreement Management", "core_commerce",
         "Manage commercial agreements, SLAs, and contractual terms"),
        ("payment_mgmt", "Payment Management", "core_commerce",
         "Process payments, refunds, and manage payment methods"),

        # Production
        ("service_catalog", "Service Catalog Management", "production",
         "Design and manage the service catalog including technical service specifications"),
        ("service_ordering", "Service Ordering", "production",
         "Decompose and orchestrate service orders into resource actions"),
        ("service_inventory", "Service Inventory", "production",
         "Maintain inventory of active service instances and configurations"),
        ("service_activation", "Service Activation & Configuration", "production",
         "Activate, configure, and modify services on the network"),
        ("service_quality", "Service Quality Management", "production",
         "Monitor and manage service quality and performance levels"),
        ("service_test", "Service Test Management", "production",
         "Plan and execute service tests to validate quality and functionality"),
        ("resource_catalog", "Resource Catalog", "production",
         "Manage the catalog of physical and logical resources"),
        ("resource_ordering", "Resource Ordering", "production",
         "Orchestrate resource provisioning and configuration orders"),
        ("resource_inventory", "Resource Inventory", "production",
         "Maintain inventory of physical and logical network resources"),
        ("resource_activation", "Resource Activation", "production",
         "Activate and configure network resources"),
        ("network_planning", "Network Planning & Design", "production",
         "Plan, design, and optimize network topology and capacity"),

        # Engagement Management
        ("digital_experience", "Digital Experience Management", "engagement",
         "Manage digital customer journeys across web, mobile, and IoT channels"),
        ("contact_mgmt", "Contact Management", "engagement",
         "Manage customer contacts and interactions across all touchpoints"),
        ("trouble_ticket", "Trouble Ticket Management", "engagement",
         "Create, track, and resolve trouble tickets and service problems"),
        ("sla_mgmt", "SLA Management", "engagement",
         "Define, monitor, and report on service level agreements"),

        # Intelligence Management
        ("analytics", "Analytics", "intelligence",
         "Provide advanced analytics, predictive models, and AI/ML capabilities"),
        ("data_governance", "Data Governance", "intelligence",
         "Govern data quality, metadata, lineage, and data catalogs"),
        ("reporting", "Reporting & Dashboards", "intelligence",
         "Generate operational and business intelligence reports and dashboards"),

        # Security & Governance
        ("identity_access", "Identity & Access Management", "security",
         "Manage identities, authentication, authorization, and access policies"),
        ("fraud_mgmt", "Fraud Management", "security",
         "Detect, investigate, and prevent fraud across services"),
        ("privacy_mgmt", "Privacy Management", "security",
         "Manage data privacy policies, consent, and regulatory compliance"),
        ("policy_mgmt", "Policy Management", "security",
         "Define and enforce business and technical policies"),

        # Decoupling & Integration
        ("event_mgmt", "Event Management", "integration",
         "Manage business events, notifications, and event-driven architectures"),
        ("api_mgmt", "API Management", "integration",
         "Manage API lifecycle, gateway, and developer portal"),
        ("integration_fabric", "Integration Fabric", "integration",
         "Provide enterprise integration middleware and message routing"),

        # Enterprise Management
        ("strategic_planning", "Strategic Planning", "enterprise",
         "Support strategic planning, business modeling, and portfolio management"),
        ("program_project_mgmt", "Program & Project Management", "enterprise",
         "Manage programs, projects, and transformation initiatives"),
        ("enterprise_risk", "Enterprise Risk Management", "enterprise",
         "Identify, assess, and manage enterprise-wide risks"),
        ("regulatory_mgmt", "Regulatory Management", "enterprise",
         "Track regulatory requirements and ensure compliance"),
        ("workforce_mgmt", "Workforce Management", "enterprise",
         "Manage workforce planning, scheduling, and skills"),
        ("financial_mgmt", "Financial Management", "enterprise",
         "Manage financial planning, budgeting, and accounting"),
        ("procurement_mgmt", "Procurement & Supply Chain", "enterprise",
         "Manage procurement, vendors, and supply chain"),
    ]

    seeds = []
    for key, name, area, desc in blocks:
        seeds.append(SeedConcept(
            id=f"tmf_{key}", name=f"TMForum ODA: {name}",
            category=SeedCategory.TMFORUM_FUNCTIONAL_BLOCK,
            description=desc, domain="telecom",
            tags=["tmforum", "oda", "telecom", area, "functional_block"],
            metadata={"oda_area": area, "reference": "TMForum ODA Functional Architecture v5"},
        ))
    return seeds


# =====================================================================
# Technology Building Blocks — real platform/infrastructure components
# =====================================================================

def _technology_building_block_seeds() -> list[SeedConcept]:
    """Concrete technology stacks as architectural building blocks."""
    tech_blocks = [
        # Container & Orchestration
        ("k8s_cluster", "Kubernetes Cluster", "container_orchestration",
         "Container orchestration platform for automated deployment, scaling, and management of containerized workloads",
         {"vendor": "CNCF", "category": "orchestration"}),
        ("k8s_namespace", "Kubernetes Namespace", "container_orchestration",
         "Logical isolation boundary within a Kubernetes cluster for multi-tenancy and resource quotas",
         {"vendor": "CNCF", "category": "orchestration"}),
        ("k8s_ingress", "Kubernetes Ingress Controller", "container_orchestration",
         "API gateway and L7 load balancer for routing external traffic to cluster services",
         {"vendor": "CNCF", "category": "networking"}),
        ("k8s_service_mesh", "Service Mesh (Istio/Linkerd)", "container_orchestration",
         "Infrastructure layer for service-to-service communication with mTLS, observability, and traffic management",
         {"vendor": "CNCF", "category": "networking"}),
        ("helm_charts", "Helm Charts", "container_orchestration",
         "Package manager for Kubernetes enabling templated, versioned application deployments",
         {"vendor": "CNCF", "category": "packaging"}),
        ("docker_registry", "Container Registry", "container_orchestration",
         "OCI-compliant container image registry for storing and distributing container images",
         {"vendor": "various", "category": "registry"}),

        # Messaging & Streaming
        ("kafka_cluster", "Apache Kafka Cluster", "messaging",
         "Distributed event streaming platform for high-throughput, fault-tolerant publish-subscribe messaging",
         {"vendor": "Apache", "category": "streaming"}),
        ("kafka_connect", "Kafka Connect", "messaging",
         "Framework for connecting Kafka with external systems via source and sink connectors",
         {"vendor": "Apache", "category": "integration"}),
        ("kafka_schema_registry", "Schema Registry", "messaging",
         "Centralized schema management for Kafka topics enabling schema evolution and compatibility",
         {"vendor": "Confluent", "category": "governance"}),
        ("rabbitmq", "RabbitMQ", "messaging",
         "Message broker implementing AMQP for reliable message queuing with routing and delivery guarantees",
         {"vendor": "VMware", "category": "messaging"}),
        ("pulsar", "Apache Pulsar", "messaging",
         "Cloud-native distributed messaging and streaming platform with multi-tenancy and geo-replication",
         {"vendor": "Apache", "category": "streaming"}),

        # Databases & Storage
        ("postgresql", "PostgreSQL", "data_storage",
         "Advanced open-source relational database with extensibility, JSONB support, and ACID compliance",
         {"vendor": "PostgreSQL Global Development Group", "category": "rdbms"}),
        ("mongodb", "MongoDB", "data_storage",
         "Document-oriented NoSQL database for flexible schema storage with horizontal scaling",
         {"vendor": "MongoDB Inc.", "category": "document_db"}),
        ("redis", "Redis", "data_storage",
         "In-memory data structure store used as cache, message broker, and real-time data platform",
         {"vendor": "Redis Ltd.", "category": "cache"}),
        ("elasticsearch", "Elasticsearch", "data_storage",
         "Distributed search and analytics engine for log analytics, full-text search, and observability",
         {"vendor": "Elastic", "category": "search"}),
        ("cassandra", "Apache Cassandra", "data_storage",
         "Wide-column distributed database for high-availability, high-write-throughput workloads",
         {"vendor": "Apache", "category": "wide_column"}),
        ("snowflake", "Snowflake", "data_storage",
         "Cloud data warehouse with separation of storage and compute, supporting structured and semi-structured data",
         {"vendor": "Snowflake", "category": "data_warehouse"}),
        ("s3_object_store", "Object Storage (S3-compatible)", "data_storage",
         "Scalable object storage for unstructured data with lifecycle policies and versioning",
         {"vendor": "AWS/MinIO", "category": "object_storage"}),

        # ERP & Business Platforms
        ("sap_s4hana", "SAP S/4HANA", "erp",
         "In-memory ERP suite covering finance, supply chain, manufacturing, and asset management on HANA database",
         {"vendor": "SAP", "category": "erp"}),
        ("sap_btp", "SAP Business Technology Platform", "erp",
         "PaaS for extending SAP with integration, analytics, AI, and custom development",
         {"vendor": "SAP", "category": "platform"}),
        ("sap_integration_suite", "SAP Integration Suite", "erp",
         "iPaaS for integrating SAP and non-SAP systems via APIs, events, and process orchestration",
         {"vendor": "SAP", "category": "integration"}),
        ("salesforce_core", "Salesforce CRM Platform", "crm",
         "Cloud CRM platform covering sales, service, and marketing automation with extensible data model",
         {"vendor": "Salesforce", "category": "crm"}),
        ("salesforce_mulesoft", "MuleSoft Anypoint Platform", "crm",
         "API-led connectivity platform for integrating SaaS, on-prem, and legacy systems",
         {"vendor": "Salesforce/MuleSoft", "category": "integration"}),
        ("salesforce_tableau", "Tableau", "crm",
         "Visual analytics platform for self-service BI, data exploration, and dashboard publishing",
         {"vendor": "Salesforce/Tableau", "category": "analytics"}),
        ("servicenow", "ServiceNow", "itsm",
         "Cloud platform for IT service management, IT operations, and enterprise workflow automation",
         {"vendor": "ServiceNow", "category": "itsm"}),

        # Observability & DevOps
        ("prometheus", "Prometheus", "observability",
         "Time-series monitoring system with PromQL query language and alerting for cloud-native workloads",
         {"vendor": "CNCF", "category": "monitoring"}),
        ("grafana", "Grafana", "observability",
         "Observability platform for metrics visualization, log exploration, and distributed tracing dashboards",
         {"vendor": "Grafana Labs", "category": "visualization"}),
        ("opentelemetry", "OpenTelemetry", "observability",
         "Vendor-neutral observability framework for collecting traces, metrics, and logs",
         {"vendor": "CNCF", "category": "instrumentation"}),
        ("argocd", "ArgoCD", "devops",
         "GitOps continuous delivery tool for Kubernetes, declaratively managing application deployments",
         {"vendor": "CNCF", "category": "gitops"}),
        ("terraform", "Terraform", "devops",
         "Infrastructure as Code tool for provisioning and managing cloud resources declaratively",
         {"vendor": "HashiCorp", "category": "iac"}),
        ("vault", "HashiCorp Vault", "devops",
         "Secrets management and encryption service for dynamic secrets, PKI, and data encryption",
         {"vendor": "HashiCorp", "category": "security"}),
        ("github_actions", "GitHub Actions", "devops",
         "CI/CD automation platform integrated with GitHub for building, testing, and deploying code",
         {"vendor": "GitHub", "category": "ci_cd"}),

        # Cloud Infrastructure
        ("aws_vpc", "AWS VPC / Azure VNet", "cloud",
         "Virtual private network isolation boundary in public cloud with subnets, routing, and security groups",
         {"vendor": "AWS/Azure", "category": "networking"}),
        ("aws_lambda", "Serverless Functions (Lambda/Azure Functions)", "cloud",
         "Event-driven serverless compute for running code without provisioning servers",
         {"vendor": "AWS/Azure", "category": "compute"}),
        ("cdn", "CDN (CloudFront/Akamai)", "cloud",
         "Content delivery network for low-latency global distribution of static and dynamic content",
         {"vendor": "various", "category": "edge"}),
        ("api_gateway", "API Gateway (Kong/AWS API GW)", "cloud",
         "Managed API gateway for rate limiting, authentication, and request routing",
         {"vendor": "various", "category": "api_management"}),

        # Data & AI
        ("spark", "Apache Spark", "data_ai",
         "Unified analytics engine for large-scale data processing, batch and streaming, with ML support",
         {"vendor": "Apache", "category": "processing"}),
        ("airflow", "Apache Airflow", "data_ai",
         "Workflow orchestration platform for authoring, scheduling, and monitoring data pipelines",
         {"vendor": "Apache", "category": "orchestration"}),
        ("mlflow", "MLflow", "data_ai",
         "ML lifecycle management platform for experiment tracking, model registry, and deployment",
         {"vendor": "Databricks", "category": "mlops"}),
        ("feature_store", "Feature Store (Feast/Tecton)", "data_ai",
         "Centralized feature management for ML pipelines supporting online and offline serving",
         {"vendor": "various", "category": "ml_infra"}),
    ]

    seeds = []
    for key, name, area, desc, meta in tech_blocks:
        meta["technology_area"] = area
        seeds.append(SeedConcept(
            id=f"tech_{key}", name=name,
            category=SeedCategory.TECHNOLOGY_BUILDING_BLOCK,
            description=desc, domain="technology",
            tags=["technology", area, meta.get("category", ""), "building_block"],
            metadata=meta,
        ))
    return seeds


# =====================================================================
# Team Topologies — organizational patterns
# Based on Team Topologies by Skelton & Pais
# =====================================================================

def _team_topology_seeds() -> list[SeedConcept]:
    """Team Topologies organizational patterns."""
    topologies = [
        # Four fundamental team types
        ("stream_aligned", "Stream-Aligned Team", "team_type",
         "Team aligned to a single flow of work from a segment of the business domain, "
         "empowered to build and deliver customer value as quickly and independently as possible",
         {"interaction_modes": ["collaboration", "x-as-a-service", "facilitating"],
          "characteristics": ["cross-functional", "long-lived", "owns end-to-end delivery"],
          "cognitive_load": "bounded by domain complexity"}),
        ("enabling", "Enabling Team", "team_type",
         "Team that assists stream-aligned teams in overcoming obstacles by detecting missing capabilities "
         "and helping to close skill gaps, typically around specific technical or product management areas",
         {"interaction_modes": ["facilitating"],
          "characteristics": ["specialists", "temporary engagement", "knowledge transfer focus"],
          "cognitive_load": "focused on capability uplift"}),
        ("complicated_subsystem", "Complicated-Subsystem Team", "team_type",
         "Team responsible for building and maintaining a subsystem that requires specialist knowledge "
         "beyond that of most stream-aligned teams (e.g., mathematical models, real-time processing)",
         {"interaction_modes": ["x-as-a-service"],
          "characteristics": ["deep specialists", "reduces cognitive load on consumers"],
          "cognitive_load": "high intrinsic complexity, shielded from others"}),
        ("platform", "Platform Team", "team_type",
         "Team that provides internal services to reduce cognitive load on stream-aligned teams, "
         "offering self-service APIs, tools, and reliable infrastructure as a product",
         {"interaction_modes": ["x-as-a-service"],
          "characteristics": ["treats platform as product", "self-service", "reduces stream team burden"],
          "cognitive_load": "abstracts infrastructure complexity"}),

        # Three interaction modes
        ("mode_collaboration", "Collaboration Interaction Mode", "interaction_mode",
         "Two teams work closely together for a defined period to discover new patterns, approaches, or practices. "
         "High-bandwidth but high-cost; should be time-boxed",
         {"suitable_for": ["new technology adoption", "exploring new domain boundaries"],
          "anti_pattern": "permanent collaboration indicates poor boundaries"}),
        ("mode_x_as_a_service", "X-as-a-Service Interaction Mode", "interaction_mode",
         "One team provides something (API, tool, platform) as a service with clear interface and SLA. "
         "Minimal collaboration needed; consumer team has autonomy",
         {"suitable_for": ["well-defined interfaces", "platform consumption", "stable subsystems"],
          "anti_pattern": "forcing x-as-a-service on immature boundaries"}),
        ("mode_facilitating", "Facilitating Interaction Mode", "interaction_mode",
         "One team helps another team learn or adopt new skills/approaches. "
         "The enabling team does not build the thing; it coaches the stream-aligned team",
         {"suitable_for": ["capability gaps", "new practice adoption", "tooling migration"],
          "anti_pattern": "enabling team permanently doing work for the other team"}),

        # Organizational sensing patterns
        ("conways_law", "Conway's Law", "organizational_pattern",
         "Organizations produce designs which are copies of their communication structures. "
         "Inverse Conway Maneuver: deliberately shape team structures to encourage desired architecture",
         {"principle": "architecture follows communication pathways",
          "application": "use to align team boundaries with architectural boundaries"}),
        ("cognitive_load", "Cognitive Load Management", "organizational_pattern",
         "Limit the cognitive load on teams to what they can effectively handle. "
         "Three types: intrinsic (domain), extraneous (environment), germane (learning)",
         {"types": ["intrinsic", "extraneous", "germane"],
          "principle": "minimize extraneous load, manage intrinsic load, maximize germane load"}),
        ("fracture_planes", "Fracture Planes", "organizational_pattern",
         "Natural lines along which to split software and teams: business domain, regulatory compliance, "
         "change cadence, team location, technology, user personas, risk",
         {"planes": ["business_domain", "regulatory", "change_cadence", "location",
                     "technology", "user_persona", "risk", "performance_isolation"],
          "principle": "split where natural seams exist to reduce coupling"}),
    ]

    seeds = []
    for key, name, pattern_type, desc, meta in topologies:
        meta["pattern_type"] = pattern_type
        meta["reference"] = "Team Topologies (Skelton & Pais, 2019)"
        seeds.append(SeedConcept(
            id=f"topo_{key}", name=name,
            category=SeedCategory.TEAM_TOPOLOGY,
            description=desc, domain="organizational",
            tags=["team_topologies", pattern_type, "organizational"],
            metadata=meta,
        ))
    return seeds


# =====================================================================
# Security Architecture Seeds
# =====================================================================

def _security_architecture_seeds() -> list[SeedConcept]:
    """Security architecture concepts and patterns."""
    items = [
        ("zero_trust", "Zero Trust Architecture",
         "Security model eliminating implicit trust — every access request is verified regardless of network location. "
         "Principles: verify explicitly, least-privilege access, assume breach.",
         {"framework": "NIST SP 800-207", "pattern": "zero_trust"}),
        ("identity_access_mgmt", "Identity & Access Management (IAM)",
         "Centralized framework for managing digital identities, authentication, authorization, and access governance. "
         "Covers SSO, MFA, RBAC, ABAC, and privileged access management.",
         {"framework": "ISO 27001", "pattern": "iam"}),
        ("security_by_design", "Security by Design",
         "Architectural approach embedding security controls at every layer from inception — threat modeling, "
         "secure coding, defense in depth, and fail-safe defaults.",
         {"framework": "OWASP", "pattern": "secure_sdlc"}),
        ("data_protection_arch", "Data Protection Architecture",
         "Encryption at rest and in transit, tokenization, data masking, key management, and DLP controls "
         "to protect sensitive data across the enterprise.",
         {"framework": "GDPR/PCI-DSS", "pattern": "data_protection"}),
        ("soc_architecture", "Security Operations Center (SOC) Architecture",
         "Architecture for centralized security monitoring — SIEM integration, incident response workflows, "
         "threat intelligence feeds, and automated playbook execution.",
         {"framework": "NIST CSF", "pattern": "soc"}),
        ("api_security", "API Security Architecture",
         "Security patterns for API ecosystems — OAuth 2.0/OIDC, API key management, rate limiting, "
         "input validation, and API gateway security policies.",
         {"framework": "OWASP API Security Top 10", "pattern": "api_security"}),
        ("network_segmentation", "Network Segmentation & Micro-segmentation",
         "Architecture for isolating network zones — DMZ, internal segments, micro-segmentation with "
         "software-defined perimeters and east-west traffic controls.",
         {"framework": "CIS Controls", "pattern": "segmentation"}),
        ("devsecops", "DevSecOps Pipeline Architecture",
         "Integrating security testing into CI/CD — SAST, DAST, SCA, container scanning, "
         "secrets detection, and compliance-as-code in deployment pipelines.",
         {"framework": "OWASP DevSecOps", "pattern": "devsecops"}),
        ("cloud_security_arch", "Cloud Security Posture Management",
         "Architecture for securing cloud workloads — CSPM, CWPP, cloud-native firewalls, "
         "identity federation, and shared responsibility model implementation.",
         {"framework": "CSA CCM", "pattern": "cloud_security"}),
        ("privacy_arch", "Privacy-by-Design Architecture",
         "Architecture patterns implementing privacy principles — data minimization, purpose limitation, "
         "consent management, right to erasure, and privacy impact assessments.",
         {"framework": "GDPR Art. 25", "pattern": "privacy"}),
        ("threat_intelligence", "Threat Intelligence Platform Architecture",
         "Architecture for collecting, correlating, and operationalizing threat intelligence — "
         "STIX/TAXII feeds, IOC management, threat hunting workflows.",
         {"framework": "MITRE ATT&CK", "pattern": "threat_intel"}),
        ("cryptographic_arch", "Cryptographic Architecture",
         "Enterprise-wide cryptographic standards — algorithm selection, key lifecycle management, "
         "PKI, certificate management, post-quantum readiness assessment.",
         {"framework": "NIST SP 800-57", "pattern": "cryptography"}),
    ]
    seeds = []
    for key, name, desc, meta in items:
        seeds.append(SeedConcept(
            id=f"sec_{key}", name=name,
            category=SeedCategory.SECURITY_ARCHITECTURE,
            description=desc, domain="security",
            tags=["security", meta["pattern"], "architecture"],
            metadata=meta,
        ))
    return seeds


# =====================================================================
# Data Architecture Seeds
# =====================================================================

def _data_architecture_seeds() -> list[SeedConcept]:
    """Data architecture concepts and patterns."""
    items = [
        ("master_data_mgmt", "Master Data Management (MDM)",
         "Strategy and architecture for creating a single authoritative source of master data — "
         "golden records, data stewardship, match/merge logic, and cross-domain consistency.",
         {"pattern": "mdm", "scope": "enterprise"}),
        ("data_mesh", "Data Mesh Architecture",
         "Decentralized data architecture treating data as a product — domain ownership, "
         "self-serve data platform, federated computational governance, and data product thinking.",
         {"pattern": "data_mesh", "reference": "Dehghani 2022"}),
        ("data_lakehouse", "Data Lakehouse Architecture",
         "Unified architecture combining data lake flexibility with warehouse reliability — "
         "ACID transactions on data lakes, schema enforcement, and unified batch/streaming.",
         {"pattern": "lakehouse", "scope": "analytics"}),
        ("data_governance_framework", "Data Governance Framework",
         "Enterprise data governance architecture — data catalog, lineage tracking, quality rules, "
         "stewardship roles, policy enforcement, and metadata management.",
         {"pattern": "governance", "scope": "enterprise"}),
        ("event_sourcing_cqrs", "Event Sourcing & CQRS",
         "Architectural pattern storing state changes as immutable events — event store, projections, "
         "command/query separation, and eventual consistency handling.",
         {"pattern": "event_sourcing", "scope": "application"}),
        ("data_quality_arch", "Data Quality Architecture",
         "Architecture for continuous data quality management — profiling, cleansing, monitoring, "
         "DQ scorecards, anomaly detection, and remediation workflows.",
         {"pattern": "data_quality", "scope": "enterprise"}),
        ("real_time_analytics", "Real-Time Analytics Architecture",
         "Architecture for sub-second analytics — stream processing (Flink/Spark Streaming), "
         "materialized views, time-series databases, and dashboarding.",
         {"pattern": "streaming_analytics", "scope": "analytics"}),
        ("data_catalog_arch", "Enterprise Data Catalog Architecture",
         "Searchable inventory of enterprise data assets — automated discovery, business glossary, "
         "lineage visualization, and usage tracking.",
         {"pattern": "data_catalog", "scope": "enterprise"}),
        ("graph_data_arch", "Graph Data Architecture",
         "Architecture using graph databases for relationship-rich data — knowledge graphs, "
         "graph analytics, ontology management, and semantic querying.",
         {"pattern": "graph_data", "scope": "application"}),
        ("data_privacy_arch", "Data Privacy & Compliance Architecture",
         "Architecture implementing data privacy regulations — consent management, data subject access requests, "
         "anonymization, pseudonymization, and cross-border data transfer controls.",
         {"pattern": "data_privacy", "scope": "compliance"}),
    ]
    seeds = []
    for key, name, desc, meta in items:
        seeds.append(SeedConcept(
            id=f"data_{key}", name=name,
            category=SeedCategory.DATA_ARCHITECTURE,
            description=desc, domain="data",
            tags=["data_architecture", meta["pattern"], meta.get("scope", "")],
            metadata=meta,
        ))
    return seeds


# =====================================================================
# Integration Architecture Seeds
# =====================================================================

def _integration_architecture_seeds() -> list[SeedConcept]:
    """Integration and API architecture concepts."""
    items = [
        ("event_driven_arch", "Event-Driven Architecture (EDA)",
         "Architecture where components communicate through asynchronous events — event brokers, "
         "event schemas, choreography vs orchestration, and eventual consistency.",
         {"pattern": "eda", "scope": "enterprise"}),
        ("api_first_design", "API-First Design",
         "Architecture strategy where APIs are the primary interface — contract-first development, "
         "OpenAPI specifications, API versioning strategy, and developer experience.",
         {"pattern": "api_first", "scope": "enterprise"}),
        ("saga_pattern", "Saga Pattern for Distributed Transactions",
         "Pattern for managing distributed transactions without 2PC — choreography sagas, "
         "orchestration sagas, compensating transactions, and failure handling.",
         {"pattern": "saga", "scope": "microservices"}),
        ("api_gateway_pattern", "API Gateway & BFF Pattern",
         "Centralized API gateway for routing, composition, and cross-cutting concerns — "
         "Backend-for-Frontend (BFF), request aggregation, and protocol translation.",
         {"pattern": "api_gateway", "scope": "microservices"}),
        ("integration_hub", "Enterprise Integration Hub",
         "Centralized integration platform — ESB, iPaaS, canonical data model, "
         "message transformation, protocol mediation, and integration monitoring.",
         {"pattern": "integration_hub", "scope": "enterprise"}),
        ("webhook_arch", "Webhook & Callback Architecture",
         "Asynchronous notification architecture — webhook registration, delivery guarantees, "
         "retry logic, signature verification, and dead letter handling.",
         {"pattern": "webhook", "scope": "application"}),
        ("graphql_federation", "GraphQL Federation Architecture",
         "Federated API architecture with GraphQL — schema composition, subgraph services, "
         "query planning, and unified graph API across domains.",
         {"pattern": "graphql", "scope": "application"}),
        ("cdc_arch", "Change Data Capture Architecture",
         "Real-time data synchronization via transaction log capture — Debezium, "
         "outbox pattern, event publishing from databases, and consistency guarantees.",
         {"pattern": "cdc", "scope": "data_integration"}),
        ("service_mesh_arch", "Service Mesh Communication Architecture",
         "Infrastructure layer managing service-to-service communication — sidecar proxies, "
         "mTLS, traffic management, observability, and circuit breakers.",
         {"pattern": "service_mesh", "scope": "microservices"}),
        ("async_messaging", "Asynchronous Messaging Patterns",
         "Enterprise messaging patterns — request/reply, publish/subscribe, competing consumers, "
         "message deduplication, ordering guarantees, and dead letter queues.",
         {"pattern": "messaging", "scope": "enterprise"}),
        ("etl_elt_arch", "ETL/ELT Pipeline Architecture",
         "Data integration pipeline architecture — batch ETL, ELT with in-warehouse transforms, "
         "incremental loading, data validation, and orchestration.",
         {"pattern": "etl", "scope": "data_integration"}),
        ("contract_testing", "Contract Testing Architecture",
         "Architecture for API contract verification — consumer-driven contracts, Pact testing, "
         "schema compatibility checks, and breaking change detection.",
         {"pattern": "contract_testing", "scope": "testing"}),
    ]
    seeds = []
    for key, name, desc, meta in items:
        seeds.append(SeedConcept(
            id=f"integ_{key}", name=name,
            category=SeedCategory.INTEGRATION_ARCHITECTURE,
            description=desc, domain="integration",
            tags=["integration", meta["pattern"], meta.get("scope", "")],
            metadata=meta,
        ))
    return seeds


# =====================================================================
# Cloud Architecture Seeds
# =====================================================================

def _cloud_architecture_seeds() -> list[SeedConcept]:
    """Cloud and infrastructure architecture concepts."""
    items = [
        ("cloud_native_arch", "Cloud-Native Architecture",
         "Architecture designed for cloud from the ground up — 12-factor apps, containerization, "
         "microservices, CI/CD, infrastructure-as-code, and dynamic scaling.",
         {"pattern": "cloud_native", "reference": "CNCF"}),
        ("multi_cloud_strategy", "Multi-Cloud Architecture Strategy",
         "Architecture spanning multiple cloud providers — workload placement, cloud abstraction layers, "
         "vendor lock-in mitigation, and cost optimization across providers.",
         {"pattern": "multi_cloud", "scope": "strategy"}),
        ("hybrid_cloud_arch", "Hybrid Cloud Architecture",
         "Architecture bridging on-premises and cloud — workload distribution, network connectivity, "
         "data sovereignty, consistent operations, and identity federation.",
         {"pattern": "hybrid_cloud", "scope": "infrastructure"}),
        ("serverless_arch", "Serverless Architecture",
         "Event-driven compute without server management — FaaS, BaaS, cold starts, "
         "execution limits, state management, and serverless anti-patterns.",
         {"pattern": "serverless", "scope": "compute"}),
        ("resilience_chaos", "Resilience & Chaos Engineering",
         "Architecture for system resilience — circuit breakers, bulkheads, retry policies, "
         "chaos experiments, game days, and failure injection testing.",
         {"pattern": "resilience", "reference": "Netflix"}),
        ("iac_gitops", "Infrastructure-as-Code & GitOps",
         "Architecture managing infrastructure through version-controlled code — Terraform, "
         "Pulumi, ArgoCD, declarative configuration, and drift detection.",
         {"pattern": "iac", "scope": "operations"}),
        ("observability_arch", "Observability Architecture",
         "Architecture for system observability — distributed tracing, metrics, logs, "
         "OpenTelemetry, SLO/SLI definitions, and alerting pipelines.",
         {"pattern": "observability", "scope": "operations"}),
        ("edge_computing", "Edge Computing Architecture",
         "Architecture distributing compute to network edge — edge nodes, content caching, "
         "IoT gateways, latency optimization, and edge-cloud synchronization.",
         {"pattern": "edge", "scope": "infrastructure"}),
        ("disaster_recovery", "Disaster Recovery Architecture",
         "Architecture ensuring business continuity — RPO/RTO targets, active-active/active-passive, "
         "geo-redundancy, automated failover, and recovery testing.",
         {"pattern": "dr", "scope": "infrastructure"}),
        ("finops_arch", "FinOps & Cloud Cost Architecture",
         "Architecture for cloud financial management — cost allocation, rightsizing, reserved instances, "
         "spot/preemptible usage, showback/chargeback, and budget alerting.",
         {"pattern": "finops", "scope": "governance"}),
        ("container_orchestration", "Container Orchestration Architecture",
         "Architecture for managing containerized workloads at scale — pod scheduling, "
         "service discovery, rolling deployments, auto-scaling, and namespace isolation.",
         {"pattern": "container_orch", "scope": "platform"}),
        ("platform_engineering", "Platform Engineering Architecture",
         "Internal developer platform architecture — self-service portals, golden paths, "
         "service catalogs, developer experience, and platform team patterns.",
         {"pattern": "platform_eng", "reference": "Team Topologies"}),
    ]
    seeds = []
    for key, name, desc, meta in items:
        seeds.append(SeedConcept(
            id=f"cloud_{key}", name=name,
            category=SeedCategory.CLOUD_ARCHITECTURE,
            description=desc, domain="cloud_infrastructure",
            tags=["cloud", meta["pattern"], meta.get("scope", meta.get("reference", ""))],
            metadata=meta,
        ))
    return seeds


# =====================================================================
# Build complete pool
# =====================================================================

def build_seed_pool() -> list[SeedConcept]:
    """Builds the complete seed pool."""
    seeds = []
    seeds.extend(_togaf_phase_seeds())
    seeds.extend(_togaf_deliverable_seeds())
    seeds.extend(_togaf_artifact_seeds())
    seeds.extend(_togaf_metamodel_seeds())
    seeds.extend(_togaf_technique_seeds())
    seeds.extend(_togaf_viewpoint_seeds())
    seeds.extend(_archimate_element_seeds())
    seeds.extend(_archimate_relationship_seeds())
    seeds.extend(_archimate_viewpoint_seeds())
    seeds.extend(_industry_case_seeds())
    seeds.extend(_standard_seeds())
    seeds.extend(_capability_seeds())
    seeds.extend(_building_block_seeds())
    seeds.extend(_stakeholder_seeds())
    # Cross-domain reference architectures
    seeds.extend(_bian_service_domain_seeds())
    seeds.extend(_tmforum_oda_seeds())
    seeds.extend(_technology_building_block_seeds())
    seeds.extend(_team_topology_seeds())
    # Domain-specific architecture seeds
    seeds.extend(_security_architecture_seeds())
    seeds.extend(_data_architecture_seeds())
    seeds.extend(_integration_architecture_seeds())
    seeds.extend(_cloud_architecture_seeds())
    return seeds


def save_seed_pool(output_path: Path | None = None) -> tuple[Path, int]:
    """Builds and saves the seed pool. Returns (path, count)."""
    seeds = build_seed_pool()
    path = output_path or Path("pools/seeds/seed_pool.json")
    save_pool(seeds, path)
    return path, len(seeds)


if __name__ == "__main__":
    path, count = save_seed_pool()
    pool = build_seed_pool()
    by_category = {}
    for s in pool:
        cat = s.category.value
        by_category[cat] = by_category.get(cat, 0) + 1
    print(f"Seed pool saved to {path}: {count} seeds")
    for cat, n in sorted(by_category.items()):
        print(f"  {cat}: {n}")
