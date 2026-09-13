# СОСТОЯНИЕ ПРОЕКТА — EgoBiz Wiki

## Текущий Commit

**Commit #02 — Knowledge Base**

Статус: **РЕАЛИЗОВАН — ожидает локальной проверки и Git commit**

## Реализовано

- Стандартизированная демонстрационная Knowledge Base для EgoTech Solutions.
- 6 предметных областей: HR, IT, Security, Operations, Customer Operations, FAQ.
- 23 Markdown-документа с русскоязычным бизнес-контентом.
- Единое техническое именование файлов и директорий: English `snake_case`.
- Единая metadata strategy в `knowledge_base/manifest.yaml`.
- Стабильные `document_id` и однозначная связь metadata с файлами.
- Source strategy для будущих citations.
- Документы подготовлены для последующего chunking/indexing.
- Dataset содержит основу для simple lookup, instruction lookup, cross-document, ambiguous и out-of-KB сценариев.
- Добавлена документация `docs/KNOWLEDGE_BASE.md`.
- Добавлены автоматические проверки структуры manifest и Markdown dataset.

## Важное архитектурное решение

MVP использует сознательно стандартизированный «идеальный документооборот»: Markdown, English `snake_case` для технических имён, русский бизнес-контент, единый manifest и единая metadata strategy.

Это внутренний нормализованный формат MVP, а не утверждение о том, что реальная корпоративная документация всегда организована так же.

**Document Standardization** вынесена в Roadmap как отдельная будущая feature для обработки разнородных PDF/DOCX/XLSX/HTML/TXT и приведения их к единому внутреннему представлению.

## Проверки

- Manifest parsing и metadata validation.
- Уникальность `document_id`.
- Уникальность путей.
- Наличие всех файлов, зарегистрированных в manifest.
- Отсутствие пустых/placeholder-документов.

## Ограничения

В Commit #02 НЕ реализованы embeddings, ChromaDB, indexing pipeline, retrieval, RAG, LLM integration, API `/chat`, Streamlit и автоматическая стандартизация документов.

## Следующий Commit

**Commit #03 — Indexing**

Следующий этап должен загрузить стандартизированные документы, выполнить chunking, создать embeddings и подготовить ChromaDB index.
