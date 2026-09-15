# EgoBiz Wiki

## AI Business Knowledge Assistant

EgoBiz Wiki — компактный RAG-ассистент для ответов на вопросы сотрудников на основе контролируемой корпоративной базы знаний.

## Текущий статус

## Level 4 — Development

## Commit #05 — RAG Pipeline

Проект содержит работоспособный end-to-end RAG pipeline:

`User Query → Retrieval → Context → LLM → Answer + Sources`

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
* dependency injection через application interfaces;
* OpenAI-compatible LLM integration;
* unit и integration tests.

Для MVP используется:

```text
RETRIEVAL_TOP_K=5
RETRIEVAL_SCORE_THRESHOLD=1.30
```

Threshold `1.30` выбран на основе реального retrieval smoke test на текущей демонстрационной Knowledge Base. Для релевантного запроса `Как оформить отпуск?` результаты имели distance до `1.2040`, а для явно нерелевантного запроса `Как заказать домик на Марсе?` ближайший результат имел distance `1.4995`.

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

Полный test suite:

```powershell
python -m pytest
```

## Knowledge Base

В Commit #02 добавлена стандартизированная демонстрационная база знаний EgoTech Solutions.

Формат, metadata strategy и принцип «идеального документооборота» описаны в:

`docs/KNOWLEDGE_BASE.md`

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

Подробное описание:

`docs/INDEXING.md`

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

`docs/RETRIEVAL.md`

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

## Testing

Текущий полный test suite:

**41 passed, 1 warning**

Предупреждение относится к `Starlette / AnyIO` и не связано с логикой проекта.

Дополнительно выполнены реальные smoke tests через ProxyAPI и FastAPI `/chat` для:

* `Как оформить отпуск?`
* `Как подключиться к VPN?`
* `Что делать при фишинговом письме?`
* `Как заказать домик на Марсе?`

Релевантные вопросы возвращают grounded answers и источники.

Out-of-KB запрос возвращает fallback и пустой список источников.

## Security

Локальный `.env` не отслеживается Git.

Секреты не должны включаться в Git или logging.

## Что сознательно НЕ реализовано

В текущем MVP не реализованы:

* API `/search`;
* Streamlit UI;
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

1. `/search` API;
2. Streamlit UI;
3. evaluation dataset и формальная оценка качества;
4. Document Standardization для разнородных PDF/DOCX/XLSX/HTML/TXT;
5. дальнейшее улучшение retrieval только на основании результатов evaluation.

## Главный принцип проекта

**SIMPLE, COMPLETE & WORKING MVP > COMPLEX, UNSTABLE PRODUCT**
