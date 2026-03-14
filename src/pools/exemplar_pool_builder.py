"""Builder for the TOGAF Exemplar Pool.

Generates ~500 exemplar task templates across different families of
tool-use patterns. Each exemplar defines a structural template without
binding to specific tools or answers.
"""

from __future__ import annotations

from pathlib import Path

from .models import Exemplar, ExemplarFamily, save_pool


def _retrieve_compute_exemplars() -> list[Exemplar]:
    """retrieve → compute pattern exemplars."""
    templates = [
        ("rc_01", "What is the maturity level of {capability} and which {deliverable} should be created first?",
         ["retrieval", "retrieval", "processing"], 1, 2, "Query capability maturity then determine deliverable priority"),
        ("rc_02", "Retrieve the current state of {system} and compute the risk score based on its technology stack age and interface count.",
         ["retrieval", "processing"], 2, 2, "Fetch system state then compute risk"),
        ("rc_03", "What is the cost-benefit ratio for migrating {system} to {target_platform}?",
         ["retrieval", "retrieval", "processing"], 2, 1, "Gather costs and benefits then compute ratio"),
        ("rc_04", "How many building blocks in {domain} are reused across more than one project?",
         ["retrieval", "processing"], 2, 1, "Retrieve building blocks then compute reuse percentage"),
        ("rc_05", "What is the compliance score of {system} against {standard} and what are the top violations?",
         ["retrieval", "retrieval", "processing"], 2, 2, "Fetch system details and standard requirements then check compliance"),
        ("rc_06", "Calculate the migration complexity score for moving {source_system} to {target_system}.",
         ["retrieval", "retrieval", "processing"], 2, 1, "Retrieve both system states then compute complexity"),
        ("rc_07", "What is the architecture quality score for the {domain} domain based on modularity and reusability?",
         ["retrieval", "processing"], 2, 1, "Retrieve architecture and compute quality score"),
        ("rc_08", "Determine the capacity planning horizon for {system} given current growth rate of {rate}%.",
         ["retrieval", "processing"], 2, 1, "Retrieve utilization data then compute capacity projection"),
        ("rc_09", "What is the technical debt principal for {system} and what is the estimated remediation cost?",
         ["retrieval", "processing"], 2, 2, "Retrieve system state then compute debt assessment"),
        ("rc_10", "Compute the interoperability score between {system_a} and {system_b}.",
         ["retrieval", "retrieval", "processing"], 2, 1, "Retrieve both systems then compute interoperability matrix"),
        ("rc_11", "Which ADM phase deliverable has the most dependencies and what is its completeness score?",
         ["retrieval", "retrieval", "processing"], 2, 2, "Retrieve deliverables and dependencies then analyze"),
        ("rc_12", "What percentage of {domain} capabilities are below maturity level 3?",
         ["retrieval", "processing"], 1, 1, "Retrieve capability assessments then compute percentage"),
        ("rc_13", "Calculate the ROI for implementing {building_block} across {count} projects.",
         ["retrieval", "processing"], 2, 1, "Retrieve block costs and project benefits then compute ROI"),
        ("rc_14", "What is the average maturity score across all capabilities in {domain}?",
         ["retrieval", "processing"], 1, 1, "Retrieve all maturity scores then compute average"),
        ("rc_15", "Determine the SLA compliance margin for {system} against {requirements}.",
         ["retrieval", "retrieval", "processing"], 2, 1, "Retrieve system metrics and SLA requirements then validate"),
        ("rc_16", "What is the transformation readiness score for {organization} given the proposed {changes}?",
         ["retrieval", "processing"], 2, 1, "Retrieve organization profile then assess readiness"),
        ("rc_17", "Calculate the weighted architecture decision score for {alternatives} given {criteria}.",
         ["retrieval", "processing"], 2, 1, "Retrieve alternative details then compute weighted scores"),
        ("rc_18", "What is the heat map classification for {capability}: invest, tolerate, migrate, or eliminate?",
         ["retrieval", "processing"], 2, 1, "Retrieve capability metrics then compute heat map position"),
        ("rc_19", "Compute the data flow throughput bottleneck between {system_a} and {system_b}.",
         ["retrieval", "retrieval", "processing"], 2, 1, "Retrieve integration details then analyze data flow"),
        ("rc_20", "What is the estimated payback period for the {initiative} initiative?",
         ["retrieval", "processing"], 2, 1, "Retrieve cost/benefit projections then compute payback"),
        ("rc_21", "Score the dependency coupling between {system_a} and {system_b} in the {domain} domain.",
         ["retrieval", "processing"], 2, 1, "Retrieve relationships then compute coupling metric"),
        ("rc_22", "What is the gap severity distribution for the {domain} architecture domain?",
         ["retrieval", "retrieval", "processing"], 2, 1, "Retrieve baseline and target states then analyze gap distribution"),
        ("rc_23", "Calculate the portfolio health score for applications in the {domain} domain.",
         ["retrieval", "processing"], 2, 1, "Retrieve application portfolio then compute health score"),
        ("rc_24", "What is the standards compliance percentage for {domain} technology components?",
         ["retrieval", "retrieval", "processing"], 2, 1, "Retrieve components and standards then check compliance"),
        ("rc_25", "Determine the architecture fitness score for the proposed {solution} solution.",
         ["retrieval", "processing"], 2, 1, "Retrieve architecture details then compute fitness score"),
    ]

    return [Exemplar(
        id=t[0], family=ExemplarFamily.RETRIEVE_COMPUTE, template=t[1],
        implied_pattern=t[2], complexity=t[3], required_tool_types=["retrieval", "processing"],
        description=t[5], sub_questions=t[4],
    ) for t in templates]


def _multi_hop_retrieval_exemplars() -> list[Exemplar]:
    """Multi-hop retrieval with filtering exemplars."""
    templates = [
        ("mh_01", "Among all building blocks that serve {service}, find which one has status 'approved' and supports {standard}.",
         ["retrieval", "retrieval", "retrieval"], 3, 1, "Multi-hop search through BBs with service and standard filters"),
        ("mh_02", "Find all stakeholders whose concerns include {concern} and who are impacted by changes in Phase {phase}.",
         ["retrieval", "retrieval", "retrieval"], 3, 1, "Stakeholder search with concern and phase cross-reference"),
        ("mh_03", "Which ArchiMate elements in the {layer} layer have relationships to elements being eliminated in the gap analysis?",
         ["retrieval", "retrieval", "retrieval"], 3, 1, "Cross-reference ArchiMate elements with gap analysis results"),
        ("mh_04", "Find all architecture decisions that reference {standard} and were approved in the last {period}.",
         ["retrieval", "retrieval"], 2, 1, "Governance log search with standard and time filters"),
        ("mh_05", "Which capabilities in {domain} are supported by building blocks with status 'proposed' but not yet 'approved'?",
         ["retrieval", "retrieval", "retrieval"], 3, 1, "Capability to BB status chain query"),
        ("mh_06", "Find all systems that have interfaces with {system} AND are classified as 'migrate' in the application portfolio.",
         ["retrieval", "retrieval", "retrieval"], 3, 1, "Integration + portfolio cross-reference"),
        ("mh_07", "Which data entities flowing between {system_a} and {system_b} have classification 'restricted'?",
         ["retrieval", "retrieval", "retrieval"], 3, 1, "Data flow + classification cross-reference"),
        ("mh_08", "Find all technology standards in the {domain} domain that are both 'deprecated' and still used by active applications.",
         ["retrieval", "retrieval", "retrieval"], 3, 1, "Standards + application portfolio cross-reference"),
        ("mh_09", "Which Phase {phase} deliverables reference principles from the {category} principle category?",
         ["retrieval", "retrieval"], 2, 1, "Deliverable to principle cross-reference"),
        ("mh_10", "Find all dispensations granted for {project} that affect {standard} compliance.",
         ["retrieval", "retrieval"], 2, 1, "Dispensation + compliance cross-reference"),
        ("mh_11", "Which ArchiMate viewpoints show elements from both the {layer_a} and {layer_b} layers?",
         ["retrieval", "retrieval", "retrieval"], 3, 1, "Viewpoint to multi-layer element analysis"),
        ("mh_12", "Find the longest dependency chain starting from {system} through all serving relationships.",
         ["retrieval", "retrieval", "retrieval", "retrieval"], 4, 1, "Recursive relationship traversal"),
        ("mh_13", "Which reference models define components that map to capabilities with maturity below {threshold}?",
         ["retrieval", "retrieval", "retrieval"], 3, 1, "Reference model to capability maturity chain"),
        ("mh_14", "Find all work packages in the roadmap that depend on building blocks with unresolved compliance violations.",
         ["retrieval", "retrieval", "retrieval"], 3, 1, "Roadmap to BB to compliance chain"),
        ("mh_15", "Which patterns from the pattern library are applicable to {system} based on its current architecture?",
         ["retrieval", "retrieval"], 2, 1, "Pattern matching based on system architecture"),
        ("mh_16", "Find all services in the value stream that are realized by applications classified as 'eliminate'.",
         ["retrieval", "retrieval", "retrieval"], 3, 1, "Value stream to application portfolio chain"),
        ("mh_17", "Which stakeholders have concerns that are not addressed by any deliverable in Phase {phase}?",
         ["retrieval", "retrieval", "retrieval"], 3, 1, "Stakeholder concern to deliverable coverage gap"),
        ("mh_18", "Find all interfaces between systems where one is in the 'invest' and the other in 'migrate' TIME category.",
         ["retrieval", "retrieval", "retrieval"], 3, 1, "Integration + TIME classification cross-reference"),
        ("mh_19", "Which ArchiMate elements are both a target of 'realization' from {element_a} and a source of 'serving' to {element_b}?",
         ["retrieval", "retrieval"], 3, 1, "Bidirectional relationship chain query"),
        ("mh_20", "Find all transition architectures that include building blocks not yet approved by the architecture board.",
         ["retrieval", "retrieval", "retrieval"], 3, 1, "Transition architecture to BB to board decision chain"),
        ("mh_21", "Which compliance requirements from {standard_a} overlap with requirements from {standard_b}?",
         ["retrieval", "retrieval"], 2, 1, "Cross-standard requirement overlap analysis"),
        ("mh_22", "Find all contracts that reference systems with risk scores above {threshold}.",
         ["retrieval", "retrieval", "retrieval"], 3, 1, "Contract to system to risk chain"),
        ("mh_23", "Which capabilities in the business capability model have no supporting building blocks defined?",
         ["retrieval", "retrieval"], 3, 1, "Capability to BB coverage gap"),
        ("mh_24", "Find all architecture board decisions that impact Phase {phase} deliverables and have status 'deferred'.",
         ["retrieval", "retrieval"], 2, 1, "Board decision to phase impact chain"),
        ("mh_25", "Which data entities are master data but have no defined data quality metrics?",
         ["retrieval", "retrieval"], 3, 1, "Data catalog to quality metrics gap"),
    ]

    return [Exemplar(
        id=t[0], family=ExemplarFamily.MULTI_HOP_RETRIEVAL, template=t[1],
        implied_pattern=t[2], complexity=t[3], required_tool_types=["retrieval"],
        description=t[5], sub_questions=t[4],
    ) for t in templates]


def _compare_decide_exemplars() -> list[Exemplar]:
    """Compare and decide pattern exemplars."""
    templates = [
        ("cd_01", "Compare the {ref_model_a} and {ref_model_b} reference models and recommend which better fits {use_case}.",
         ["retrieval", "retrieval", "processing"], 3, 2, "Retrieve two reference models then compare and decide"),
        ("cd_02", "Compare two architecture alternatives for {system}: {option_a} vs {option_b}. Which has better cost-benefit?",
         ["retrieval", "retrieval", "processing", "processing"], 3, 2, "Retrieve alternatives then compare across dimensions"),
        ("cd_03", "Should {system} be classified as Tolerate, Invest, Migrate, or Eliminate? Compare against criteria.",
         ["retrieval", "retrieval", "processing"], 3, 1, "Retrieve system state and criteria then classify"),
        ("cd_04", "Compare the compliance posture of {system_a} vs {system_b} against {standard}. Which needs more remediation?",
         ["retrieval", "retrieval", "processing", "processing"], 3, 2, "Compare compliance of two systems"),
        ("cd_05", "Evaluate whether {pattern_a} or {pattern_b} is more suitable for {use_case} based on quality attributes.",
         ["retrieval", "retrieval", "processing"], 3, 1, "Compare patterns against quality attributes"),
        ("cd_06", "Which migration strategy (big bang, phased, or parallel) is optimal for {system} given its dependencies?",
         ["retrieval", "processing", "processing"], 3, 1, "Evaluate migration strategies based on dependencies"),
        ("cd_07", "Compare the maturity levels of {capability_a} and {capability_b} and recommend which to invest in first.",
         ["retrieval", "retrieval", "processing"], 2, 2, "Compare capability maturities and prioritize"),
        ("cd_08", "Should {building_block} be built in-house or procured? Compare based on cost, time, and strategic fit.",
         ["retrieval", "processing", "processing"], 3, 1, "Build vs buy decision analysis"),
        ("cd_09", "Compare the risk profiles of transition architecture {ta_a} and {ta_b}. Which is safer?",
         ["retrieval", "retrieval", "processing", "processing"], 3, 2, "Compare risk profiles of transition architectures"),
        ("cd_10", "Which viewpoint ({viewpoint_a} or {viewpoint_b}) better addresses the concerns of {stakeholder}?",
         ["retrieval", "retrieval", "retrieval", "processing"], 3, 1, "Compare viewpoints against stakeholder concerns"),
        ("cd_11", "Compare cloud deployment options ({option_a}, {option_b}, {option_c}) for {workload} based on SLA requirements.",
         ["retrieval", "retrieval", "retrieval", "processing"], 3, 1, "Multi-option cloud deployment comparison"),
        ("cd_12", "Which data architecture approach (centralized DW, data lake, or data mesh) best fits {organization}?",
         ["retrieval", "processing", "processing"], 3, 1, "Data architecture approach comparison"),
        ("cd_13", "Compare the integration approaches (API, messaging, file) for connecting {system_a} to {system_b}.",
         ["retrieval", "retrieval", "processing"], 3, 1, "Integration approach comparison"),
        ("cd_14", "Evaluate two roadmap alternatives for {program}: aggressive (2-wave) vs conservative (4-wave).",
         ["retrieval", "processing", "processing", "processing"], 4, 2, "Roadmap alternative evaluation"),
        ("cd_15", "Which SBB implementation ({sbb_a} or {sbb_b}) better realizes the {abb} architecture building block?",
         ["retrieval", "retrieval", "processing"], 3, 1, "SBB to ABB realization comparison"),
        ("cd_16", "Compare the transformation readiness of {org_unit_a} vs {org_unit_b} for the {initiative} initiative.",
         ["retrieval", "retrieval", "processing", "processing"], 3, 2, "Transformation readiness comparison"),
        ("cd_17", "Which Phase ({phase_a} or {phase_b}) should be prioritized based on current gap analysis results?",
         ["retrieval", "retrieval", "processing"], 3, 1, "Phase prioritization based on gaps"),
        ("cd_18", "Compare {framework_a} and {framework_b} standards for applicability to {domain}.",
         ["retrieval", "retrieval", "processing"], 2, 1, "Standards framework comparison"),
        ("cd_19", "Evaluate whether to extend {existing_system} or replace with {new_system} based on TCO and risk.",
         ["retrieval", "retrieval", "processing", "processing"], 3, 2, "Extend vs replace decision"),
        ("cd_20", "Which technology radar ring (adopt, trial, assess, hold) should {technology} be placed in?",
         ["retrieval", "retrieval", "processing"], 2, 1, "Technology radar classification decision"),
    ]

    return [Exemplar(
        id=t[0], family=ExemplarFamily.COMPARE_DECIDE, template=t[1],
        implied_pattern=t[2], complexity=t[3], required_tool_types=["retrieval", "processing"],
        description=t[5], sub_questions=t[4],
    ) for t in templates]


def _gap_analysis_exemplars() -> list[Exemplar]:
    """Gap analysis pattern exemplars."""
    templates = [
        ("ga_01", "Perform a full gap analysis for {domain} architecture, identifying all new, eliminated, and changed elements.",
         ["retrieval", "retrieval", "processing"], 3, 3, "Complete domain gap analysis"),
        ("ga_02", "Which elements are being eliminated in {domain} and what are the downstream dependencies affected?",
         ["retrieval", "retrieval", "processing", "processing"], 3, 2, "Elimination impact analysis"),
        ("ga_03", "Identify all gaps in {domain} where stakeholder concerns from {stakeholder} are not addressed.",
         ["retrieval", "retrieval", "retrieval", "processing"], 4, 2, "Stakeholder-concern gap analysis"),
        ("ga_04", "What are the cross-domain gaps between {domain_a} and {domain_b} architecture layers?",
         ["retrieval", "retrieval", "processing"], 3, 2, "Cross-domain gap analysis"),
        ("ga_05", "Compute consolidated gaps across all architecture domains for {project} and prioritize by risk.",
         ["retrieval", "retrieval", "retrieval", "processing", "processing"], 4, 3, "Consolidated multi-domain gap analysis"),
        ("ga_06", "Which gaps in {domain} can be addressed by existing building blocks vs. requiring new development?",
         ["retrieval", "retrieval", "processing"], 3, 2, "Gap to building block coverage analysis"),
        ("ga_07", "Identify gaps between the current {capability} capability maturity and the target maturity level.",
         ["retrieval", "retrieval", "processing"], 2, 1, "Capability maturity gap analysis"),
        ("ga_08", "What compliance gaps exist for {system} when transitioning from {standard_a} to {standard_b}?",
         ["retrieval", "retrieval", "retrieval", "processing"], 3, 2, "Standards transition gap analysis"),
        ("ga_09", "Perform gap analysis between {reference_model} reference model and the current {domain} architecture.",
         ["retrieval", "retrieval", "processing"], 3, 2, "Reference model gap analysis"),
        ("ga_10", "Identify security architecture gaps in the proposed {system} design against {security_standard}.",
         ["retrieval", "retrieval", "processing"], 3, 2, "Security gap analysis"),
        ("ga_11", "What data architecture gaps exist between the current and target state for {domain}?",
         ["retrieval", "retrieval", "processing"], 3, 2, "Data architecture gap analysis"),
        ("ga_12", "Identify integration gaps when adding {new_system} to the existing {domain} ecosystem.",
         ["retrieval", "retrieval", "processing"], 3, 2, "Integration gap analysis for new system"),
        ("ga_13", "Analyze gaps in the {phase} deliverables against TOGAF requirements.",
         ["retrieval", "retrieval", "processing"], 2, 2, "ADM deliverable completeness gap analysis"),
        ("ga_14", "What organizational capability gaps exist to support the {initiative} transformation?",
         ["retrieval", "processing"], 2, 2, "Organizational capability gap analysis"),
        ("ga_15", "Identify gaps between current monitoring capabilities and the target observability architecture.",
         ["retrieval", "retrieval", "processing"], 3, 2, "Observability gap analysis"),
        ("ga_16", "Compute the gap analysis between existing APIs and the target API-first architecture for {domain}.",
         ["retrieval", "retrieval", "processing"], 3, 2, "API architecture gap analysis"),
        ("ga_17", "What gaps exist between the current disaster recovery capability and the target RTO/RPO objectives?",
         ["retrieval", "retrieval", "processing"], 3, 2, "DR capability gap analysis"),
        ("ga_18", "Identify gaps in the value stream {value_stream} between current and target capability mapping.",
         ["retrieval", "retrieval", "processing"], 3, 2, "Value stream capability gap analysis"),
        ("ga_19", "Analyze the gap between current team topology and the target operating model for {domain}.",
         ["retrieval", "processing"], 2, 2, "Team topology gap analysis"),
        ("ga_20", "What vendor/technology gaps exist in the current {domain} platform against the target reference architecture?",
         ["retrieval", "retrieval", "processing"], 3, 2, "Technology platform gap analysis"),
    ]

    return [Exemplar(
        id=t[0], family=ExemplarFamily.GAP_ANALYSIS, template=t[1],
        implied_pattern=t[2], complexity=t[3], required_tool_types=["retrieval", "processing"],
        description=t[5], sub_questions=t[4],
    ) for t in templates]


def _aggregate_exemplars() -> list[Exemplar]:
    """Retrieve → process → aggregate pattern exemplars."""
    templates = [
        ("ag_01", "Calculate the percentage of building block reuse across the {domain_a}, {domain_b}, and {domain_c} domains.",
         ["retrieval", "retrieval", "retrieval", "processing"], 3, 1, "Multi-domain building block reuse aggregation"),
        ("ag_02", "What is the distribution of risk levels (high/medium/low) across all systems in {domain}?",
         ["retrieval", "processing"], 2, 1, "Risk level distribution aggregation"),
        ("ag_03", "Compute the average architecture quality score across all {layer} layer components.",
         ["retrieval", "processing"], 2, 1, "Layer-wide quality score aggregation"),
        ("ag_04", "What percentage of applications in the portfolio are classified as each TIME category?",
         ["retrieval", "processing"], 2, 1, "Portfolio TIME classification distribution"),
        ("ag_05", "Summarize the total gap count by type (new, eliminated, changed) across all domains.",
         ["retrieval", "retrieval", "retrieval", "processing"], 3, 1, "Cross-domain gap count aggregation"),
        ("ag_06", "What is the compliance score distribution across all {count} systems against {standard}?",
         ["retrieval", "processing"], 2, 1, "Compliance score distribution"),
        ("ag_07", "Calculate the total estimated migration cost for all systems in the {phase} wave.",
         ["retrieval", "retrieval", "processing"], 3, 1, "Wave migration cost aggregation"),
        ("ag_08", "Summarize the stakeholder concern coverage across all Phase {phase} deliverables.",
         ["retrieval", "retrieval", "processing"], 3, 1, "Stakeholder concern coverage aggregation"),
        ("ag_09", "What is the mean technical debt score across all {domain} applications?",
         ["retrieval", "processing"], 2, 1, "Domain-wide technical debt aggregation"),
        ("ag_10", "Aggregate the capacity utilization across all infrastructure components in {domain}.",
         ["retrieval", "processing"], 2, 1, "Infrastructure utilization aggregation"),
        ("ag_11", "Compute the total number of dispensations by standard across the enterprise.",
         ["retrieval", "processing"], 2, 1, "Enterprise-wide dispensation aggregation"),
        ("ag_12", "What is the distribution of architecture decisions by status across all projects?",
         ["retrieval", "processing"], 2, 1, "Decision status distribution"),
        ("ag_13", "Calculate the weighted average maturity across all capabilities in the {value_stream} value stream.",
         ["retrieval", "retrieval", "processing"], 3, 1, "Value stream maturity aggregation"),
        ("ag_14", "Summarize the interface count and type distribution for all systems in {domain}.",
         ["retrieval", "processing"], 2, 1, "Interface distribution analysis"),
        ("ag_15", "What is the age distribution of technology components across the enterprise?",
         ["retrieval", "processing"], 2, 1, "Technology age distribution"),
        ("ag_16", "Aggregate the ROI projections across all active migration initiatives.",
         ["retrieval", "processing"], 2, 1, "Portfolio ROI aggregation"),
        ("ag_17", "Calculate the total work package count and resource allocation by roadmap wave.",
         ["retrieval", "processing"], 2, 1, "Roadmap wave resource aggregation"),
        ("ag_18", "What is the standard compliance coverage percentage by domain?",
         ["retrieval", "retrieval", "processing"], 3, 1, "Domain compliance coverage aggregation"),
        ("ag_19", "Summarize the viewpoint coverage — which ArchiMate viewpoints have been used vs. available?",
         ["retrieval", "processing"], 2, 1, "Viewpoint usage coverage analysis"),
        ("ag_20", "Calculate the cross-system dependency density metric for the {domain} application landscape.",
         ["retrieval", "processing"], 2, 1, "Dependency density aggregation"),
    ]

    return [Exemplar(
        id=t[0], family=ExemplarFamily.AGGREGATE, template=t[1],
        implied_pattern=t[2], complexity=t[3], required_tool_types=["retrieval", "processing"],
        description=t[5], sub_questions=t[4],
    ) for t in templates]


def _compliance_check_exemplars() -> list[Exemplar]:
    """Compliance check pattern exemplars."""
    templates = [
        ("cc_01", "Check {system} compliance against {standard_a} and {standard_b}. Report all critical and high violations.",
         ["retrieval", "retrieval", "retrieval", "processing"], 3, 2, "Multi-standard compliance check"),
        ("cc_02", "Verify that the proposed {building_block} design meets all {standard} requirements.",
         ["retrieval", "retrieval", "processing"], 3, 2, "Building block compliance verification"),
        ("cc_03", "Execute a compliance assessment for all systems in {domain} against {standard}. Which systems fail?",
         ["retrieval", "retrieval", "processing"], 3, 2, "Domain-wide compliance sweep"),
        ("cc_04", "Does the {transition_architecture} transition architecture introduce any new {standard} violations?",
         ["retrieval", "retrieval", "processing"], 3, 2, "Transition architecture compliance check"),
        ("cc_05", "Check if the dispensation for {system} regarding {standard} is still valid and what risks it introduces.",
         ["retrieval", "retrieval", "processing"], 3, 2, "Dispensation validity and risk check"),
        ("cc_06", "Verify the architecture contract for {project} against the actual implementation state.",
         ["retrieval", "retrieval", "processing"], 3, 2, "Contract compliance verification"),
        ("cc_07", "Execute a cross-standard compliance check: does {system} meet both {standard_a} and {standard_b}?",
         ["retrieval", "retrieval", "retrieval", "processing", "processing"], 4, 3, "Cross-standard compliance analysis"),
        ("cc_08", "Check if the data architecture for {system} complies with {privacy_standard} data residency requirements.",
         ["retrieval", "retrieval", "processing"], 3, 1, "Data residency compliance check"),
        ("cc_09", "Verify that all {phase} deliverables meet TOGAF compliance requirements.",
         ["retrieval", "retrieval", "processing"], 2, 2, "ADM deliverable compliance check"),
        ("cc_10", "Execute an architecture compliance review for {project} implementation against the approved architecture.",
         ["retrieval", "retrieval", "processing"], 3, 2, "Implementation compliance review"),
        ("cc_11", "Check if {system} meets the enterprise architecture principles for {category}.",
         ["retrieval", "retrieval", "processing"], 2, 2, "Principle compliance check"),
        ("cc_12", "Verify that all APIs in {domain} conform to the API design standards.",
         ["retrieval", "retrieval", "processing"], 3, 2, "API standards compliance check"),
        ("cc_13", "Execute a security compliance check for {system} against {security_standard} requirements.",
         ["retrieval", "retrieval", "processing"], 3, 2, "Security compliance verification"),
        ("cc_14", "Check compliance of {system} audit trail capabilities against {regulatory_standard}.",
         ["retrieval", "retrieval", "processing"], 3, 1, "Audit compliance check"),
        ("cc_15", "Verify that the migration plan for {system} complies with change management governance.",
         ["retrieval", "retrieval", "processing"], 2, 2, "Migration plan governance compliance"),
    ]

    return [Exemplar(
        id=t[0], family=ExemplarFamily.COMPLIANCE_CHECK, template=t[1],
        implied_pattern=t[2], complexity=t[3], required_tool_types=["retrieval", "processing"],
        description=t[5], sub_questions=t[4],
    ) for t in templates]


def _risk_assessment_exemplars() -> list[Exemplar]:
    """Risk assessment pattern exemplars."""
    templates = [
        ("ra_01", "Assess the risk of migrating {system} considering technology, data, integration, and organizational factors.",
         ["retrieval", "retrieval", "processing"], 3, 3, "Comprehensive migration risk assessment"),
        ("ra_02", "What is the combined risk score for the {transition_arch} transition architecture?",
         ["retrieval", "retrieval", "processing"], 3, 1, "Transition architecture risk scoring"),
        ("ra_03", "Identify the top 5 risk factors for the {initiative} initiative and their mitigation strategies.",
         ["retrieval", "retrieval", "processing"], 3, 2, "Initiative risk identification and mitigation"),
        ("ra_04", "Assess the risk of a compliance gap in {system} for {standard} and estimate remediation effort.",
         ["retrieval", "retrieval", "processing", "processing"], 3, 2, "Compliance gap risk assessment"),
        ("ra_05", "What are the cascading risks if {system} migration fails during Wave {wave}?",
         ["retrieval", "retrieval", "processing", "processing"], 4, 2, "Cascading failure risk analysis"),
        ("ra_06", "Compute risk scores for all systems in the {phase} migration wave and identify the highest-risk one.",
         ["retrieval", "processing"], 3, 2, "Wave risk ranking"),
        ("ra_07", "Assess the operational risk of running {system_a} and {system_b} in parallel during migration.",
         ["retrieval", "retrieval", "processing"], 3, 1, "Parallel run risk assessment"),
        ("ra_08", "What is the vendor lock-in risk for choosing {sbb} as the implementation for {abb}?",
         ["retrieval", "retrieval", "processing"], 2, 2, "Vendor lock-in risk analysis"),
        ("ra_09", "Assess the risk impact on {stakeholder} if {system} migration is delayed by {period}.",
         ["retrieval", "retrieval", "processing", "processing"], 3, 2, "Delay impact risk assessment"),
        ("ra_10", "Compute the aggregate risk exposure for the {program} program across all work packages.",
         ["retrieval", "processing"], 3, 1, "Program-wide risk aggregation"),
        ("ra_11", "Assess the data loss risk during migration from {source} to {target} for {data_type} data.",
         ["retrieval", "retrieval", "processing"], 3, 1, "Data migration risk assessment"),
        ("ra_12", "What is the risk of a single point of failure in the {domain} technology architecture?",
         ["retrieval", "processing"], 2, 1, "SPOF risk analysis"),
        ("ra_13", "Evaluate the security risk introduced by the new {interface} interface between {system_a} and {system_b}.",
         ["retrieval", "retrieval", "processing"], 3, 1, "Interface security risk evaluation"),
        ("ra_14", "Assess the organizational change management risk for the {transformation} transformation.",
         ["retrieval", "processing"], 2, 2, "Change management risk assessment"),
        ("ra_15", "What risks are introduced if the {dispensation} dispensation is extended beyond its expiry date?",
         ["retrieval", "retrieval", "processing"], 2, 2, "Dispensation extension risk analysis"),
    ]

    return [Exemplar(
        id=t[0], family=ExemplarFamily.RISK_ASSESSMENT, template=t[1],
        implied_pattern=t[2], complexity=t[3], required_tool_types=["retrieval", "processing"],
        description=t[5], sub_questions=t[4],
    ) for t in templates]


def _roadmap_planning_exemplars() -> list[Exemplar]:
    """Roadmap and migration planning exemplars."""
    templates = [
        ("rp_01", "Generate a migration roadmap for {system} with 3 waves based on dependencies and business priority.",
         ["retrieval", "retrieval", "retrieval", "processing"], 4, 3, "Multi-wave migration roadmap generation"),
        ("rp_02", "What is the optimal sequencing of work packages for the {initiative} initiative?",
         ["retrieval", "retrieval", "processing"], 3, 1, "Work package sequencing optimization"),
        ("rp_03", "In which roadmap wave should {building_block} be deployed given its dependencies?",
         ["retrieval", "retrieval", "processing"], 3, 1, "Building block deployment sequencing"),
        ("rp_04", "Generate a transition architecture sequence for moving from {current} to {target} with {count} plateaus.",
         ["retrieval", "retrieval", "processing"], 3, 2, "Transition architecture sequencing"),
        ("rp_05", "Does the current roadmap for {program} fit within the {budget} budget and {timeline} timeline?",
         ["retrieval", "processing", "processing"], 3, 2, "Roadmap feasibility check"),
        ("rp_06", "What is the critical path in the {program} migration roadmap and what are the slack activities?",
         ["retrieval", "processing"], 3, 2, "Critical path analysis"),
        ("rp_07", "Resequence the {program} roadmap to prioritize {standard} compliance remediation in Wave 1.",
         ["retrieval", "retrieval", "processing"], 3, 2, "Compliance-driven roadmap resequencing"),
        ("rp_08", "What dependencies need to be resolved before {work_package} can start?",
         ["retrieval", "retrieval", "processing"], 2, 1, "Dependency resolution analysis"),
        ("rp_09", "Generate a parallel execution plan for Waves {wave_a} and {wave_b} to compress the timeline.",
         ["retrieval", "processing"], 3, 2, "Parallel wave execution planning"),
        ("rp_10", "What happens to the roadmap if {work_package} is delayed by {weeks} weeks?",
         ["retrieval", "processing"], 3, 2, "Schedule impact analysis"),
        ("rp_11", "Create a phased rollout plan for {system} across {region_count} regions.",
         ["retrieval", "processing"], 3, 2, "Regional phased rollout planning"),
        ("rp_12", "What are the resource conflicts between Wave {wave_a} and Wave {wave_b} work packages?",
         ["retrieval", "retrieval", "processing"], 3, 1, "Resource conflict analysis"),
        ("rp_13", "Generate a rollback plan for Wave {wave} in case of critical issues during deployment.",
         ["retrieval", "processing"], 2, 2, "Rollback plan generation"),
        ("rp_14", "Compute the value delivered at each transition architecture plateau for {program}.",
         ["retrieval", "retrieval", "processing"], 3, 1, "Incremental value delivery analysis"),
        ("rp_15", "What quick wins can be extracted from the {program} roadmap for early delivery?",
         ["retrieval", "processing"], 2, 1, "Quick win identification"),
    ]

    return [Exemplar(
        id=t[0], family=ExemplarFamily.ROADMAP_PLANNING, template=t[1],
        implied_pattern=t[2], complexity=t[3], required_tool_types=["retrieval", "processing"],
        description=t[5], sub_questions=t[4],
    ) for t in templates]


def _stakeholder_analysis_exemplars() -> list[Exemplar]:
    """Stakeholder analysis pattern exemplars."""
    templates = [
        ("sa_01", "Map all stakeholder concerns for {project} and identify which are not addressed by current deliverables.",
         ["retrieval", "retrieval", "retrieval", "processing"], 4, 3, "Stakeholder concern coverage mapping"),
        ("sa_02", "Create a stakeholder power/interest grid for the {initiative} initiative.",
         ["retrieval", "processing"], 2, 1, "Power/interest grid generation"),
        ("sa_03", "Which stakeholders will be most impacted by the {change} architecture change?",
         ["retrieval", "retrieval", "processing"], 3, 2, "Change impact stakeholder analysis"),
        ("sa_04", "Generate a communication plan for the {program} program based on stakeholder concerns.",
         ["retrieval", "retrieval", "processing"], 3, 2, "Stakeholder communication plan"),
        ("sa_05", "Identify conflicting concerns between {stakeholder_a} and {stakeholder_b} for {project}.",
         ["retrieval", "retrieval", "processing"], 2, 2, "Concern conflict identification"),
        ("sa_06", "Which viewpoints should be presented to {stakeholder} based on their concerns?",
         ["retrieval", "retrieval", "processing"], 2, 1, "Viewpoint selection for stakeholder"),
        ("sa_07", "Map the {stakeholder} influence network and identify key alliance opportunities.",
         ["retrieval", "processing"], 2, 2, "Stakeholder influence network analysis"),
        ("sa_08", "What architecture artifacts should be reviewed by {stakeholder} in Phase {phase}?",
         ["retrieval", "retrieval", "processing"], 2, 2, "Stakeholder artifact review mapping"),
        ("sa_09", "Assess the level of stakeholder buy-in for the {initiative} initiative across all impacted groups.",
         ["retrieval", "retrieval", "processing"], 3, 1, "Stakeholder buy-in assessment"),
        ("sa_10", "Generate a RACI matrix for {project} architecture deliverables across stakeholder groups.",
         ["retrieval", "retrieval", "processing"], 3, 1, "RACI matrix generation"),
        ("sa_11", "Which executive stakeholders have concerns that conflict with the proposed {change}?",
         ["retrieval", "retrieval", "processing"], 3, 2, "Executive concern conflict analysis"),
        ("sa_12", "Map stakeholder concerns to architecture principles and identify principle gaps.",
         ["retrieval", "retrieval", "processing"], 3, 2, "Concern to principle coverage analysis"),
        ("sa_13", "Create an engagement timeline for {stakeholder} across all ADM phases for {project}.",
         ["retrieval", "retrieval", "processing"], 2, 1, "Stakeholder engagement timeline"),
        ("sa_14", "Identify all stakeholders who should be on the architecture board for {project}.",
         ["retrieval", "processing"], 2, 1, "Board membership recommendation"),
        ("sa_15", "Assess the impact of {decision} on each stakeholder group and recommend mitigation.",
         ["retrieval", "retrieval", "processing"], 3, 2, "Decision impact assessment per stakeholder"),
    ]

    return [Exemplar(
        id=t[0], family=ExemplarFamily.STAKEHOLDER_ANALYSIS, template=t[1],
        implied_pattern=t[2], complexity=t[3], required_tool_types=["retrieval", "processing"],
        description=t[5], sub_questions=t[4],
    ) for t in templates]


def _cost_benefit_exemplars() -> list[Exemplar]:
    """Cost-benefit analysis pattern exemplars."""
    templates = [
        ("cb_01", "Compute the full cost-benefit analysis for the {initiative} initiative over a {years}-year horizon.",
         ["retrieval", "retrieval", "processing"], 3, 3, "Multi-year cost-benefit analysis"),
        ("cb_02", "What is the break-even point for migrating {system} to {target_platform}?",
         ["retrieval", "retrieval", "processing"], 3, 1, "Migration break-even analysis"),
        ("cb_03", "Compare the TCO of {option_a} vs {option_b} for {use_case} over 5 years.",
         ["retrieval", "retrieval", "processing", "processing"], 3, 2, "TCO comparison analysis"),
        ("cb_04", "What is the cost of NOT migrating {system} (maintaining status quo) vs migrating?",
         ["retrieval", "retrieval", "processing", "processing"], 3, 2, "Status quo cost analysis"),
        ("cb_05", "Calculate the NPV and IRR for the {program} program given current cost projections.",
         ["retrieval", "processing"], 3, 2, "NPV and IRR computation"),
        ("cb_06", "What is the cost impact of adding {standard} compliance to the {system} migration scope?",
         ["retrieval", "retrieval", "processing"], 3, 1, "Compliance cost impact analysis"),
        ("cb_07", "Compute the opportunity cost of delaying {initiative} by {months} months.",
         ["retrieval", "processing"], 2, 1, "Delay opportunity cost analysis"),
        ("cb_08", "What is the projected ROI at each roadmap wave completion for {program}?",
         ["retrieval", "processing"], 3, 1, "Incremental ROI projection"),
        ("cb_09", "Calculate the cost avoidance from eliminating {count} legacy systems in Wave {wave}.",
         ["retrieval", "processing"], 2, 1, "Legacy elimination cost avoidance"),
        ("cb_10", "What is the cost impact of choosing a phased vs big-bang migration for {system}?",
         ["retrieval", "processing", "processing"], 3, 2, "Migration strategy cost comparison"),
        ("cb_11", "Compute the staffing cost for {program} assuming {fte} FTEs over {months} months.",
         ["retrieval", "processing"], 2, 1, "Program staffing cost computation"),
        ("cb_12", "What is the benefit realization timeline for the {initiative} initiative?",
         ["retrieval", "processing"], 2, 1, "Benefit realization timeline"),
        ("cb_13", "Calculate the risk-adjusted ROI for {initiative} considering a {risk_factor}% risk factor.",
         ["retrieval", "processing"], 2, 1, "Risk-adjusted ROI computation"),
        ("cb_14", "What is the infrastructure cost saving from consolidating {count} platforms into {target}?",
         ["retrieval", "processing"], 2, 1, "Platform consolidation savings"),
        ("cb_15", "Compute the total cost of compliance remediation for {standard} across all affected systems.",
         ["retrieval", "retrieval", "processing"], 3, 1, "Enterprise compliance remediation cost"),
    ]

    return [Exemplar(
        id=t[0], family=ExemplarFamily.COST_BENEFIT, template=t[1],
        implied_pattern=t[2], complexity=t[3], required_tool_types=["retrieval", "processing"],
        description=t[5], sub_questions=t[4],
    ) for t in templates]


def _complex_multi_step_exemplars() -> list[Exemplar]:
    """Complex multi-step exemplars combining multiple patterns (K=3 level)."""
    templates = [
        ("cx_01", "For {system}: (1) identify all SOX violations, (2) determine in which roadmap wave they get remediated, "
                  "(3) check if the payback period fits within Waves 1+2, (4) identify which approved SBB addresses the gap.",
         ["retrieval", "retrieval", "processing", "retrieval", "processing", "retrieval"], 5, 4,
         "Complex: compliance + roadmap + cost-benefit + building block cross-analysis"),
        ("cx_02", "For {domain} modernization: (1) compute gaps between current and target, (2) rank by risk score, "
                  "(3) map to stakeholder concerns, (4) generate a prioritized roadmap.",
         ["retrieval", "retrieval", "processing", "processing", "retrieval", "processing", "processing"], 5, 4,
         "Complex: gap analysis + risk + stakeholder + roadmap"),
        ("cx_03", "Assess the {system} migration: (1) current state and dependencies, (2) compliance gaps against {standard_a} and {standard_b}, "
                  "(3) cost-benefit with risk adjustment, (4) recommend migration wave placement.",
         ["retrieval", "retrieval", "processing", "processing", "processing", "processing"], 5, 4,
         "Complex: state assessment + compliance + cost-benefit + roadmap"),
        ("cx_04", "For the {initiative} initiative: (1) identify all affected stakeholders and their concerns, "
                  "(2) map concerns to architecture gaps, (3) compute remediation costs, (4) generate communication plan.",
         ["retrieval", "retrieval", "processing", "processing", "processing"], 5, 4,
         "Complex: stakeholder + gap + cost + communication"),
        ("cx_05", "Evaluate {building_block}: (1) which capabilities it supports, (2) compliance status, "
                  "(3) reuse potential across domains, (4) cost-benefit of standardizing it.",
         ["retrieval", "retrieval", "processing", "processing", "processing"], 5, 4,
         "Complex: capability + compliance + reuse + cost-benefit"),
        ("cx_06", "For {domain} platform: (1) assess current maturity across all capabilities, (2) identify capabilities below threshold, "
                  "(3) compute gap analysis for each, (4) generate migration roadmap with cost estimates.",
         ["retrieval", "processing", "retrieval", "processing", "processing", "processing"], 5, 4,
         "Complex: maturity + gaps + roadmap + cost"),
        ("cx_07", "Architecture review for {project}: (1) verify deliverable completeness for Phase {phase}, "
                  "(2) check compliance against architecture principles, (3) assess stakeholder concern coverage, (4) identify risks.",
         ["retrieval", "retrieval", "processing", "retrieval", "processing", "processing"], 5, 4,
         "Complex: deliverables + compliance + stakeholders + risk"),
        ("cx_08", "Technology refresh analysis for {domain}: (1) inventory all technology components with age, "
                  "(2) assess against technology radar, (3) compute technical debt, (4) generate refresh roadmap.",
         ["retrieval", "retrieval", "processing", "processing"], 4, 4,
         "Complex: inventory + radar + debt + roadmap"),
        ("cx_09", "Vendor evaluation for {abb}: (1) list candidate SBBs, (2) check compliance for each, "
                  "(3) compute TCO comparison, (4) assess vendor lock-in risk for each.",
         ["retrieval", "retrieval", "processing", "processing", "processing"], 5, 4,
         "Complex: SBB listing + compliance + cost + risk"),
        ("cx_10", "End-to-end {initiative} assessment: (1) transformation readiness, (2) cross-domain gap analysis, "
                  "(3) stakeholder impact assessment, (4) detailed cost-benefit with NPV/IRR, (5) phased roadmap.",
         ["retrieval", "processing", "retrieval", "processing", "retrieval", "processing", "processing", "processing"], 5, 5,
         "Complex: readiness + gaps + stakeholders + cost-benefit + roadmap"),
        ("cx_11", "Data governance assessment for {domain}: (1) catalog all data entities, (2) check classification compliance, "
                  "(3) identify data quality gaps, (4) compute remediation priority based on business impact.",
         ["retrieval", "retrieval", "processing", "processing", "processing"], 4, 4,
         "Complex: data catalog + compliance + quality + prioritization"),
        ("cx_12", "Integration architecture review for {system}: (1) map all interfaces and data flows, "
                  "(2) analyze bottlenecks and security gaps, (3) check API standards compliance, (4) recommend target architecture.",
         ["retrieval", "retrieval", "processing", "processing", "processing"], 5, 4,
         "Complex: interface mapping + analysis + compliance + recommendation"),
        ("cx_13", "Cloud migration assessment for {system}: (1) current state with dependencies, (2) workload analysis and cloud readiness, "
                  "(3) compliance check for cloud deployment, (4) cost comparison on-prem vs cloud, (5) migration roadmap.",
         ["retrieval", "retrieval", "processing", "processing", "processing", "processing"], 5, 5,
         "Complex: state + readiness + compliance + cost + roadmap"),
        ("cx_14", "Security architecture assessment for {domain}: (1) identify all sensitive data flows, (2) map security controls, "
                  "(3) check compliance against {security_standard}, (4) compute risk scores, (5) prioritize remediation.",
         ["retrieval", "retrieval", "retrieval", "processing", "processing", "processing"], 5, 5,
         "Complex: data flow + controls + compliance + risk + priority"),
        ("cx_15", "Portfolio rationalization for {domain}: (1) inventory all applications with metrics, (2) compute TIME classification, "
                  "(3) identify consolidation opportunities, (4) compute savings from rationalization, (5) generate transition roadmap.",
         ["retrieval", "processing", "processing", "processing", "processing"], 5, 5,
         "Complex: inventory + classification + consolidation + savings + roadmap"),
        ("cx_16", "Architecture principle compliance audit: (1) retrieve all principles, (2) check each domain for adherence, "
                  "(3) identify all violations with severity, (4) compute remediation effort and cost.",
         ["retrieval", "retrieval", "processing", "processing"], 4, 4,
         "Complex: principles + domain checks + violations + cost"),
        ("cx_17", "Value stream optimization for {value_stream}: (1) map current stages and capabilities, "
                  "(2) identify bottleneck stages, (3) gap analysis for each bottleneck, (4) compute improvement ROI.",
         ["retrieval", "retrieval", "processing", "processing", "processing"], 4, 4,
         "Complex: value stream + bottleneck + gaps + ROI"),
        ("cx_18", "M&A architecture due diligence for {company}: (1) assess technology landscape, "
                  "(2) identify integration complexity, (3) compliance gap analysis, (4) estimate integration cost and timeline.",
         ["retrieval", "retrieval", "processing", "processing", "processing"], 5, 4,
         "Complex: landscape + complexity + compliance + cost"),
        ("cx_19", "API strategy assessment for {domain}: (1) inventory current APIs, (2) compare against API design standards, "
                  "(3) assess API maturity, (4) identify monetization opportunities, (5) generate API roadmap.",
         ["retrieval", "retrieval", "processing", "processing", "processing"], 5, 5,
         "Complex: inventory + standards + maturity + monetization + roadmap"),
        ("cx_20", "Operating model transformation for {organization}: (1) assess current team topology, "
                  "(2) map capabilities to teams, (3) identify skill gaps, (4) design target operating model, (5) create transformation roadmap.",
         ["retrieval", "retrieval", "processing", "processing", "processing"], 5, 5,
         "Complex: topology + capability mapping + skills + design + roadmap"),
    ]

    return [Exemplar(
        id=t[0], family=ExemplarFamily.ROADMAP_PLANNING, template=t[1],
        implied_pattern=t[2], complexity=t[3], required_tool_types=["retrieval", "processing"],
        description=t[5], sub_questions=t[4],
    ) for t in templates]


def build_exemplar_pool() -> list[Exemplar]:
    """Builds the complete exemplar pool."""
    exemplars = []
    exemplars.extend(_retrieve_compute_exemplars())
    exemplars.extend(_multi_hop_retrieval_exemplars())
    exemplars.extend(_compare_decide_exemplars())
    exemplars.extend(_gap_analysis_exemplars())
    exemplars.extend(_aggregate_exemplars())
    exemplars.extend(_compliance_check_exemplars())
    exemplars.extend(_risk_assessment_exemplars())
    exemplars.extend(_roadmap_planning_exemplars())
    exemplars.extend(_stakeholder_analysis_exemplars())
    exemplars.extend(_cost_benefit_exemplars())
    exemplars.extend(_complex_multi_step_exemplars())
    return exemplars


def save_exemplar_pool(output_path: Path | None = None) -> tuple[Path, int]:
    """Builds and saves the exemplar pool. Returns (path, count)."""
    exemplars = build_exemplar_pool()
    path = output_path or Path("pools/exemplars/exemplar_pool.json")
    save_pool(exemplars, path)
    return path, len(exemplars)


if __name__ == "__main__":
    path, count = save_exemplar_pool()
    pool = build_exemplar_pool()
    by_family = {}
    for e in pool:
        fam = e.family.value
        by_family[fam] = by_family.get(fam, 0) + 1
    print(f"Exemplar pool saved to {path}: {count} exemplars")
    for fam, n in sorted(by_family.items()):
        print(f"  {fam}: {n}")
