# СОСТОЯНИЕ ПРОЕКТА — EgoBiz Wiki

## Текущий Commit

**Commit #05 — RAG Pipeline**

Статус: **РЕАЛИЗОВАН — ПРОТЕСТИРОВАН — ГОТОВ К COMMIT**

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
* Добавлены `ChatRequest`, `ChatResponse` и `ChatSource`.
* Добавлена dependency injection через `get_rag_service`.
* FastAPI route не содержит инфраструктурной логики.

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

## Проверки

### Full test suite

**41 passed, 1 warning**

Warning:

`Starlette / AnyIO DeprecationWarning`

Предупреждение относится к внешней зависимости и не связано с логикой проекта.

### Real end-to-end smoke tests

Проверены:

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

Таким образом, end-to-end flow работает через:

```text
FastAPI → RAGService → RetrievalService → ChromaDB → LLM
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

* `POST /search`;
* Streamlit UI;
* formal evaluation dataset;
* Document Standardization;
* Agentic RAG;
* hybrid search;
* reranking;
* external web search;
* long-term memory.

## Следующий этап

Следующий рабочий этап — **Commit #06**.

Предварительно необходимо определить его минимальную границу и не начинать реализацию до подтверждения плана.

Приоритетные следующие компоненты:

1. `POST /search`;
2. Streamlit UI;
3. evaluation dataset.

При выборе следующего этапа сохраняется принцип:

**SIMPLE, COMPLETE & WORKING MVP > COMPLEX, UNSTABLE PRODUCT**

## Git State

Перед завершением Commit #05 необходимо проверить:

```text
git status
git log
git remote
```

После commit:

* local `main` должен быть синхронизирован с `origin/main`;
* рабочее дерево должно быть чистым.

## Backup

После завершения Commit #05 необходимо создать backup без:

```text
.git
.venv
__pycache__
.pytest_cache
```

Предыдущий backup:

```text
C:\Users\alexe\Desktop\ego-biz-wiki-backup-commit04
```

## Завершение Commit #05

До финального commit необходимо:

1. Обновить README.
2. Обновить PROJECT_STATE.
3. Проверить полный test suite.
4. Проверить `git diff --check`.
5. Проверить staged diff.
6. Создать Git commit.
7. Push в `origin/main`.
8. Проверить GitHub synchronization.
9. Проверить чистое рабочее дерево.
10. Создать backup.
11. Подготовить Transfer Prompt для следующего чата.
