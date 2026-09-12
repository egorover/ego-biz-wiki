# EgoBiz Wiki

### AI Business Knowledge Assistant

EgoBiz Wiki — компактный RAG-ассистент для ответов на вопросы сотрудников на основе контролируемой корпоративной базы знаний.

## Текущий статус

**Level 4 — Development**

**Commit #01 — Project Foundation**

На данном этапе проект содержит работоспособный фундамент приложения и эндпоинт `/health`. RAG, индексация базы знаний, интеграция с LLM, поиск релевантной информации и Streamlit UI будут реализованы на последующих этапах.

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
