# EgoBiz Wiki

## AI Business Knowledge Assistant

EgoBiz Wiki — компактный RAG-ассистент для ответов на вопросы сотрудников на основе контролируемой корпоративной базы знаний.

## Текущий статус

## Level 4 — Development

## Commit #02 — Knowledge Base

Проект содержит работоспособный фундамент приложения, эндпоинт `/health` и стандартизированную демонстрационную корпоративную базу знаний. Индексация, embeddings, retrieval, RAG, LLM-интеграция и Streamlit UI будут реализованы на последующих этапах.

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
