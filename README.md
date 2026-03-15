# DIVE-TOGAF

**Evidence-driven synthesis of TOGAF/ArchiMate training data**

Система генерации обучающих датасетов для enterprise-architecture задач по методологии DIVE (Diverse Inventory of tool-use Verification and Evaluation). Три декуплированных пула ресурсов + pipeline сбора evidence + генерация обоснованных (Q, A) пар с полной провенансной цепочкой.

---

## Ключевой инвариант: grounding by construction

Порядок инвертирован относительно наивного подхода:

```
1. Сначала выполняются реальные инструменты  →  evidence set
2. Потом из их output'ов выводится задача      →  (question, answer)
```

Это гарантирует:

- **Executability** -- траектория tool calls уже существует до генерации Q/A
- **Verifiability** -- каждый факт в ответе имеет `[E<n>]` ссылку, разрешаемую в конкретный `{tool_name, arguments, result}`
- **Diversity** -- три ортогональных измерения разнообразия: что можно делать (tools), о чём (seeds), в какой форме (exemplars)

## Архитектура

```
┌──────────────────────────────────────────────────────────────────────┐
│                        Три декуплированных пула                      │
├──────────────────┬──────────────────┬────────────────────────────────┤
│   Tool Pool      │   Seed Pool      │   Exemplar Pool               │
│   184 записей    │   547 концептов  │   265 шаблонов                │
│   82 unique tools│                  │                                │
│                  │   22 категории:  │   12 семейств:                │
│   11 доменов:    │   TOGAF phases,  │   retrieve_compute,           │
│   ADM, ArchiMate,│   deliverables,  │   multi_hop_retrieval,        │
│   Repository,    │   artifacts,     │   compare_decide,             │
│   Governance,    │   ArchiMate,     │   gap_analysis,               │
│   General,       │   BIAN, TMForum, │   compliance_check, ...       │
│   Analysis,      │   Security,      │                                │
│   Security,      │   Data, Integ.,  │   complexity: 1-5             │
│   Data, Integ.,  │   Cloud, ...     │   sub_questions: 1-5          │
│   Cloud, TechRad │                  │                                │
│                  │                  │                                │
│   2 типа:        │                  │                                │
│   retrieval (139)│                  │                                │
│   processing (45)│                  │                                │
└──────────────────┴──────────────────┴────────────────────────────────┘
                            │
                    PoolSampler.sample_config()
                    (soft-affinity sampling: ≥3 domain-relevant tools)
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     Synthesis Pipeline                               │
│                                                                      │
│   FOR k = 1..K:   (per-iteration tool resampling: 70% keep, 30% swap)│
│     ┌──────────────────────────────────────────────────────────┐    │
│     │ CollectorAgent (single-rollout):                         │    │
│     │   → 1 prompt → 1 model response → ≤6 tool calls         │    │
│     │   → K>1: compressed evidence summary (~1KB vs ~5KB raw)  │    │
│     │   → результат: EvidenceSet с реальными tool outputs      │    │
│     └──────────────────────────────────────────────────────────┘    │
│                          │                                           │
│                          ▼                                           │
│     ┌──────────────────────────────────────────────────────────┐    │
│     │ TaskGenerator: генерация (Q, A) из evidence              │    │
│     │   → каждый факт в ответе цитирует [E<n>]                │    │
│     │   → _validate_grounding() проверяет цитаты               │    │
│     │   → retry при нарушениях (до 2 попыток)                  │    │
│     │   → grounding_score: 0.0 - 1.0                          │    │
│     └──────────────────────────────────────────────────────────┘    │
│                          │                                           │
│                          ▼                                           │
│     SynthesizedTask с evidence_trajectory                           │
│                                                                      │
│   DatasetWriter → dataset.jsonl, full_results.jsonl, summary.json   │
│                                                                      │
│   ┌──────────────────────────────────────────────────────────┐      │
│   │ SFT Stage (DIVE §3.4):                                   │      │
│   │   TeacherAgent.rollout(Q, T) → trajectory τ               │      │
│   │   verify(τ.final_answer, A) → rejection sampling          │      │
│   │   → sft_dataset.jsonl                                     │      │
│   └──────────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────────┘
```

## Быстрый старт

### Требования

- Python 3.10+
- API-ключ Moonshot/Kimi: [platform.moonshot.ai](https://platform.moonshot.ai/)

### Установка

```bash
git clone <repo-url>
cd dive-togaf

# Зависимости
pip install openai networkx numpy lxml requests

# API-ключ
export KIMI_API_KEY=your-api-key-here
```

### Запуск

```bash
# Через shell-обёртку (проверит зависимости и соберёт пулы автоматически)
./run_synthesis.sh

# Или напрямую через Python
python3 build_pools.py          # собрать три пула
python3 run_synthesis.py        # запустить синтез
```

### Параметры CLI

```
python3 run_synthesis.py [OPTIONS]

  --batch-size N         Количество циклов синтеза (default: 3)
  --k-iterations K       Итерации углубления на цикл (default: 3)
  --seed-category CAT    Фильтр по категории seed'ов (напр. bian_service_domain)
  --random-seed S        Фиксированный seed для воспроизводимости
  --output-dir DIR       Директория вывода (default: output/)
  --model MODEL          Модель Kimi (default: kimi-k2.5)
  --verbose              Debug-логирование
```

### Примеры

```bash
# 5 циклов, только банковские seed'ы
./run_synthesis.sh --batch-size 5 --seed-category bian_service_domain

# Воспроизводимый запуск
python3 run_synthesis.py --batch-size 10 --random-seed 42

# Debug-режим
python3 run_synthesis.py --verbose --batch-size 1 --k-iterations 1
```

## Три пула

### Tool Pool (184 записи, 82 уникальных инструмента)

Два типа инструментов, 11 доменов:

| Домен | Retrieval | Processing | Всего |
|-------|-----------|------------|-------|
| ADM (фазы A-H) | 47 | 5 | 52 |
| ArchiMate | 33 | 1 | 34 |
| Repository | 28 | 1 | 29 |
| Governance | 19 | 7 | 26 |
| General | 10 | 9 | 19 |
| Analysis | 0 | 12 | 12 |
| Technology Radar | 1 | 2 | 3 |
| Data Architecture | 1 | 2 | 3 |
| Security | 0 | 2 | 2 |
| Integration | 0 | 2 | 2 |
| Cloud Infrastructure | 0 | 2 | 2 |

Каждый инструмент содержит: `id`, `name`, `description`, `parameters` (с типами и enum'ами), `return_schema`, `examples`.

### Seed Pool (547 концептов, 22 категории)

| Категория | Кол-во | Примеры |
|-----------|--------|---------|
| `archimate_element` | 60 | Business Process, Application Service |
| `bian_service_domain` | 57 | Loan Origination, Customer Management |
| `togaf_artifact` | 51 | Stakeholder Map, Gap Analysis Matrix |
| `tmforum_functional_block` | 44 | Service Ordering, Party Management |
| `technology_building_block` | 40 | Kubernetes, Kafka, PostgreSQL |
| `togaf_metamodel_entity` | 31 | Actor, BusinessFunction, ApplicationComponent |
| `industry_case` | 29 | Banking Reference Architecture |
| `archimate_viewpoint` | 24 | Layered, Motivation |
| `stakeholder` | 23 | CIO, Enterprise Architect |
| `togaf_deliverable` | 22 | Architecture Vision Document |
| `capability` | 22 | Business Capability Map |
| `building_block` | 22 | Architecture Building Blocks |
| `standard` | 19 | ISO 27001, COBIT |
| `togaf_technique` | 14 | Business Scenarios, Capability-Based Planning |
| `archimate_relationship` | 13 | Serving, Composition, Realization |
| `security_architecture` | 12 | Zero Trust, IAM, DevSecOps, Privacy-by-Design |
| `integration_architecture` | 12 | Event-Driven Architecture, Saga, CDC, API-First |
| `cloud_architecture` | 12 | Cloud-Native, Serverless, FinOps, GitOps |
| `togaf_phase` | 10 | Preliminary, Phase A-H, Requirements Mgmt |
| `togaf_viewpoint` | 10 | Business Process Viewpoint |
| `team_topology` | 10 | Stream-Aligned, Platform Team |
| `data_architecture` | 10 | Data Mesh, MDM, Data Lakehouse, Event Sourcing |

### Exemplar Pool (265 шаблонов)

| Семейство | Кол-во | Complexity | Описание |
|-----------|--------|-----------|----------|
| `retrieve_compute` | 25 | 2-3 | Извлечь данные + вычислить метрику |
| `multi_hop_retrieval` | 15 | 3-4 | Навигация по цепочке связей |
| `compare_decide` | 12 | 2-3 | Сравнить два элемента, принять решение |
| `gap_analysis` | 10 | 3-4 | Текущее vs целевое состояние |
| `compliance_check` | 8 | 2-3 | Валидация против стандартов |
| `risk_assessment` | 8 | 3-4 | Идентификация и квантификация рисков |
| `roadmap_planning` | 10 | 4-5 | Планирование трансформации |
| `stakeholder_analysis` | 8 | 3 | Анализ влияния на стейкхолдеров |
| `cost_benefit` | 8 | 3-4 | Анализ затрат и выгод |
| `architecture_decision` | 8 | 3-4 | ADR-стиль архитектурных решений |
| `architecture_kata` | 8 | 2-5 | Учебные упражнения |
| `aggregate` | 8 | 2-3 | Агрегация из нескольких источников |

## Soft-Affinity Toolset Sampling

Проблема: при чистом random sampling нишевые seeds (TMForum, Security, Data) получают toolset без релевантных инструментов → ~33% waste в tool calls.

Решение — stratified sampling с мягкой гарантией:

```
sample_tools_with_affinity(seed, pool, toolset_size=15, min_affinity=3):
  1. CATEGORY_DOMAIN_MAP[seed.category] → affinity_domains (1-3 домена)
  2. Partition pool: affinity_tools ∩ other_tools
  3. Гарантировать ≥3 affinity tools в toolset
  4. Остальные слоты (~75%) — random из полного пула
  5. Shuffle для устранения позиционного bias
```

| Seed | Без affinity | С affinity | Гарантия |
|------|-------------|------------|----------|
| TMForum ODA | 2.2 avg | 4.7 avg | ≥3 |
| Security Architecture | ~2 avg | 5-6 avg | ≥3 |
| Data Architecture | ~2 avg | 5 avg | ≥3 |
| TOGAF Phase | ~5 avg | 8 avg | ≥3 |

Per-iteration resampling (K>1) также поддерживает affinity: после 30% swap проверяется порог, при нехватке — affinity repair.

## Payload Stabilization (Single-Rollout Collector)

Проблема: multi-round tool-calling loop (до 8 rounds) накапливал сообщения → ~34KB payload на K=3 → `RemoteProtocolError`.

Решение — single-rollout архитектура:

```
Phase 1 — Single-rollout per iteration:
  Было:  prompt → model → tool calls → results → model → tool calls → ... (до 8 rounds)
  Стало: prompt → model → ≤6 tool calls → collect evidence → done

Phase 2 — Evidence compression:
  Было:  K>1 prompt содержит raw JSON evidence (~5KB)
  Стало: compressed_summary() — одна строка на evidence item (~1KB):
    - [E0] compute_coupling: Ca=3.9, components: 3 items, health_score=0.88
    - [E1] current_state_query: maturity_level=2, issues=[debt, scalability]
```

| Метрика | Было | Стало |
|---------|------|-------|
| Messages per iteration | ~20 | 3 |
| Evidence in K>1 prompt | ~5KB | ~1KB |
| Total payload K=3 | ~34KB | ≤15KB |
| RemoteProtocolError | частый | устранён |

## Live Tools

Из 82 уникальных инструментов большинство имеет live-реализацию на статических справочниках или реальных библиотеках:

| Источник данных | Инструменты | Описание |
|----------------|------------|----------|
| **TOGAF ADM справочник** (~47) | ADM-фазы, deliverables, техники | Статическая база знаний по TOGAF Standard |
| **BIAN/Compliance справочник** (~50) | BIAN-домены, compliance, reference models | Статическая база по BIAN, GDPR, PCI DSS и др. |
| **ArchiMate справочник** (~40) | Элементы, viewpoints, метамодель | Статическая база по ArchiMate 3.2 |
| **NetworkX** (20) | Граф-анализ зависимостей | `graph_compute_centrality`, `graph_find_cycles`, `graph_compute_critical_path` |
| **lxml** (10) | Парсинг ArchiMate XML | `archimate_parse_model_info`, `archimate_list_elements` |
| **GitHub API** (5) | Поиск open-source | `github_search_repositories`, `github_get_repository` |

При вызове `ToolExecutor`:
1. Если есть live-реализация — выполняет на справочнике/библиотеке (быстро, без LLM)
2. Если live-вызов упал — fallback на LLM-симуляцию
3. Если live-реализации нет — LLM генерирует JSON по `return_schema` (помечается `_simulated: true`)

Результаты симулированных вызовов помечаются `_simulated: true`, а при ошибке парсинга JSON — `_parse_failed: true`. Grounding validation штрафует score задач, опирающихся на симулированные данные.

## Grounding Invariant: как он обеспечивается

### Порядок данных (структурная гарантия)

```python
# orchestrator.py -- порядок зафиксирован в коде
for k in range(1, K + 1):
    evidence = collector.collect_iteration(seed, k, evidence)   # ШАГ 1: tool calls
    task = generator.generate(seed, evidence, exemplars, k)     # ШАГ 2: Q/A из evidence
```

Генератор физически не может создать задачу без evidence -- evidence передаётся как аргумент.

### Принудительное цитирование (prompt-уровень)

Системный промпт генератора требует `[E<n>]` на каждый факт:

```
GROUNDING INVARIANT -- THIS IS NON-NEGOTIABLE:
- Every claim in the answer MUST cite its source as [E<number>]
- You may ONLY use data that appears in the evidence items
- If a fact cannot be traced to a specific [E<n>], you MUST NOT include it
```

### Валидация (post-generation gate)

`_validate_grounding()` проверяет:

| Проверка | Действие при нарушении |
|----------|----------------------|
| Ответ содержит >= 1 `[E<n>]` | score = 0.0, retry |
| Все cited IDs в пределах evidence set | violation + retry |
| Declared `cited_evidence` совпадает с текстовыми цитатами | warning |
| Complexity >= 2 требует >= 2 evidence items | violation |

При нарушении -- retry с явным указанием ошибок (до `max_regen_attempts`).

### Провенансная цепочка в датасете

Каждая запись в `dataset.jsonl` содержит:

```json
{
  "question": "...",
  "answer": "... maturity is 1.2 [E2] ... compliance factor 10/10 [E4] ...",
  "cited_evidence_ids": [2, 4],
  "evidence_trajectory": [
    {
      "evidence_id": 2,
      "iteration": 1,
      "tool_name": "graph_compute_component_health",
      "arguments": {"component_id": "loan_origination"},
      "result_summary": "{\"maturity\": 1.2, ...}"
    },
    {
      "evidence_id": 4,
      "iteration": 2,
      "tool_name": "compliance_check_regulatory",
      "arguments": {"domain": "lending"},
      "result_summary": "{\"compliance_factor\": 10, ...}"
    }
  ],
  "grounding_score": 0.95
}
```

## SFT Trajectory Generation (DIVE §3.4)

После синтеза D_task, отдельный этап генерирует SFT-данные через teacher rollout + rejection sampling:

```python
for (Q, A, T) in D_task:
    τ = teacher.rollout(Q, T)        # teacher решает задачу с tool calls
    if verify(τ.final_answer, A):    # rejection sampling
        D_sft.append((Q, A, T, τ))
```

`TeacherAgent` использует ту же модель и тот же toolset для решения задач из D_task. Траектория записывается в chat-формате с `<think>` блоками и `<tool_call>` разметкой. `verify_answer()` сравнивает финальный ответ teacher'а с reference answer по ключевым токенам (числа, имена, метрики).

Результат: `sft_dataset.jsonl` с полными траекториями для fine-tuning.

## Выходные файлы

| Файл | Формат | Содержание |
|------|--------|-----------|
| `output/dataset.jsonl` | JSONL | Одна строка на задачу: question, answer, cited_evidence_ids, evidence_trajectory, grounding_score |
| `output/full_results.jsonl` | JSONL | Полные результаты цикла: seed, все evidence items, все tasks |
| `output/summary.json` | JSON | Статистика: grounding_rate, complexity_distribution, seed_categories, task_families |
| `output/sft_dataset.jsonl` | JSONL | SFT-траектории: messages с tool calls, final_answer, verified flag |
| `output/sft_summary.json` | JSON | Acceptance rate, pass/fail counts |

## Тесты

```bash
# Все тесты (54 теста)
python -m pytest tests/ -v --ignore=tests/test_live_tools.py

# Только пулы (быстро, без API)
python -m pytest tests/test_pools.py -v

# Core tools (NetworkX + ArchiMate, без API)
python -m pytest tests/test_core_tools.py -v

# Live tools (реальные API-вызовы)
python -m pytest tests/test_live_tools.py -v
```

54 теста проверяют: размеры пулов (≥ 150 tools, ≥ 500 seeds, ≥ 200 exemplars), уникальность ID, покрытие всех 22 категорий/11 доменов/12 семейств, граф-операции NetworkX, парсинг ArchiMate XML, centrality/coupling/critical path, интеграцию ArchiMate-to-NetworkX pipeline.

## Структура проекта

```
dive-togaf/
├── build_pools.py                    # Сборка трёх пулов → JSON
├── run_synthesis.py                  # Запуск pipeline синтеза
├── run_synthesis.sh                  # Shell-обёртка с проверками
│
├── pools/                            # Сгенерированные JSON-пулы
│   ├── tools/tool_pool.json          #   184 записей (82 unique)
│   ├── seeds/seed_pool.json          #   547 концептов
│   └── exemplars/exemplar_pool.json  #   265 шаблонов
│
├── src/
│   ├── pools/                        # Построители пулов
│   │   ├── models.py                 # Enum'ы и dataclass'ы (22 SeedCategory, 11 ToolDomain)
│   │   ├── tool_pool_builder.py      # 82 инструмента × параметрические варианты
│   │   ├── seed_pool_builder.py      # 547 seed-концептов
│   │   ├── exemplar_pool_builder.py  # 265 шаблонов задач
│   │   ├── sampler.py                # Soft-affinity sampling + CATEGORY_DOMAIN_MAP
│   │   └── live_tools/               # Реальные реализации
│   │       ├── togaf_adm_tools.py
│   │       ├── repository_reference_tools.py
│   │       ├── archimate_reference_tools.py
│   │       ├── networkx_tools.py     # 20 граф-инструментов (NetworkX)
│   │       ├── archimate_parser_tools.py  # 10 ArchiMate XML парсер (lxml)
│   │       ├── wikipedia_tools.py    # 5 GitHub API
│   │       └── wikidata_tools.py     # 5 Open Library API
│   │
│   └── synthesis/                    # Pipeline синтеза
│       ├── kimi_client.py            # Клиент Moonshot/Kimi K2.5
│       ├── collector.py              # Single-rollout evidence collection (≤6 tools/iter)
│       ├── generator.py              # Генерация Q/A + grounding validation
│       ├── teacher.py                # Teacher rollout + rejection sampling (SFT)
│       ├── orchestrator.py           # Оркестрация + affinity resampling + запись
│       └── tool_executor.py          # Live + LLM-симуляция инструментов
│
└── tests/
    ├── test_pools.py                 # Валидация пулов (размеры, категории, домены)
    ├── test_core_tools.py            # NetworkX + ArchiMate тесты
    └── test_live_tools.py            # Тесты с реальными API
```

## Модель

Используется **Kimi-K2.5** через Moonshot API (`https://api.moonshot.ai/v1`), OpenAI-совместимый SDK.

- Модель: `kimi-k2.5`
- Temperature: не настраивается для kimi-k2.5 (ограничение API Moonshot)
- Retry: до 3 попыток с exponential backoff (2s, 4s, 8s)
- Tool calling: нативный через OpenAI-format function calling
- Streaming: включен для thinking models (избежание timeout'ов)

## Комбинаторное пространство

При 82 уникальных инструментах, 547 seed'ах и 265 exemplar'ах:

```
N_configs = 547 × C(184, 15) × C(265, 4) ≈ 10^30
```

С учётом per-iteration resampling (30% swap на K=2,3) и soft-affinity (уникальный affinity partition на seed), каждый цикл работает с уникальной комбинацией. Seed diversity enforcement (shuffled queue) гарантирует, что все 547 seeds будут использованы до первого повтора.

## Лицензия

Все права защищены. Для использования свяжитесь с авторами.
