"""Repository, Governance, and General domain reference tools."""
from __future__ import annotations
from typing import Any

# =====================================================================
# BIAN Service Domains
# =====================================================================
_BIAN_DOMAINS: dict[str, dict] = {
    "customer_offer": {"domain": "Customer Offer", "business_area": "Sales & Service", "description": "Manage the processing of a product offer to new/existing customers.", "service_operations": ["Initiate", "Evaluate", "Update", "Execute", "Request", "Retrieve"], "asset_type": "Customer Offer Procedure", "behavioral_qualifiers": ["Product Selection", "Pricing", "Disclosure", "Compliance"]},
    "customer_campaign_management": {"domain": "Customer Campaign Management", "business_area": "Sales & Service", "description": "Design and execute targeted customer campaigns across channels.", "service_operations": ["Create", "Update", "Execute", "Request", "Retrieve", "Control"], "asset_type": "Customer Campaign Management Plan", "behavioral_qualifiers": ["Campaign Design", "Execution", "Assessment", "Channel Management"]},
    "payment_order": {"domain": "Payment Order", "business_area": "Payments", "description": "Handle the processing and execution of payment transactions.", "service_operations": ["Initiate", "Update", "Execute", "Request", "Retrieve", "Control"], "asset_type": "Payment Order Transaction", "behavioral_qualifiers": ["Order Capture", "Execution", "Clearing", "Settlement", "Reporting"]},
    "payment_execution": {"domain": "Payment Execution", "business_area": "Payments", "description": "Process payment execution including clearing and settlement.", "service_operations": ["Initiate", "Update", "Execute", "Retrieve"], "asset_type": "Payment Execution Transaction", "behavioral_qualifiers": ["Mechanism Selection", "Payment Processing", "Clearing", "Settlement"]},
    "securities_trade": {"domain": "Securities Trade", "business_area": "Capital Markets", "description": "Manage securities trading operations including order management.", "service_operations": ["Initiate", "Update", "Execute", "Request", "Retrieve"], "asset_type": "Securities Trade Transaction", "behavioral_qualifiers": ["Order Capture", "Order Execution", "Position Management", "Allocation"]},
    "loan": {"domain": "Loan", "business_area": "Lending", "description": "Handle the complete lifecycle of loan products.", "service_operations": ["Initiate", "Update", "Execute", "Request", "Retrieve", "Control"], "asset_type": "Loan Facility", "behavioral_qualifiers": ["Origination", "Servicing", "Disbursement", "Repayment", "Collections"]},
    "credit_risk_assessment": {"domain": "Credit Risk Assessment", "business_area": "Risk Management", "description": "Assess and monitor credit risk for lending and trading.", "service_operations": ["Evaluate", "Execute", "Request", "Retrieve"], "asset_type": "Credit Risk Assessment", "behavioral_qualifiers": ["Scoring", "Rating", "Exposure Analysis", "Limit Setting"]},
    "customer_relationship_management": {"domain": "Customer Relationship Management", "business_area": "Sales & Service", "description": "Manage the overall customer relationship lifecycle.", "service_operations": ["Initiate", "Update", "Execute", "Request", "Retrieve"], "asset_type": "Customer Relationship Management Plan", "behavioral_qualifiers": ["Development", "Incident Management", "Contact", "Plan Management"]},
    "deposit_account": {"domain": "Current Account", "business_area": "Deposits & Lending", "description": "Manage current/checking account operations and servicing.", "service_operations": ["Initiate", "Update", "Execute", "Request", "Retrieve", "Control"], "asset_type": "Current Account Facility", "behavioral_qualifiers": ["Interest", "Service Fees", "Account Lien", "Account Sweep", "Payments"]},
    "savings_account": {"domain": "Savings Account", "business_area": "Deposits & Lending", "description": "Manage savings account products and operations.", "service_operations": ["Initiate", "Update", "Execute", "Request", "Retrieve"], "asset_type": "Savings Account Facility", "behavioral_qualifiers": ["Interest", "Service Fees", "Deposits", "Withdrawals"]},
    "card_financial_settlement": {"domain": "Card Financial Settlement", "business_area": "Cards", "description": "Process card transaction settlement and reconciliation.", "service_operations": ["Initiate", "Update", "Execute", "Retrieve"], "asset_type": "Card Financial Settlement Transaction", "behavioral_qualifiers": ["Payment", "Settlement", "Reconciliation", "Dispute"]},
    "regulatory_compliance": {"domain": "Regulatory Compliance", "business_area": "Risk & Compliance", "description": "Ensure compliance with regulatory requirements.", "service_operations": ["Evaluate", "Update", "Request", "Retrieve"], "asset_type": "Regulatory Compliance Assessment", "behavioral_qualifiers": ["Monitoring", "Assessment", "Reporting", "Remediation"]},
    "fraud_detection": {"domain": "Fraud Detection", "business_area": "Risk & Compliance", "description": "Detect and manage potential fraudulent activities.", "service_operations": ["Evaluate", "Execute", "Request", "Retrieve"], "asset_type": "Fraud Detection Analysis", "behavioral_qualifiers": ["Alert", "Case Management", "Resolution", "Prevention"]},
    "know_your_customer": {"domain": "Know Your Customer", "business_area": "Risk & Compliance", "description": "Manage KYC procedures for customer due diligence.", "service_operations": ["Initiate", "Evaluate", "Update", "Request", "Retrieve"], "asset_type": "KYC Procedure", "behavioral_qualifiers": ["Identity Verification", "Risk Assessment", "Screening", "Ongoing Monitoring"]},
    "market_risk": {"domain": "Market Risk", "business_area": "Risk Management", "description": "Assess and monitor market risk exposure.", "service_operations": ["Evaluate", "Execute", "Request", "Retrieve"], "asset_type": "Market Risk Assessment", "behavioral_qualifiers": ["VaR Calculation", "Stress Testing", "Sensitivity Analysis", "Limit Monitoring"]},
    "operational_risk": {"domain": "Operational Risk", "business_area": "Risk Management", "description": "Identify, assess, and manage operational risk events.", "service_operations": ["Evaluate", "Update", "Request", "Retrieve"], "asset_type": "Operational Risk Assessment", "behavioral_qualifiers": ["Risk Identification", "Loss Event Management", "KRI Monitoring", "Scenario Analysis"]},
    "trade_finance": {"domain": "Trade Finance", "business_area": "Corporate Banking", "description": "Process trade finance instruments (LC, guarantees, collections).", "service_operations": ["Initiate", "Update", "Execute", "Request", "Retrieve"], "asset_type": "Trade Finance Facility", "behavioral_qualifiers": ["Letter of Credit", "Documentary Collection", "Guarantee", "Financing"]},
    "corporate_lending": {"domain": "Corporate Lending", "business_area": "Corporate Banking", "description": "Manage corporate loan facilities and syndicated lending.", "service_operations": ["Initiate", "Update", "Execute", "Request", "Retrieve", "Control"], "asset_type": "Corporate Lending Facility", "behavioral_qualifiers": ["Origination", "Syndication", "Servicing", "Restructuring"]},
    "wealth_management": {"domain": "Wealth Management", "business_area": "Wealth & Asset Management", "description": "Provide wealth management advisory and portfolio services.", "service_operations": ["Initiate", "Update", "Execute", "Request", "Retrieve"], "asset_type": "Wealth Management Plan", "behavioral_qualifiers": ["Financial Planning", "Portfolio Management", "Advisory", "Reporting"]},
    "asset_management": {"domain": "Asset Management", "business_area": "Wealth & Asset Management", "description": "Manage investment portfolios and fund operations.", "service_operations": ["Initiate", "Update", "Execute", "Request", "Retrieve"], "asset_type": "Investment Portfolio", "behavioral_qualifiers": ["Portfolio Construction", "Trading", "NAV Calculation", "Reporting"]},
}

# =====================================================================
# Compliance Frameworks
# =====================================================================
_COMPLIANCE: dict[str, dict] = {
    "gdpr": {"standard": "GDPR", "full_name": "General Data Protection Regulation", "requirements": [{"id": "Art.5", "title": "Principles of Processing", "description": "Lawfulness, fairness, transparency, purpose limitation, data minimization, accuracy, storage limitation, integrity/confidentiality", "category": "principles"}, {"id": "Art.6", "title": "Lawfulness of Processing", "description": "Processing must have legal basis: consent, contract, legal obligation, vital interests, public task, legitimate interests", "category": "legal_basis"}, {"id": "Art.13-14", "title": "Information to Data Subject", "description": "Provide identity of controller, purposes, recipients, retention period, rights of data subject", "category": "transparency"}, {"id": "Art.15-22", "title": "Data Subject Rights", "description": "Right of access, rectification, erasure, restriction, portability, objection, automated decision-making", "category": "rights"}, {"id": "Art.25", "title": "Data Protection by Design and Default", "description": "Implement appropriate technical and organizational measures, pseudonymization, data minimization by default", "category": "design"}, {"id": "Art.32", "title": "Security of Processing", "description": "Implement appropriate security measures: encryption, pseudonymization, resilience, testing", "category": "security"}, {"id": "Art.33-34", "title": "Breach Notification", "description": "Notify supervisory authority within 72 hours, notify data subjects without undue delay for high risk", "category": "breach"}, {"id": "Art.35", "title": "Data Protection Impact Assessment", "description": "DPIA required when processing likely results in high risk to rights and freedoms", "category": "assessment"}, {"id": "Art.37-39", "title": "Data Protection Officer", "description": "Designate DPO for public authorities, large-scale processing, special categories", "category": "governance"}]},
    "pci_dss": {"standard": "PCI DSS", "full_name": "Payment Card Industry Data Security Standard", "requirements": [{"id": "Req.1", "title": "Network Security Controls", "description": "Install and maintain network security controls to protect cardholder data", "category": "network"}, {"id": "Req.2", "title": "Secure Configuration", "description": "Apply secure configurations to all system components", "category": "configuration"}, {"id": "Req.3", "title": "Protect Stored Account Data", "description": "Protect stored account data using encryption, truncation, masking, hashing", "category": "data_protection"}, {"id": "Req.4", "title": "Protect Data in Transit", "description": "Protect cardholder data with strong cryptography during transmission over open networks", "category": "encryption"}, {"id": "Req.5", "title": "Anti-Malware", "description": "Protect all systems and networks from malicious software", "category": "malware"}, {"id": "Req.6", "title": "Secure Development", "description": "Develop and maintain secure systems and software", "category": "development"}, {"id": "Req.7", "title": "Access Control", "description": "Restrict access to system components and cardholder data by business need-to-know", "category": "access"}, {"id": "Req.8", "title": "User Identification", "description": "Identify users and authenticate access to system components", "category": "authentication"}, {"id": "Req.9", "title": "Physical Access", "description": "Restrict physical access to cardholder data", "category": "physical"}, {"id": "Req.10", "title": "Logging and Monitoring", "description": "Log and monitor all access to system components and cardholder data", "category": "monitoring"}, {"id": "Req.11", "title": "Security Testing", "description": "Test security of systems and networks regularly", "category": "testing"}, {"id": "Req.12", "title": "Security Policy", "description": "Support information security with organizational policies and programs", "category": "policy"}]},
    "sox": {"standard": "SOX", "full_name": "Sarbanes-Oxley Act", "requirements": [{"id": "Sec.302", "title": "Corporate Responsibility for Financial Reports", "description": "CEO/CFO must certify financial statements accuracy and completeness", "category": "certification"}, {"id": "Sec.404", "title": "Internal Controls Assessment", "description": "Annual assessment of effectiveness of internal controls over financial reporting", "category": "controls"}, {"id": "Sec.409", "title": "Real-Time Disclosure", "description": "Disclose material changes in financial condition or operations on rapid/current basis", "category": "disclosure"}, {"id": "Sec.802", "title": "Document Retention", "description": "Criminal penalties for altering, destroying, or concealing records", "category": "retention"}]},
    "hipaa": {"standard": "HIPAA", "full_name": "Health Insurance Portability and Accountability Act", "requirements": [{"id": "Privacy", "title": "Privacy Rule", "description": "Protect individually identifiable health information (PHI) with permitted uses and disclosures", "category": "privacy"}, {"id": "Security", "title": "Security Rule", "description": "Administrative, physical, and technical safeguards for electronic PHI", "category": "security"}, {"id": "Breach", "title": "Breach Notification Rule", "description": "Notify individuals, HHS, and media (if >500) of unsecured PHI breaches", "category": "breach"}]},
    "basel_iii": {"standard": "Basel III", "full_name": "Basel III Capital Adequacy Framework", "requirements": [{"id": "Capital", "title": "Capital Requirements", "description": "Minimum CET1 4.5%, Tier 1 6%, Total Capital 8%, plus conservation buffer 2.5%", "category": "capital"}, {"id": "Leverage", "title": "Leverage Ratio", "description": "Minimum leverage ratio of 3% (Tier 1 capital / total exposure)", "category": "leverage"}, {"id": "LCR", "title": "Liquidity Coverage Ratio", "description": "High-quality liquid assets >= 100% of 30-day net cash outflows", "category": "liquidity"}, {"id": "NSFR", "title": "Net Stable Funding Ratio", "description": "Available stable funding >= required stable funding over 1 year", "category": "liquidity"}]},
    "iso_27001": {"standard": "ISO 27001", "full_name": "Information Security Management System", "requirements": [{"id": "A.5", "title": "Information Security Policies", "description": "Provide management direction for information security in accordance with business requirements", "category": "policy"}, {"id": "A.6", "title": "Organization of Information Security", "description": "Establish management framework for implementation and operation of ISMS", "category": "organization"}, {"id": "A.8", "title": "Asset Management", "description": "Identify organizational assets, define protection responsibilities, classify information", "category": "assets"}, {"id": "A.9", "title": "Access Control", "description": "Limit access to information and processing facilities based on business requirements", "category": "access"}]},
    "cobit": {"standard": "COBIT", "full_name": "Control Objectives for Information and Related Technologies", "requirements": [{"id": "EDM", "title": "Evaluate, Direct and Monitor", "description": "Governance objectives: ensure benefits delivery, risk optimization, resource optimization", "category": "governance"}, {"id": "APO", "title": "Align, Plan and Organize", "description": "Management of IT strategy, architecture, innovation, portfolio, budget, HR, relationships", "category": "management"}, {"id": "BAI", "title": "Build, Acquire and Implement", "description": "Management of programs, solutions, changes, assets, configuration, knowledge, availability", "category": "implementation"}, {"id": "DSS", "title": "Deliver, Service and Support", "description": "Management of operations, service requests, problems, continuity, security, controls", "category": "operations"}]},
    "itil": {"standard": "ITIL", "full_name": "Information Technology Infrastructure Library", "requirements": [{"id": "SVS", "title": "Service Value System", "description": "Guiding principles, governance, service value chain, practices, continual improvement", "category": "framework"}, {"id": "SVC", "title": "Service Value Chain", "description": "Plan, Improve, Engage, Design & Transition, Obtain/Build, Deliver & Support", "category": "value_chain"}, {"id": "Practices", "title": "34 Management Practices", "description": "General, Service, Technical management practices for end-to-end service management", "category": "practices"}]},
    "nist_csf": {"standard": "NIST CSF", "full_name": "NIST Cybersecurity Framework", "requirements": [{"id": "ID", "title": "Identify", "description": "Asset management, business environment, governance, risk assessment, risk management strategy", "category": "identify"}, {"id": "PR", "title": "Protect", "description": "Access control, awareness training, data security, information protection, maintenance, protective technology", "category": "protect"}, {"id": "DE", "title": "Detect", "description": "Anomalies and events, security continuous monitoring, detection processes", "category": "detect"}, {"id": "RS", "title": "Respond", "description": "Response planning, communications, analysis, mitigation, improvements", "category": "respond"}, {"id": "RC", "title": "Recover", "description": "Recovery planning, improvements, communications", "category": "recover"}]},
    "togaf_compliance": {"standard": "TOGAF Compliance", "full_name": "TOGAF Architecture Compliance Review", "requirements": [{"id": "AC1", "title": "Architecture Conformance", "description": "Verify implementation conforms to the defined architecture vision and specifications", "category": "conformance"}, {"id": "AC2", "title": "Standards Compliance", "description": "Ensure adherence to defined technology and architecture standards", "category": "standards"}, {"id": "AC3", "title": "Principles Compliance", "description": "Verify architecture decisions align with defined architecture principles", "category": "principles"}]},
    "fedramp": {"standard": "FedRAMP", "full_name": "Federal Risk and Authorization Management Program", "requirements": [{"id": "Low", "title": "Low Impact Controls", "description": "125 security controls for low-impact cloud systems", "category": "controls"}, {"id": "Moderate", "title": "Moderate Impact Controls", "description": "325 security controls for moderate-impact cloud systems", "category": "controls"}, {"id": "High", "title": "High Impact Controls", "description": "421 security controls for high-impact cloud systems", "category": "controls"}]},
    "ccpa": {"standard": "CCPA", "full_name": "California Consumer Privacy Act", "requirements": [{"id": "Rights", "title": "Consumer Rights", "description": "Right to know, delete, opt-out of sale, non-discrimination for exercising rights", "category": "rights"}, {"id": "Notice", "title": "Notice Requirements", "description": "Notice at collection, privacy policy, financial incentive notice", "category": "notice"}]},
    "dora": {"standard": "DORA", "full_name": "Digital Operational Resilience Act", "requirements": [{"id": "ICT-RM", "title": "ICT Risk Management", "description": "ICT risk management framework, identification, protection, detection, response, recovery", "category": "risk"}, {"id": "Incident", "title": "ICT Incident Management", "description": "Classification, reporting, and management of ICT-related incidents", "category": "incident"}, {"id": "Testing", "title": "Digital Operational Resilience Testing", "description": "Basic testing, advanced threat-led penetration testing (TLPT) for significant entities", "category": "testing"}, {"id": "TPP", "title": "Third-Party Risk", "description": "Manage ICT third-party provider risk, oversight framework for critical providers", "category": "third_party"}]},
    "nis2": {"standard": "NIS2", "full_name": "Network and Information Systems Directive 2", "requirements": [{"id": "RM", "title": "Risk Management Measures", "description": "Policies on risk analysis, incident handling, business continuity, supply chain security", "category": "risk"}, {"id": "Reporting", "title": "Incident Reporting", "description": "Early warning (24h), incident notification (72h), final report (1 month)", "category": "reporting"}]},
    "mifid2": {"standard": "MiFID II", "full_name": "Markets in Financial Instruments Directive II", "requirements": [{"id": "Trans", "title": "Transaction Reporting", "description": "Report transactions to competent authorities by T+1", "category": "reporting"}, {"id": "BestEx", "title": "Best Execution", "description": "Take all sufficient steps to obtain best possible result for clients", "category": "conduct"}, {"id": "Governance", "title": "Product Governance", "description": "Product approval process, target market identification, distribution strategy", "category": "governance"}]},
    "psd2": {"standard": "PSD2", "full_name": "Payment Services Directive 2", "requirements": [{"id": "SCA", "title": "Strong Customer Authentication", "description": "Two-factor authentication for electronic payments using knowledge, possession, inherence", "category": "authentication"}, {"id": "OpenBanking", "title": "Open Banking APIs", "description": "Account Servicing Payment Service Providers must provide APIs for third-party access", "category": "access"}, {"id": "Security", "title": "Operational Security", "description": "Risk assessment, incident reporting, secure communication channels", "category": "security"}]},
}

# =====================================================================
# Reference Models
# =====================================================================
_REFERENCE_MODELS: dict[str, dict] = {
    "trm": {"model_name": "TOGAF TRM", "description": "TOGAF Technical Reference Model — taxonomy of platform services", "components": [{"name": "Data Interchange Services", "layer": "platform"}, {"name": "Data Management Services", "layer": "platform"}, {"name": "Graphics and Imaging Services", "layer": "platform"}, {"name": "International Operation Services", "layer": "platform"}, {"name": "Location and Directory Services", "layer": "platform"}, {"name": "Network Services", "layer": "platform"}, {"name": "Operating System Services", "layer": "platform"}, {"name": "Security Services", "layer": "platform"}, {"name": "Software Engineering Services", "layer": "platform"}, {"name": "Transaction Processing Services", "layer": "platform"}, {"name": "User Interface Services", "layer": "platform"}], "mappings": ["Maps to Application Platform entity in TOGAF metamodel"]},
    "iii_rm": {"model_name": "TOGAF III-RM", "description": "Integrated Information Infrastructure Reference Model", "components": [{"name": "Brokering Applications", "layer": "application"}, {"name": "Development Tools", "layer": "application"}, {"name": "Application Server", "layer": "infrastructure"}, {"name": "Business Logic Services", "layer": "infrastructure"}, {"name": "Infrastructure Applications", "layer": "infrastructure"}, {"name": "Qualities of Service", "layer": "infrastructure"}], "mappings": ["Maps boundaryless information flow concepts", "Connects to TRM platform services"]},
    "soa_ra": {"model_name": "SOA Reference Architecture", "description": "Service-Oriented Architecture reference layers", "components": [{"name": "Consumer Layer", "layer": "presentation"}, {"name": "Business Process Layer", "layer": "process"}, {"name": "Service Layer", "layer": "service"}, {"name": "Service Component Layer", "layer": "component"}, {"name": "Operational Systems Layer", "layer": "systems"}, {"name": "Integration Layer (ESB)", "layer": "infrastructure"}, {"name": "Quality of Service Layer", "layer": "cross-cutting"}, {"name": "Governance Layer", "layer": "cross-cutting"}], "mappings": ["Maps to ArchiMate service and application layers"]},
    "cloud_ra": {"model_name": "Cloud Reference Architecture", "description": "NIST Cloud Computing Reference Architecture", "components": [{"name": "Cloud Consumer", "layer": "consumer"}, {"name": "Cloud Provider (SaaS/PaaS/IaaS)", "layer": "provider"}, {"name": "Cloud Broker", "layer": "broker"}, {"name": "Cloud Auditor", "layer": "auditor"}, {"name": "Cloud Carrier", "layer": "carrier"}], "mappings": ["Maps deployment models: public, private, hybrid, community"]},
    "security_ra": {"model_name": "Security Reference Architecture", "description": "Enterprise security reference architecture layers", "components": [{"name": "Identity & Access Management", "layer": "security"}, {"name": "Data Protection", "layer": "security"}, {"name": "Application Security", "layer": "security"}, {"name": "Network Security", "layer": "security"}, {"name": "Endpoint Security", "layer": "security"}, {"name": "Security Operations (SOC)", "layer": "operations"}, {"name": "Governance, Risk & Compliance", "layer": "governance"}], "mappings": ["Maps to NIST CSF functions: Identify, Protect, Detect, Respond, Recover"]},
    "integration_ra": {"model_name": "Integration Reference Architecture", "description": "Enterprise integration patterns and layers", "components": [{"name": "API Gateway", "layer": "edge"}, {"name": "Event Broker / Messaging", "layer": "middleware"}, {"name": "Integration Platform", "layer": "middleware"}, {"name": "Data Integration / ETL", "layer": "data"}, {"name": "B2B Gateway", "layer": "external"}], "mappings": ["Enterprise Integration Patterns (Hohpe/Woolf)", "Maps to technology layer in ArchiMate"]},
    "data_ra": {"model_name": "Data Reference Architecture", "description": "Enterprise data management reference layers", "components": [{"name": "Data Sources", "layer": "ingestion"}, {"name": "Data Lake / Warehouse", "layer": "storage"}, {"name": "Data Processing (Batch/Stream)", "layer": "processing"}, {"name": "Data Governance & Catalog", "layer": "governance"}, {"name": "Data Consumption / Analytics", "layer": "consumption"}, {"name": "Master Data Management", "layer": "governance"}], "mappings": ["DAMA DMBOK knowledge areas"]},
    "bian": {"model_name": "BIAN Service Landscape", "description": "Banking Industry Architecture Network service domain model", "components": [{"name": "Sales & Service", "layer": "business_area"}, {"name": "Operations & Execution", "layer": "business_area"}, {"name": "Risk & Compliance", "layer": "business_area"}, {"name": "Corporate Banking", "layer": "business_area"}, {"name": "Wealth & Asset Management", "layer": "business_area"}, {"name": "Payments", "layer": "business_area"}], "mappings": ["300+ service domains organized by business area", "Maps to TOGAF business services and application components"]},
    "tmforum_oda": {"model_name": "TM Forum ODA", "description": "Open Digital Architecture for telecommunications", "components": [{"name": "Core Commerce", "layer": "functional"}, {"name": "Production", "layer": "functional"}, {"name": "Intelligence Management", "layer": "functional"}, {"name": "Engagement Management", "layer": "functional"}, {"name": "Party Management", "layer": "functional"}], "mappings": ["SID information model", "eTOM process framework", "TAM application map"]},
    "acord": {"model_name": "ACORD Reference Architecture", "description": "Association for Cooperative Operations Research and Development", "components": [{"name": "Policy Administration", "layer": "core"}, {"name": "Claims Management", "layer": "core"}, {"name": "Billing", "layer": "core"}, {"name": "Reinsurance", "layer": "core"}, {"name": "Data Standards (XML/JSON)", "layer": "standards"}], "mappings": ["Insurance industry data standards", "Maps to TOGAF business and application layers"]},
    "hl7_fhir": {"model_name": "HL7 FHIR", "description": "Fast Healthcare Interoperability Resources", "components": [{"name": "Patient Resource", "layer": "clinical"}, {"name": "Observation Resource", "layer": "clinical"}, {"name": "Encounter Resource", "layer": "workflow"}, {"name": "Medication Resource", "layer": "medication"}, {"name": "FHIR REST API", "layer": "infrastructure"}], "mappings": ["Healthcare interoperability standard", "RESTful API-based resource model"]},
}

# =====================================================================
# Standards
# =====================================================================
_STANDARDS: dict[str, dict] = {
    "security": {"type": "Security Standards", "standards": [{"name": "TLS 1.3", "scope": "Transport encryption"}, {"name": "AES-256", "scope": "Data encryption at rest"}, {"name": "OAuth 2.0 / OIDC", "scope": "API authentication and authorization"}, {"name": "OWASP Top 10", "scope": "Application security"}, {"name": "Zero Trust Architecture", "scope": "Network security model"}]},
    "integration": {"type": "Integration Standards", "standards": [{"name": "REST / OpenAPI 3.0", "scope": "Synchronous API design"}, {"name": "AsyncAPI", "scope": "Event-driven API design"}, {"name": "gRPC / Protocol Buffers", "scope": "High-performance RPC"}, {"name": "Apache Kafka", "scope": "Event streaming platform"}, {"name": "CloudEvents", "scope": "Event metadata standard"}]},
    "data": {"type": "Data Standards", "standards": [{"name": "ISO 8601", "scope": "Date and time formats"}, {"name": "ISO 4217", "scope": "Currency codes"}, {"name": "ISO 3166", "scope": "Country codes"}, {"name": "JSON Schema", "scope": "Data validation"}, {"name": "Apache Avro / Parquet", "scope": "Data serialization and storage"}]},
    "infrastructure": {"type": "Infrastructure Standards", "standards": [{"name": "Kubernetes", "scope": "Container orchestration"}, {"name": "Terraform / IaC", "scope": "Infrastructure as Code"}, {"name": "Prometheus / Grafana", "scope": "Monitoring and observability"}, {"name": "OCI (Container Images)", "scope": "Container image standard"}, {"name": "GitOps (ArgoCD/Flux)", "scope": "Deployment methodology"}]},
    "application": {"type": "Application Standards", "standards": [{"name": "12-Factor App", "scope": "Cloud-native application design"}, {"name": "Domain-Driven Design", "scope": "Software architecture"}, {"name": "CQRS / Event Sourcing", "scope": "Data management patterns"}, {"name": "Microservices", "scope": "Service decomposition"}, {"name": "CI/CD Pipelines", "scope": "Deployment automation"}]},
    "regulatory": {"type": "Regulatory Standards", "standards": [{"name": "GDPR", "scope": "Data privacy (EU)"}, {"name": "PCI DSS v4.0", "scope": "Payment card security"}, {"name": "SOX", "scope": "Financial reporting controls"}, {"name": "DORA", "scope": "Digital operational resilience (EU)"}]},
    "industry": {"type": "Industry Standards", "standards": [{"name": "BIAN", "scope": "Banking service domains"}, {"name": "ISO 20022", "scope": "Financial messaging"}, {"name": "SWIFT MT/MX", "scope": "Interbank messaging"}, {"name": "FIX Protocol", "scope": "Securities trading"}]},
}

# =====================================================================
# Business Capabilities (banking)
# =====================================================================
_CAPABILITIES: dict[str, list] = {
    "customer_management": [
        {"name": "Customer Onboarding", "level": 2, "sub_capabilities": ["KYC Verification", "Account Opening", "Product Enrollment", "Document Management"]},
        {"name": "Customer Service", "level": 2, "sub_capabilities": ["Case Management", "Channel Support", "Complaint Handling", "Service Requests"]},
        {"name": "Customer Analytics", "level": 2, "sub_capabilities": ["Segmentation", "Lifetime Value Analysis", "Churn Prediction", "Next Best Action"]},
    ],
    "lending": [
        {"name": "Loan Origination", "level": 2, "sub_capabilities": ["Application Processing", "Credit Assessment", "Decisioning", "Documentation"]},
        {"name": "Loan Servicing", "level": 2, "sub_capabilities": ["Payment Processing", "Statement Generation", "Interest Calculation", "Fee Management"]},
        {"name": "Collections", "level": 2, "sub_capabilities": ["Early Collections", "Late Collections", "Debt Recovery", "Write-off Management"]},
    ],
    "payments": [
        {"name": "Payment Processing", "level": 2, "sub_capabilities": ["Payment Initiation", "Payment Execution", "Clearing", "Settlement"]},
        {"name": "Card Services", "level": 2, "sub_capabilities": ["Card Issuance", "Transaction Authorization", "Fraud Detection", "Dispute Management"]},
    ],
    "risk_management": [
        {"name": "Credit Risk", "level": 2, "sub_capabilities": ["Credit Scoring", "Portfolio Analysis", "Provisioning", "Limit Management"]},
        {"name": "Market Risk", "level": 2, "sub_capabilities": ["VaR Calculation", "Stress Testing", "Sensitivity Analysis", "P&L Attribution"]},
        {"name": "Operational Risk", "level": 2, "sub_capabilities": ["Loss Event Management", "KRI Monitoring", "Scenario Analysis", "RCSA"]},
    ],
    "compliance": [
        {"name": "Regulatory Reporting", "level": 2, "sub_capabilities": ["Capital Adequacy", "Liquidity Reporting", "Transaction Reporting", "Statistical Reporting"]},
        {"name": "AML/KYC", "level": 2, "sub_capabilities": ["Transaction Monitoring", "Sanctions Screening", "Customer Due Diligence", "SAR Filing"]},
    ],
}

# =====================================================================
# TOGAF Artifacts Catalog (for search)
# =====================================================================
_ARTIFACTS = [
    {"name": "Architecture Vision", "category": "deliverable", "phase": "A", "description": "High-level aspirational view of end architecture"},
    {"name": "Stakeholder Map Matrix", "category": "artifact", "phase": "A", "description": "Stakeholder identification and concern mapping"},
    {"name": "Business Capability Map", "category": "artifact", "phase": "B", "description": "Hierarchical decomposition of business capabilities"},
    {"name": "Value Stream Map", "category": "artifact", "phase": "B", "description": "End-to-end value delivery activities"},
    {"name": "Organization Map", "category": "artifact", "phase": "B", "description": "Organizational units and relationships"},
    {"name": "Business Process Model", "category": "artifact", "phase": "B", "description": "Detailed business process flows (BPMN)"},
    {"name": "Application Portfolio Catalog", "category": "artifact", "phase": "C", "description": "Inventory of all applications with metadata"},
    {"name": "Data Entity Catalog", "category": "artifact", "phase": "C", "description": "Master list of data entities and ownership"},
    {"name": "Technology Standards Catalog", "category": "artifact", "phase": "D", "description": "Approved technology standards and products"},
    {"name": "Architecture Roadmap", "category": "deliverable", "phase": "E-F", "description": "Prioritized implementation plan with work packages"},
    {"name": "Gap Analysis Matrix", "category": "artifact", "phase": "B-D", "description": "Baseline vs target comparison with identified gaps"},
    {"name": "Architecture Contract", "category": "deliverable", "phase": "G", "description": "Agreement on deliverables and quality standards"},
    {"name": "Compliance Assessment", "category": "deliverable", "phase": "G", "description": "Architecture conformance review results"},
    {"name": "Architecture Requirements Specification", "category": "deliverable", "phase": "B-D", "description": "Quantitative statements for solution implementation"},
    {"name": "Architecture Definition Document", "category": "deliverable", "phase": "B-D", "description": "Core architectural artifacts and models"},
    {"name": "Implementation and Migration Plan", "category": "deliverable", "phase": "F", "description": "Detailed plan for transitioning to target architecture"},
    {"name": "Risk Register", "category": "artifact", "phase": "A-H", "description": "Identified risks with impact and mitigation strategies"},
    {"name": "Architecture Principles", "category": "artifact", "phase": "Preliminary", "description": "Guiding principles for architecture decisions"},
    {"name": "Business Interaction Matrix", "category": "artifact", "phase": "B", "description": "Inter-organizational interaction dependencies"},
    {"name": "Application Communication Diagram", "category": "artifact", "phase": "C", "description": "Application-to-application communication flows"},
]


def _fuzzy_match(query: str, text: str) -> bool:
    query_lower = query.lower()
    return any(word in text.lower() for word in query_lower.split() if len(word) > 2)


# =====================================================================
# Tool functions
# =====================================================================
def repo_search_artifacts(query: str = "", category: str = "", limit: int = 10, **kwargs) -> dict:
    results = [a for a in _ARTIFACTS if _fuzzy_match(query, f"{a['name']} {a['description']} {a['category']} {a['phase']}")]
    if category:
        results = [a for a in results if category.lower() in a["category"].lower()]
    return {"artifacts": results[:limit], "total": len(results)}


def repo_get_patterns(pattern_type: str = "", domain: str = "", **kwargs) -> dict:
    patterns = [
        {"name": "Layered Architecture", "type": "structural", "description": "Organize components into horizontal layers with defined responsibilities", "applicability": "Enterprise-wide separation of concerns"},
        {"name": "Microservices", "type": "structural", "description": "Decompose application into independently deployable services", "applicability": "Large-scale distributed systems"},
        {"name": "Event-Driven Architecture", "type": "integration", "description": "Use events to communicate between loosely coupled services", "applicability": "Asynchronous processing, complex event flows"},
        {"name": "API Gateway", "type": "integration", "description": "Single entry point for API consumers with cross-cutting concerns", "applicability": "API management, rate limiting, authentication"},
        {"name": "CQRS", "type": "data", "description": "Separate read and write models for different optimization", "applicability": "High-read or high-write workloads"},
        {"name": "Saga Pattern", "type": "integration", "description": "Manage distributed transactions through choreography or orchestration", "applicability": "Cross-service business transactions"},
        {"name": "Strangler Fig", "type": "migration", "description": "Gradually replace legacy system by routing traffic to new implementation", "applicability": "Legacy modernization"},
        {"name": "Anti-Corruption Layer", "type": "integration", "description": "Isolate subsystem from external model differences", "applicability": "Legacy integration, bounded contexts"},
    ]
    if pattern_type:
        patterns = [p for p in patterns if pattern_type.lower() in p["type"].lower()]
    return {"patterns": patterns, "total": len(patterns)}


def repo_get_principles(**kwargs) -> dict:
    return {"principles": [
        {"name": "Business Continuity", "statement": "Enterprise operations are maintained despite system interruptions", "rationale": "Business processes depend on architecture reliability", "implications": ["Disaster recovery required", "Redundancy in critical systems"]},
        {"name": "Data is an Asset", "statement": "Data is an asset that has value to the enterprise and is managed accordingly", "rationale": "Data enables better decision-making", "implications": ["Data governance required", "Data quality management", "Master data management"]},
        {"name": "Technology Independence", "statement": "Applications are independent of specific technology choices", "rationale": "Avoid vendor lock-in and enable technology evolution", "implications": ["Use open standards", "Abstract technology dependencies", "API-first design"]},
        {"name": "Common Use Applications", "statement": "Shared applications are preferred over per-unit custom solutions", "rationale": "Reduce cost and complexity through reuse", "implications": ["Shared services catalog", "Reuse assessments", "Standard platforms"]},
        {"name": "Service Orientation", "statement": "Architecture is based on services that mirror real-world business activities", "rationale": "Enable agility and composability", "implications": ["Service catalog", "API standards", "Loose coupling"]},
    ]}


def capability_catalog_search(query: str = "", **kwargs) -> dict:
    results = []
    for domain, caps in _CAPABILITIES.items():
        for cap in caps:
            if _fuzzy_match(query, f"{cap['name']} {domain} {' '.join(cap['sub_capabilities'])}"):
                results.append({**cap, "domain": domain})
    return {"capabilities": results, "total": len(results)}


def stakeholder_catalog_search(query: str = "", **kwargs) -> dict:
    stakeholders = [
        {"name": "CIO", "role": "Chief Information Officer", "concerns": ["IT strategy alignment", "Technology investment", "Digital transformation"]},
        {"name": "CTO", "role": "Chief Technology Officer", "concerns": ["Technology standards", "Platform strategy", "Innovation"]},
        {"name": "CISO", "role": "Chief Information Security Officer", "concerns": ["Security posture", "Compliance", "Risk management"]},
        {"name": "CDO", "role": "Chief Data Officer", "concerns": ["Data governance", "Data quality", "Analytics strategy"]},
        {"name": "Business Process Owner", "role": "Process Owner", "concerns": ["Process efficiency", "Automation", "Customer experience"]},
        {"name": "Enterprise Architect", "role": "Architecture Lead", "concerns": ["Architecture coherence", "Standards compliance", "Technical debt"]},
        {"name": "Solution Architect", "role": "Project Architect", "concerns": ["Solution design", "Technology selection", "Integration"]},
        {"name": "Project Manager", "role": "Delivery Lead", "concerns": ["Timeline", "Budget", "Resource allocation", "Risk"]},
    ]
    if query:
        stakeholders = [s for s in stakeholders if _fuzzy_match(query, f"{s['name']} {s['role']} {' '.join(s['concerns'])}")]
    return {"stakeholders": stakeholders, "total": len(stakeholders)}


def current_state_query(domain: str = "", **kwargs) -> dict:
    return {"state": "baseline", "description": "Current architecture state", "characteristics": ["Legacy monolithic systems", "Point-to-point integrations", "Manual processes", "Siloed data stores"], "maturity_level": 2, "key_issues": ["Technical debt", "Scalability limitations", "Data inconsistency", "High operational cost"]}


def target_state_query(domain: str = "", **kwargs) -> dict:
    return {"state": "target", "description": "Target architecture state", "characteristics": ["Cloud-native microservices", "Event-driven integration", "Automated workflows", "Unified data platform"], "maturity_level": 4, "key_benefits": ["Scalability", "Agility", "Cost optimization", "Data-driven decisions"]}


def governance_log_query(query: str = "", **kwargs) -> dict:
    return {"entries": [
        {"date": "2024-Q4", "type": "Architecture Board Decision", "description": "Approved cloud migration strategy for core banking", "status": "approved"},
        {"date": "2024-Q3", "type": "Dispensation", "description": "Temporary exception for legacy integration protocol", "status": "active", "expiry": "2025-Q2"},
        {"date": "2024-Q2", "type": "Compliance Review", "description": "Annual architecture compliance assessment completed", "status": "completed"},
    ], "total": 3}


def business_capability_model_query(domain: str = "", level: int = 2, **kwargs) -> dict:
    if domain and domain in _CAPABILITIES:
        caps = _CAPABILITIES[domain]
    else:
        caps = []
        for d, c in _CAPABILITIES.items():
            if not domain or _fuzzy_match(domain, d):
                caps.extend([{**cap, "domain": d} for cap in c])
    return {"capabilities": caps}


def application_portfolio_query(filter: str = "", status: str = "", **kwargs) -> dict:
    apps = [
        {"name": "Core Banking System", "type": "core", "status": "active", "technology": "Java/Oracle", "business_criticality": "high", "lifecycle_stage": "mature", "annual_cost": 2500000},
        {"name": "Internet Banking Portal", "type": "channel", "status": "active", "technology": "React/Node.js", "business_criticality": "high", "lifecycle_stage": "growing", "annual_cost": 800000},
        {"name": "Mobile Banking App", "type": "channel", "status": "active", "technology": "Flutter", "business_criticality": "high", "lifecycle_stage": "growing", "annual_cost": 600000},
        {"name": "Payment Gateway", "type": "integration", "status": "active", "technology": "Java/Kafka", "business_criticality": "critical", "lifecycle_stage": "mature", "annual_cost": 1200000},
        {"name": "CRM System", "type": "support", "status": "active", "technology": "Salesforce", "business_criticality": "medium", "lifecycle_stage": "mature", "annual_cost": 500000},
        {"name": "Legacy Loan System", "type": "core", "status": "retiring", "technology": "COBOL/DB2", "business_criticality": "high", "lifecycle_stage": "declining", "annual_cost": 1800000},
        {"name": "Data Warehouse", "type": "analytics", "status": "active", "technology": "Snowflake", "business_criticality": "medium", "lifecycle_stage": "growing", "annual_cost": 400000},
        {"name": "Risk Engine", "type": "core", "status": "active", "technology": "Python/Spark", "business_criticality": "critical", "lifecycle_stage": "growing", "annual_cost": 900000},
    ]
    if filter:
        apps = [a for a in apps if _fuzzy_match(filter, f"{a['name']} {a['type']} {a['technology']}")]
    if status:
        apps = [a for a in apps if a["status"] == status]
    return {"applications": apps}


def get_bian_service_domain(domain_name: str = "", business_area: str = "", **kwargs) -> dict:
    for key, data in _BIAN_DOMAINS.items():
        if domain_name.lower() in key.lower() or domain_name.lower() in data["domain"].lower():
            if not business_area or business_area.lower() in data["business_area"].lower():
                return data
    # Fuzzy search
    for key, data in _BIAN_DOMAINS.items():
        if _fuzzy_match(domain_name, f"{key} {data['domain']} {data['description']}"):
            return data
    return {"domain": domain_name, "error": "Not found", "available_domains": [d["domain"] for d in _BIAN_DOMAINS.values()]}


def get_tmforum_functional_block(block_name: str = "", **kwargs) -> dict:
    blocks = {
        "core_commerce": {"block": "Core Commerce Management", "functions": ["Product Offering", "Customer Management", "Sales Management", "Order Management", "Billing & Revenue"], "oda_component": "Core Commerce"},
        "production": {"block": "Production", "functions": ["Service Management", "Resource Management", "Network Management", "Partner Management"], "oda_component": "Production"},
        "engagement": {"block": "Engagement Management", "functions": ["Channel Management", "Marketing Management", "Interaction Management"], "oda_component": "Engagement"},
    }
    for key, data in blocks.items():
        if block_name.lower() in key.lower() or block_name.lower() in data["block"].lower():
            return data
    return {"block": block_name, "functions": [], "available_blocks": list(blocks.keys())}


def value_stream_query(stream_name: str = "", **kwargs) -> dict:
    return {"stream_name": stream_name or "Customer Onboarding", "stages": [
        {"name": "Acquisition", "description": "Attract and identify potential customers", "capabilities": ["Marketing", "Lead Management"]},
        {"name": "Application", "description": "Capture customer information and requirements", "capabilities": ["Application Processing", "Document Management"]},
        {"name": "Assessment", "description": "Evaluate customer eligibility and risk", "capabilities": ["KYC/AML", "Credit Assessment", "Risk Scoring"]},
        {"name": "Approval", "description": "Decision and approval workflow", "capabilities": ["Decisioning", "Compliance Check"]},
        {"name": "Fulfillment", "description": "Account/product setup and activation", "capabilities": ["Account Opening", "Product Enrollment", "Card Issuance"]},
        {"name": "Servicing", "description": "Ongoing customer service and support", "capabilities": ["Customer Service", "Transaction Processing", "Statement Generation"]},
    ]}


def integration_catalog_query(query: str = "", **kwargs) -> dict:
    integrations = [
        {"name": "Core Banking API", "type": "REST", "protocol": "HTTPS", "description": "Account operations and balance inquiries"},
        {"name": "Payment Hub", "type": "Event", "protocol": "Kafka", "description": "Payment processing event stream"},
        {"name": "SWIFT Interface", "type": "Messaging", "protocol": "MQ/SWIFT", "description": "International payment messaging"},
        {"name": "Credit Bureau Link", "type": "REST", "protocol": "HTTPS", "description": "Credit check and scoring"},
        {"name": "Regulatory Reporting Feed", "type": "Batch", "protocol": "SFTP", "description": "Daily/monthly regulatory data feeds"},
    ]
    if query:
        integrations = [i for i in integrations if _fuzzy_match(query, f"{i['name']} {i['description']}")]
    return {"integrations": integrations, "total": len(integrations)}


def data_catalog_query(query: str = "", **kwargs) -> dict:
    entities = [
        {"name": "Customer", "type": "master_data", "owner": "Customer Management", "classification": "PII", "storage": "Customer MDM"},
        {"name": "Account", "type": "master_data", "owner": "Core Banking", "classification": "confidential", "storage": "Core Banking DB"},
        {"name": "Transaction", "type": "transactional", "owner": "Payments", "classification": "confidential", "storage": "Transaction Store"},
        {"name": "Product", "type": "reference_data", "owner": "Product Management", "classification": "internal", "storage": "Product Catalog"},
        {"name": "Risk Score", "type": "derived", "owner": "Risk Management", "classification": "confidential", "storage": "Risk Engine DB"},
    ]
    if query:
        entities = [e for e in entities if _fuzzy_match(query, f"{e['name']} {e['type']} {e['owner']}")]
    return {"entities": entities, "total": len(entities)}


def maturity_assessment_query(domain: str = "", **kwargs) -> dict:
    return {"domain": domain or "Enterprise Architecture", "maturity_model": "ACMM", "levels": [
        {"level": 1, "name": "Initial", "description": "Ad-hoc, no formal process", "current": False},
        {"level": 2, "name": "Under Development", "description": "Basic processes defined", "current": True},
        {"level": 3, "name": "Defined", "description": "Standardized processes organization-wide", "current": False},
        {"level": 4, "name": "Managed", "description": "Measured and controlled processes", "current": False},
        {"level": 5, "name": "Optimizing", "description": "Continuous improvement integrated", "current": False},
    ], "current_level": 2, "target_level": 4}


def technology_radar_query(category: str = "", **kwargs) -> dict:
    return get_technology_radar(category=category, **kwargs)


def get_technology_radar(category: str = "", **kwargs) -> dict:
    items = [
        {"name": "Kubernetes", "ring": "Adopt", "quadrant": "Platforms", "description": "Container orchestration standard"},
        {"name": "Apache Kafka", "ring": "Adopt", "quadrant": "Platforms", "description": "Event streaming platform"},
        {"name": "GraphQL", "ring": "Trial", "quadrant": "Languages & Frameworks", "description": "API query language"},
        {"name": "WebAssembly", "ring": "Assess", "quadrant": "Languages & Frameworks", "description": "Portable execution format"},
        {"name": "Service Mesh (Istio)", "ring": "Trial", "quadrant": "Platforms", "description": "Microservice networking"},
        {"name": "eBPF", "ring": "Assess", "quadrant": "Techniques", "description": "Kernel-level observability"},
        {"name": "Platform Engineering", "ring": "Adopt", "quadrant": "Techniques", "description": "Internal developer platforms"},
        {"name": "AI-Assisted Development", "ring": "Trial", "quadrant": "Tools", "description": "LLM-powered code generation"},
    ]
    if category:
        items = [i for i in items if category.lower() in i["quadrant"].lower() or category.lower() in i["ring"].lower()]
    return {"items": items, "quadrants": ["Techniques", "Platforms", "Tools", "Languages & Frameworks"], "rings": ["Adopt", "Trial", "Assess", "Hold"]}


def portfolio_query_projects(filter: str = "", **kwargs) -> dict:
    return {"projects": [
        {"name": "Core Banking Modernization", "status": "in_progress", "phase": "E", "budget": 15000000, "timeline": "2024-2026", "priority": "critical"},
        {"name": "Open Banking API Platform", "status": "in_progress", "phase": "G", "budget": 3000000, "timeline": "2024-2025", "priority": "high"},
        {"name": "Data Lake Migration", "status": "planning", "phase": "F", "budget": 5000000, "timeline": "2025-2026", "priority": "high"},
        {"name": "Legacy Loan System Replacement", "status": "in_progress", "phase": "G", "budget": 8000000, "timeline": "2024-2026", "priority": "critical"},
        {"name": "Cloud Migration Phase 2", "status": "planning", "phase": "E", "budget": 4000000, "timeline": "2025-2027", "priority": "medium"},
    ]}


def compliance_get_requirements(standard: str = "", category: str = "", **kwargs) -> dict:
    data = _COMPLIANCE.get(standard, {})
    if not data:
        for key, val in _COMPLIANCE.items():
            if standard.lower() in key.lower() or standard.lower() in val.get("standard", "").lower():
                data = val
                break
    if not data:
        return {"standard": standard, "error": "Unknown standard", "available": list(_COMPLIANCE.keys())}
    result = {"standard": data["standard"], "full_name": data.get("full_name", ""), "requirements": data["requirements"]}
    if category:
        result["requirements"] = [r for r in result["requirements"] if category.lower() in r.get("category", "").lower()]
    return result


def repo_get_reference_model(model_name: str = "", detail_level: str = "summary", **kwargs) -> dict:
    data = _REFERENCE_MODELS.get(model_name, {})
    if not data:
        for key, val in _REFERENCE_MODELS.items():
            if model_name.lower() in key.lower():
                data = val
                break
    if not data:
        return {"model_name": model_name, "error": "Unknown model", "available": list(_REFERENCE_MODELS.keys())}
    return {"model_name": data["model_name"], "description": data["description"], "components": data["components"], "mappings": data["mappings"]}


def repo_get_standards(standard_type: str = "", detail_level: str = "summary", **kwargs) -> dict:
    data = _STANDARDS.get(standard_type, {})
    if not data:
        return {"standard_type": standard_type, "error": "Unknown type", "available": list(_STANDARDS.keys())}
    return {"standard_type": data["type"], "standards": data["standards"]}


def repo_get_building_block(block_type: str = "", **kwargs) -> dict:
    blocks = {
        "architecture_building_block": {"type": "Architecture Building Block (ABB)", "description": "A constituent of the architecture model that describes a single aspect of the overall model", "characteristics": ["Technology-agnostic", "Defines required capability", "Part of Architecture Continuum"], "examples": ["Customer Management Service", "Payment Processing Service", "Data Integration Service"]},
        "solution_building_block": {"type": "Solution Building Block (SBB)", "description": "A candidate solution component that maps to an ABB", "characteristics": ["Technology-specific", "Product/vendor-specific", "Part of Solutions Continuum"], "examples": ["Salesforce CRM", "Apache Kafka", "Oracle Database", "Kubernetes"]},
    }
    data = blocks.get(block_type, {})
    return data if data else {"type": block_type, "error": "Unknown block type"}


def governance_get_board_decisions(**kwargs) -> dict:
    return {"decisions": [
        {"id": "ABD-2024-001", "date": "2024-10-15", "title": "Cloud-First Strategy Adoption", "status": "approved", "impact": "All new applications must be cloud-native"},
        {"id": "ABD-2024-002", "date": "2024-08-20", "title": "API-First Integration Standard", "status": "approved", "impact": "All system integrations via REST/event APIs"},
        {"id": "ABD-2024-003", "date": "2024-06-10", "title": "Data Mesh Adoption for Analytics", "status": "under_review", "impact": "Decentralized data ownership with federated governance"},
    ]}


def governance_get_contracts(**kwargs) -> dict:
    return {"contracts": [
        {"id": "AC-2024-001", "project": "Core Banking Modernization", "status": "active", "compliance_level": "full", "review_date": "2025-Q1"},
        {"id": "AC-2024-002", "project": "Open Banking APIs", "status": "active", "compliance_level": "partial", "dispensations": 1, "review_date": "2025-Q2"},
    ]}


def governance_get_dispensations(**kwargs) -> dict:
    return {"dispensations": [
        {"id": "DISP-2024-001", "project": "Open Banking APIs", "reason": "Legacy protocol required for partner integration (SOAP)", "status": "active", "expiry": "2025-Q2", "conditions": ["Must migrate to REST by expiry", "Security review required"]},
    ]}


def _make_handler(fn, key_param: str, key_value: str):
    def handler(**kwargs):
        kwargs.pop(key_param, None)
        return fn(**{key_param: key_value, **kwargs})
    return handler


TOOL_REGISTRY: dict[str, Any] = {
    # 1:1 tools
    "repo_search_artifacts": repo_search_artifacts,
    "repo_get_patterns": repo_get_patterns,
    "repo_get_principles": repo_get_principles,
    "capability_catalog_search": capability_catalog_search,
    "stakeholder_catalog_search": stakeholder_catalog_search,
    "current_state_query": current_state_query,
    "target_state_query": target_state_query,
    "governance_log_query": governance_log_query,
    "business_capability_model_query": business_capability_model_query,
    "application_portfolio_query": application_portfolio_query,
    "get_bian_service_domain": get_bian_service_domain,
    "get_tmforum_functional_block": get_tmforum_functional_block,
    "value_stream_query": value_stream_query,
    "integration_catalog_query": integration_catalog_query,
    "data_catalog_query": data_catalog_query,
    "maturity_assessment_query": maturity_assessment_query,
    "technology_radar_query": technology_radar_query,
    "portfolio_query_projects": portfolio_query_projects,
    "get_technology_radar": get_technology_radar,
    "governance_get_board_decisions": governance_get_board_decisions,
    "governance_get_contracts": governance_get_contracts,
    "governance_get_dispensations": governance_get_dispensations,
}

# Building block variants
for _bb_key in ("architecture_building_block", "solution_building_block"):
    TOOL_REGISTRY[f"repo_get_building_block_{_bb_key}"] = _make_handler(repo_get_building_block, "block_type", _bb_key)

# Reference model variants
for _rm_key in _REFERENCE_MODELS:
    TOOL_REGISTRY[f"repo_get_reference_model_{_rm_key}"] = _make_handler(repo_get_reference_model, "model_name", _rm_key)

# Standards variants
for _std_key in _STANDARDS:
    TOOL_REGISTRY[f"repo_get_standards_{_std_key}"] = _make_handler(repo_get_standards, "standard_type", _std_key)

# Compliance variants
for _comp_key in _COMPLIANCE:
    TOOL_REGISTRY[f"compliance_get_requirements_{_comp_key}"] = _make_handler(compliance_get_requirements, "standard", _comp_key)
