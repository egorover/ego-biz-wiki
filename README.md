# EgoBiz Wiki

## AI Business Knowledge Assistant

EgoBiz Wiki — компактный RAG-ассистент для ответов на вопросы сотрудников на основе контролируемой корпоративной базы знаний.

## Текущий статус

## Level 4 — Development

## Commit #06 — Search Endpoint

Проект содержит работоспособный end-to-end RAG pipeline и отдельный semantic search API:

```text
User Query → Retrieval → Context → LLM → Answer + Sources
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
* dependency injection через application interfaces;
* OpenAI-compatible LLM integration;
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

```powershell
python -m uvicorn app.main:app --reload
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

## Knowledge Base

В Commit #02 добавлена стандартизированная демонстрационная база знаний EgoTech Solutions.

Формат, metadata strategy и принцип «идеального документооборота» описаны в:

```text
docs/KNOWLEDGE_BASE.md
```

Это сознательно нормализованный внутренний формат MVP, а не утверждение о реальном состоянии корпоративной документации.

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

## Testing

Текущий полный test suite:

**45 passed, 1 warning**

Предупреждение относится к `Starlette / AnyIO` и не связано с логикой проекта.

Дополнительно выполнены реальные API smoke tests.

Проверены:

* `GET /health`;
* `POST /chat`;
* `POST /search`.

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

## Security

Локальный `.env` не отслеживается Git.

Секреты не должны включаться в Git или logging.

## Что сознательно НЕ реализовано

В текущем MVP не реализованы:

* Streamlit UI;
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

1. Streamlit UI;
2. evaluation dataset и формальная оценка качества;
3. Document Standardization для разнородных PDF/DOCX/XLSX/HTML/TXT;
4. дальнейшее улучшение retrieval только на основании результатов evaluation;
5. другие расширения MVP только при наличии обоснованных требований.

## Главный принцип проекта

**SIMPLE, COMPLETE & WORKING MVP > COMPLEX, UNSTABLE PRODUCT**
