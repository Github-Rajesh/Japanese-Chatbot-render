@echo off
REM Docker deployment script for Japanese Chatbot (Windows)

echo 🚀 Japanese Chatbot Docker Deployment
echo ======================================
echo.

REM Check if .env file exists
if not exist .env (
    echo ⚠️  Warning: .env file not found!
    echo Creating .env from template...
    if exist .denv.example (
        copy .denv.example .env
        echo ✅ Created .env file. Please edit it and add your OPENAI_API_KEY
        echo.
        pause
    ) else (
        echo ❌ Error: .denv.example not found. Please create .env manually.
        exit /b 1
    )
)

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo ✅ Docker is running
echo.

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist "data\vectorstore" mkdir "data\vectorstore"
if not exist "knowledge base main\uploads" mkdir "knowledge base main\uploads"
echo ✅ Directories created
echo.

REM Build and start containers
echo 🔨 Building and starting containers...
docker-compose up -d --build

echo.
echo ✅ Deployment complete!
echo.
echo 📊 Container Status:
docker-compose ps
echo.
echo 🌐 Access the application:
echo    Frontend: http://localhost
echo    Backend API: http://localhost:8000
echo.
echo 📝 View logs:
echo    docker-compose logs -f
echo.
echo 🛑 Stop services:
echo    docker-compose down
echo.

pause

