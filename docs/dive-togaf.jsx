import { useState } from "react";

const phases = [
  {
    id: "pool",
    title: "1. Подготовка ресурсов",
    subtitle: "Diverse Synthesis Resource Preparation",
    color: "#0ea5e9",
    sections: [
      {
        name: "🔧 Tool Pool — 47 инструментов TOGAF-домена",
        content: (
          <div>
            <p style={{ marginBottom: 12, color: "var(--text-secondary)", lineHeight: 1.6 }}>
              По аналогии с DIVE, строим пул инструментов из двух примитивов: <strong style={{color:"#22d3ee"}}>Retrieval</strong> (получение данных) 
              и <strong style={{color:"#f472b6"}}>Processing</strong> (вычисление/трансформация). Оборачиваем реальные API и базы знаний TOGAF.
            </p>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
              <thead>
                <tr style={{ borderBottom: "2px solid #334155" }}>
                  <th style={{ padding: "8px 6px", textAlign: "left", color: "#94a3b8" }}>Категория</th>
                  <th style={{ padding: "8px 6px", textAlign: "left", color: "#22d3ee" }}>Retrieval</th>
                  <th style={{ padding: "8px 6px", textAlign: "left", color: "#f472b6" }}>Processing</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["ADM Phases", "adm_get_phase_details, adm_get_deliverables, adm_get_inputs_outputs", "adm_validate_phase_sequence"],
                  ["Architecture Repository", "repo_search_artifacts, repo_get_building_block, repo_get_reference_model, repo_get_standards", "repo_classify_artifact, repo_compute_reuse_score"],
                  ["ArchiMate Modeling", "archimate_get_element, archimate_search_viewpoints, archimate_get_relationships", "archimate_validate_model, archimate_compute_dependencies"],
                  ["Capability & Gap Analysis", "capability_catalog_search, business_capability_map, current_state_query", "gap_analysis_compute, maturity_assessment, capability_heat_map"],
                  ["Stakeholder Mgmt", "stakeholder_catalog_search, concern_registry_lookup, raci_matrix_query", "stakeholder_impact_analyze, power_interest_classify"],
                  ["Compliance & Governance", "architecture_compliance_rules, governance_log_search, dispensation_registry", "compliance_check_execute, risk_score_compute"],
                  ["Migration & Roadmap", "project_portfolio_query, transition_architecture_get, work_package_search", "roadmap_generate, dependency_sort, cost_benefit_analyze"],
                  ["General", "search_web, browse_page", "code_execution"],
                ].map(([cat, r, p], i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #1e293b" }}>
                    <td style={{ padding: "8px 6px", color: "#e2e8f0", fontWeight: 600, fontSize: 12 }}>{cat}</td>
                    <td style={{ padding: "8px 6px", color: "#67e8f9", fontSize: 11.5, fontFamily: "monospace" }}>{r}</td>
                    <td style={{ padding: "8px 6px", color: "#f9a8d4", fontSize: 11.5, fontFamily: "monospace" }}>{p}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ),
      },
      {
        name: "🌱 Seed Pool — ~2000 концептов TOGAF",
        content: (
          <div>
            <p style={{ marginBottom: 12, color: "var(--text-secondary)", lineHeight: 1.6 }}>
              Якорные концепты из спецификации TOGAF, ArchiMate, реальных кейсов. Каждый seed привязан к домену и запускает синтез в конкретной точке пространства знаний.
            </p>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              {[
                { domain: "ADM Phases", seeds: ["Phase B: Business Architecture", "Architecture Vision Stakeholder Map", "Preliminary Phase Governance", "Phase E Consolidation Gaps", "Phase H Architecture Change Request"] },
                { domain: "Паттерны", seeds: ["Zero Trust Reference Architecture", "Event-Driven Integration Pattern", "API Gateway Building Block", "Microservices Decomposition", "Data Mesh Topology"] },
                { domain: "Индустрии", seeds: ["Banking Core Modernization", "Healthcare FHIR Integration", "Telecom 5G Network Slicing", "Government GovStack", "Retail Omnichannel Platform"] },
                { domain: "Governance", seeds: ["Architecture Board Review Process", "TOGAF Compliance Assessment", "Dispensation Request Workflow", "Enterprise Continuum Classification", "Architecture Debt Register"] },
              ].map((g, i) => (
                <div key={i} style={{ background: "#0f172a", borderRadius: 8, padding: 12, border: "1px solid #1e293b" }}>
                  <div style={{ fontSize: 11, color: "#94a3b8", fontWeight: 700, marginBottom: 8, textTransform: "uppercase", letterSpacing: 1 }}>{g.domain}</div>
                  {g.seeds.map((s, j) => (
                    <div key={j} style={{ fontSize: 12.5, color: "#e2e8f0", padding: "3px 0", borderBottom: j < g.seeds.length - 1 ? "1px solid #1e293b" : "none" }}>
                      <span style={{ color: "#3b82f6", marginRight: 6 }}>→</span>{s}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>
        ),
      },
      {
        name: "📋 Exemplar Pool — 500 шаблонов задач",
        content: (
          <div>
            <p style={{ marginBottom: 12, color: "var(--text-secondary)", lineHeight: 1.6 }}>
              Задачи-образцы без привязки к инструментам. Каждый задаёт <em>структуру рассуждения</em> и <em>имплицитный паттерн вызовов</em>.
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {[
                { pattern: "Retrieve → Compare → Decide", ex: "Какой из двух reference models (TRM, III-RM) лучше подходит для интеграции legacy-систем банка? Сравните покрытие компонентов и выберите.", color: "#22d3ee" },
                { pattern: "Retrieve → Process → Aggregate", ex: "Для данного набора building blocks подсчитайте процент повторного использования по каждому домену архитектуры (Business, Data, Application, Technology).", color: "#a78bfa" },
                { pattern: "Multi-hop Retrieval → Gap Analysis", ex: "Найдите все stakeholder concerns из фазы A, сопоставьте с deliverables фазы B и определите, какие concerns не покрыты ни одним артефактом.", color: "#34d399" },
                { pattern: "Retrieve → Validate → Report", ex: "Проверьте, соответствует ли предложенная архитектура решения стандартам корпоративного Architecture Repository. Перечислите нарушения.", color: "#fb923c" },
                { pattern: "Retrieve → Compute → Rank", ex: "Среди всех transition architectures на текущей roadmap, какая имеет наилучшее соотношение cost/benefit при горизонте 3 года?", color: "#f472b6" },
              ].map((item, i) => (
                <div key={i} style={{ background: "#0f172a", borderRadius: 8, padding: "10px 14px", borderLeft: `3px solid ${item.color}` }}>
                  <div style={{ fontSize: 11, color: item.color, fontWeight: 700, marginBottom: 4, fontFamily: "monospace" }}>{item.pattern}</div>
                  <div style={{ fontSize: 12.5, color: "#cbd5e1", lineHeight: 1.5 }}>«{item.ex}»</div>
                </div>
              ))}
            </div>
          </div>
        ),
      },
    ],
  },
  {
    id: "evidence",
    title: "2. Evidence-Driven Synthesis",
    subtitle: "Цикл: Сбор улик → Вывод задач",
    color: "#8b5cf6",
    sections: [
      {
        name: "⚙️ Config Sampling — случайная конфигурация",
        content: (
          <div>
            <p style={{ marginBottom: 14, color: "var(--text-secondary)", lineHeight: 1.6 }}>
              Перед каждым циклом синтеза случайно выбираются: seed, toolset (15–47 инструментов) и 3–5 exemplars.
            </p>
            <div style={{ background: "#0f172a", borderRadius: 10, padding: 16, fontFamily: "monospace", fontSize: 12.5, lineHeight: 1.8, border: "1px solid #1e293b" }}>
              <div style={{ color: "#94a3b8" }}>{"// Пример конфигурации цикла #42"}</div>
              <div><span style={{ color: "#f472b6" }}>Seed</span>: <span style={{ color: "#fbbf24" }}>"Banking Core Modernization"</span></div>
              <div><span style={{ color: "#f472b6" }}>Toolset</span> <span style={{ color: "#64748b" }}>(22 из 47)</span>:</div>
              <div style={{ paddingLeft: 16, color: "#67e8f9" }}>
                [adm_get_phase_details, adm_get_deliverables,<br/>
                &nbsp;repo_search_artifacts, repo_get_building_block,<br/>
                &nbsp;repo_get_reference_model, repo_get_standards,<br/>
                &nbsp;archimate_get_element, archimate_get_relationships,<br/>
                &nbsp;archimate_compute_dependencies,<br/>
                &nbsp;capability_catalog_search, current_state_query,<br/>
                &nbsp;gap_analysis_compute, maturity_assessment,<br/>
                &nbsp;stakeholder_catalog_search, raci_matrix_query,<br/>
                &nbsp;stakeholder_impact_analyze,<br/>
                &nbsp;compliance_check_execute, risk_score_compute,<br/>
                &nbsp;project_portfolio_query, roadmap_generate,<br/>
                &nbsp;cost_benefit_analyze, code_execution]
              </div>
              <div><span style={{ color: "#f472b6" }}>Exemplars</span>:</div>
              <div style={{ paddingLeft: 16, color: "#a5f3fc" }}>
                1. "Retrieve → Compare → Decide" (сравнение моделей)<br/>
                2. "Multi-hop → Gap Analysis" (поиск непокрытых concerns)<br/>
                3. "Retrieve → Compute → Rank" (ранжирование)
              </div>
            </div>
          </div>
        ),
      },
      {
        name: "🔄 Итерация K=1: Первичный сбор и вывод",
        content: (
          <div>
            <div style={{ background: "#0c1425", borderRadius: 10, padding: 14, border: "1px solid #1e3a5f", marginBottom: 14 }}>
              <div style={{ color: "#22d3ee", fontWeight: 700, fontSize: 13, marginBottom: 10 }}>a. Evidence Collection (K=1)</div>
              <div style={{ fontSize: 12, color: "#94a3b8", marginBottom: 8 }}>Агент-коллектор исследует "Banking Core Modernization" с помощью реальных инструментов:</div>
              <div style={{ fontFamily: "monospace", fontSize: 11.5, lineHeight: 2 }}>
                <div style={{ color: "#64748b" }}>{"// Шаг 1: Reasoning"}</div>
                <div style={{ color: "#e2e8f0", background: "#1e293b", padding: "4px 8px", borderRadius: 4, marginBottom: 4 }}>
                  <span style={{ color: "#fbbf24" }}>{"<think>"}</span> Нужно найти, какие фазы ADM релевантны для банковской модернизации и какие артефакты они требуют...
                </div>
                <div style={{ color: "#64748b" }}>{"// Шаг 2: Tool call"}</div>
                <div style={{ background: "#0a2540", padding: "4px 8px", borderRadius: 4, marginBottom: 4, border: "1px solid #1e3a5f" }}>
                  <span style={{ color: "#22d3ee" }}>adm_get_phase_details</span>(<span style={{ color: "#fbbf24" }}>phase="B"</span>)<br/>
                  <span style={{ color: "#64748b" }}>→</span> <span style={{ color: "#34d399" }}>{"{ deliverables: ['Business Architecture Document', 'Organization Map', 'Business Interaction Matrix', ...], inputs: ['Architecture Vision', 'Stakeholder Map'], techniques: ['Business Capability Modeling', 'Value Stream Mapping'] }"}</span>
                </div>
                <div style={{ color: "#64748b" }}>{"// Шаг 3: Tool call"}</div>
                <div style={{ background: "#0a2540", padding: "4px 8px", borderRadius: 4, marginBottom: 4, border: "1px solid #1e3a5f" }}>
                  <span style={{ color: "#22d3ee" }}>capability_catalog_search</span>(<span style={{ color: "#fbbf24" }}>domain="banking", query="core systems"</span>)<br/>
                  <span style={{ color: "#64748b" }}>→</span> <span style={{ color: "#34d399" }}>{"{ capabilities: [{name: 'Payment Processing', maturity: 2, systems: ['SWIFT Gateway', 'Core Banking v3.1']}, {name: 'Customer Onboarding', maturity: 3, systems: ['CRM Portal', 'KYC Engine']}, {name: 'Loan Origination', maturity: 1, systems: ['Legacy COBOL LOS']}] }"}</span>
                </div>
                <div style={{ color: "#64748b" }}>{"// Шаг 4: Tool call"}</div>
                <div style={{ background: "#0a2540", padding: "4px 8px", borderRadius: 4, marginBottom: 4, border: "1px solid #1e3a5f" }}>
                  <span style={{ color: "#22d3ee" }}>repo_get_reference_model</span>(<span style={{ color: "#fbbf24" }}>name="TRM"</span>)<br/>
                  <span style={{ color: "#64748b" }}>→</span> <span style={{ color: "#34d399" }}>{"{ layers: ['Application Platform', 'Communications Infrastructure', 'Processing', 'Data Management'], components: 42, focus: 'technology standards' }"}</span>
                </div>
                <div style={{ color: "#64748b" }}>{"// Шаг 5: Tool call"}</div>
                <div style={{ background: "#0a2540", padding: "4px 8px", borderRadius: 4, marginBottom: 4, border: "1px solid #1e3a5f" }}>
                  <span style={{ color: "#22d3ee" }}>maturity_assessment</span>(<span style={{ color: "#fbbf24" }}>capabilities=["Payment Processing", "Customer Onboarding", "Loan Origination"]</span>)<br/>
                  <span style={{ color: "#64748b" }}>→</span> <span style={{ color: "#34d399" }}>{"{ scores: {payment: 2.1, onboarding: 3.4, loan: 1.2}, avg: 2.23, recommendation: 'Focus on Loan Origination (critical gap)' }"}</span>
                </div>
              </div>
            </div>
            <div style={{ background: "#1a0c25", borderRadius: 10, padding: 14, border: "1px solid #3b1e5f" }}>
              <div style={{ color: "#a78bfa", fontWeight: 700, fontSize: 13, marginBottom: 10 }}>c/d. Task Derivation (K=1)</div>
              <div style={{ fontSize: 12, color: "#94a3b8", marginBottom: 8 }}>Генератор задач наблюдает все улики и выводит пару (Q, A), строго опирающуюся на собранные данные:</div>
              <div style={{ background: "#0f172a", borderRadius: 8, padding: 12, border: "1px solid #334155" }}>
                <div style={{ fontSize: 12, color: "#fbbf24", fontWeight: 700, marginBottom: 6 }}>QUERY (K=1):</div>
                <div style={{ fontSize: 13, color: "#e2e8f0", lineHeight: 1.6, marginBottom: 10 }}>
                  В банке, проходящем модернизацию core-систем, три ключевые capability имеют maturity-уровни: Payment Processing (2.1), Customer Onboarding (3.4) и Loan Origination (1.2). 
                  Какая из capability имеет наименьший уровень зрелости и какой deliverable фазы B ADM должен быть разработан первым для адресации этого gap?
                </div>
                <div style={{ fontSize: 12, color: "#22d3ee", fontWeight: 700, marginBottom: 4 }}>ANSWER:</div>
                <div style={{ fontSize: 13, color: "#34d399", lineHeight: 1.5 }}>
                  Loan Origination (maturity 1.2); Business Architecture Document
                </div>
              </div>
            </div>
          </div>
        ),
      },
      {
        name: "🔄 Итерация K=2: Углубление и усложнение",
        content: (
          <div>
            <div style={{ background: "#0c1425", borderRadius: 10, padding: 14, border: "1px solid #1e3a5f", marginBottom: 14 }}>
              <div style={{ color: "#22d3ee", fontWeight: 700, fontSize: 13, marginBottom: 10 }}>a. Evidence Collection (K=2)</div>
              <div style={{ fontSize: 12, color: "#94a3b8", marginBottom: 8 }}>Коллектор получает предыдущий query как контекст и расширяет исследование:</div>
              <div style={{ fontFamily: "monospace", fontSize: 11.5, lineHeight: 2 }}>
                <div style={{ background: "#0a2540", padding: "4px 8px", borderRadius: 4, marginBottom: 4, border: "1px solid #1e3a5f" }}>
                  <span style={{ color: "#22d3ee" }}>current_state_query</span>(<span style={{ color: "#fbbf24" }}>capability="Loan Origination"</span>)<br/>
                  <span style={{ color: "#64748b" }}>→</span> <span style={{ color: "#34d399" }}>{"{ system: 'Legacy COBOL LOS', age: 23, interfaces: 4, monthly_txn: 12400, dependencies: ['Credit Bureau API', 'Document Management', 'Core Banking v3.1'] }"}</span>
                </div>
                <div style={{ background: "#0a2540", padding: "4px 8px", borderRadius: 4, marginBottom: 4, border: "1px solid #1e3a5f" }}>
                  <span style={{ color: "#22d3ee" }}>archimate_get_relationships</span>(<span style={{ color: "#fbbf24" }}>element="Legacy COBOL LOS"</span>)<br/>
                  <span style={{ color: "#64748b" }}>→</span> <span style={{ color: "#34d399" }}>{"{ serves: ['Loan Officers', 'Risk Department'], accesses: ['Customer DB', 'Loan Portfolio DB'], composed_of: ['Application Module', 'Batch Processing', 'Report Generator'] }"}</span>
                </div>
                <div style={{ background: "#0a2540", padding: "4px 8px", borderRadius: 4, marginBottom: 4, border: "1px solid #1e3a5f" }}>
                  <span style={{ color: "#22d3ee" }}>gap_analysis_compute</span>(<span style={{ color: "#fbbf24" }}>baseline="Legacy COBOL LOS", target="Cloud-native LOS"</span>)<br/>
                  <span style={{ color: "#64748b" }}>→</span> <span style={{ color: "#34d399" }}>{"{ gaps: [{type: 'new', desc: 'API Gateway for partners'}, {type: 'eliminated', desc: 'Batch Processing'}, {type: 'changed', desc: 'Report Generator → Real-time Dashboard'}], gap_count: 3 }"}</span>
                </div>
                <div style={{ background: "#0a2540", padding: "4px 8px", borderRadius: 4, marginBottom: 4, border: "1px solid #1e3a5f" }}>
                  <span style={{ color: "#22d3ee" }}>stakeholder_catalog_search</span>(<span style={{ color: "#fbbf24" }}>domain="Loan Origination"</span>)<br/>
                  <span style={{ color: "#64748b" }}>→</span> <span style={{ color: "#34d399" }}>{"{ stakeholders: [{name: 'CTO', concern: 'technical debt'}, {name: 'Head of Lending', concern: 'regulatory compliance'}, {name: 'CFO', concern: 'migration cost'}] }"}</span>
                </div>
                <div style={{ background: "#0a2540", padding: "4px 8px", borderRadius: 4, marginBottom: 4, border: "1px solid #1e3a5f" }}>
                  <span style={{ color: "#f472b6" }}>risk_score_compute</span>(<span style={{ color: "#fbbf24" }}>system="Legacy COBOL LOS", factors=["age", "dependencies", "compliance"]</span>)<br/>
                  <span style={{ color: "#64748b" }}>→</span> <span style={{ color: "#34d399" }}>{"{ risk_score: 8.7, category: 'Critical', factors: {age: 9, dependencies: 7, compliance: 10} }"}</span>
                </div>
              </div>
            </div>
            <div style={{ background: "#1a0c25", borderRadius: 10, padding: 14, border: "1px solid #3b1e5f" }}>
              <div style={{ color: "#a78bfa", fontWeight: 700, fontSize: 13, marginBottom: 10 }}>c/d. Task Derivation (K=2) — усложнённая задача</div>
              <div style={{ background: "#0f172a", borderRadius: 8, padding: 12, border: "1px solid #334155" }}>
                <div style={{ fontSize: 12, color: "#fbbf24", fontWeight: 700, marginBottom: 6 }}>EVOLVED QUERY (K=2):</div>
                <div style={{ fontSize: 13, color: "#e2e8f0", lineHeight: 1.6, marginBottom: 10 }}>
                  Банк модернизирует систему Loan Origination (legacy COBOL, 23 года, maturity 1.2). 
                  Gap-анализ между текущей и целевой (cloud-native) архитектурой выявил 3 gap-элемента. 
                  Среди stakeholder concerns есть "regulatory compliance" (Head of Lending) и "migration cost" (CFO). 
                  Риск-скор системы — 8.7 (Critical), причём фактор compliance имеет максимальный балл 10.
                  <br/><br/>
                  (1) Сколько gap-элементов типа "new" (требующих создания с нуля) выявлено и каков их характер?<br/>
                  (2) Какой stakeholder, скорее всего, будет наиболее обеспокоен наличием gap типа "eliminated" и почему?<br/>
                  (3) Учитывая, что compliance-фактор = 10, а concern Head of Lending — "regulatory compliance", 
                  какой deliverable фазы B следует приоритизировать для адресации этого пересечения?
                </div>
                <div style={{ fontSize: 12, color: "#22d3ee", fontWeight: 700, marginBottom: 4 }}>EVOLVED ANSWER:</div>
                <div style={{ fontSize: 13, color: "#34d399", lineHeight: 1.6 }}>
                  (1) 1 gap типа "new": API Gateway for partners.<br/>
                  (2) CFO — ликвидация Batch Processing снижает затраты на миграцию, что адресует его concern "migration cost".<br/>
                  (3) Business Interaction Matrix — документирует взаимодействие между подразделениями и регуляторными требованиями, напрямую адресуя concern Head of Lending.
                </div>
              </div>
            </div>
          </div>
        ),
      },
      {
        name: "🔄 Итерация K=3: Финальная комплексная задача",
        content: (
          <div>
            <div style={{ background: "#0c1425", borderRadius: 10, padding: 14, border: "1px solid #1e3a5f", marginBottom: 14 }}>
              <div style={{ color: "#22d3ee", fontWeight: 700, fontSize: 13, marginBottom: 10 }}>a. Evidence Collection (K=3) — ещё глубже</div>
              <div style={{ fontFamily: "monospace", fontSize: 11.5, lineHeight: 2 }}>
                <div style={{ background: "#0a2540", padding: "4px 8px", borderRadius: 4, marginBottom: 4, border: "1px solid #1e3a5f" }}>
                  <span style={{ color: "#22d3ee" }}>repo_get_building_block</span>(<span style={{ color: "#fbbf24" }}>type="SBB", domain="loan origination"</span>)<br/>
                  <span style={{ color: "#64748b" }}>→</span> <span style={{ color: "#34d399" }}>{"{ blocks: [{name: 'Cloud LOS Microservice', type: 'SBB', status: 'proposed', implements: 'ABB-LoanProcessing'}, {name: 'API Gateway v2', type: 'SBB', status: 'approved', implements: 'ABB-IntegrationLayer'}] }"}</span>
                </div>
                <div style={{ background: "#0a2540", padding: "4px 8px", borderRadius: 4, marginBottom: 4, border: "1px solid #1e3a5f" }}>
                  <span style={{ color: "#22d3ee" }}>compliance_check_execute</span>(<span style={{ color: "#fbbf24" }}>block="Cloud LOS Microservice", standards=["PCI-DSS", "SOX"]</span>)<br/>
                  <span style={{ color: "#64748b" }}>→</span> <span style={{ color: "#34d399" }}>{"{ results: [{standard: 'PCI-DSS', status: 'compliant'}, {standard: 'SOX', status: 'non-compliant', violations: ['audit trail gaps', 'data retention <7yr']}] }"}</span>
                </div>
                <div style={{ background: "#0a2540", padding: "4px 8px", borderRadius: 4, marginBottom: 4, border: "1px solid #1e3a5f" }}>
                  <span style={{ color: "#f472b6" }}>cost_benefit_analyze</span>(<span style={{ color: "#fbbf24" }}>project="LOS Migration", horizon=3</span>)<br/>
                  <span style={{ color: "#64748b" }}>→</span> <span style={{ color: "#34d399" }}>{"{ total_cost: 4.2M, total_benefit: 7.8M, roi: 85.7, payback_months: 22, npv: 2.1M }"}</span>
                </div>
                <div style={{ background: "#0a2540", padding: "4px 8px", borderRadius: 4, marginBottom: 4, border: "1px solid #1e3a5f" }}>
                  <span style={{ color: "#f472b6" }}>roadmap_generate</span>(<span style={{ color: "#fbbf24" }}>gaps=[...], constraints=["SOX compliance first"]</span>)<br/>
                  <span style={{ color: "#64748b" }}>→</span> <span style={{ color: "#34d399" }}>{"{ phases: [{name: 'Wave 1', duration: '6mo', items: ['SOX remediation', 'Audit trail implementation']}, {name: 'Wave 2', duration: '9mo', items: ['Cloud LOS deployment', 'API Gateway integration']}, {name: 'Wave 3', duration: '3mo', items: ['Legacy decommission', 'Batch elimination']}] }"}</span>
                </div>
              </div>
            </div>
            <div style={{ background: "#1a0c25", borderRadius: 10, padding: 14, border: "1px solid #3b1e5f" }}>
              <div style={{ color: "#a78bfa", fontWeight: 700, fontSize: 13, marginBottom: 10 }}>📦 Финальная DIVE-задача (K=3)</div>
              <div style={{ background: "#0f172a", borderRadius: 8, padding: 14, border: "1px solid #334155" }}>
                <div style={{ fontSize: 12, color: "#fbbf24", fontWeight: 700, marginBottom: 6 }}>FINAL QUERY:</div>
                <div style={{ fontSize: 13, color: "#e2e8f0", lineHeight: 1.7, marginBottom: 12 }}>
                  Банк проводит модернизацию системы Loan Origination (legacy COBOL, 23 года, risk score 8.7/10, compliance factor = 10). 
                  Gap-анализ выявил необходимость API Gateway (gap: new), ликвидацию Batch Processing (gap: eliminated) и замену Report Generator на Real-time Dashboard (gap: changed). 
                  Предложен Solution Building Block "Cloud LOS Microservice" (статус: proposed), который прошёл проверку PCI-DSS (compliant), но не прошёл SOX (violations: audit trail gaps, data retention {"<"}7yr).
                  <br/><br/>
                  Roadmap миграции состоит из 3 волн. Cost-benefit анализ показывает ROI 85.7% при горизонте 3 года и payback period 22 месяца.
                  <br/><br/>
                  (1) Какие два нарушения SOX должны быть устранены в Wave 1 перед развёртыванием Cloud LOS?<br/>
                  (2) В какой волне происходит ликвидация Batch Processing и совпадает ли это с gap-элементом типа "eliminated"?<br/>
                  (3) Учитывая ROI 85.7% и payback 22 мес., укладывается ли окупаемость в горизонт Wave 1 + Wave 2 (суммарно 15 мес.)? Ответьте да/нет и укажите разницу.<br/>
                  (4) Какой SBB со статусом "approved" готов к реализации и какой ABB он имплементирует?
                </div>
                <div style={{ fontSize: 12, color: "#22d3ee", fontWeight: 700, marginBottom: 4 }}>REFERENCE ANSWER:</div>
                <div style={{ fontSize: 13, color: "#34d399", lineHeight: 1.7 }}>
                  (1) audit trail gaps; data retention {"<"}7yr<br/>
                  (2) Wave 3; Да, совпадает — "Legacy decommission, Batch elimination" в Wave 3 = gap "eliminated" для Batch Processing.<br/>
                  (3) Нет, payback 22 мес. {">"} 15 мес. (Wave 1 + Wave 2). Разница: 7 месяцев.<br/>
                  (4) API Gateway v2, имплементирует ABB-IntegrationLayer.
                </div>
              </div>
              <div style={{ marginTop: 12, padding: "8px 12px", background: "#1e1b4b", borderRadius: 6, fontSize: 12, color: "#a5b4fc" }}>
                <strong>Stats:</strong> Calls: 12 | Available tools: 22 | Unique tools used: 9 | R/P topology: R+P/DAG/d3-4/w3-5
              </div>
            </div>
          </div>
        ),
      },
    ],
  },
  {
    id: "training",
    title: "3. Agentic Training",
    subtitle: "SFT + RL на DIVE-задачах",
    color: "#10b981",
    sections: [
      {
        name: "📊 Масштаб датасета",
        content: (
          <div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12, marginBottom: 16 }}>
              {[
                { label: "Синтезировано задач", value: "~15K", sub: "K=3 итерации × ~5K циклов" },
                { label: "SFT траекторий", value: "~6K", sub: "после rejection sampling" },
                { label: "RL frontier задач", value: "~800", sub: "pass@8 ∈ [1, 5]" },
              ].map((m, i) => (
                <div key={i} style={{ background: "#0f172a", borderRadius: 10, padding: 14, textAlign: "center", border: "1px solid #1e293b" }}>
                  <div style={{ fontSize: 28, fontWeight: 800, color: "#34d399" }}>{m.value}</div>
                  <div style={{ fontSize: 12, color: "#e2e8f0", fontWeight: 600 }}>{m.label}</div>
                  <div style={{ fontSize: 11, color: "#64748b", marginTop: 4 }}>{m.sub}</div>
                </div>
              ))}
            </div>
          </div>
        ),
      },
      {
        name: "🎓 SFT: Supervised Fine-Tuning",
        content: (
          <div>
            <p style={{ marginBottom: 12, color: "var(--text-secondary)", lineHeight: 1.6 }}>
              Учитель (например, Claude-4-Sonnet) решает каждую задачу (Q, A, T). Если ответ совпадает с reference answer — траектория принимается.
            </p>
            <div style={{ background: "#0f172a", borderRadius: 10, padding: 14, fontFamily: "monospace", fontSize: 11.5, border: "1px solid #1e293b", lineHeight: 1.8 }}>
              <div style={{ color: "#64748b" }}>{"// SFT Training Instance"}</div>
              <div><span style={{ color: "#f472b6" }}>System</span>: You are an enterprise architecture agent with tools: [adm_get_phase_details, ...]</div>
              <div><span style={{ color: "#22d3ee" }}>User</span>: {"<query>"} Банк модернизирует систему Loan Origination... {"</query>"}</div>
              <div><span style={{ color: "#a78bfa" }}>Assistant trajectory</span>:</div>
              <div style={{ paddingLeft: 12 }}>
                <span style={{ color: "#fbbf24" }}>{"<think>"}</span> Нужно найти SOX violations... <span style={{ color: "#fbbf24" }}>{"</think>"}</span><br/>
                <span style={{ color: "#22d3ee" }}>{"<tool_call>"}</span> compliance_check_execute(block="Cloud LOS...") <span style={{ color: "#22d3ee" }}>{"</tool_call>"}</span><br/>
                <span style={{ color: "#34d399" }}>{"<tool_response>"}</span> {"{ violations: [...] }"} <span style={{ color: "#34d399" }}>{"</tool_response>"}</span><br/>
                <span style={{ color: "#fbbf24" }}>{"<think>"}</span> Теперь проверю roadmap волны... <span style={{ color: "#fbbf24" }}>{"</think>"}</span><br/>
                <span style={{ color: "#22d3ee" }}>{"<tool_call>"}</span> roadmap_generate(...) <span style={{ color: "#22d3ee" }}>{"</tool_call>"}</span><br/>
                ...{" → "}Финальный ответ ✓ совпадает с A
              </div>
              <div style={{ marginTop: 8, color: "#34d399" }}>✓ Trajectory accepted → добавлена в D_sft</div>
            </div>
          </div>
        ),
      },
      {
        name: "🚀 RL: Reinforcement Learning",
        content: (
          <div>
            <p style={{ marginBottom: 12, color: "var(--text-secondary)", lineHeight: 1.6 }}>
              После SFT-инициализации, RL (GRPO) на frontier-задачах. Reward = корректность + формат.
            </p>
            <div style={{ background: "#0f172a", borderRadius: 10, padding: 14, border: "1px solid #1e293b", marginBottom: 14 }}>
              <div style={{ fontSize: 12, color: "#94a3b8", marginBottom: 8 }}>Пример frontier-задачи (pass@8 = 3/8 → learnability ✓)</div>
              <div style={{ fontFamily: "monospace", fontSize: 11.5, lineHeight: 1.8 }}>
                <div><span style={{ color: "#f472b6" }}>R</span> = <span style={{ color: "#fbbf24" }}>α</span> × R_format + R_correct</div>
                <div style={{ marginTop: 6, color: "#64748b" }}>{"// Пример roll-outs:"}</div>
                <div><span style={{ color: "#34d399" }}>Rollout 1:</span> ✓ correct (R=1.0) — нашёл правильный путь через 7 tool calls</div>
                <div><span style={{ color: "#ef4444" }}>Rollout 2:</span> ✗ incorrect (R=0.0) — вызвал wrong tool, ответ неполный</div>
                <div><span style={{ color: "#34d399" }}>Rollout 3:</span> ✓ correct (R=1.0) — альтернативный путь через 5 tool calls</div>
                <div><span style={{ color: "#ef4444" }}>Rollout 4:</span> ✗ format error (R=-0.5) — невалидный tool call</div>
                <div style={{ color: "#64748b" }}>...</div>
              </div>
            </div>
            <div style={{ background: "#052e16", borderRadius: 8, padding: 12, border: "1px solid #166534", fontSize: 13, color: "#86efac", lineHeight: 1.6 }}>
              <strong>Ключевой инсайт из DIVE:</strong> RL усиливает тренд diversity-scaling. 
              Разрыв RL–SFT растёт с ростом разнообразия: модель находит новые эффективные паттерны tool-use 
              через exploration, а не просто имитирует учителя.
            </div>
          </div>
        ),
      },
    ],
  },
  {
    id: "eval",
    title: "4. Ожидаемая оценка",
    subtitle: "Гипотетические бенчмарки",
    color: "#f59e0b",
    sections: [
      {
        name: "📈 Гипотетические результаты",
        content: (
          <div>
            <p style={{ marginBottom: 12, color: "var(--text-secondary)", lineHeight: 1.6 }}>
              По аналогии с результатами DIVE (+22 пункта по 9 OOD бенчмаркам), ожидаемые улучшения в TOGAF-домене:
            </p>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
              <thead>
                <tr style={{ borderBottom: "2px solid #334155" }}>
                  <th style={{ padding: "8px 6px", textAlign: "left", color: "#94a3b8" }}>Бенчмарк</th>
                  <th style={{ padding: "8px 6px", textAlign: "center", color: "#94a3b8" }}>Tier</th>
                  <th style={{ padding: "8px 6px", textAlign: "center", color: "#94a3b8" }}>Base</th>
                  <th style={{ padding: "8px 6px", textAlign: "center", color: "#22d3ee" }}>+SFT</th>
                  <th style={{ padding: "8px 6px", textAlign: "center", color: "#a78bfa" }}>+RL</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["TOGAF-Eval (in-domain)", "L1", "12", "34", "41"],
                  ["EA Compliance Check (OOD tools)", "L3", "5", "22", "30"],
                  ["ArchiMate Modeling (OOD)", "L3", "8", "18", "25"],
                  ["ADM Phase Navigation", "L2", "15", "38", "48"],
                  ["Cross-domain Gap Analysis", "L3", "3", "15", "22"],
                ].map(([name, tier, base, sft, rl], i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #1e293b" }}>
                    <td style={{ padding: "8px 6px", color: "#e2e8f0" }}>{name}</td>
                    <td style={{ padding: "8px 6px", textAlign: "center", color: "#64748b" }}>{tier}</td>
                    <td style={{ padding: "8px 6px", textAlign: "center", color: "#94a3b8" }}>{base}</td>
                    <td style={{ padding: "8px 6px", textAlign: "center", color: "#22d3ee", fontWeight: 700 }}>{sft}</td>
                    <td style={{ padding: "8px 6px", textAlign: "center", color: "#a78bfa", fontWeight: 700 }}>{rl}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ),
      },
    ],
  },
];

export default function DIVETOGAFGuide() {
  const [activePhase, setActivePhase] = useState("pool");
  const [openSections, setOpenSections] = useState({});

  const toggle = (key) => setOpenSections((p) => ({ ...p, [key]: !p[key] }));
  const current = phases.find((p) => p.id === activePhase);

  return (
    <div style={{
      minHeight: "100vh",
      background: "#020617",
      color: "#e2e8f0",
      fontFamily: "'Segoe UI', system-ui, sans-serif",
      padding: "24px 16px",
      "--text-secondary": "#94a3b8",
    }}>
      <div style={{ maxWidth: 820, margin: "0 auto" }}>
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <div style={{ fontSize: 11, color: "#64748b", textTransform: "uppercase", letterSpacing: 2, marginBottom: 8 }}>
            Гипотетический пример
          </div>
          <h1 style={{ fontSize: 28, fontWeight: 800, margin: 0, background: "linear-gradient(135deg, #22d3ee, #a78bfa, #f472b6)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
            DIVE × TOGAF
          </h1>
          <p style={{ fontSize: 14, color: "#94a3b8", marginTop: 8, lineHeight: 1.5 }}>
            Применение рецепта Evidence-Driven Synthesis к домену Enterprise Architecture
          </p>
        </div>

        {/* Phase Nav */}
        <div style={{ display: "flex", gap: 6, marginBottom: 24, flexWrap: "wrap" }}>
          {phases.map((p) => (
            <button
              key={p.id}
              onClick={() => setActivePhase(p.id)}
              style={{
                flex: 1,
                minWidth: 140,
                padding: "10px 8px",
                border: activePhase === p.id ? `2px solid ${p.color}` : "1px solid #1e293b",
                borderRadius: 10,
                background: activePhase === p.id ? `${p.color}15` : "#0f172a",
                color: activePhase === p.id ? p.color : "#64748b",
                cursor: "pointer",
                fontSize: 12,
                fontWeight: 700,
                transition: "all 0.2s",
              }}
            >
              <div>{p.title}</div>
              <div style={{ fontSize: 10, fontWeight: 400, marginTop: 2, opacity: 0.7 }}>{p.subtitle}</div>
            </button>
          ))}
        </div>

        {/* Content */}
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {current.sections.map((s, i) => {
            const key = `${current.id}-${i}`;
            const isOpen = openSections[key] !== false; // default open
            return (
              <div key={key} style={{ background: "#0f172a", borderRadius: 12, border: "1px solid #1e293b", overflow: "hidden" }}>
                <button
                  onClick={() => toggle(key)}
                  style={{
                    width: "100%",
                    padding: "14px 16px",
                    background: "transparent",
                    border: "none",
                    color: "#e2e8f0",
                    fontSize: 14,
                    fontWeight: 700,
                    cursor: "pointer",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    textAlign: "left",
                  }}
                >
                  <span>{s.name}</span>
                  <span style={{ color: "#64748b", fontSize: 18, transform: isOpen ? "rotate(0)" : "rotate(-90deg)", transition: "transform 0.2s" }}>▾</span>
                </button>
                {isOpen && (
                  <div style={{ padding: "0 16px 16px", animation: "fadeIn 0.2s" }}>
                    {s.content}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div style={{ textAlign: "center", marginTop: 32, padding: "16px", borderTop: "1px solid #1e293b", fontSize: 12, color: "#475569", lineHeight: 1.6 }}>
          Все данные гипотетические. Реальная реализация потребует: (1) обёртки API TOGAF-совместимых инструментов,
          (2) валидации tool pool через unit-тесты, (3) запуска синтеза через Claude/GPT, (4) обучения на Qwen3-8B или аналоге.
        </div>
      </div>
    </div>
  );
}
