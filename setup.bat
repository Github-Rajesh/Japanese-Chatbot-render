@echo off
echo ============================================
echo Japanese Knowledge Base Chatbot Setup
echo ============================================
echo.

REM Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found! Please install Python 3.9+
    pause
    exit /b 1
)
python --version
echo.

REM Create virtual environment
echo [2/5] Creating virtual environment...
if exist .venv (
    echo Virtual environment already exists. Skipping...
) else (
    python -m venv .venv
    echo Virtual environment created.
)
echo.

REM Activate and install dependencies
echo [3/5] Installing dependencies...
call .venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
echo.

REM Check Ollama
echo [4/5] Checking Ollama installation...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: Ollama not found!
    echo Please install Ollama from: https://ollama.ai
    echo Then run: ollama pull yuiseki/rakutenai-2.0-mini:1.5b-instruct
) else (
    echo Ollama found!
    echo.
    echo Checking RakutenAI model...
    ollama list | findstr "rakutenai-2.0-mini" >nul 2>&1
    if %errorlevel% neq 0 (
        echo RakutenAI model not found. Pulling model...
        ollama pull yuiseki/rakutenai-2.0-mini:1.5b-instruct
    ) else (
        echo RakutenAI model is installed.
    )
)
echo.

REM Check .env file
echo [5/5] Checking environment configuration...
if exist .env (
    echo .env file found.
) else (
    echo Warning: .env file not found!
    echo Please create .env file with your OpenAI API key.
)
echo.

echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Ensure .env file contains your OPENAI_API_KEY
echo 2. Run start_backend.bat to start the backend server
echo 3. Run start_frontend.bat to start the frontend
echo 4. Open http://localhost:3000 in your browser
echo.
pause

