@echo off
echo [BEI] Stopping BEI Backend running on port 8001...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo [BEI] Stopped successfully.
pause
