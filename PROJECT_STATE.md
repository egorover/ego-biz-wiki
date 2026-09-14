# СОСТОЯНИЕ ПРОЕКТА — EgoBiz Wiki

## Текущий Commit

**Commit #03 — Indexing**

Статус: **РЕАЛИЗОВАН — ожидает Git commit**

## Реализовано

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
* Добавлены unit и integration tests для indexing subsystem.
* Конфигурация indexing вынесена в Pydantic Settings.
* API key хранится только во внешнем `.env` и не отслеживается Git.

## Архитектура Commit #03

Текущий indexing pipeline:

Knowledge Base
↓
manifest.yaml
↓
Document loading
↓
Metadata
↓
Chunking
↓
Embeddings
↓
ChromaDB

Application orchestration выполняется через `IndexingService`.

Domain-модели не зависят от ChromaDB, LangChain или конкретного provider SDK.

ChromaDB используется непосредственно через `chromadb`.

Embeddings реализованы через `langchain-openai` и OpenAI-compatible API.

## Проверки

### Tests

Полный test suite:

**16 passed, 1 warning**

Предупреждение относится к совместимости `Starlette` / `AnyIO` и не связано с кодом Commit #03.

### Dependencies

Проверены фактически используемые зависимости:

* `PyYAML`
* `chromadb`
* `langchain-openai`
* `langchain-text-splitters`
* `tiktoken`

Импорты проходят успешно.

Отдельный пакет `langchain-chroma` для текущей реализации не используется.

### Real indexing

Реальный indexing выполнен через ProxyAPI.

Результат:

* Documents loaded: **23**
* Chunks created: **23**
* Embeddings API response: **HTTP 200 OK**
* Chroma collection: **`ego_biz_wiki`**
* Chroma records: **23**

После повторного запуска indexing:

* Chroma records: **23**

Таким образом, повторный indexing не создаёт дубликаты логических chunks.

### Security

Проверено:

```text
git check-ignore .env
→ .env
```

Локальный `.env` не отслеживается Git.

Секреты не должны включаться в Git или logging.

## Важные архитектурные решения

MVP использует сознательно стандартизированный «идеальный документооборот»: Markdown, English `snake_case` для технических имён, русский бизнес-контент, единый manifest и единая metadata strategy.

Это внутренний нормализованный формат MVP, а не утверждение о том, что реальная корпоративная документация всегда организована так же.

**Document Standardization** вынесена в Roadmap как отдельная будущая feature для обработки разнородных PDF/DOCX/XLSX/HTML/TXT и приведения их к единому внутреннему представлению.

Для Commit #03 сознательно не реализованы:

* Retrieval
* RAG
* reranking
* hybrid search
* Agentic RAG
* LLM answer generation
* API `/index`
* Streamlit integration
* long-term memory

## Ограничения

Commit #03 создаёт индекс, пригодный для последующего Retrieval, но Retrieval пока не реализован.

Количество chunks зависит от фактического содержимого документов. Для текущего набора 23 документов после indexing получено 23 chunks.

Параметры `chunk_size=800` и `chunk_overlap=120` являются стартовыми и должны быть дополнительно проверены на этапе evaluation.

## Следующий Commit

**Commit #04 — Retrieval**

Следующий этап должен реализовать similarity search по существующему ChromaDB index и вернуть релевантные chunks с их metadata и source information.

## Git State

Текущий базовый commit перед Commit #03:

`9bc1f68 feat: add knowledge base`

Commit #03 на момент обновления данного файла:

**ещё не создан.**
