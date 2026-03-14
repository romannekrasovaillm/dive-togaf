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
│   172 инструмента│   501 концепт    │   265 шаблонов                │
│                  │                  │                                │
│   5 доменов:     │   15 категорий:  │   12 семейств:                │
│   ADM, ArchiMate,│   TOGAF phases,  │   retrieve_compute,           │
│   Repository,    │   deliverables,  │   multi_hop_retrieval,        │
│   Governance,    │   artifacts,     │   compare_decide,             │
│   General        │   ArchiMate,     │   gap_analysis,               │
│                  │   BIAN, ...      │   compliance_check, ...       │
│   2 типа:        │                  │                                │
│   retrieval (138)│                  │   complexity: 1-5             │
│   processing (34)│                  │   sub_questions: 1-5          │
└──────────────────┴──────────────────┴────────────────────────────────┘
                            │
                    PoolSampler.sample_config()
                    (независимая выборка из каждого пула)
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     Synthesis Pipeline                               │
│                                                                      │
│   FOR k = 1..K:                                                     │
│     ┌──────────────────────────────────────────────────────────┐    │
│     │ CollectorAgent: сбор evidence через tool calls           │    │
│     │   → вызывает 3-6 инструментов за раунд                  │    │
│     │   → каждая итерация углубляет предыдущие находки         │    │
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
  --max-tool-rounds M    Макс. tool calls на итерацию (default: 4)
  --seed-category CAT    Фильтр по категории seed'ов (напр. bian_service_domain)
  --random-seed S        Фиксированный seed для воспроизводимости
  --output-dir DIR       Директория вывода (default: output/)
  --model MODEL          Модель Kimi (default: kimi-k2.5)
  --temperature T        Температура LLM (игнорируется для kimi-k2.5)
  --verbose              Debug-логирование + дампы промптов в output/prompt_dumps/
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

### Tool Pool (172 инструмента)

Два типа инструментов, семь доменов:

| Домен | Retrieval | Processing | Всего |
|-------|-----------|------------|-------|
| ADM (фазы A-H) | 47 | 5 | 52 |
| ArchiMate | 33 | 1 | 34 |
| Repository | 28 | 1 | 29 |
| Governance | 19 | 4 | 23 |
| General | 8 | 11 | 19 |
| Analysis | 0 | 12 | 12 |
| Technology Radar | 1 | 2 | 3 |

Каждый инструмент содержит: `id`, `name`, `description`, `parameters` (с типами и enum'ами), `return_schema`, `examples`.

### Seed Pool (501 концепт)

| Категория | Количество | Примеры |
|-----------|-----------|---------|
| `togaf_phase` | 10 | Preliminary, Phase A-H, Requirements Mgmt |
| `togaf_deliverable` | ~60 | Architecture Vision, Business Capability Map |
| `togaf_artifact` | ~40 | Stakeholder Map, Gap Analysis Matrix |
| `togaf_technique` | ~25 | Business Scenarios, Capability-Based Planning |
| `metamodel_entity` | ~30 | Actor, BusinessFunction, ApplicationComponent |
| `archimate_element` | ~50 | Business Process, Application Service |
| `archimate_relationship` | ~30 | Serving, Composition, Realization |
| `bian_service_domain` | ~10 | Loan Origination, Customer Management |
| `industry_case` | ~10 | Banking Reference Architecture |
| `togaf_viewpoint` | ~20 | Business Process Viewpoint |

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

## Live Tools

Из 172 инструментов пула большинство имеет live-реализацию на статических справочниках или реальных библиотеках:

| Источник данных | Инструменты | Описание |
|----------------|------------|----------|
| **TOGAF ADM справочник** (~47) | ADM-фазы, deliverables, техники | Статическая база знаний по TOGAF Standard |
| **BIAN/Compliance справочник** (~50) | BIAN-домены, compliance, reference models | Статическая база по BIAN, GDPR, PCI DSS и др. |
| **ArchiMate справочник** (~69) | Элементы, viewpoints, метамодель, анализ | Статическая база по ArchiMate 3.2 + 33 processing tools |
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

## Выходные файлы

| Файл | Формат | Содержание |
|------|--------|-----------|
| `output/dataset.jsonl` | JSONL | Одна строка на задачу: question, answer, cited_evidence_ids, evidence_trajectory, grounding_score (инкрементальная запись) |
| `output/full_results.jsonl` | JSONL | Полные результаты цикла: seed, все evidence items, все tasks (инкрементальная запись) |
| `output/summary.json` | JSON | Статистика: grounding_rate, complexity_distribution, seed_categories, task_families |
| `output/prompt_dumps/` | JSON | Дампы промптов (только в `--verbose` режиме) |

## Тесты

```bash
# Все тесты
python -m pytest tests/ -v

# Только пулы (быстро, без API)
python -m pytest tests/test_pools.py -v

# Core tools (NetworkX + ArchiMate, без API)
python -m pytest tests/test_core_tools.py -v

# Live tools (реальные API-вызовы)
python -m pytest tests/test_live_tools.py -v
```

17 тестов пулов проверяют: размеры (>= 150 tools, >= 400 seeds, >= 200 exemplars), уникальность ID, покрытие типов/доменов/категорий/семейств, сериализацию, декуплированность пулов.

30+ тестов core tools проверяют: граф-операции NetworkX, парсинг ArchiMate XML, centrality/coupling/critical path, интеграцию ArchiMate-to-NetworkX pipeline.

## Структура проекта

```
dive-togaf/
├── build_pools.py                    # Сборка трёх пулов → JSON
├── run_synthesis.py                  # Запуск pipeline синтеза
├── run_synthesis.sh                  # Shell-обёртка с проверками
│
├── pools/                            # Сгенерированные JSON-пулы
│   ├── tools/tool_pool.json
│   ├── seeds/seed_pool.json
│   └── exemplars/exemplar_pool.json
│
├── src/
│   ├── pools/                        # Построители пулов
│   │   ├── models.py                 # Enum'ы и dataclass'ы
│   │   ├── tool_pool_builder.py      # 172 инструмента
│   │   ├── seed_pool_builder.py      # 501 seed-концепт
│   │   ├── exemplar_pool_builder.py  # 265 шаблонов задач
│   │   ├── sampler.py               # Декуплированная выборка
│   │   └── live_tools/              # Реальные реализации
│   │       ├── togaf_adm_tools.py     # TOGAF ADM справочник (~47 tools)
│   │       ├── repository_reference_tools.py  # BIAN, compliance, repo (~50 tools)
│   │       ├── archimate_reference_tools.py   # ArchiMate элементы/viewpoints/metamodel (~69 tools)
│   │       ├── networkx_tools.py     # 20 граф-инструментов (NetworkX)
│   │       ├── archimate_parser_tools.py  # 10 ArchiMate XML парсер (lxml)
│   │       ├── wikipedia_tools.py    # 5 GitHub API
│   │       └── wikidata_tools.py     # 5 Open Library API
│   │
│   └── synthesis/                    # Pipeline синтеза
│       ├── kimi_client.py            # Клиент Moonshot/Kimi K2.5 (streaming, thinking, retry, logging)
│       ├── collector.py              # Сбор evidence (K итераций)
│       ├── generator.py             # Генерация Q/A + grounding validation
│       ├── orchestrator.py          # Оркестрация + инкрементальная запись датасета
│       └── tool_executor.py         # Live + LLM-симуляция инструментов
│
└── tests/
    ├── test_pools.py                 # 17 тестов валидации пулов
    ├── test_core_tools.py            # 30+ тестов NetworkX + ArchiMate
    └── test_live_tools.py            # Тесты с реальными API
```

## Модель

Используется **Kimi-K2.5** через Moonshot API (`https://api.moonshot.ai/v1`), OpenAI-совместимый SDK.

- Модель: `kimi-k2.5` (thinking model)
- Temperature: не настраивается для kimi-k2.5 (ограничение API Moonshot)
- **Thinking mode**: `reasoning_content` полностью сохраняется и эхо-передаётся обратно в API
- **Streaming**: все вызовы через `stream=true` для предотвращения timeout'ов при длинном reasoning (15-30с на раунд)
- **max_completion_tokens**: ≥ 32768 (требование Moonshot для thinking-моделей: `reasoning_content + content`)
- Retry: до 5 попыток с exponential backoff (2s, 4s, ..., 32s); клиентские ошибки (400-499, кроме 429) не повторяются
- Timeout: 120с на запрос
- Tool calling: нативный через OpenAI-format function calling
- **Rate limit pacing**: 2с пауза между tool-call раундами, 3с между K-итерациями
- **Prompt caching**: `prompt_cache_key` на сессию (UUID) по документации Moonshot
- **Инкрементальное сохранение**: результаты записываются на диск после каждого цикла (не теряются при сбое)
- **On-the-fly sampling**: каждый цикл сэмплирует свежую конфигурацию из пулов (12-20 инструментов за цикл)

### Логирование

При `--verbose` включается расширенное логирование:

- Размер payload (bytes, ~token estimate) на каждый API-вызов
- Usage-статистика ответа: `prompt_tokens`, `completion_tokens`, `cached_tokens`
- Время ответа, `finish_reason`
- При ошибках: HTTP status, response headers (`retry-after`, `x-ratelimit-*`), request content length
- Дампы полных промптов в `output/prompt_dumps/` (JSON с метаданными)

## Комбинаторное пространство

При 172 инструментах, 501 seed'е и 265 exemplar'ах:

```
N_configs = 501 × C(172, 16) × C(265, 4) ≈ 10^24
```

Каждый цикл синтеза работает с уникальной комбинацией (seed, tools_subset, exemplars_subset), обеспечивая высокое разнообразие генерируемого датасета.

## Лицензия

Все права защищены. Для использования свяжитесь с авторами.
