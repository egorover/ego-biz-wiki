# Локальная настройка

## Требования

Python 3.12 или новее в поддерживаемом диапазоне Python 3.x.

## Windows PowerShell

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

Ожидаемый ответ health-check:

```json
{
  "status": "ok",
  "service": "EgoBiz Wiki",
  "version": "0.1.0"
}
```

## Knowledge Base

Демонстрационная база знаний находится в `knowledge_base/`. Её структура и правила подготовки документов описаны в `docs/KNOWLEDGE_BASE.md`.
