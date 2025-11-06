#!/bin/bash
# Docker deployment script for Japanese Chatbot

set -e

echo "🚀 Japanese Chatbot Docker Deployment"
echo "======================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating .env from template..."
    if [ -f .denv.example ]; then
        cp .denv.example .env
        echo "✅ Created .env file. Please edit it and add your OPENAI_API_KEY"
        echo ""
        read -p "Press Enter after you've added your API key to .env..."
    else
        echo "❌ Error: .denv.example not found. Please create .env manually."
        exit 1
    fi
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/vectorstore
mkdir -p "knowledge base main/uploads"
echo "✅ Directories created"
echo ""

# Build and start containers
echo "🔨 Building and starting containers..."
docker-compose up -d --build

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Container Status:"
docker-compose ps
echo ""
echo "🌐 Access the application:"
echo "   Frontend: http://localhost"
echo "   Backend API: http://localhost:8000"
echo ""
echo "📝 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""

