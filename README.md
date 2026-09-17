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

Если в Knowledge Base недостаточно информации, система не пытается придумать ответ и возвращает:

> В базе знаний не найдено достаточно информации для достоверного ответа на этот вопрос.

---

## Current Status

**Commit #08 — Formal Evaluation Dataset**

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
* формальный evaluation dataset.

Текущий evaluation dataset содержит **38 контролируемых evaluation cases**.

Evaluation dataset предназначен для систематической проверки качества текущего RAG pipeline и дальнейшего анализа Retrieval.

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

Текущий threshold является **MVP baseline** и не считается окончательно оптимальным.

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

Если после Retrieval не найдено достаточно релевантного контекста, LLM не вызывается.

Это позволяет отделить ситуацию «информация отсутствует в базе» от генерации ответа без достаточной опоры на Knowledge Base.

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
└── README.md
```

`dataset.yaml` содержит **38 evaluation cases**.

Каждый case содержит контролируемые данные, необходимые для последующей оценки поведения системы.

Evaluation dataset используется для проверки:

* качества Retrieval;
* соответствия ответа ожидаемому контексту;
* поведения системы при недостатке информации;
* покрытия основных сценариев Knowledge Base.

Evaluation не является второй Knowledge Base и не изменяет основной RAG pipeline.

Следующий этап проекта — запуск формальной оценки на текущем baseline и анализ результатов.

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
│   └── README.md
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
45 passed
1 warning
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

Ближайший этап:

1. запустить формальную Evaluation;
2. получить baseline results;
3. проанализировать ошибки Retrieval и RAG;
4. определить необходимость изменений;
5. повторно измерить результат после изменений.

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
