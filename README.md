# EgoBiz Wiki

**AI Business Knowledge Assistant**

[![CI](https://github.com/egorover/ego-biz-wiki/actions/workflows/ci.yml/badge.svg)](https://github.com/egorover/ego-biz-wiki/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141.1-009688?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.64.0-FF4B4B?logo=streamlit&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-vector%20store-5A67D8)

EgoBiz Wiki — компактный RAG-based AI-ассистент для ответов на вопросы сотрудников на основе контролируемой корпоративной базы знаний.

Проект разработан как выпускной проект курса и представляет собой рабочий MVP для демонстрационной компании **EgoTech Solutions**.

Основной принцип проекта:

> **SIMPLE, COMPLETE & WORKING MVP > COMPLEX, UNSTABLE PRODUCT**

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

## Current Status

Последний функциональный commit: **Commit #09 — Post-MVP Evaluation**

После завершения функциональной истории проекта были отдельно добавлены технические и документационные изменения, включая GitHub Actions CI и синхронизацию документации.

Основные функциональные возможности MVP реализованы:

- корпоративная Knowledge Base;
- документный indexing pipeline;
- persistent ChromaDB vector store;
- semantic Retrieval;
- configurable retrieval threshold;
- RAG pipeline;
- OpenAI-compatible LLM provider;
- deterministic fallback при отсутствии достаточного контекста;
- FastAPI backend;
- `/health`, `/search` и `/chat`;
- Streamlit UI;
- отображение источников;
- unit и integration tests;
- формальный evaluation dataset;
- автоматизированный evaluation runner;
- GitHub Actions CI.

Текущий evaluation dataset содержит **38 контролируемых evaluation cases**.

После Commit #09 проведена формальная оценка текущего RAG baseline.

### Evaluation results

- Cases: 38
- Source cases: 30
- Behavior Accuracy: 92.1%
- Expected Source Hit Rate: 100.0%
- Source Attribution Accuracy: 93.3%
- Fallback Accuracy: 100.0%

Evaluation выявил отдельные ограничения текущего baseline, связанные с Top-K retrieval и обработкой ambiguous queries. Эти ограничения зафиксированы как baseline limitations и используются для определения дальнейших технических шагов.

GitHub Actions CI проверяет проект на Python 3.12 и 3.13 и запускает полный набор тестов.

Continuous Integration реализован. Continuous Deployment (CD) в текущем MVP не реализован.

---

## Основные возможности

### Knowledge Base

В демонстрационной Knowledge Base находятся документы EgoTech Solutions по направлениям:

- HR;
- IT;
- Security;
- Operations;
- Customer Operations;
- FAQ.

Текущая база содержит **23 Markdown-документа и `manifest.yaml`**.

Используемый в MVP нормализованный Markdown-формат представляет собой наш идеальный документооборот.

Это сознательное упрощение для демонстрационного проекта, а не утверждение о том, что реальные корпоративные документы всегда имеют такую структуру.

### Indexing

Документы Knowledge Base проходят indexing pipeline:

```text
Documents
    |
  Load
    |
Split into chunks
    |
Generate embeddings
    |
Store in ChromaDB
```

Индекс является persistent и используется последующими Retrieval-запросами.

Indexing запускается отдельным скриптом:

```bash
python scripts/index_knowledge_base.py
```

В текущем MVP отдельный API endpoint для indexing не предусмотрен.

### Retrieval

Retrieval выполняет semantic search по ChromaDB.

Текущие MVP-параметры:

- Chunk size: 800
- Chunk overlap: 120
- Embedding model: `text-embedding-3-small`
- Top-K: 5
- Distance threshold: 1.30

Используется Chroma distance: меньшее значение означает более близкое векторное соответствие.

Текущий threshold является MVP baseline и оценивается на формальном evaluation dataset.

### RAG

Основной `/chat` pipeline:

```text
User Query
    |
Query Embedding
    |
ChromaDB Retrieval
    |
Top-K + Threshold
    |
Relevant Context
    |
LLM
    |
Answer + Sources
```

Если после Retrieval не найдено достаточно релевантного контекста, LLM не вызывается и используется deterministic fallback.

Текущий RAG pipeline также использует fallback, если LLM возвращает пустой ответ или точную fallback-фразу.

Текущий LLM prompt требует использовать предоставленный контекст, если он содержит прямой ответ, и применять fallback только при недостатке информации.

### API

Backend реализован на FastAPI.

Основные endpoints:

- `GET /health`
- `POST /search`
- `POST /chat`

#### `/health`

Проверка доступности backend.

#### `/search`

Выполняет Retrieval без вызова LLM.

Используется для:

- демонстрации Retrieval;
- диагностики;
- просмотра найденных chunks;
- подготовки данных для оценки.

#### `/chat`

Выполняет полный RAG pipeline и возвращает:

- ответ;
- источники.

### Streamlit UI

Пользовательский интерфейс реализован на Streamlit.

UI:

- отправляет запросы в FastAPI;
- отображает ответ;
- отображает источники;
- проверяет пустой запрос;
- обрабатывает недоступность backend.

Streamlit не содержит собственной RAG-логики.

Вся основная бизнес-логика находится в backend.

### Evaluation

Для систематической проверки качества проекта создан отдельный evaluation layer:

```text
evaluation/
├── dataset.yaml
├── README.md
└── run_evaluation.py
```

`dataset.yaml` содержит 38 evaluation cases:

- relevant — 14;
- cross_category — 8;
- typical_user — 4;
- source_attribution — 4;
- out_of_kb — 5;
- ambiguous — 3.

Evaluation runner использует существующий RAG pipeline, а не отдельную реализацию Retrieval или RAG.

#### Метрики

Используются четыре основные метрики:

- Behavior Accuracy;
- Expected Source Hit Rate;
- Source Attribution Accuracy;
- Fallback Accuracy.

Для метрик, связанных с ожидаемыми источниками, используются 30 cases, содержащих `expected_sources`.

Текущий baseline:

- Behavior Accuracy: 92.1%;
- Expected Source Hit Rate: 100.0%;
- Source Attribution Accuracy: 93.3%;
- Fallback Accuracy: 100.0%.

Evaluation не использует LLM-as-a-Judge или специализированные evaluation frameworks.

Evaluation является отдельным слоем проверки качества и не изменяет основную архитектуру MVP.

#### Выявленные ограничения

Evaluation выявил:

- два retrieval cases, в которых один из ожидаемых документов не попадает в текущий Top-K;
- три ambiguous cases, для которых dataset ожидает clarification, тогда как текущий MVP возвращает answer;
- необходимость корректного учёта fallback-фразы в evaluation classifier.

Эти результаты рассматриваются как baseline limitations и используются для принятия дальнейших технических решений.

## Architecture

Проект использует упрощённый вариант Clean Architecture.

Основные слои:

```text
app/
├── domain/
├── application/
├── infrastructure/
├── api/
└── ui/
```

### Domain

Содержит основные модели и абстракции системы.

Domain layer не зависит от ChromaDB, LangChain, provider SDK или FastAPI.

### Application

Содержит application services, orchestration и application-level protocols.

### Infrastructure

Содержит реализации:

- ChromaDB;
- embeddings;
- LLM provider;
- document loaders.

### API

FastAPI endpoints и HTTP layer.

### UI

Streamlit presentation layer.

Подробнее архитектура описана в `ARCHITECTURE.md`.

## Technology Stack

- Python 3.12+
- FastAPI
- Streamlit
- `langchain-text-splitters`
- `langchain-openai`
- OpenAI API / OpenAI-compatible API
- ChromaDB
- OpenAI Embeddings
- Pydantic Settings
- pytest
- GitHub Actions

Поддерживается работа через OpenAI-compatible provider, включая ProxyAPI, без provider-specific branching в application logic.

## Project Structure

```text
ego-biz-wiki/
├── app/
│   ├── api/
│   ├── application/
│   ├── domain/
│   └── infrastructure/
│
├── evaluation/
│   ├── dataset.yaml
│   ├── README.md
│   └── run_evaluation.py
│
├── knowledge_base/
│   ├── customer_operations/
│   ├── faq/
│   ├── hr/
│   ├── it/
│   ├── operations/
│   ├── security/
│   └── manifest.yaml
│
├── scripts/
│   └── index_knowledge_base.py
│
├── tests/
│   ├── integration/
│   └── unit/
│
├── ui/
│   └── streamlit_app.py
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .env.example
├── .gitignore
├── ARCHITECTURE.md
├── EgoBiz_Wiki.bat
├── PROJECT_STATE.md
├── README.md
└── pyproject.toml
```

## Local Demo Launch

Для локальной демонстрации проекта предусмотрен one-click launcher:

```text
EgoBiz_Wiki.bat
```

Launcher запускает:

1. FastAPI backend на `http://127.0.0.1:8000`;
2. Streamlit UI;
3. браузер автоматически открывается Streamlit.

Перед запуском должен быть создан локальный virtual environment `.venv` и установлены зависимости проекта.

Для ручного запуска backend:

```bash
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Для ручного запуска UI:

```bash
.venv\Scripts\python.exe -m streamlit run ui\streamlit_app.py
```

Desktop shortcut используется только для удобства локальной демонстрации и не является частью Git repository.

## Testing

Проект покрыт unit и integration tests.

Текущее состояние тестового набора:

- 55 passed
- 1 warning

Evaluation-specific tests:

- 8 passed

Предупреждение связано с deprecated API в зависимости Starlette/AnyIO и не является ошибкой проектной логики.

## Continuous Integration

GitHub Actions workflow запускается:

- при push в `main`;
- при pull_request в `main`.

CI проверяет проект на:

- Python 3.12;
- Python 3.13.

Для каждой версии выполняются установка test dependencies и полный набор pytest.

Continuous Integration реализован.

Continuous Deployment (CD) в текущем MVP не реализован.

## Architectural Constraints

MVP сознательно не использует:

- Agentic RAG;
- agents;
- LangGraph;
- hybrid search;
- reranking;
- external web search;
- long-term memory;
- сложную orchestration.

Эти подходы могут рассматриваться только после появления подтверждённой необходимости и результатов evaluation.

Главный критерий развития проекта:

> Сначала измерить проблему — затем усложнять систему.

## Roadmap

Следующие направления после завершения текущего MVP:

- анализ результатов Evaluation;
- анализ отдельных Retrieval limitations;
- проверка необходимости изменения Top-K и `RETRIEVAL_SCORE_THRESHOLD`;
- повторное измерение после обоснованных изменений;
- улучшение обработки ambiguous queries, если это потребуется для MVP;
- проверка необходимости containerization и deployment в зависимости от требований курса.

Возможные дальнейшие направления:

- Retrieval optimization;
- Document Standardization;
- поддержка PDF/DOCX/XLSX/HTML/TXT;
- дополнительные evaluation cases;
- расширение Knowledge Base;
- Docker/containerization;
- deployment.

Advanced RAG approaches добавляются только при наличии измеренного обоснования.

## Project Philosophy

EgoBiz Wiki создаётся как небольшой, понятный и воспроизводимый рабочий MVP, а не как максимально сложная AI-система.

Архитектура должна оставаться:

- простой;
- тестируемой;
- расширяемой;
- понятной для сопровождения;
- достаточной для поставленной задачи.

> **SIMPLE, COMPLETE & WORKING MVP > COMPLEX, UNSTABLE PRODUCT**

