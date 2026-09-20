@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found.
    echo Expected: %~dp0.venv
    pause
    exit /b 1
)

echo Starting EgoBiz Wiki backend...
start "EgoBiz Wiki - API" cmd /k ".venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

echo Starting EgoBiz Wiki UI...
start "EgoBiz Wiki - Streamlit" cmd /k ".venv\Scripts\python.exe -m streamlit run ui\streamlit_app.py"

exit /b 0