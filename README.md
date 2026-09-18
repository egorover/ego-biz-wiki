# EgoBiz Wiki

## AI Business Knowledge Assistant

EgoBiz Wiki — компактный RAG-based AI-ассистент для ответов на вопросы сотрудников на основе контролируемой корпоративной базы знаний.

Проект разработан как выпускной проект курса и представляет собой рабочий MVP для демонстрационной компании **EgoTech Solutions**.

Основной принцип проекта:

> **SIMPLE, COMPLETE & WORKING MVP > COMPLEX, UNSTABLE PRODUCT**

---

## Что делает EgoBiz Wiki

Сотрудник задаёт вопрос на естественном языке.

EgoBiz Wiki:

1. преобразует вопрос в embedding;
2. выполняет semantic search по корпоративной Knowledge Base;
3. отбирает релевантные фрагменты;
4. передаёт найденный контекст в LLM;
5. формирует ответ на основе найденной информации;
6. показывает источники, использованные для ответа.

Если в Knowledge Base недостаточно информации, система возвращает:

> В базе знаний не найдено достаточно информации для достоверного ответа на этот вопрос.

При отсутствии достаточного контекста LLM не вызывается.

---

## Current Status

**Commit #09 — Post-MVP Evaluation**

Основные функциональные возможности MVP реализованы:

* корпоративная Knowledge Base;
* документный indexing pipeline;
* persistent ChromaDB vector store;
* semantic Retrieval;
* configurable retrieval threshold;
* RAG pipeline;
* OpenAI-compatible LLM provider;
* deterministic fallback при отсутствии достаточного контекста;
* FastAPI backend;
* `/health`, `/index`, `/search` и `/chat`;
* Streamlit UI;
* отображение источников;
* unit и integration tests;
* формальный evaluation dataset;
* автоматизированный evaluation runner.

Текущий evaluation dataset содержит **38 контролируемых evaluation cases**.

После Commit #09 проведена первичная формальная оценка текущего RAG baseline.

### Evaluation results

```text
Cases:                         38
Source cases:                  30
Behavior Accuracy:             92.1%
Expected Source Hit Rate:      100.0%
Source Attribution Accuracy:   93.3%
Fallback Accuracy:             100.0%
```

Evaluation выявил отдельные ограничения текущего baseline, связанные с Top-K retrieval и обработкой ambiguous queries. Эти ограничения зафиксированы как baseline limitations и не являются основанием для автоматического усложнения архитектуры.

---

## Основные возможности

### Knowledge Base

В демонстрационной Knowledge Base находятся документы EgoTech Solutions по направлениям:

* HR;
* IT;
* Security;
* Operations;
* Customer Operations;
* FAQ.

Текущая база содержит **23 Markdown-документа** и `manifest.yaml`.

Используемый в MVP нормализованный Markdown-формат представляет собой **наш идеальный документооборот**.

Это сознательное упрощение для демонстрационного проекта, а не утверждение о том, что реальные корпоративные документы всегда имеют такую структуру.

---

### Indexing

Документы Knowledge Base проходят indexing pipeline:

```text
Documents
    ↓
Load
    ↓
Split into chunks
    ↓
Generate embeddings
    ↓
Store in ChromaDB
```

Индекс является persistent и используется последующими Retrieval-запросами.

---

### Retrieval

Retrieval выполняет semantic search по ChromaDB.

Текущие MVP-параметры:

```text
Chunk size: 800
Chunk overlap: 120
Embedding model: text-embedding-3-small
Top-K: 5
Distance threshold: 1.30
```

Используется Chroma distance: меньшее значение означает более близкое векторное соответствие.

Текущий threshold является **MVP baseline** и оценивается на формальном evaluation dataset.

---

### RAG

Основной `/chat` pipeline:

```text
User Query
    ↓
Query Embedding
    ↓
ChromaDB Retrieval
    ↓
Top-K + Threshold
    ↓
Relevant Context
    ↓
LLM
    ↓
Answer + Sources
```

Если после Retrieval не найдено достаточно релевантного контекста, LLM не вызывается и используется deterministic fallback.

Production RAG также использует fallback, если LLM возвращает пустой ответ или точную fallback-фразу.

Текущий LLM prompt требует использовать предоставленный контекст, если он содержит прямой ответ, и применять fallback только при недостатке информации.

---

## API

Backend реализован на **FastAPI**.

Основные endpoints:

```text
GET  /health
POST /index
POST /search
POST /chat
```

### `/health`

Проверка доступности backend.

### `/index`

Запуск indexing pipeline и обновление persistent vector store.

### `/search`

Выполняет Retrieval без вызова LLM.

Используется для:

* демонстрации Retrieval;
* диагностики;
* просмотра найденных chunks;
* подготовки данных для оценки.

### `/chat`

Выполняет полный RAG pipeline и возвращает:

* ответ;
* источники.

---

## Streamlit UI

Пользовательский интерфейс реализован на **Streamlit**.

UI:

* отправляет запросы в FastAPI;
* отображает ответ;
* отображает источники;
* проверяет пустой запрос;
* обрабатывает недоступность backend.

Streamlit не содержит собственной RAG-логики.

Вся основная бизнес-логика находится в backend.

---

## Evaluation

Для систематической проверки качества проекта создан отдельный evaluation layer:

```text
evaluation/
├── dataset.yaml
├── README.md
└── run_evaluation.py
```

`dataset.yaml` содержит **38 evaluation cases**:

* `relevant` — 14;
* `cross_category` — 8;
* `typical_user` — 4;
* `source_attribution` — 4;
* `out_of_kb` — 5;
* `ambiguous` — 3.

Evaluation runner использует **существующий production RAG pipeline**, а не отдельную реализацию Retrieval или RAG.

### Метрики

Используются четыре основные метрики:

1. **Behavior Accuracy**
2. **Expected Source Hit Rate**
3. **Source Attribution Accuracy**
4. **Fallback Accuracy**

Для метрик, связанных с ожидаемыми источниками, используются 30 cases, содержащих `expected_sources`.

Текущий результат baseline:

```text
Behavior Accuracy:             92.1%
Expected Source Hit Rate:      100.0%
Source Attribution Accuracy:   93.3%
Fallback Accuracy:             100.0%
```

Evaluation не использует LLM-as-a-Judge или специализированные evaluation frameworks.

Evaluation является отдельным слоем проверки качества и не изменяет основную архитектуру MVP.

### Выявленные ограничения

Evaluation выявил:

* два retrieval cases, в которых один из ожидаемых документов не попадает в текущий Top-K;
* три ambiguous cases, для которых dataset ожидает clarification, тогда как текущий MVP возвращает answer;
* необходимость корректного учёта fallback-фразы в evaluation classifier.

Эти результаты используются для принятия дальнейших технических решений.

---

## Architecture

Проект использует упрощённый вариант **Clean Architecture**.

Основные слои:

```text
app/
├── domain/
├── application/
├── infrastructure/
└── api/

ui/
```

### Domain

Содержит основные модели и абстракции системы.

### Application

Содержит application services и orchestration.

### Infrastructure

Содержит реализации:

* ChromaDB;
* embeddings;
* LLM provider;
* document loaders.

### API

FastAPI endpoints и HTTP layer.

### UI

Streamlit presentation layer.

Подробнее архитектура описана в [`ARCHITECTURE.md`](ARCHITECTURE.md).

---

## Technology Stack

* Python 3.12+
* FastAPI
* Streamlit
* LangChain
* OpenAI API / OpenAI-compatible API
* ChromaDB
* OpenAI Embeddings
* Pydantic Settings
* pytest
* Docker
* GitHub Actions

Поддерживается работа через OpenAI-compatible provider, включая ProxyAPI, без provider-specific branching в application logic.

---

## Project Structure

```text
ego-biz-wiki/
├── app/
│   ├── api/
│   ├── application/
│   ├── domain/
│   └── infrastructure/
├── knowledge_base/
├── evaluation/
│   ├── dataset.yaml
│   ├── README.md
│   └── run_evaluation.py
├── scripts/
├── tests/
├── ui/
├── docs/
├── .env.example
├── ARCHITECTURE.md
├── PROJECT_STATE.md
├── README.md
├── Dockerfile
└── pyproject.toml
```

---

## Testing

Проект покрыт unit и integration tests.

Текущее состояние:

```text
55 passed
1 warning
```

Evaluation-specific tests:

```text
8 passed
```

Предупреждение связано с deprecated API в зависимости `Starlette/AnyIO` и не является ошибкой проектной логики.

---

## Architectural Constraints

MVP сознательно не использует:

* Agentic RAG;
* agents;
* LangGraph;
* hybrid search;
* reranking;
* external web search;
* long-term memory;
* сложную orchestration.

Эти подходы могут рассматриваться только после появления подтверждённой необходимости и результатов evaluation.

Главный критерий развития проекта:

> **Сначала измерить проблему — затем усложнять систему.**

---

## Roadmap

Ближайшее направление:

1. анализ результатов Evaluation;
2. анализ отдельных Retrieval limitations;
3. проверка необходимости изменения `top-k` и `RETRIEVAL_SCORE_THRESHOLD`;
4. повторное измерение после обоснованных изменений;
5. улучшение обработки ambiguous queries, если это потребуется для MVP.

Возможные дальнейшие направления:

* Retrieval optimization;
* Document Standardization;
* поддержка PDF/DOCX/XLSX/HTML/TXT;
* дополнительные evaluation cases;
* расширение Knowledge Base.

Advanced RAG approaches добавляются только при наличии измеренного обоснования.

---

## Project Philosophy

EgoBiz Wiki создаётся как **небольшой, понятный и воспроизводимый рабочий MVP**, а не как максимально сложная AI-система.

Архитектура должна оставаться:

* простой;
* тестируемой;
* расширяемой;
* понятной для сопровождения;
* достаточной для поставленной задачи.

**SIMPLE, COMPLETE & WORKING MVP > COMPLEX, UNSTABLE PRODUCT**
