@echo off
echo Starting Japanese Knowledge Base Chatbot Frontend...
echo.

REM Check if Python HTTP server can be used
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found!
    pause
    exit /b 1
)

cd frontend
echo Starting HTTP server on http://localhost:3000
echo.
echo Open your browser and go to: http://localhost:3000
echo Press Ctrl+C to stop the server.
echo.

python -m http.server 3000

