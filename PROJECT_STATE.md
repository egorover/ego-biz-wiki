# СОСТОЯНИЕ ПРОЕКТА — EgoBiz Wiki

## Текущий Commit

**Commit #06 — Search Endpoint**

Статус: **РЕАЛИЗОВАН — ПРОТЕСТИРОВАН — ЗАКОММИЧЕН — ОТПРАВЛЕН В GITHUB**

Commit:

```text
7dff25b feat: implement search endpoint
```

GitHub:

```text
https://github.com/egorover/ego-biz-wiki
```

## Реализовано

### Knowledge Base

* Сохранён нормализованный формат Knowledge Base из Commit #02.
* Используется демонстрационная корпоративная база знаний EgoTech Solutions.
* Knowledge Base содержит 23 Markdown-документа.
* Используется единый `manifest.yaml`.
* Используется единая metadata strategy.

### Indexing

* Реализован indexing pipeline.

* Реализована загрузка документов через `knowledge_base/manifest.yaml`.

* Реализован token-aware chunking.

* Начальные параметры:

  * `chunk_size=800`
  * `chunk_overlap=120`

* Реализована генерация embeddings через OpenAI-compatible API.

* Поддерживается ProxyAPI через `OPENAI_BASE_URL`.

* Реализовано persistent storage в ChromaDB.

* Используется коллекция `ego_biz_wiki`.

* Используются детерминированные `chunk_id`.

* Повторный indexing выполняется через upsert.

* Добавлена документация `docs/INDEXING.md`.

### Retrieval

* Реализована semantic retrieval subsystem.

* Добавлена domain-модель `RetrievedChunk`.

* Добавлен application service `RetrievalService`.

* Application layer использует:

  * `QueryEmbeddingProvider`
  * `RetrievalVectorStore`

* Реализован query embedding.

* Реализован ChromaDB similarity search.

* Реализован configurable `top_k`.

* Реализован configurable distance threshold.

* Результаты сортируются по distance.

* Реализовано сохранение metadata, source, document_id, chunk_id и distance.

* Реализована обработка пустой ChromaDB collection.

* Реализована валидация query, `top_k` и threshold.

* Добавлена документация `docs/RETRIEVAL.md`.

### RAG

* Добавлена domain-модель `RAGResponse`.
* Добавлена domain-модель `RAGSource`.
* Реализован application service `RAGService`.
* Retrieval подключён к RAG application flow.
* Реализована передача retrieved chunks в LLM context.
* Реализована генерация grounded answer через LLM.
* Реализован фиксированный fallback при отсутствии релевантного контекста.
* При отсутствии context LLM не вызывается.
* Реализовано формирование уникального списка источников.
* Application layer не зависит от конкретного LLM provider.

### LLM

* Добавлен `RAGLLMProvider` Protocol.
* Добавлен `OpenAILLMProvider`.
* Используется `ChatOpenAI` через OpenAI-compatible API.
* Добавлена конфигурация `CHAT_MODEL`.
* По умолчанию используется `gpt-4o-mini`.
* System prompt требует отвечать только на основании предоставленного context.
* System prompt запрещает использование внешних знаний и выдумывание фактов.
* Ответы генерируются на русском языке.

### API

* Сохранён `GET /health`.
* Добавлен `POST /chat`.
* Добавлен `POST /search`.
* Добавлены `ChatRequest`, `ChatResponse` и `ChatSource`.
* Добавлены `SearchRequest`, `SearchResponse` и `SearchResult`.
* Добавлена dependency injection через `get_rag_service`.
* Добавлена dependency injection через `get_retrieval_service`.
* `POST /search` использует существующий `RetrievalService`.
* `POST /search` не вызывает LLM.
* FastAPI routes не содержат инфраструктурной логики.

### Search Endpoint

Реализован:

```text
POST /search
```

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

Endpoint использует параметры retrieval из application configuration:

```text
RETRIEVAL_TOP_K=5
RETRIEVAL_SCORE_THRESHOLD=1.30
```

Дополнительные `top_k` и `threshold` в API request не передаются.

## Текущий RAG pipeline

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

Для `POST /search` pipeline заканчивается на retrieved results:

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

LLM для `POST /search` не используется.

## Конфигурация Retrieval

Текущие параметры:

```text
RETRIEVAL_TOP_K=5
RETRIEVAL_SCORE_THRESHOLD=1.30
```

Threshold `1.30` выбран на основании реального smoke test текущей Knowledge Base.

Измеренные значения:

```text
Relevant:
0.6799
1.0037
1.0832
1.1158
1.2040

Irrelevant:
1.4995
1.6523
1.6688
1.6930
1.7101
```

Таким образом, для текущей демонстрационной Knowledge Base threshold `1.30` сохраняет релевантные результаты и отбрасывает результаты явно нерелевантного запроса.

Важно: threshold является эмпирической конфигурацией текущего MVP, а не универсальным значением для любых embedding models или корпусов.

## Fallback

Точный fallback:

```text
В базе знаний не найдено достаточно информации для достоверного ответа на этот вопрос.
```

При отсутствии retrieved chunks:

```text
answer = fallback
sources = []
```

LLM при этом не вызывается.

Для `POST /search` при отсутствии релевантных результатов возвращается:

```json
{
  "results": []
}
```

## Проверки

### Full test suite

**45 passed, 1 warning**

Warning:

`Starlette / AnyIO DeprecationWarning`

Предупреждение относится к внешней зависимости и не связано с логикой проекта.

### API verification

Проверены:

```text
GET /health
POST /chat
POST /search
```

Для `POST /search` проверены:

```text
Положительный запрос:
Как оформить отпуск?
```

Результат:

* HTTP 200;
* найдены релевантные Knowledge Base chunks;
* возвращены `chunk_id`, `document_id`, `title`, `source`, `content`, `distance`;
* LLM не вызывается.

Нерелевантный запрос:

```text
Как заказать домик на Марсе?
```

Результат:

```json
{
  "results": []
}
```

### Search unit tests

Проверены:

* корректное преобразование `RetrievedChunk` в API response;
* пустой список результатов;
* отклонение пустого query;
* корректный вызов `RetrievalService`.

### Integration tests

Проверены:

* `GET /health`;
* `POST /chat`;
* `POST /search`;
* изоляция FastAPI dependency overrides между тестами.

## Real end-to-end smoke tests

Ранее проверены:

```text
Как оформить отпуск?
Как подключиться к VPN?
Что делать при фишинговом письме?
Как заказать домик на Марсе?
```

Первые три запроса вернули grounded answers и релевантные Knowledge Base sources.

Запрос:

```text
Как заказать домик на Марсе?
```

вернул:

```text
В базе знаний не найдено достаточно информации для достоверного ответа на этот вопрос.
```

и:

```json
"sources": []
```

Таким образом, основной end-to-end flow работает через:

```text
FastAPI → RAGService → RetrievalService → ChromaDB → LLM
```

Search flow работает через:

```text
FastAPI → RetrievalService → ChromaDB
```

## Архитектурные решения

Архитектура:

```text
Domain
↓
Application
↓
Infrastructure
↓
API
```

Application layer использует Protocols и не зависит от конкретных инфраструктурных реализаций.

Для `POST /search` используется тот же `RetrievalService`, что и в RAG pipeline. Отдельный механизм поиска не создавался.

MVP сознательно не использует:

* Agentic RAG;
* LangGraph;
* hybrid search;
* reranking;
* external web search;
* long-term memory;
* multi-agent orchestration.

## Knowledge Base — важное решение

MVP использует сознательно стандартизированный **«идеальный документооборот»**:

* Markdown;
* единые технические имена;
* русский бизнес-контент;
* единый manifest;
* единая metadata strategy.

Это нормализованный внутренний формат демонстрационного MVP, а не утверждение о том, что реальные корпоративные документы всегда организованы таким образом.

**Document Standardization** вынесена в Roadmap как будущая feature для обработки разнородных PDF/DOCX/XLSX/HTML/TXT и приведения их к единому внутреннему представлению.

## Security

Проверено:

```text
git check-ignore .env
→ .env
```

Локальный `.env` не отслеживается Git.

API keys не должны попадать в Git или logging.

## Что осталось вне текущего MVP

Не реализованы:

* Streamlit UI;
* formal evaluation dataset;
* Document Standardization;
* Agentic RAG;
* hybrid search;
* reranking;
* external web search;
* long-term memory.

## Следующий этап

Следующий рабочий этап — **Commit #07**.

Предварительно необходимо определить его минимальную границу и не начинать реализацию до подтверждения плана.

Приоритетные следующие компоненты:

1. Streamlit UI;
2. formal evaluation dataset.

При выборе следующего этапа сохраняется принцип:

**SIMPLE, COMPLETE & WORKING MVP > COMPLEX, UNSTABLE PRODUCT**

## Git State

Текущее состояние:

```text
Commit:
7dff25b feat: implement search endpoint
```

Удалённый репозиторий:

```text
https://github.com/egorover/ego-biz-wiki
```

Ветка:

```text
main
```

Синхронизация:

```text
local main = origin/main
```

Рабочее дерево:

```text
clean
```

Последняя проверка:

```text
git status
→ Your branch is up to date with 'origin/main'.
→ nothing to commit, working tree clean
```

## Backup

Backup текущего состояния Commit #06 создан:

```text
C:\Users\alexe\Desktop\ego-biz-wiki-backup-commit06
```

Backup не содержит:

```text
.git
.venv
__pycache__
.pytest_cache
```

Наличие ключевого файла проверено:

```text
app\api\routes\search.py
→ True
```

Предыдущий backup:

```text
C:\Users\alexe\Desktop\ego-biz-wiki-backup-commit05
```

## Завершение Commit #06

Выполнено:

1. Реализован `POST /search`.
2. Добавлены API schemas.
3. Добавлена dependency injection для `RetrievalService`.
4. Добавлены unit tests.
5. Обновлены integration tests.
6. Выполнен полный test suite.
7. Выполнен `git diff --check`.
8. Создан Git commit.
9. Выполнен push в `origin/main`.
10. Проверена GitHub synchronization.
11. Проверено чистое рабочее дерево.
12. Создан backup.
13. Подготовлено состояние проекта для следующего рабочего этапа.
