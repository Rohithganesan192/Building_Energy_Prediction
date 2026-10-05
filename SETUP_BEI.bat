@echo off
setlocal
cd /d "%~dp0"

echo [BEI] Setting up the Building Energy Intelligence Project...

echo [BEI] Checking Python...
python --version
if %errorlevel% neq 0 (
    echo [BEI] Python is not installed or not in PATH. Please install Python 3.9+.
    pause
    exit /b 1
)

echo [BEI] Checking Node.js...
node --version
if %errorlevel% neq 0 (
    echo [BEI] Node.js is not installed or not in PATH. Please install Node.js 18+.
    pause
    exit /b 1
)

if not exist venv (
    echo [BEI] Creating Python virtual environment...
    python -m venv venv
)

echo [BEI] Installing Python dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt
pip install python-dotenv

if not exist .env (
    echo [BEI] Creating default .env file...
    copy .env.example .env
)

echo [BEI] Installing frontend dependencies and building production assets...
cd app\ui
call npm install
call npm run build
cd ..\..

echo [BEI] Setup completed successfully!
pause
