@echo off
setlocal
cd /d "%~dp0"

echo [BEI] Checking for frontend production build...
if not exist "app\ui\dist\index.html" (
    echo [BEI] ERROR: React production build not found in app\ui\dist.
    echo [BEI] Please run SETUP_BEI.bat first to build the frontend.
    pause
    exit /b 1
)

echo [BEI] Starting FastAPI Backend on 127.0.0.1:8001...
if exist "venv\Scripts\python.exe" (
    start "BEI Backend" cmd /c "venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001"
) else (
    start "BEI Backend" cmd /c "python -m uvicorn app.main:app --host 127.0.0.1 --port 8001"
)

echo [BEI] Waiting for backend health check...
:wait_loop
curl -s http://127.0.0.1:8001/health >nul 2>&1
if %errorlevel% neq 0 (
    timeout /t 1 >nul
    goto wait_loop
)

echo [BEI] Backend is ready. Launching browser...
start http://127.0.0.1:8001/

echo [BEI] Application launched successfully!
echo [BEI] Keep the backend console window open to use the application.
