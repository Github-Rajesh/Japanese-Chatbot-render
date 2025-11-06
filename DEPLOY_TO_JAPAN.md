# Deploy Your Chatbot to Japan - Complete Guide

This guide will help you deploy your Japanese Chatbot to a public server so people in Japan can access it.

## 🎯 What You Need

1. **A cloud server** (VPS) in Japan region (recommended) or any public server
2. **A domain name** (optional, but recommended)
3. **Your OpenAI API key**

## 📋 Step-by-Step Deployment

### Option 1: Quick Deploy (Recommended for Beginners)

#### Choose a Cloud Provider

**Recommended providers with Japan servers:**
- **Vultr** (Tokyo) - $6/month, easiest setup
- **DigitalOcean** (Tokyo) - $6/month, great documentation
- **Linode** (Tokyo) - $5/month, good performance
- **AWS** (Tokyo) - Pay-as-you-go, enterprise-grade
- **Google Cloud** (Tokyo) - Free tier available
- **Azure** (Japan East) - Enterprise-focused

#### Step 1: Create a Server

1. Sign up for your chosen provider
2. Create a new server/instance:
   - **Region**: Tokyo, Japan
   - **OS**: Ubuntu 22.04 LTS
   - **Size**: 2GB RAM minimum (4GB recommended)
   - **Storage**: 20GB minimum

#### Step 2: Connect to Your Server

**Windows (using PowerShell or Command Prompt):**
```bash
ssh root@YOUR_SERVER_IP
```

**Or use PuTTY** (Windows):
- Download PuTTY from https://www.putty.org/
- Enter your server IP
- Click "Open"
- Login with username: `root` or `ubuntu` (depending on provider)

#### Step 3: Install Docker

Once connected to your server, run:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Verify installation
docker --version
docker compose version
```

#### Step 4: Transfer Your Project

**Option A: Using Git (Recommended)**

1. **Push your code to GitHub/GitLab** (if not already):
   ```bash
   # On your local machine
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GIT_REPO_URL
   git push -u origin main
   ```

2. **On your server**, clone the repository:
   ```bash
   git clone YOUR_GIT_REPO_URL
   cd Japanese-Chatbot
   ```

**Option B: Using SCP (Direct transfer)**

On your local Windows machine (PowerShell):
```powershell
# Create a zip of your project (excluding unnecessary files)
# Then transfer using SCP
scp -r . user@YOUR_SERVER_IP:/home/user/japanese-chatbot/
```

Or use WinSCP (Windows GUI):
- Download from https://winscp.net/
- Connect to your server
- Drag and drop your project folder

#### Step 5: Set Up Environment Variables

On your server:
```bash
cd Japanese-Chatbot
nano .env
```

Add your OpenAI API key:
```
OPENAI_API_KEY=your_openai_api_key_here
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=production
```

Save and exit (Ctrl+X, then Y, then Enter)

#### Step 6: Deploy with Docker

```bash
# Build and start containers
docker compose up -d --build

# Check status
docker compose ps

# View logs
docker compose logs -f
```

#### Step 7: Configure Firewall

Allow HTTP traffic:
```bash
# Allow port 80 (HTTP)
sudo ufw allow 80/tcp

# Allow port 443 (HTTPS) if you'll use SSL
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

#### Step 8: Access Your Chatbot

Your chatbot is now accessible at:
```
http://YOUR_SERVER_IP
```

**Share this URL with people in Japan!**

---

## 🔒 Option 2: Deploy with HTTPS (Recommended for Production)

### Why HTTPS?
- Secure connection
- Better user trust
- Required for some features

### Step 1: Get a Domain Name

1. **Buy a domain** (optional):
   - Namecheap, GoDaddy, Google Domains
   - Domain suggestions: `yourchatbot.jp`, `yourchatbot.com`

2. **Point domain to your server**:
   - Add an A record: `@` → `YOUR_SERVER_IP`
   - Or use subdomain: `chatbot.yourdomain.com` → `YOUR_SERVER_IP`

### Step 2: Install SSL Certificate (Let's Encrypt - Free!)

On your server:
```bash
# Install Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
```

### Step 3: Update Docker Compose for HTTPS

Edit `docker-compose.yml`:

```yaml
nginx:
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./certbot/conf:/etc/letsencrypt
    - ./certbot/www:/var/www/certbot
```

### Step 4: Get SSL Certificate

```bash
# Stop containers temporarily
docker compose down

# Get certificate (replace with your domain)
sudo certbot certonly --standalone -d yourdomain.com

# Start containers
docker compose up -d
```

### Step 5: Update Nginx Configuration

Create `nginx-ssl.conf` or update `nginx.conf` to include SSL settings.

Your chatbot will be accessible at:
```
https://yourdomain.com
```

---

## 🌐 Option 3: Deploy Using Cloud Provider's Container Service

### AWS (Tokyo Region)

1. **Use AWS ECS or EC2**
2. **Or use AWS App Runner** (simplest)

### Google Cloud (Tokyo)

1. **Use Cloud Run** (serverless containers)
2. **Or use Compute Engine**

### Azure (Japan East)

1. **Use Container Instances**
2. **Or use App Service**

---

## 📝 Quick Reference Commands

### On Your Server:

```bash
# View logs
docker compose logs -f

# Restart services
docker compose restart

# Stop services
docker compose down

# Update application
git pull
docker compose up -d --build

# Check container status
docker compose ps

# View resource usage
docker stats
```

### Backup Data:

```bash
# Backup vectorstore
tar -czf vectorstore-backup.tar.gz data/vectorstore/

# Backup knowledge base
tar -czf knowledge-base-backup.tar.gz "knowledge base main/"
```

---

## 🔍 Troubleshooting

### Can't access from browser?

1. **Check firewall**:
   ```bash
   sudo ufw status
   sudo ufw allow 80/tcp
   ```

2. **Check if containers are running**:
   ```bash
   docker compose ps
   ```

3. **Check logs**:
   ```bash
   docker compose logs backend
   docker compose logs nginx
   ```

4. **Test from server**:
   ```bash
   curl http://localhost
   ```

### Container won't start?

1. **Check .env file exists**:
   ```bash
   cat .env
   ```

2. **Check disk space**:
   ```bash
   df -h
   ```

3. **Check Docker logs**:
   ```bash
   docker compose logs
   ```

### Slow performance?

1. **Use a Japan-based server** (Tokyo region)
2. **Increase server resources** (more RAM/CPU)
3. **Enable CDN** (Cloudflare) for static assets

---

## 💡 Recommendations for Japan Deployment

### Best Practices:

1. ✅ **Use Tokyo region server** for lowest latency
2. ✅ **Enable HTTPS** for security
3. ✅ **Use a domain name** (easier to share)
4. ✅ **Set up monitoring** (optional)
5. ✅ **Regular backups** of vectorstore and knowledge base
6. ✅ **Keep Docker updated**

### Cost Estimates:

- **Vultr/DigitalOcean**: $6-12/month (basic setup)
- **Domain**: $10-15/year
- **SSL**: Free (Let's Encrypt)
- **Total**: ~$8-15/month

---

## 🚀 Next Steps After Deployment

1. **Test the chatbot** from a device in Japan
2. **Share the URL** with your users
3. **Monitor usage** via server logs
4. **Set up backups** (automated if possible)
5. **Consider adding analytics** (optional)

---

## 📞 Need Help?

If you encounter issues:

1. Check the logs: `docker compose logs -f`
2. Verify firewall settings
3. Ensure port 80 is open
4. Check server resources (CPU/RAM)
5. Verify .env file has correct API key

---

## ✅ Deployment Checklist

- [ ] Server created in Japan region
- [ ] Docker installed on server
- [ ] Project transferred to server
- [ ] .env file created with API key
- [ ] Docker containers running
- [ ] Firewall configured (port 80 open)
- [ ] Chatbot accessible via IP address
- [ ] (Optional) Domain name configured
- [ ] (Optional) HTTPS configured
- [ ] Tested from Japan

**Once all checked, your chatbot is live and accessible from Japan!** 🎉

