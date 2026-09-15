# СОСТОЯНИЕ ПРОЕКТА — EgoBiz Wiki

## Текущий Commit

**Commit #04 — Retrieval**

Статус: **РЕАЛИЗОВАН — ожидает Git commit**

## Реализовано

### Knowledge Base и Indexing

* Сохранён и подтверждён нормализованный формат Knowledge Base из Commit #02.
* Реализован indexing pipeline для корпоративной Knowledge Base.
* Добавлена загрузка документов через `knowledge_base/manifest.yaml`.
* Реализована передача document metadata в индекс.
* Реализован token-aware chunking.
* Начальные параметры chunking: `chunk_size=800`, `chunk_overlap=120`.
* Реализована генерация embeddings через OpenAI-compatible API.
* Поддерживается работа через ProxyAPI с использованием `OPENAI_BASE_URL`.
* Реализовано persistent storage в ChromaDB.
* Используется коллекция `ego_biz_wiki`.
* Реализованы детерминированные `chunk_id` в формате `{document_id}:{chunk_index}`.
* Реализован повторный indexing через обновление существующих IDs без создания дубликатов.
* Добавлен CLI entrypoint `scripts/index_knowledge_base.py`.
* Добавлена документация `docs/INDEXING.md`.

### Retrieval

* Реализована semantic retrieval subsystem поверх существующего ChromaDB index.
* Добавлена domain-модель `RetrievedChunk`.
* Добавлен application service `RetrievalService`.
* Application layer работает через `QueryEmbeddingProvider` и `RetrievalVectorStore` Protocols.
* Реализована генерация query embedding через тот же embedding provider, который используется при indexing.
* Добавлен метод `embed_query()` в `OpenAIEmbeddingProvider`.
* Реализован similarity search через native ChromaDB API.
* Реализован configurable `top_k`.
* Значение `RETRIEVAL_TOP_K` по умолчанию: `5`.
* Добавлен опциональный `RETRIEVAL_SCORE_THRESHOLD`.
* Threshold применяется как максимальный Chroma distance: меньшее расстояние означает более близкий результат.
* Результаты сортируются от наиболее близкого к наиболее далёкому.
* Сохраняются `content`, `metadata`, `source`, `document_id`, `chunk_id` и `distance`.
* Пустая ChromaDB collection корректно возвращает пустой результат.
* Реализована валидация пустого query, `top_k` и threshold.
* Добавлены unit и integration tests для Retrieval subsystem.
* Добавлена документация `docs/RETRIEVAL.md`.

## Архитектура Commit #04

Текущий pipeline Retrieval:

```text
User Query
↓
Query Embedding
↓
ChromaDB Similarity Search
↓
Top-K Results
↓
Optional Distance Threshold
↓
Sorted Retrieved Chunks
```

Архитектура приложения:

```text
Domain
↓
Application
↓
Infrastructure
```

`RetrievalService` не зависит от конкретной реализации ChromaDB или embedding provider.

Application layer использует Protocols:

* `QueryEmbeddingProvider`
* `RetrievalVectorStore`

Конкретные инфраструктурные реализации находятся в:

* `app/infrastructure/embeddings/openai.py`
* `app/infrastructure/vector_store/chroma.py`

ChromaDB используется непосредственно через `chromadb`.

Отдельный пакет `langchain-chroma` не используется.

## Проверки

### Tests

Unit tests Retrieval:

**10 passed**

Integration tests Retrieval:

**2 passed**

Полный test suite проекта:

**28 passed, 1 warning**

Предупреждение относится к совместимости `Starlette` / `AnyIO` и не связано с логикой Commit #04.

### Compilation

Проверена компиляция изменённых Python-модулей через `compileall`.

Ошибок компиляции нет.

### Real Retrieval Smoke Test

Выполнен реальный smoke test с существующим ChromaDB index и реальным embedding provider через ProxyAPI.

Проверены запросы:

* `Как оформить отпуск?`
* `Как подключиться к VPN?`
* `Что делать при фишинговом письме?`
* `Как заказать домик на Марсе?`

Для первых трёх запросов возвращены релевантные документы Knowledge Base:

* HR / Политика отпусков
* IT / Корпоративный VPN
* Security / Фишинг

Для out-of-KB запроса про домик на Марсе релевантного документа не найдено; результаты имеют существенно большие distance.

Таким образом, базовый semantic retrieval работает на реальном индексе.

### Security

Проверено:

```text
git check-ignore .env
→ .env
```

Локальный `.env` не отслеживается Git.

Секреты не должны включаться в Git или logging.

## Конфигурация Retrieval

В `.env.example` добавлены:

```text
RETRIEVAL_TOP_K=5
RETRIEVAL_SCORE_THRESHOLD=
```

`RETRIEVAL_SCORE_THRESHOLD` по умолчанию не задан.

Это позволяет на текущем этапе использовать top-K retrieval без обязательного threshold и дополнительно настраивать порог после evaluation.

## Важные архитектурные решения

MVP использует сознательно стандартизированный «идеальный документооборот»: Markdown, English `snake_case` для технических имён, русский бизнес-контент, единый manifest и единая metadata strategy.

Это внутренний нормализованный формат MVP, а не утверждение о том, что реальная корпоративная документация всегда организована так же.

**Document Standardization** вынесена в Roadmap как отдельная будущая feature для обработки разнородных PDF/DOCX/XLSX/HTML/TXT и приведения их к единому внутреннему представлению.

Основной принцип разработки:

**SIMPLE, COMPLETE & WORKING MVP > COMPLEX, UNSTABLE PRODUCT**

Поэтому Commit #04 реализует только необходимый semantic retrieval и не добавляет преждевременную архитектурную сложность.

## Что сознательно НЕ реализовано

В Commit #04 не реализованы:

* RAG pipeline
* LLM answer generation
* Agentic RAG
* LangGraph
* hybrid search
* reranking
* external web search
* long-term memory
* API `/chat`
* API `/search`
* Streamlit integration

Эти компоненты будут рассматриваться только на соответствующих следующих этапах MVP.

## Ограничения

Retrieval использует distance, возвращаемый ChromaDB.

`RETRIEVAL_SCORE_THRESHOLD` является максимальным допустимым distance, а не нормализованным similarity score.

Текущее значение `RETRIEVAL_TOP_K=5` является стартовой конфигурацией и должно быть дополнительно проверено на этапе evaluation.

Качество retrieval оценивается по фактической релевантности результатов и будет дополнительно проверено на evaluation dataset.

## Следующий Commit

**Следующий этап — RAG pipeline.**

Он должен использовать реализованный Retrieval как источник контекста для генерации ответа через LLM.

При этом должны сохраняться:

* ответ только на основании найденного контекста;
* источники ответа;
* fallback при недостаточном контексте;
* отсутствие внешнего web search в MVP.

## Git State

Последний созданный и отправленный в remote commit:

`b627e32 docs: update README for commit 03`

Текущий Commit #04:

**ещё не создан.**

После завершения проверки Commit #04 должен быть создан отдельным Git commit.

## Следующий рабочий шаг

Перед созданием Git commit необходимо:

1. Проверить `git diff`.
2. Проверить `git status`.
3. Выполнить финальный test suite.
4. Проверить рабочее дерево.
5. Создать Git commit:

```text
feat: implement retrieval
```

6. Выполнить push в `origin/main`.
7. Обновить `PROJECT_STATE.md` после создания commit.
8. Создать backup текущего состояния.
9. Подготовить context-transfer prompt для следующего этапа.

Главный принцип:

**SIMPLE, COMPLETE & WORKING MVP > COMPLEX, UNSTABLE PRODUCT**
