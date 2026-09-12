# Local Setup

## Requirements

Python 3.12 or newer within the supported Python 3.x range.

## Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
Copy-Item .env.example .env
```

## Start

```powershell
python -m uvicorn app.main:app --reload
```

## Verify

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
python -m pytest
```

Expected health response:

```json
{
  "status": "ok",
  "service": "EgoBiz Wiki",
  "version": "0.1.0"
}
```
