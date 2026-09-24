@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found.
    echo Expected: %~dp0.venv
    pause
    exit /b 1
)

echo Checking EgoBiz Wiki backend...

powershell -NoProfile -Command "$connection = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue; if ($connection) { exit 0 } else { exit 1 }"

if errorlevel 1 (
    echo Starting EgoBiz Wiki backend...
    start "EgoBiz Wiki - API" cmd /k ".venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
) else (
    echo EgoBiz Wiki backend is already running.
)

timeout /t 3 /nobreak >nul

echo Checking EgoBiz Wiki UI...

powershell -NoProfile -Command "$connection = Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue; if ($connection) { exit 0 } else { exit 1 }"

if errorlevel 1 (
    echo Starting EgoBiz Wiki UI...
    start "EgoBiz Wiki - Streamlit" cmd /k ".venv\Scripts\python.exe -m streamlit run ui\streamlit_app.py"
) else (
    echo EgoBiz Wiki UI is already running.
)

exit /b 0