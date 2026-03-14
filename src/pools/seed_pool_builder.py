"""Builder for the TOGAF Seed Pool.

Generates ~2000 seed concepts across TOGAF phases, artifacts, techniques,
ArchiMate elements/viewpoints, industry cases, standards, capabilities,
building blocks, and stakeholders.
"""

from __future__ import annotations

from pathlib import Path

from .models import SeedConcept, SeedCategory, save_pool


def _togaf_phase_seeds() -> list[SeedConcept]:
    """ADM phase-specific seeds."""
    seeds = []
    phases = {
        "preliminary": ("Preliminary Phase", "Establishes architecture capability, principles, and governance framework"),
        "vision_A": ("Phase A: Architecture Vision", "Develops high-level aspirational vision and obtains approval"),
        "business_B": ("Phase B: Business Architecture", "Develops the Business Architecture to support the Architecture Vision"),
        "infosys_C": ("Phase C: Information Systems Architecture", "Develops Data and Application Architectures"),
        "tech_D": ("Phase D: Technology Architecture", "Develops the Technology Architecture"),
        "opportunities_E": ("Phase E: Opportunities and Solutions", "Generates initial implementation and migration plan"),
        "migration_F": ("Phase F: Migration Planning", "Finalizes detailed implementation and migration plan"),
        "governance_G": ("Phase G: Implementation Governance", "Provides architecture oversight of implementation"),
        "change_H": ("Phase H: Architecture Change Management", "Manages changes to the architecture"),
        "requirements": ("Requirements Management", "Manages architecture requirements throughout ADM"),
    }

    for key, (name, desc) in phases.items():
        seeds.append(SeedConcept(
            id=f"phase_{key}", name=name, category=SeedCategory.TOGAF_PHASE,
            description=desc, domain="adm",
            tags=["phase", key],
        ))

    # Sub-aspects of each phase
    phase_aspects = [
        ("B_business_process_modeling", "Phase B Business Process Modeling", "Modeling business processes for target architecture"),
        ("B_organization_modeling", "Phase B Organization Modeling", "Defining target organizational structures"),
        ("B_business_function_decomposition", "Phase B Business Function Decomposition", "Decomposing business functions to atomic level"),
        ("B_business_service_identification", "Phase B Business Service Identification", "Identifying business services from processes"),
        ("C_data_entity_modeling", "Phase C Data Entity Modeling", "Modeling logical data entities and relationships"),
        ("C_data_migration_planning", "Phase C Data Migration Planning", "Planning data migration between systems"),
        ("C_application_portfolio_rationalization", "Phase C Application Portfolio Rationalization", "Rationalizing the application landscape"),
        ("C_application_integration_design", "Phase C Application Integration Design", "Designing integration between applications"),
        ("D_platform_selection", "Phase D Platform Selection", "Selecting technology platforms for target architecture"),
        ("D_infrastructure_consolidation", "Phase D Infrastructure Consolidation", "Consolidating infrastructure components"),
        ("D_cloud_architecture_design", "Phase D Cloud Architecture Design", "Designing cloud-native technology architecture"),
        ("D_network_architecture_design", "Phase D Network Architecture Design", "Designing network topology and security zones"),
        ("E_consolidation_gaps", "Phase E Consolidation Gaps", "Consolidating gaps from all architecture domains"),
        ("E_work_package_identification", "Phase E Work Package Identification", "Identifying discrete work packages for migration"),
        ("E_transition_architecture_creation", "Phase E Transition Architecture Creation", "Creating intermediate transition architectures"),
        ("F_implementation_factor_assessment", "Phase F Implementation Factor Assessment", "Assessing factors affecting migration sequencing"),
        ("F_business_value_assessment", "Phase F Business Value Assessment", "Assessing business value of work packages"),
        ("F_migration_risk_assessment", "Phase F Migration Risk Assessment", "Assessing risks of migration approach"),
        ("G_compliance_review_setup", "Phase G Compliance Review Setup", "Setting up architecture compliance review process"),
        ("G_implementation_monitoring", "Phase G Implementation Monitoring", "Monitoring conformance during implementation"),
        ("H_change_impact_analysis", "Phase H Change Impact Analysis", "Analyzing impact of proposed architecture changes"),
        ("H_architecture_refresh_trigger", "Phase H Architecture Refresh Trigger", "Identifying triggers for architecture refresh cycles"),
    ]

    for key, name, desc in phase_aspects:
        seeds.append(SeedConcept(
            id=f"phase_aspect_{key}", name=name, category=SeedCategory.TOGAF_PHASE,
            description=desc, domain="adm",
            tags=["phase", "aspect"],
        ))

    return seeds


def _togaf_artifact_seeds() -> list[SeedConcept]:
    """TOGAF artifact-specific seeds."""
    artifacts = [
        # Catalogs
        ("principles_catalog", "Principles Catalog", "Catalog of architecture principles with rationale and implications"),
        ("stakeholder_map_catalog", "Stakeholder Map Catalog", "Catalog of stakeholders with power, interest, and concerns"),
        ("value_chain_diagram", "Value Chain Diagram", "Visual representation of enterprise value chain activities"),
        ("solution_concept_diagram", "Solution Concept Diagram", "High-level visual of proposed solution approach"),
        ("organization_decomposition", "Organization Decomposition Diagram", "Hierarchical view of organizational structure"),
        ("business_capability_map", "Business Capability Map", "Heat-mapped view of business capabilities"),
        ("business_interaction_matrix", "Business Interaction Matrix", "Matrix of interactions between business functions"),
        ("actor_role_matrix", "Actor/Role Matrix", "Mapping of actors to their roles"),
        ("business_footprint_diagram", "Business Footprint Diagram", "Mapping of business goals to organizational units"),
        ("business_service_info_diagram", "Business Service/Information Diagram", "Mapping between services and information"),
        ("functional_decomposition", "Functional Decomposition Diagram", "Hierarchical decomposition of functions"),
        ("product_lifecycle_diagram", "Product Lifecycle Diagram", "Lifecycle stages of products/services"),
        ("goal_objective_service", "Goal/Objective/Service Diagram", "Mapping goals to services"),

        # Data artifacts
        ("data_entity_relationship", "Data Entity/Relationship Diagram", "Logical data model with relationships"),
        ("data_dissemination_diagram", "Data Dissemination Diagram", "Data flow between systems"),
        ("data_lifecycle_diagram", "Data Lifecycle Diagram", "Lifecycle management of data entities"),
        ("data_security_diagram", "Data Security Diagram", "Data classification and security controls"),
        ("data_migration_diagram", "Data Migration Diagram", "Data migration approach and mapping"),
        ("conceptual_data_model", "Conceptual Data Model", "High-level data concepts and relationships"),
        ("logical_data_model", "Logical Data Model", "Detailed logical data structure"),
        ("data_quality_model", "Data Quality Model", "Data quality dimensions and metrics"),

        # Application artifacts
        ("application_portfolio_catalog", "Application Portfolio Catalog", "Inventory of enterprise applications"),
        ("application_interface_catalog", "Application/Interface Catalog", "Catalog of application interfaces"),
        ("application_communication_diagram", "Application Communication Diagram", "Inter-application communication flows"),
        ("application_migration_diagram", "Application Migration Diagram", "Application migration roadmap"),
        ("application_use_case_diagram", "Application Use Case Diagram", "Application use cases and actors"),
        ("software_distribution_diagram", "Software Distribution Diagram", "Software deployment topology"),
        ("process_application_realization", "Process/Application Realization Diagram", "How applications realize processes"),
        ("application_function_matrix", "Application/Function Matrix", "Mapping applications to business functions"),

        # Technology artifacts
        ("technology_standards_catalog", "Technology Standards Catalog", "Approved technology standards"),
        ("technology_portfolio_catalog", "Technology Portfolio Catalog", "Technology component inventory"),
        ("environments_locations_diagram", "Environments and Locations Diagram", "Physical and logical locations"),
        ("platform_decomposition", "Platform Decomposition Diagram", "Platform component breakdown"),
        ("processing_diagram", "Processing Diagram", "Processing flows and nodes"),
        ("network_computing_diagram", "Network Computing/Hardware Diagram", "Network and compute infrastructure"),
        ("communications_engineering", "Communications Engineering Diagram", "Communication infrastructure detail"),

        # Governance artifacts
        ("architecture_contract", "Architecture Contract", "Agreement on deliverables and conformance"),
        ("compliance_assessment", "Compliance Assessment", "Assessment of implementation compliance"),
        ("architecture_requirements_spec", "Architecture Requirements Specification", "Consolidated architecture requirements"),
        ("architecture_definition_document", "Architecture Definition Document", "Comprehensive architecture definition"),
        ("architecture_roadmap", "Architecture Roadmap", "Time-based view of architecture evolution"),
        ("transition_architecture", "Transition Architecture", "Intermediate architecture state"),
        ("implementation_migration_plan", "Implementation and Migration Plan", "Detailed implementation plan"),
        ("architecture_vision_document", "Architecture Vision Document", "Approved architecture vision"),
        ("statement_of_architecture_work", "Statement of Architecture Work", "Scope and approach agreement"),
        ("architecture_change_request", "Architecture Change Request", "Formal request for architecture change"),
        ("architecture_board_minutes", "Architecture Board Minutes", "Decisions and actions from board meetings"),
    ]

    seeds = []
    for key, name, desc in artifacts:
        seeds.append(SeedConcept(
            id=f"artifact_{key}", name=name, category=SeedCategory.TOGAF_ARTIFACT,
            description=desc, domain="togaf",
            tags=["artifact"],
        ))
    return seeds


def _togaf_technique_seeds() -> list[SeedConcept]:
    """TOGAF technique-specific seeds."""
    techniques = [
        ("stakeholder_management", "Stakeholder Management Technique", "Identifying, classifying, and managing stakeholder engagement"),
        ("architecture_principles_technique", "Architecture Principles Technique", "Defining and cataloging architecture principles"),
        ("business_scenarios", "Business Scenarios Technique", "Using scenarios to discover and document requirements"),
        ("gap_analysis_technique", "Gap Analysis Technique", "Identifying gaps between baseline and target"),
        ("migration_planning_technique", "Migration Planning Technique", "Sequencing and planning migration"),
        ("interoperability_technique", "Interoperability Requirements Technique", "Defining interoperability requirements"),
        ("business_transformation_readiness", "Business Transformation Readiness Assessment", "Assessing organizational readiness for change"),
        ("risk_management_technique", "Risk Management Technique", "Identifying and mitigating architecture risks"),
        ("capability_based_planning", "Capability-Based Planning Technique", "Planning based on business capabilities"),
        ("architecture_patterns_technique", "Architecture Patterns Technique", "Applying proven architecture patterns"),
        ("architecture_compliance_review", "Architecture Compliance Review", "Reviewing implementations for conformance"),
        ("architecture_maturity_assessment", "Architecture Maturity Assessment", "Assessing enterprise architecture maturity"),
        ("value_chain_analysis", "Value Chain Analysis", "Analyzing value chain for optimization opportunities"),
        ("swot_analysis", "SWOT Analysis for Architecture", "Strengths/Weaknesses/Opportunities/Threats analysis"),
        ("time_classification", "TIME Classification", "Tolerate/Invest/Migrate/Eliminate application classification"),
        ("wardley_mapping", "Wardley Mapping", "Value chain evolution mapping technique"),
        ("business_model_canvas_ea", "Business Model Canvas for EA", "Applying BMC to enterprise architecture"),
        ("architecture_decision_records", "Architecture Decision Records", "Documenting architecture decisions"),
        ("fitness_function_design", "Fitness Function Design", "Defining automated architecture fitness functions"),
        ("domain_driven_design_togaf", "Domain-Driven Design in TOGAF", "Applying DDD concepts within TOGAF"),
        ("event_storming_architecture", "Event Storming for Architecture", "Using event storming for architecture discovery"),
        ("architecture_runway_planning", "Architecture Runway Planning", "Planning architecture runway for agile delivery"),
    ]

    seeds = []
    for key, name, desc in techniques:
        seeds.append(SeedConcept(
            id=f"technique_{key}", name=name, category=SeedCategory.TOGAF_TECHNIQUE,
            description=desc, domain="togaf",
            tags=["technique"],
        ))
    return seeds


def _archimate_element_seeds() -> list[SeedConcept]:
    """ArchiMate element seeds across all layers."""
    elements = [
        # Strategy layer
        ("resource", "Resource", "strategy", "Asset owned or controlled"),
        ("capability", "Capability", "strategy", "Ability to employ resources to achieve goals"),
        ("value_stream", "Value Stream", "strategy", "Sequence of activities creating stakeholder value"),
        ("course_of_action", "Course of Action", "strategy", "Approach to achieve a goal"),

        # Business layer
        ("business_actor", "Business Actor", "business", "Organizational entity capable of performing behavior"),
        ("business_role", "Business Role", "business", "Responsibility for specific behavior"),
        ("business_collaboration", "Business Collaboration", "business", "Aggregate of roles performing collective behavior"),
        ("business_interface", "Business Interface", "business", "Point of access for business services"),
        ("business_process", "Business Process", "business", "Sequence of business behaviors achieving a result"),
        ("business_function", "Business Function", "business", "Collection of behavior based on criteria"),
        ("business_interaction", "Business Interaction", "business", "Unit of collective behavior"),
        ("business_event", "Business Event", "business", "Organizational state change"),
        ("business_service", "Business Service", "business", "Externally visible unit of functionality"),
        ("business_object", "Business Object", "business", "Concept relevant from a business perspective"),
        ("contract", "Contract", "business", "Formal or informal specification of agreement"),
        ("representation", "Representation", "business", "Perceptible form of business object"),
        ("product", "Product", "business", "Coherent collection of services with contract"),

        # Application layer
        ("application_component", "Application Component", "application", "Encapsulated application functionality"),
        ("application_collaboration", "Application Collaboration", "application", "Aggregate of components performing collective behavior"),
        ("application_interface", "Application Interface", "application", "Point of access for application services"),
        ("application_function", "Application Function", "application", "Automated behavior element"),
        ("application_interaction", "Application Interaction", "application", "Unit of collective application behavior"),
        ("application_process", "Application Process", "application", "Sequence of application behaviors"),
        ("application_event", "Application Event", "application", "Application state change"),
        ("application_service", "Application Service", "application", "Externally visible unit of app functionality"),
        ("data_object", "Data Object", "application", "Data structured for automated processing"),

        # Technology layer
        ("node", "Node", "technology", "Computational or physical resource hosting artifacts"),
        ("device", "Device", "technology", "Physical IT resource for processing"),
        ("system_software", "System Software", "technology", "Platform software"),
        ("technology_collaboration", "Technology Collaboration", "technology", "Aggregate of nodes performing collective behavior"),
        ("technology_interface", "Technology Interface", "technology", "Point of access for technology services"),
        ("path", "Path", "technology", "Link between two or more nodes"),
        ("communication_network", "Communication Network", "technology", "Set of structures connecting nodes"),
        ("technology_function", "Technology Function", "technology", "Collection of technology behavior"),
        ("technology_process", "Technology Process", "technology", "Sequence of technology behaviors"),
        ("technology_interaction", "Technology Interaction", "technology", "Unit of collective technology behavior"),
        ("technology_event", "Technology Event", "technology", "Technology state change"),
        ("technology_service", "Technology Service", "technology", "Externally visible unit of tech functionality"),
        ("artifact", "Artifact", "technology", "Piece of data used or produced"),

        # Physical layer
        ("equipment", "Equipment", "physical", "Physical machine or instrument"),
        ("facility", "Facility", "physical", "Physical structure or environment"),
        ("distribution_network", "Distribution Network", "physical", "Physical medium for transport"),
        ("material", "Material", "physical", "Tangible physical element"),

        # Motivation layer
        ("stakeholder_element", "Stakeholder", "motivation", "Role of individual or organization with interest"),
        ("driver", "Driver", "motivation", "External or internal condition motivating change"),
        ("assessment", "Assessment", "motivation", "Result of analysis of a driver"),
        ("goal", "Goal", "motivation", "End state to be achieved"),
        ("outcome", "Outcome", "motivation", "End result"),
        ("principle", "Principle", "motivation", "Qualitative statement guiding design"),
        ("requirement_element", "Requirement", "motivation", "Statement of need"),
        ("constraint", "Constraint", "motivation", "Factor limiting realization"),
        ("meaning", "Meaning", "motivation", "Knowledge or expertise"),
        ("value", "Value", "motivation", "Relative worth"),

        # Implementation & Migration
        ("work_package", "Work Package", "implementation_migration", "Series of actions to achieve a result"),
        ("deliverable", "Deliverable", "implementation_migration", "Precisely-defined outcome of work package"),
        ("implementation_event", "Implementation Event", "implementation_migration", "State change during implementation"),
        ("plateau", "Plateau", "implementation_migration", "Relatively stable state of architecture"),
        ("gap_element", "Gap", "implementation_migration", "Difference between two plateaus"),
    ]

    seeds = []
    for key, name, layer, desc in elements:
        seeds.append(SeedConcept(
            id=f"archimate_element_{key}", name=name,
            category=SeedCategory.ARCHIMATE_ELEMENT,
            description=desc, domain=f"archimate_{layer}",
            tags=["archimate", "element", layer],
        ))
    return seeds


def _archimate_viewpoint_seeds() -> list[SeedConcept]:
    """ArchiMate viewpoint seeds."""
    viewpoints = [
        ("organization_vp", "Organization Viewpoint", "Shows organizational structure of an enterprise"),
        ("business_process_cooperation_vp", "Business Process Cooperation Viewpoint", "Shows relationships between business processes"),
        ("product_vp", "Product Viewpoint", "Shows value a product offers to customers"),
        ("application_cooperation_vp", "Application Cooperation Viewpoint", "Shows application components and their relationships"),
        ("application_usage_vp", "Application Usage Viewpoint", "Shows how applications are used by business processes"),
        ("technology_usage_vp", "Technology Usage Viewpoint", "Shows how technology supports applications"),
        ("technology_vp", "Technology Viewpoint", "Shows technology infrastructure"),
        ("information_structure_vp", "Information Structure Viewpoint", "Shows information structure including data types"),
        ("service_realization_vp", "Service Realization Viewpoint", "Shows how services are realized by behavior and components"),
        ("implementation_deployment_vp", "Implementation and Deployment Viewpoint", "Shows how applications map to technology"),
        ("layered_vp", "Layered Viewpoint", "Provides overview across multiple layers"),
        ("landscape_map_vp", "Landscape Map Viewpoint", "Shows architecture elements in a grid layout"),
        ("goal_realization_vp", "Goal Realization Viewpoint", "Shows how goals are realized through requirements"),
        ("requirements_realization_vp", "Requirements Realization Viewpoint", "Shows how requirements are realized by elements"),
        ("motivation_vp", "Motivation Viewpoint", "Shows motivational elements and their relationships"),
        ("strategy_vp", "Strategy Viewpoint", "Shows strategic course of action and resources"),
        ("capability_map_vp", "Capability Map Viewpoint", "Shows business capabilities and their relationships"),
        ("outcome_realization_vp", "Outcome Realization Viewpoint", "Shows how outcomes are achieved"),
        ("resource_map_vp", "Resource Map Viewpoint", "Shows allocation of resources"),
        ("value_stream_vp", "Value Stream Viewpoint", "Shows value streams and stages"),
        ("migration_vp", "Migration Viewpoint", "Shows transition between architecture plateaus"),
        ("project_vp", "Project Viewpoint", "Shows project structure and deliverables"),
        ("stakeholder_vp", "Stakeholder Viewpoint", "Shows stakeholder interests and concerns"),
        ("physical_vp", "Physical Viewpoint", "Shows physical environment and equipment"),
    ]

    seeds = []
    for key, name, desc in viewpoints:
        seeds.append(SeedConcept(
            id=f"archimate_{key}", name=name, category=SeedCategory.ARCHIMATE_VIEWPOINT,
            description=desc, domain="archimate",
            tags=["archimate", "viewpoint"],
        ))
    return seeds


def _industry_case_seeds() -> list[SeedConcept]:
    """Industry-specific case seeds."""
    cases = [
        # Banking & Finance
        ("banking_core_modernization", "Banking Core Modernization", "banking", "Modernizing legacy core banking systems to cloud-native architecture"),
        ("payment_hub_transformation", "Payment Hub Transformation", "banking", "Centralizing payment processing across channels"),
        ("digital_banking_platform", "Digital Banking Platform", "banking", "Building omnichannel digital banking experience"),
        ("open_banking_api_ecosystem", "Open Banking API Ecosystem", "banking", "Implementing PSD2/open banking API infrastructure"),
        ("aml_kyc_platform", "AML/KYC Platform Modernization", "banking", "Anti-money laundering and KYC platform overhaul"),
        ("wealth_management_digital", "Wealth Management Digitalization", "banking", "Digital transformation of wealth advisory services"),
        ("trade_finance_blockchain", "Trade Finance Blockchain", "banking", "Blockchain-based trade finance platform"),
        ("credit_scoring_ai", "AI-Powered Credit Scoring", "banking", "Machine learning-based credit risk assessment"),
        ("real_time_payments", "Real-Time Payments Infrastructure", "banking", "Implementing instant payment capabilities"),
        ("regulatory_reporting_platform", "Regulatory Reporting Platform", "banking", "Automated regulatory reporting infrastructure"),
        ("mobile_banking_redesign", "Mobile Banking Redesign", "banking", "Redesigning mobile banking user experience"),
        ("branch_transformation", "Branch Transformation", "banking", "Digital transformation of physical branches"),
        ("loan_origination_modernization", "Loan Origination System Modernization", "banking", "Modernizing end-to-end loan origination"),
        ("fraud_detection_realtime", "Real-Time Fraud Detection", "banking", "Real-time fraud detection and prevention"),
        ("data_warehouse_migration", "Data Warehouse Cloud Migration", "banking", "Migrating enterprise data warehouse to cloud"),

        # Insurance
        ("insurance_claims_digital", "Insurance Claims Digitalization", "insurance", "End-to-end digital claims processing"),
        ("insurance_underwriting_ai", "AI-Powered Underwriting", "insurance", "Machine learning-based risk assessment for underwriting"),
        ("insurance_policy_admin", "Policy Administration Modernization", "insurance", "Modernizing policy admin systems"),
        ("insurtech_platform", "InsurTech Platform Integration", "insurance", "Integrating InsurTech capabilities into legacy ecosystem"),
        ("telematics_iot_insurance", "Telematics/IoT Insurance Platform", "insurance", "Usage-based insurance with IoT data"),

        # Healthcare
        ("healthcare_fhir_integration", "Healthcare FHIR Integration", "healthcare", "HL7 FHIR-based healthcare data interoperability"),
        ("ehr_modernization", "EHR System Modernization", "healthcare", "Electronic health record system modernization"),
        ("telemedicine_platform", "Telemedicine Platform Architecture", "healthcare", "Scalable telemedicine platform design"),
        ("clinical_data_lake", "Clinical Data Lake", "healthcare", "Enterprise clinical data lake for analytics"),
        ("patient_engagement_portal", "Patient Engagement Portal", "healthcare", "Patient-facing engagement and communication platform"),
        ("medical_device_iot", "Medical Device IoT Platform", "healthcare", "IoT platform for medical device integration"),
        ("drug_supply_chain", "Drug Supply Chain Traceability", "healthcare", "Pharmaceutical supply chain track and trace"),
        ("health_information_exchange", "Health Information Exchange", "healthcare", "Regional health information exchange network"),
        ("genomics_data_platform", "Genomics Data Platform", "healthcare", "Platform for genomics data analysis and storage"),
        ("hospital_erp_migration", "Hospital ERP Migration", "healthcare", "Migrating hospital management systems"),

        # Telecom
        ("telecom_5g_network_slicing", "Telecom 5G Network Slicing", "telecom", "5G network slicing architecture for multi-tenant services"),
        ("telecom_bss_transformation", "BSS Transformation", "telecom", "Business support system transformation to TM Forum standards"),
        ("telecom_oss_modernization", "OSS Modernization", "telecom", "Operations support system cloud migration"),
        ("telecom_api_gateway", "Telecom API Gateway Platform", "telecom", "Unified API gateway for telecom services"),
        ("telecom_edge_computing", "Edge Computing Platform", "telecom", "Multi-access edge computing architecture"),
        ("telecom_iot_platform", "Telecom IoT Platform", "telecom", "IoT connectivity and device management platform"),
        ("telecom_digital_twin", "Network Digital Twin", "telecom", "Digital twin for network planning and optimization"),
        ("telecom_customer_360", "Customer 360 Platform", "telecom", "Unified customer view across all channels"),

        # Manufacturing
        ("smart_factory", "Smart Factory Architecture", "manufacturing", "Industry 4.0 smart factory implementation"),
        ("manufacturing_mes", "MES Modernization", "manufacturing", "Manufacturing execution system modernization"),
        ("digital_twin_manufacturing", "Manufacturing Digital Twin", "manufacturing", "Digital twin for manufacturing processes"),
        ("supply_chain_control_tower", "Supply Chain Control Tower", "manufacturing", "End-to-end supply chain visibility platform"),
        ("predictive_maintenance_platform", "Predictive Maintenance Platform", "manufacturing", "IoT-based predictive maintenance architecture"),
        ("quality_management_digital", "Digital Quality Management", "manufacturing", "Digitalized quality management processes"),

        # Government
        ("gov_digital_services", "Government Digital Services", "government", "Citizen-facing digital government services"),
        ("gov_data_sharing", "Cross-Agency Data Sharing", "government", "Secure data sharing between government agencies"),
        ("gov_legacy_modernization", "Government Legacy Modernization", "government", "Modernizing decades-old government IT systems"),
        ("smart_city_platform", "Smart City Platform", "government", "Integrated smart city services architecture"),
        ("gov_identity_platform", "Digital Identity Platform", "government", "National digital identity and authentication"),
        ("defense_enterprise_arch", "Defense Enterprise Architecture", "government", "DoDAF/MODAF-aligned defense architecture"),

        # Retail
        ("omnichannel_retail", "Omnichannel Retail Platform", "retail", "Unified commerce across physical and digital channels"),
        ("retail_supply_chain", "Retail Supply Chain Optimization", "retail", "AI-driven supply chain optimization"),
        ("personalization_engine", "Personalization Engine", "retail", "Real-time customer personalization platform"),
        ("retail_pos_modernization", "POS System Modernization", "retail", "Point-of-sale system cloud migration"),
        ("marketplace_platform", "Marketplace Platform", "retail", "Multi-vendor marketplace architecture"),

        # Energy & Utilities
        ("smart_grid", "Smart Grid Architecture", "energy", "Intelligent electricity grid modernization"),
        ("energy_trading_platform", "Energy Trading Platform", "energy", "Real-time energy trading and settlement"),
        ("renewable_energy_management", "Renewable Energy Management", "energy", "Distributed renewable energy orchestration"),
        ("utility_metering", "Advanced Metering Infrastructure", "energy", "Smart metering and demand response"),
        ("carbon_tracking", "Carbon Emissions Tracking Platform", "energy", "Enterprise carbon footprint tracking and reporting"),

        # Cross-industry
        ("cloud_migration_enterprise", "Enterprise Cloud Migration", "cross_industry", "Comprehensive cloud migration program"),
        ("microservices_decomposition", "Microservices Decomposition", "cross_industry", "Monolith to microservices transformation"),
        ("api_platform_enterprise", "Enterprise API Platform", "cross_industry", "Organization-wide API management platform"),
        ("data_mesh_implementation", "Data Mesh Implementation", "cross_industry", "Implementing data mesh architecture paradigm"),
        ("zero_trust_architecture", "Zero Trust Security Architecture", "cross_industry", "Zero trust network architecture implementation"),
        ("event_driven_architecture", "Event-Driven Architecture", "cross_industry", "Enterprise event-driven architecture transformation"),
        ("multicloud_governance", "Multi-Cloud Governance", "cross_industry", "Governance framework for multi-cloud environments"),
        ("devops_platform", "DevOps Platform Architecture", "cross_industry", "Enterprise DevOps platform and toolchain"),
        ("ai_ml_platform", "AI/ML Platform Architecture", "cross_industry", "Enterprise AI and machine learning platform"),
        ("integration_platform", "Integration Platform Modernization", "cross_industry", "ESB to iPaaS migration"),
        ("identity_access_management", "IAM Platform Modernization", "cross_industry", "Identity and access management overhaul"),
        ("observability_platform", "Observability Platform", "cross_industry", "Unified observability and monitoring"),
        ("crm_transformation", "CRM Transformation", "cross_industry", "Customer relationship management modernization"),
        ("erp_cloud_migration", "ERP Cloud Migration", "cross_industry", "Migrating ERP to cloud-based platform"),
        ("content_management_headless", "Headless CMS Architecture", "cross_industry", "Headless content management system architecture"),
    ]

    seeds = []
    for key, name, industry, desc in cases:
        seeds.append(SeedConcept(
            id=f"case_{key}", name=name, category=SeedCategory.INDUSTRY_CASE,
            description=desc, domain=industry,
            tags=["industry_case", industry],
        ))
    return seeds


def _standard_seeds() -> list[SeedConcept]:
    """Standard/framework seeds."""
    standards = [
        ("togaf_10", "TOGAF Standard 10th Edition", "The Open Group Architecture Framework version 10"),
        ("togaf_9_2", "TOGAF Standard 9.2", "The Open Group Architecture Framework version 9.2"),
        ("archimate_3_2", "ArchiMate 3.2 Specification", "ArchiMate modeling language specification"),
        ("it4it", "IT4IT Reference Architecture", "IT value chain reference architecture"),
        ("iso_42010", "ISO/IEC/IEEE 42010", "Systems and software engineering architecture description"),
        ("zachman", "Zachman Framework", "Enterprise architecture classification taxonomy"),
        ("feaf", "Federal Enterprise Architecture Framework", "US Federal government EA framework"),
        ("dodaf", "DoDAF 2.02", "Department of Defense Architecture Framework"),
        ("modaf", "MODAF", "UK Ministry of Defence Architecture Framework"),
        ("nato_af", "NATO Architecture Framework", "NATO C3 systems architecture framework"),
        ("sabsa", "SABSA Framework", "Security architecture framework"),
        ("cobit_2019", "COBIT 2019", "IT governance and management framework"),
        ("itil_4", "ITIL 4", "IT service management framework"),
        ("iso_27001_standard", "ISO 27001:2022", "Information security management system"),
        ("nist_csf_standard", "NIST Cybersecurity Framework", "Cybersecurity risk management framework"),
        ("pci_dss_standard", "PCI DSS v4.0", "Payment card industry data security standard"),
        ("sox_standard", "SOX Compliance", "Sarbanes-Oxley Act compliance"),
        ("gdpr_standard", "GDPR", "General Data Protection Regulation"),
        ("hipaa_standard", "HIPAA", "Health Insurance Portability and Accountability Act"),
        ("basel_iii_standard", "Basel III", "Banking regulatory framework"),
        ("dora_standard", "DORA", "Digital Operational Resilience Act"),
        ("nis2_standard", "NIS2 Directive", "Network and Information Security Directive 2"),
        ("mifid2_standard", "MiFID II", "Markets in Financial Instruments Directive"),
        ("psd2_standard", "PSD2", "Payment Services Directive 2"),
        ("ccpa_standard", "CCPA", "California Consumer Privacy Act"),
        ("bian_standard", "BIAN", "Banking Industry Architecture Network"),
        ("tmforum_oda_standard", "TM Forum ODA", "Open Digital Architecture"),
        ("acord_standard", "ACORD Standards", "Insurance data standards"),
        ("hl7_fhir_standard", "HL7 FHIR", "Healthcare interoperability standard"),
        ("openapi_spec", "OpenAPI Specification", "API description standard"),
        ("asyncapi_spec", "AsyncAPI Specification", "Async API description standard"),
        ("cncf_landscape", "CNCF Landscape", "Cloud Native Computing Foundation landscape"),
        ("twelve_factor_app", "12-Factor App", "Methodology for building SaaS applications"),
        ("well_architected_aws", "AWS Well-Architected Framework", "Cloud architecture best practices"),
        ("azure_waf", "Azure Well-Architected Framework", "Microsoft cloud architecture guidance"),
        ("gcp_arch_framework", "GCP Architecture Framework", "Google Cloud architecture guidance"),
        ("safe_framework", "SAFe", "Scaled Agile Framework"),
        ("less_framework", "LeSS", "Large-Scale Scrum framework"),
        ("team_topologies", "Team Topologies", "Organizing business and technology teams"),
        ("c4_model", "C4 Model", "Software architecture visualization model"),
    ]

    seeds = []
    for key, name, desc in standards:
        seeds.append(SeedConcept(
            id=f"standard_{key}", name=name, category=SeedCategory.STANDARD,
            description=desc, domain="standards",
            tags=["standard"],
        ))
    return seeds


def _capability_seeds() -> list[SeedConcept]:
    """Business capability seeds across industries."""
    capabilities = [
        # Banking capabilities
        ("banking_payment_processing", "Payment Processing", "banking", "Processing financial transactions"),
        ("banking_customer_onboarding", "Customer Onboarding", "banking", "Onboarding new banking customers"),
        ("banking_loan_origination", "Loan Origination", "banking", "End-to-end loan processing"),
        ("banking_risk_management", "Risk Management", "banking", "Financial risk assessment and mitigation"),
        ("banking_regulatory_compliance", "Regulatory Compliance", "banking", "Ensuring regulatory adherence"),
        ("banking_fraud_management", "Fraud Management", "banking", "Detecting and preventing fraud"),
        ("banking_treasury_management", "Treasury Management", "banking", "Corporate treasury operations"),
        ("banking_trade_settlement", "Trade Settlement", "banking", "Securities trade settlement"),
        ("banking_customer_analytics", "Customer Analytics", "banking", "Customer behavior analysis"),
        ("banking_digital_channels", "Digital Channel Management", "banking", "Managing digital banking channels"),
        ("banking_account_management", "Account Management", "banking", "Managing customer accounts"),
        ("banking_credit_decisioning", "Credit Decisioning", "banking", "Automated credit decisions"),
        ("banking_collateral_management", "Collateral Management", "banking", "Managing loan collateral"),
        ("banking_reconciliation", "Reconciliation", "banking", "Financial reconciliation processes"),
        ("banking_reporting", "Regulatory Reporting", "banking", "Mandatory regulatory reporting"),

        # Healthcare capabilities
        ("health_patient_registration", "Patient Registration", "healthcare", "Registering and identifying patients"),
        ("health_clinical_documentation", "Clinical Documentation", "healthcare", "Creating and managing clinical records"),
        ("health_order_management", "Order Management", "healthcare", "Managing clinical orders"),
        ("health_medication_management", "Medication Management", "healthcare", "Prescribing and dispensing medications"),
        ("health_lab_management", "Laboratory Management", "healthcare", "Managing lab orders and results"),
        ("health_imaging", "Medical Imaging", "healthcare", "DICOM imaging and PACS management"),
        ("health_scheduling", "Patient Scheduling", "healthcare", "Scheduling appointments and resources"),
        ("health_billing", "Medical Billing", "healthcare", "Claims processing and billing"),
        ("health_population_health", "Population Health Management", "healthcare", "Managing health at population level"),
        ("health_care_coordination", "Care Coordination", "healthcare", "Coordinating care across providers"),

        # Telecom capabilities
        ("telecom_network_planning", "Network Planning", "telecom", "Planning network infrastructure"),
        ("telecom_service_provisioning", "Service Provisioning", "telecom", "Activating customer services"),
        ("telecom_billing_rating", "Billing and Rating", "telecom", "Usage rating and billing"),
        ("telecom_customer_care", "Customer Care", "telecom", "Customer support and service"),
        ("telecom_network_monitoring", "Network Monitoring", "telecom", "Real-time network monitoring"),
        ("telecom_spectrum_management", "Spectrum Management", "telecom", "Radio spectrum allocation"),
        ("telecom_partner_management", "Partner Management", "telecom", "Managing MVNO and partner relationships"),
        ("telecom_product_catalog", "Product Catalog Management", "telecom", "Managing telecom product offerings"),

        # Manufacturing capabilities
        ("mfg_production_planning", "Production Planning", "manufacturing", "Planning production schedules"),
        ("mfg_quality_control", "Quality Control", "manufacturing", "Ensuring product quality"),
        ("mfg_inventory_management", "Inventory Management", "manufacturing", "Managing raw materials and finished goods"),
        ("mfg_supply_chain", "Supply Chain Management", "manufacturing", "Managing suppliers and logistics"),
        ("mfg_maintenance", "Maintenance Management", "manufacturing", "Equipment maintenance and repair"),
        ("mfg_product_lifecycle", "Product Lifecycle Management", "manufacturing", "Managing product from design to disposal"),
        ("mfg_shop_floor", "Shop Floor Management", "manufacturing", "Managing shop floor operations"),
        ("mfg_demand_forecasting", "Demand Forecasting", "manufacturing", "Predicting product demand"),

        # Cross-industry capabilities
        ("cross_identity_management", "Identity and Access Management", "cross_industry", "Managing user identities and access"),
        ("cross_data_governance", "Data Governance", "cross_industry", "Governing data quality and lifecycle"),
        ("cross_api_management", "API Management", "cross_industry", "Managing API lifecycle and access"),
        ("cross_event_management", "Event Management", "cross_industry", "Managing business and technical events"),
        ("cross_document_management", "Document Management", "cross_industry", "Managing enterprise documents"),
        ("cross_workflow_automation", "Workflow Automation", "cross_industry", "Automating business workflows"),
        ("cross_analytics_bi", "Analytics and BI", "cross_industry", "Business intelligence and analytics"),
        ("cross_master_data", "Master Data Management", "cross_industry", "Managing master data entities"),
        ("cross_notification", "Notification Management", "cross_industry", "Managing multi-channel notifications"),
        ("cross_audit_logging", "Audit and Logging", "cross_industry", "Enterprise audit trail and logging"),
    ]

    seeds = []
    for key, name, domain, desc in capabilities:
        seeds.append(SeedConcept(
            id=f"capability_{key}", name=name, category=SeedCategory.CAPABILITY,
            description=desc, domain=domain,
            tags=["capability", domain],
        ))
    return seeds


def _building_block_seeds() -> list[SeedConcept]:
    """Architecture and Solution Building Block seeds."""
    blocks = [
        # Architecture Building Blocks (ABBs)
        ("abb_api_gateway", "API Gateway ABB", "Architecture building block for API management and gateway"),
        ("abb_message_broker", "Message Broker ABB", "Architecture building block for asynchronous messaging"),
        ("abb_identity_provider", "Identity Provider ABB", "Architecture building block for authentication/authorization"),
        ("abb_data_store", "Data Store ABB", "Architecture building block for data persistence"),
        ("abb_event_bus", "Event Bus ABB", "Architecture building block for event-driven communication"),
        ("abb_service_mesh", "Service Mesh ABB", "Architecture building block for service-to-service communication"),
        ("abb_etl_pipeline", "ETL Pipeline ABB", "Architecture building block for data extraction/transformation/loading"),
        ("abb_monitoring", "Monitoring ABB", "Architecture building block for observability"),
        ("abb_cache_layer", "Cache Layer ABB", "Architecture building block for caching"),
        ("abb_search_engine", "Search Engine ABB", "Architecture building block for full-text search"),
        ("abb_workflow_engine", "Workflow Engine ABB", "Architecture building block for workflow orchestration"),
        ("abb_notification_service", "Notification Service ABB", "Architecture building block for notifications"),
        ("abb_file_storage", "File Storage ABB", "Architecture building block for unstructured data storage"),
        ("abb_container_platform", "Container Platform ABB", "Architecture building block for container orchestration"),
        ("abb_cdn", "CDN ABB", "Architecture building block for content delivery"),
        ("abb_load_balancer", "Load Balancer ABB", "Architecture building block for traffic distribution"),
        ("abb_waf", "WAF ABB", "Architecture building block for web application firewall"),
        ("abb_secret_management", "Secret Management ABB", "Architecture building block for secrets and keys"),
        ("abb_ci_cd_pipeline", "CI/CD Pipeline ABB", "Architecture building block for continuous integration/deployment"),
        ("abb_logging_aggregator", "Logging Aggregator ABB", "Architecture building block for centralized logging"),

        # Solution Building Blocks (SBBs)
        ("sbb_kong_gateway", "Kong API Gateway SBB", "Kong-based API gateway implementation"),
        ("sbb_kafka_cluster", "Apache Kafka SBB", "Kafka-based message broker implementation"),
        ("sbb_keycloak", "Keycloak SBB", "Keycloak-based identity provider implementation"),
        ("sbb_postgresql", "PostgreSQL SBB", "PostgreSQL database implementation"),
        ("sbb_mongodb", "MongoDB SBB", "MongoDB document store implementation"),
        ("sbb_elasticsearch", "Elasticsearch SBB", "Elasticsearch search engine implementation"),
        ("sbb_redis", "Redis SBB", "Redis cache implementation"),
        ("sbb_kubernetes", "Kubernetes SBB", "Kubernetes container platform implementation"),
        ("sbb_istio", "Istio Service Mesh SBB", "Istio service mesh implementation"),
        ("sbb_airflow", "Apache Airflow SBB", "Airflow workflow orchestration implementation"),
        ("sbb_prometheus_grafana", "Prometheus/Grafana SBB", "Prometheus + Grafana monitoring stack"),
        ("sbb_vault", "HashiCorp Vault SBB", "Vault-based secret management implementation"),
        ("sbb_jenkins", "Jenkins SBB", "Jenkins CI/CD implementation"),
        ("sbb_github_actions", "GitHub Actions SBB", "GitHub Actions CI/CD implementation"),
        ("sbb_terraform", "Terraform SBB", "Terraform infrastructure-as-code implementation"),
        ("sbb_snowflake", "Snowflake SBB", "Snowflake cloud data warehouse implementation"),
        ("sbb_databricks", "Databricks SBB", "Databricks data engineering platform"),
        ("sbb_mulesoft", "MuleSoft SBB", "MuleSoft integration platform implementation"),
        ("sbb_cloud_los_microservice", "Cloud LOS Microservice SBB", "Cloud-native loan origination microservice"),
        ("sbb_api_gateway_v2", "API Gateway v2 SBB", "Next-generation API gateway implementation"),
    ]

    seeds = []
    for key, name, desc in blocks:
        seeds.append(SeedConcept(
            id=f"block_{key}", name=name, category=SeedCategory.BUILDING_BLOCK,
            description=desc, domain="architecture",
            tags=["building_block", "abb" if key.startswith("abb") else "sbb"],
        ))
    return seeds


def _stakeholder_seeds() -> list[SeedConcept]:
    """Stakeholder role seeds."""
    stakeholders = [
        # Executive
        ("ceo", "Chief Executive Officer", "executive", "Overall enterprise strategy and direction"),
        ("cto", "Chief Technology Officer", "executive", "Technology strategy and innovation"),
        ("cio", "Chief Information Officer", "executive", "IT strategy and digital transformation"),
        ("cfo", "Chief Financial Officer", "executive", "Financial strategy and cost management"),
        ("coo", "Chief Operating Officer", "executive", "Operational excellence"),
        ("cdo", "Chief Data Officer", "executive", "Data strategy and governance"),
        ("ciso", "Chief Information Security Officer", "executive", "Information security strategy"),
        ("cdto", "Chief Digital Transformation Officer", "executive", "Digital transformation leadership"),
        ("cro", "Chief Risk Officer", "executive", "Enterprise risk management"),
        ("cpo", "Chief Product Officer", "executive", "Product strategy and lifecycle"),

        # Architecture
        ("chief_architect", "Chief Enterprise Architect", "architecture", "Enterprise architecture leadership"),
        ("domain_architect_business", "Business Domain Architect", "architecture", "Business architecture domain"),
        ("domain_architect_data", "Data Architect", "architecture", "Data architecture domain"),
        ("domain_architect_application", "Application Architect", "architecture", "Application architecture domain"),
        ("domain_architect_technology", "Technology Architect", "architecture", "Technology/infrastructure architecture"),
        ("solution_architect", "Solution Architect", "architecture", "Solution-level architecture design"),
        ("security_architect", "Security Architect", "architecture", "Security architecture design"),
        ("integration_architect", "Integration Architect", "architecture", "Integration architecture design"),
        ("cloud_architect", "Cloud Architect", "architecture", "Cloud architecture design"),

        # Business
        ("business_unit_head", "Business Unit Head", "business", "Business unit P&L and strategy"),
        ("product_manager", "Product Manager", "business", "Product requirements and roadmap"),
        ("business_analyst", "Business Analyst", "business", "Requirements analysis and documentation"),
        ("process_owner", "Business Process Owner", "business", "Business process design and optimization"),
        ("head_of_lending", "Head of Lending", "business", "Lending operations and strategy"),
        ("head_of_payments", "Head of Payments", "business", "Payment operations and strategy"),
        ("head_of_compliance", "Head of Compliance", "business", "Regulatory compliance management"),
        ("head_of_operations", "Head of Operations", "business", "Operational efficiency"),
        ("head_of_customer_service", "Head of Customer Service", "business", "Customer service excellence"),

        # Technical
        ("dev_team_lead", "Development Team Lead", "technical", "Software development leadership"),
        ("devops_engineer", "DevOps Engineer", "technical", "CI/CD and infrastructure automation"),
        ("sre", "Site Reliability Engineer", "technical", "System reliability and performance"),
        ("dba", "Database Administrator", "technical", "Database management and optimization"),
        ("qa_lead", "QA Lead", "technical", "Quality assurance and testing"),
        ("infra_manager", "Infrastructure Manager", "technical", "Infrastructure operations"),
        ("network_engineer", "Network Engineer", "technical", "Network design and operations"),
        ("security_engineer", "Security Engineer", "technical", "Security implementation and monitoring"),

        # Governance
        ("architecture_board_chair", "Architecture Board Chair", "governance", "Architecture governance decisions"),
        ("program_manager", "Program Manager", "governance", "Program execution and governance"),
        ("pmo_director", "PMO Director", "governance", "Portfolio and project management"),
        ("audit_manager", "Internal Audit Manager", "governance", "Audit and compliance oversight"),
        ("risk_manager", "Risk Manager", "governance", "Operational risk management"),
        ("vendor_manager", "Vendor/Supplier Manager", "governance", "Vendor relationship management"),

        # External
        ("regulator", "Regulatory Authority", "external", "Regulatory oversight and requirements"),
        ("external_auditor", "External Auditor", "external", "Independent audit and assurance"),
        ("customer_representative", "Customer Representative", "external", "Customer needs and feedback"),
        ("partner_integration", "Integration Partner", "external", "Third-party integration concerns"),
        ("cloud_provider", "Cloud Service Provider", "external", "Cloud infrastructure and services"),
    ]

    seeds = []
    for key, name, role_type, desc in stakeholders:
        seeds.append(SeedConcept(
            id=f"stakeholder_{key}", name=name, category=SeedCategory.STAKEHOLDER,
            description=desc, domain=role_type,
            tags=["stakeholder", role_type],
        ))
    return seeds


def build_seed_pool() -> list[SeedConcept]:
    """Builds the complete seed pool."""
    seeds = []
    seeds.extend(_togaf_phase_seeds())
    seeds.extend(_togaf_artifact_seeds())
    seeds.extend(_togaf_technique_seeds())
    seeds.extend(_archimate_element_seeds())
    seeds.extend(_archimate_viewpoint_seeds())
    seeds.extend(_industry_case_seeds())
    seeds.extend(_standard_seeds())
    seeds.extend(_capability_seeds())
    seeds.extend(_building_block_seeds())
    seeds.extend(_stakeholder_seeds())
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
