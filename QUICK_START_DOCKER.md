# Quick Start: Docker Deployment

Follow these steps to deploy your Japanese Chatbot using Docker.

## Prerequisites

✅ Docker Desktop installed and running  
✅ OpenAI API key

## Step 1: Create .env File

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key_here
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=production
```

## Step 2: Deploy

### Option A: Using the deployment script (Windows)
```bash
docker-deploy.bat
```

### Option B: Using the deployment script (Linux/Mac)
```bash
chmod +x docker-deploy.sh
./docker-deploy.sh
```

### Option C: Manual deployment
```bash
docker-compose up -d --build
```

## Step 3: Access the Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000

## Useful Commands

### View logs
```bash
docker-compose logs -f
```

### Stop services
```bash
docker-compose down
```

### Restart services
```bash
docker-compose restart
```

### View running containers
```bash
docker-compose ps
```

## Deploying to a Server in Japan

**📖 For detailed step-by-step instructions, see [DEPLOY_TO_JAPAN.md](DEPLOY_TO_JAPAN.md)**

Quick summary:

1. **Choose a cloud provider** with Japan region:
   - Vultr (Tokyo) - $6/month, easiest
   - DigitalOcean (Tokyo) - $6/month
   - AWS (Tokyo) - Pay-as-you-go
   - Google Cloud (Tokyo) - Free tier available

2. **Create a server** (Ubuntu 22.04, 2GB+ RAM)

3. **Install Docker**:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo apt install docker-compose-plugin -y
   ```

4. **Transfer your project** (via Git or SCP)

5. **Create .env file** with your API key

6. **Deploy**:
   ```bash
   docker compose up -d --build
   ```

7. **Configure firewall**:
   ```bash
   sudo ufw allow 80/tcp
   ```

8. **Access** via `http://YOUR_SERVER_IP`

## Notes

- First startup may take 2-5 minutes to index PDFs
- Vectorstore data is persisted in `./data/vectorstore/`
- Knowledge base PDFs are in `./knowledge base main/`
- Ollama (for RakutenAI) is optional - the app works without it

For detailed deployment instructions, see `DOCKER_DEPLOYMENT.md`.

