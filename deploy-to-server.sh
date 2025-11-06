#!/bin/bash
# Script to deploy Japanese Chatbot to a server
# Run this on your server after connecting via SSH

set -e

echo "🚀 Japanese Chatbot Server Deployment"
echo "======================================"
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Please run with sudo or as root"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose if not installed
if ! command -v docker compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    apt install docker-compose-plugin -y
else
    echo "✅ Docker Compose already installed"
fi

# Configure firewall
echo "🔥 Configuring firewall..."
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env file..."
    cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key_here
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=production
EOF
    echo "✅ Created .env file. Please edit it and add your OPENAI_API_KEY"
    echo ""
    read -p "Press Enter after you've added your API key to .env..."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/vectorstore
mkdir -p "knowledge base main/uploads"
echo "✅ Directories created"

# Build and start containers
echo "🔨 Building and starting containers..."
docker compose up -d --build

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Container Status:"
docker compose ps
echo ""
echo "🌐 Your chatbot is now accessible at:"
echo "   http://$(hostname -I | awk '{print $1}')"
echo ""
echo "📝 To view logs:"
echo "   docker compose logs -f"
echo ""

