# Docker Deployment Guide for Japanese Chatbot

This guide will help you deploy the Japanese Chatbot using Docker so it can be accessed by users in Japan.

## Prerequisites

- Docker Desktop installed and running
- OpenAI API key
- (Optional) Ollama installed if you want to run RakutenAI locally

## Quick Start

### 1. Prepare Environment Variables

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key_here
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=production
```

### 2. Build and Start Containers

```bash
docker-compose up -d --build
```

This will:
- Build the backend container with all dependencies
- Build the nginx container for frontend and reverse proxy
- Start both services

### 3. Access the Application

- **Frontend**: http://localhost (or http://your-server-ip)
- **Backend API**: http://localhost:8000 (or http://your-server-ip:8000)

## Deployment for Production (Japan)

### Option 1: Deploy on a VPS/Cloud Server in Japan

#### Recommended Cloud Providers:
- **AWS (Tokyo region)**: EC2 instance
- **Google Cloud (Tokyo region)**: Compute Engine
- **Azure (Japan East)**: Virtual Machine
- **DigitalOcean (Tokyo)**: Droplet
- **Vultr (Tokyo)**: Instance
- **Linode (Tokyo)**: Linode

#### Steps:

1. **Set up a server** (Ubuntu 22.04 recommended):
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   
   # Install Docker Compose
   sudo apt install docker-compose-plugin -y
   ```

2. **Transfer your project** to the server:
   ```bash
   # Using SCP (from your local machine)
   scp -r . user@your-server-ip:/path/to/japanese-chatbot/
   ```

   Or use Git:
   ```bash
   # On server
   git clone your-repo-url
   cd Japanese-Chatbot
   ```

3. **Set up environment variables**:
   ```bash
   # Create .env file
   nano .env
   # Add your OPENAI_API_KEY
   ```

4. **Build and start**:
   ```bash
   docker-compose up -d --build
   ```

5. **Configure firewall** (if needed):
   ```bash
   # Allow HTTP (port 80)
   sudo ufw allow 80/tcp
   # Allow HTTPS (port 443) if using SSL
   sudo ufw allow 443/tcp
   ```

6. **Set up domain** (optional):
   - Point your domain to the server IP
   - Update `nginx.conf` with your domain name
   - Consider using Let's Encrypt for SSL

### Option 2: Deploy with SSL (HTTPS)

For production, you should use HTTPS. Here's how:

#### Using Let's Encrypt with Certbot:

1. **Install Certbot**:
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   ```

2. **Get SSL certificate**:
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

3. **Update docker-compose.yml** to expose port 443:
   ```yaml
   nginx:
     ports:
       - "80:80"
       - "443:443"
     volumes:
       - ./certbot/conf:/etc/letsencrypt
       - ./certbot/www:/var/www/certbot
   ```

### Option 3: Deploy on Docker Hub / Container Registry

1. **Build and tag images**:
   ```bash
   docker build -t your-username/japanese-chatbot-backend:latest .
   docker build -t your-username/japanese-chatbot-nginx:latest -f Dockerfile.nginx .
   ```

2. **Push to registry**:
   ```bash
   docker push your-username/japanese-chatbot-backend:latest
   docker push your-username/japanese-chatbot-nginx:latest
   ```

3. **On your server**, pull and run:
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

## Managing the Deployment

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f nginx
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

### Update Application
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build
```

### Backup Data
```bash
# Backup vectorstore
tar -czf vectorstore-backup-$(date +%Y%m%d).tar.gz data/vectorstore/

# Backup knowledge base
tar -czf knowledge-base-backup-$(date +%Y%m%d).tar.gz "knowledge base main/"
```

### Restore Data
```bash
# Restore vectorstore
tar -xzf vectorstore-backup-YYYYMMDD.tar.gz

# Restore knowledge base
tar -xzf knowledge-base-backup-YYYYMMDD.tar.gz
```

## Configuration

### Port Configuration

To change the ports, edit `docker-compose.yml`:

```yaml
nginx:
  ports:
    - "8080:80"  # Change 8080 to your desired port
```

### Environment Variables

Edit `.env` file or `docker-compose.yml`:

```yaml
backend:
  environment:
    - OPENAI_API_KEY=${OPENAI_API_KEY}
    - PORT=8000
```

### Ollama Configuration

If you want to run Ollama in Docker (for RakutenAI), uncomment the ollama service in `docker-compose.yml`:

```yaml
ollama:
  image: ollama/ollama:latest
  container_name: japanese-chatbot-ollama
  restart: unless-stopped
  volumes:
    - ollama-data:/root/.ollama
  ports:
    - "11434:11434"
```

Then pull the model:
```bash
docker exec -it japanese-chatbot-ollama ollama pull yuiseki/rakutenai-2.0-mini:1.5b-instruct
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs backend

# Check if port is already in use
netstat -tulpn | grep :80
```

### Backend can't connect to Ollama
- If Ollama is running externally, make sure it's accessible
- Update `backend/config.py` to use the correct Ollama URL
- If using Docker, ensure they're on the same network

### Vectorstore not persisting
- Check volume mounts in `docker-compose.yml`
- Ensure `data/` directory has correct permissions
- Verify the volume is mounted: `docker inspect japanese-chatbot-backend`

### PDF uploads failing
- Check nginx `client_max_body_size` in `nginx.conf`
- Verify disk space: `df -h`
- Check file permissions

## Performance Optimization

### For Production in Japan:

1. **Use a Japan-based server** (Tokyo region recommended)
2. **Enable CDN** for static assets (Cloudflare, AWS CloudFront)
3. **Optimize Docker images**:
   ```bash
   # Use multi-stage builds
   # Already implemented in Dockerfile
   ```
4. **Scale services** (if needed):
   ```yaml
   backend:
     deploy:
       replicas: 2
   ```

## Monitoring

### Health Checks
- Backend: http://your-server/health
- Nginx: http://your-server/health

### Resource Usage
```bash
# View container stats
docker stats

# View disk usage
docker system df
```

## Security Considerations

1. **Use HTTPS** in production
2. **Restrict CORS** in `backend/main.py` (currently allows all origins)
3. **Use secrets management** for API keys (Docker secrets, AWS Secrets Manager)
4. **Regular updates**: Keep Docker images updated
5. **Firewall**: Only expose necessary ports

## Support

For issues:
1. Check logs: `docker-compose logs`
2. Verify environment variables
3. Check network connectivity
4. Ensure all volumes are mounted correctly

