@echo off
setlocal
cd /d "%~dp0.."
if not exist ".venv\Scripts\python.exe" (
  py -3.12 -m venv .venv
  if errorlevel 1 (
    echo Install Python 3.12 from python.org, then run this script again.
    exit /b 1
  )
)
".venv\Scripts\python.exe" -m pip install --require-hashes -r requirements.lock
if errorlevel 1 exit /b 1
call npm ci --no-audit --no-fund
if errorlevel 1 exit /b 1
call npm run build:desktop
if errorlevel 1 exit /b 1
echo Setup complete. Run scripts\start.cmd to start Chembrain.
