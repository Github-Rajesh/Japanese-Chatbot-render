@echo off
echo Starting Japanese Knowledge Base Chatbot Backend...
echo.

REM Activate virtual environment
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo Virtual environment activated.
) else (
    echo Error: Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then run: .venv\Scripts\activate
    echo Then run: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Start backend server
echo.
echo Starting FastAPI server on http://localhost:8000
echo Press Ctrl+C to stop the server.
echo.

cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

