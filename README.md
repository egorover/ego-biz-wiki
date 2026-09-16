# EgoBiz Wiki

## AI Business Knowledge Assistant

EgoBiz Wiki — компактный RAG-ассистент для ответов на вопросы сотрудников на основе контролируемой корпоративной базы знаний.

## Текущий статус

## Level 4 — Development

## Commit #07 — Streamlit UI

Проект содержит работоспособный end-to-end RAG pipeline, semantic search API и минимальный пользовательский интерфейс Streamlit:

```text
User → Streamlit UI → FastAPI → Retrieval → Context → LLM → Answer + Sources
```

Для поиска без генерации ответа:

```text
Search Query → Retrieval → Search Results
```

Реализованы:

* стандартизированная демонстрационная Knowledge Base EgoTech Solutions;

* indexing pipeline;

* persistent ChromaDB index;

* semantic retrieval;

* configurable `top_k`;

* configurable distance threshold;

* grounded LLM answer generation;

* fallback при недостаточном контексте;

* источники ответа;

* FastAPI endpoint `/chat`;

* FastAPI endpoint `/search`;

* FastAPI endpoint `/index`;

* dependency injection через application interfaces;

* OpenAI-compatible LLM integration;

* Streamlit UI;

* отображение ответа и источников в пользовательском интерфейсе;

* обработка пустого запроса;

* обработка недоступности FastAPI;

* unit и integration tests.

Для MVP используется:

```text
RETRIEVAL_TOP_K=5

RETRIEVAL_SCORE_THRESHOLD=1.30
```

Threshold `1.30` выбран на основе реальных retrieval smoke tests на текущей демонстрационной Knowledge Base.

Для релевантного запроса:

```text
Как оформить отпуск?
```

результаты имели distance до `1.2040`.

Для явно нерелевантного запроса:

```text
Как заказать домик на Марсе?
```

ближайший результат имел distance `1.4995`.

При отсутствии результатов после threshold применяется точный fallback:

```text
В базе знаний не найдено достаточно информации для достоверного ответа на этот вопрос.
```

В этом случае источники не возвращаются.

## Архитектура

Основной application flow:

```text
User Query
    ↓
Streamlit UI
    ↓
POST /chat
    ↓
FastAPI
    ↓
Query Embedding
    ↓
ChromaDB Similarity Search
    ↓
Top-K
    ↓
Distance Threshold
    ↓
Retrieved Context
    ↓
LLM
    ↓
Answer + Sources
```

Search flow:

```text
Search Query
    ↓
POST /search
    ↓
FastAPI
    ↓
Query Embedding
    ↓
ChromaDB Similarity Search
    ↓
Top-K
    ↓
Distance Threshold
    ↓
Search Results
```

Для `POST /search` LLM не используется.

Архитектура приложения:

```text
Domain
    ↓
Application
    ↓
Infrastructure
    ↓
API
```

Streamlit является отдельным пользовательским интерфейсом и не содержит собственной RAG-логики.

Application layer не зависит от конкретной реализации LLM, embeddings или vector store.

Для этого используются Protocols:

* `QueryEmbeddingProvider`

* `RetrievalVectorStore`

* `RAGLLMProvider`

* `RAGRetrievalService`

Конкретные инфраструктурные реализации находятся в `app/infrastructure/`.

## Требования

* Python 3.12+

* pip

* Git

## Локальная установка

### Windows PowerShell

```powershell
py -3.12 -m venv .venv

.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

python -m pip install -e ".[test]"

Copy-Item .env.example .env
```

Перед запуском необходимо настроить API credentials в `.env`.

Для ProxyAPI:

```text
OPENAI_BASE_URL=https://api.proxyapi.ru/openai/v1
```

## Запуск

FastAPI:

```powershell
python -m uvicorn app.main:app --reload
```

Streamlit запускается в отдельном PowerShell:

```powershell
streamlit run .\ui\streamlit_app.py
```

Адрес FastAPI для Streamlit настраивается через:

```text
STREAMLIT_API_URL=http://127.0.0.1:8000
```

## Проверка

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Chat:

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/chat" `
  -ContentType "application/json" `
  -Body '{"query":"Как оформить отпуск?"}' |
  ConvertTo-Json -Depth 5
```

Search:

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/search" `
  -ContentType "application/json" `
  -Body '{"query":"Как оформить отпуск?"}' |
  ConvertTo-Json -Depth 5
```

Полный test suite:

```powershell
python -m pytest
```

Streamlit:

```powershell
streamlit run .\ui\streamlit_app.py
```

После запуска Streamlit использует существующий FastAPI endpoint `/chat`.

## Knowledge Base

В Commit #02 добавлена стандартизированная демонстрационная база знаний EgoTech Solutions.

Формат, metadata strategy и принцип «идеального документооборота» описаны в:

```text
docs/KNOWLEDGE_BASE.md
```

Это сознательно нормализованный внутренний формат MVP, а не утверждение о реальном состоянии корпоративной документации.

Текущая Knowledge Base содержит 23 Markdown-документа и `manifest.yaml`.

## Indexing

В Commit #03 реализован indexing pipeline:

```text
Documents
    ↓
Manifest
    ↓
Load
    ↓
Chunking
    ↓
Embeddings
    ↓
ChromaDB
```

Основные параметры chunking:

```text
chunk_size=800

chunk_overlap=120
```

Подробное описание:

```text
docs/INDEXING.md
```

## Retrieval

В Commit #04 реализован semantic retrieval поверх ChromaDB.

Retrieval pipeline:

```text
Query
    ↓
Query Embedding
    ↓
Chroma Similarity Search
    ↓
Top-K
    ↓
Distance Threshold
    ↓
Retrieved Chunks
```

Подробное описание:

```text
docs/RETRIEVAL.md
```

## RAG

В Commit #05 retrieval подключён к LLM и реализован полноценный MVP RAG pipeline.

RAG service:

```text
Query
    ↓
Retrieval
    ↓
Context
    ↓
LLM
    ↓
RAGResponse
    ├── answer
    └── sources
```

LLM получает только retrieved context и системную инструкцию не использовать внешние знания и не выдумывать факты.

При отсутствии релевантного контекста LLM не вызывается, а application layer возвращает фиксированный fallback.

## Search

В Commit #06 реализован отдельный API для semantic search:

```text
POST /search
```

Search endpoint использует существующий `RetrievalService` и не вызывает LLM.

Request:

```json
{
  "query": "Как оформить отпуск?"
}
```

Response:

```json
{
  "results": [
    {
      "chunk_id": "...",
      "document_id": "hr-vacation-policy",
      "title": "Политика отпусков",
      "source": "HR / Политика отпусков",
      "content": "...",
      "distance": 0.68
    }
  ]
}
```

При отсутствии релевантных результатов:

```json
{
  "results": []
}
```

Параметры retrieval для Search API берутся из конфигурации приложения:

```text
RETRIEVAL_TOP_K=5

RETRIEVAL_SCORE_THRESHOLD=1.30
```

Дополнительные `top_k` и `threshold` в API request не передаются.

## Streamlit UI

В Commit #07 реализован минимальный пользовательский интерфейс на Streamlit.

Streamlit UI использует существующий FastAPI backend и не содержит собственной RAG-логики.

Основной flow:

```text
User
    ↓
Streamlit UI
    ↓
POST /chat
    ↓
FastAPI
    ↓
RAG Pipeline
    ↓
Answer + Sources
```

UI поддерживает:

* ввод вопроса;

* проверку пустого запроса;

* получение ответа через существующий `POST /chat`;

* отображение ответа;

* отображение источников;

* отображение fallback при отсутствии достаточного контекста;

* сообщение об ошибке при недоступности FastAPI.

UI является тонким presentation layer и не дублирует retrieval или RAG logic.

## API

### `GET /health`

Проверка доступности приложения.

### `POST /chat`

Ответ на вопрос пользователя на основании Knowledge Base.

Request:

```json
{
  "query": "Как оформить отпуск?"
}
```

Response:

```json
{
  "answer": "...",
  "sources": [
    {
      "document_id": "hr-vacation-policy",
      "title": "Политика отпусков",
      "source": "HR / Политика отпусков"
    }
  ]
}
```

Если релевантный контекст отсутствует:

```json
{
  "answer": "В базе знаний не найдено достаточно информации для достоверного ответа на этот вопрос.",
  "sources": []
}
```

### `POST /search`

Semantic search по Knowledge Base без генерации ответа LLM.

Request:

```json
{
  "query": "Как оформить отпуск?"
}
```

Response содержит:

```text
chunk_id

document_id

title

source

content

distance
```

### `POST /index`

Индексация документов Knowledge Base.

Endpoint используется для построения и обновления persistent ChromaDB index.

## Testing

Текущий полный test suite:

**45 passed, 1 warning**

Предупреждение относится к `Starlette / AnyIO` и не связано с логикой проекта.

Дополнительно выполнены реальные API smoke tests.

Проверены:

* `GET /health`;

* `POST /chat`;

* `POST /search`;

* запуск Streamlit UI;

* взаимодействие Streamlit UI с FastAPI.

Для `POST /search` проверены:

* релевантный запрос `Как оформить отпуск?`;

* нерелевантный запрос `Как заказать домик на Марсе?`;

* корректное возвращение search results;

* корректное возвращение пустого списка результатов;

* отсутствие вызова LLM.

Для `POST /chat` проверены:

* `Как оформить отпуск?`;

* `Как подключиться к VPN?`;

* `Что делать при фишинговом письме?`;

* `Как заказать домик на Марсе?`.

Релевантные вопросы возвращают grounded answers и источники.

Out-of-KB запрос возвращает fallback и пустой список источников.

Для Streamlit UI проверены:

* запуск интерфейса;

* ввод релевантного вопроса;

* получение ответа через FastAPI;

* отображение источников;

* обработка fallback;

* обработка пустого запроса;

* обработка недоступности FastAPI.

## Security

Локальный `.env` не отслеживается Git.

Секреты не должны включаться в Git или logging.

## Что сознательно НЕ реализовано

В текущем MVP не реализованы:

* formal evaluation dataset;

* Document Standardization для разнородных PDF/DOCX/XLSX/HTML/TXT;

* Agentic RAG;

* LangGraph;

* hybrid search;

* reranking;

* external web search;

* long-term memory;

* сложная multi-agent orchestration.

Эти компоненты не добавляются до тех пор, пока они не будут оправданы требованиями MVP и evaluation.

## Roadmap

Следующие возможные этапы:

1. evaluation dataset и формальная оценка качества;

2. Document Standardization для разнородных PDF/DOCX/XLSX/HTML/TXT;

3. дальнейшее улучшение retrieval только на основании результатов evaluation;

4. другие расширения MVP только при наличии обоснованных требований.

**Streamlit UI уже реализован в Commit #07 и больше не является частью Roadmap.**

## Главный принцип проекта

**SIMPLE, COMPLETE & WORKING MVP > COMPLEX, UNSTABLE PRODUCT**
