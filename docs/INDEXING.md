# Indexing

## Назначение

Commit #03 превращает нормализованную Knowledge Base EgoTech Solutions в индекс,
пригодный для следующего этапа Retrieval.

## Pipeline

```text
knowledge_base/
    ↓
manifest.yaml
    ↓
load Markdown + metadata
    ↓
token-aware chunking
    ↓
OpenAI-compatible embeddings
    ↓
persistent ChromaDB
```

## Конфигурация

По умолчанию используются:

- chunk size: `800` tokens;
- chunk overlap: `120` tokens;
- embedding model: `text-embedding-3-small`;
- Chroma collection: `ego_biz_wiki`;
- local persistence: `.chroma/`.

Настройки задаются через `.env` и `Pydantic Settings`.
`OPENAI_BASE_URL` позволяет направить embedding requests на OpenAI-compatible
ProxyAPI endpoint.

## Запуск

В активированном виртуальном окружении:

```powershell
python scripts/index_knowledge_base.py
```

Успешный запуск должен обработать все документы, зарегистрированные в
`knowledge_base/manifest.yaml`, создать chunks и сохранить их в локальном
ChromaDB.

## Детерминированные IDs

Каждый chunk получает ID вида:

```text
{document_id}:{chunk_index}
```

Повторный запуск использует `upsert`, поэтому существующие logical chunks
обновляются вместо создания дубликатов.

## Metadata

Каждый chunk сохраняет исходную metadata документа, включая `document_id`,
`path`, `title`, `category`, `subcategory`, `source`, `version`, `language`,
`access_level` и `updated_at`, а также `chunk_index`.

## Границы Commit #03

В этом этапе отсутствуют Retrieval, RAG, LLM generation, API `/index`, `/chat`,
Streamlit и long-term memory. Эти функции реализуются последующими commits.
