@echo off
setlocal
cd /d "%~dp0.."
if not exist ".venv\Scripts\python.exe" (
  echo Run scripts\setup.cmd first.
  exit /b 1
)
if not exist "dist\index.html" (
  echo Run scripts\setup.cmd first.
  exit /b 1
)
if "%CHEMBRAIN_PORT%"=="" set "CHEMBRAIN_PORT=8000"
".venv\Scripts\python.exe" -m uvicorn server.app:app --host 127.0.0.1 --port %CHEMBRAIN_PORT%
