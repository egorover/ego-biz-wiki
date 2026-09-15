# EgoBiz Wiki

## AI Business Knowledge Assistant

EgoBiz Wiki — компактный RAG-ассистент для ответов на вопросы сотрудников на основе контролируемой корпоративной базы знаний.

## Текущий статус

## Level 4 — Development

## Commit #04 — Retrieval

Проект содержит работоспособный фундамент приложения, эндпоинт `/health`, стандартизированную демонстрационную корпоративную базу знаний, рабочий indexing pipeline и semantic retrieval.

Документы загружаются через `manifest.yaml`, разбиваются на chunks, получают embeddings и сохраняются в persistent ChromaDB index.

Retrieval pipeline выполняет:

`Query → Query Embedding → Chroma Similarity Search → Top-K → Optional Distance Threshold → Retrieved Chunks`

Реализованы unit- и integration-тесты. Текущий полный набор тестов: **28 passed**.

RAG pipeline, LLM-интеграция, API `/search` и `/chat`, а также Streamlit UI будут реализованы на последующих этапах.

## Требования

- Python 3.12+
- pip
- Git

## Локальная установка

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
Copy-Item .env.example .env
```

## Запуск

```powershell
python -m uvicorn app.main:app --reload
```

## Проверка

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
python -m pytest
```

## Knowledge Base

В Commit #02 добавлена стандартизированная демонстрационная база знаний EgoTech Solutions. Формат, metadata strategy и принцип «идеального документооборота» описаны в `docs/KNOWLEDGE_BASE.md`.

## Retrieval

В Commit #04 реализован semantic retrieval поверх существующего ChromaDB index.

Архитектура разделяет Domain, Application и Infrastructure layers. Application layer работает через Protocols, поэтому конкретная реализация vector store не распространяется на application logic.

Подробное описание retrieval pipeline, конфигурации и тестирования: `docs/RETRIEVAL.md`.
