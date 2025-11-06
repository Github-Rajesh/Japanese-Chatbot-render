# Free Hosting Guide - Deploy Your Chatbot for Free

This guide shows you how to host your Japanese Chatbot for **FREE** using Docker, so anyone from anywhere (including Japan) can access it.

## 🆓 Free Hosting Options

### Option 1: Render.com (Easiest - Recommended) ⭐

**Free Tier:**
- ✅ Free web service
- ✅ Automatic SSL (HTTPS)
- ✅ Custom domain support
- ✅ Docker support
- ⚠️ Spins down after 15 minutes of inactivity (starts automatically on request)
- ⚠️ 750 hours/month free

**Steps:**

1. **Sign up at https://render.com** (free account)

2. **Push your code to GitHub**:
   ```bash
   # On your local machine
   git init
   git add .
   git commit -m "Initial commit"
   
   # Create a repo on GitHub, then:
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

3. **Create a new Web Service on Render**:
   - Go to Dashboard → New → Web Service
   - Connect your GitHub repository
   - Select your repository

4. **Configure the service**:
   - **Name**: `japanese-chatbot` (or any name)
   - **Environment**: `Docker`
   - **Region**: Choose closest to Japan (Singapore or Tokyo if available)
   - **Build Command**: (leave empty - Docker handles it)
   - **Start Command**: (leave empty - Docker handles it)

5. **Add Environment Variables**:
   - Click "Environment" tab
   - Add: `OPENAI_API_KEY` = `your_api_key_here`
   - Add: `HOST` = `0.0.0.0`
   - **Note**: Render automatically sets `PORT` (usually 10000), so you don't need to set it

6. **Deploy**:
   - Click "Create Web Service"
   - Wait for build (5-10 minutes first time)
   - Your chatbot will be live at: `https://your-app-name.onrender.com`

**Note**: You'll need to update your `docker-compose.yml` to work with Render (see below).

---

### Option 2: Railway.app (Best for Docker Compose)

**Free Tier:**
- ✅ $5 credit monthly (free tier)
- ✅ Automatic SSL
- ✅ Docker & Docker Compose support
- ✅ Custom domain
- ⚠️ Credit-based billing (usually free for small apps)

**Steps:**

1. **Sign up at https://railway.app** (GitHub login)

2. **Push your code to GitHub** (same as Render)

3. **Create a new project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

4. **Configure services**:
   - Railway will detect `docker-compose.yml`
   - It will automatically create services for backend and nginx

5. **Add Environment Variables**:
   - Go to Variables tab
   - Add: `OPENAI_API_KEY` = `your_api_key_here`

6. **Deploy**:
   - Railway auto-deploys on git push
   - Your chatbot will be live at: `https://your-app.up.railway.app`

---

### Option 3: Fly.io (Great for Docker)

**Free Tier:**
- ✅ 3 shared-cpu VMs free
- ✅ 3GB persistent volumes free
- ✅ Automatic SSL
- ✅ Global edge network
- ⚠️ Requires credit card (but free tier is truly free)

**Steps:**

1. **Install Fly CLI**:
   ```bash
   # Windows (PowerShell)
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```

2. **Sign up**: https://fly.io (free account)

3. **Login**:
   ```bash
   fly auth login
   ```

4. **Create a Fly app**:
   ```bash
   fly launch
   ```

5. **Configure and deploy**:
   - Follow the prompts
   - Add secrets: `fly secrets set OPENAI_API_KEY=your_key`

6. **Your app will be live** at: `https://your-app.fly.dev`

---

### Option 4: Oracle Cloud Always Free (Advanced)

**Free Tier:**
- ✅ Always free VPS (2 VMs)
- ✅ 200GB storage
- ✅ Unlimited bandwidth
- ✅ Full control (like a regular server)
- ⚠️ Requires more setup

**Steps:**

1. **Sign up at https://www.oracle.com/cloud/free/**

2. **Create a VM** (Ubuntu 22.04)

3. **Follow the regular server deployment** (see DEPLOY_TO_JAPAN.md)

4. **Free forever** (no credit card required for always-free tier)

---

## 🐳 Preparing Docker for Free Hosting

Most free platforms expect a single Dockerfile, not docker-compose. Here's how to adapt:

### Option A: Use Render.com (Single Container)

Create a combined Dockerfile that runs both backend and nginx:

```dockerfile
# Dockerfile.render
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    nginx \
    tesseract-ocr \
    tesseract-ocr-jpn \
    tesseract-ocr-jpn-vert \
    poppler-utils \
    libmagic1 \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY frontend/ /usr/share/nginx/html/

# Copy nginx config
COPY nginx-render.conf /etc/nginx/sites-available/default

# Copy supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create directories
RUN mkdir -p "knowledge base main/uploads" "data/vectorstore"

# Expose port (Render uses PORT environment variable)
EXPOSE 10000

# Start supervisor (runs both nginx and backend)
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
```

### Option B: Use Railway.app (Docker Compose)

Railway supports docker-compose.yml directly! Just use your existing setup.

---

## 📝 Setup Instructions by Platform

### For Render.com:

1. **Create `Dockerfile.render`** (see above or use the one I'll create)

2. **Create `supervisord.conf`**:
   ```ini
   [supervisord]
   nodaemon=true

   [program:backend]
   command=python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   directory=/app
   autostart=true
   autorestart=true
   stdout_logfile=/dev/stdout
   stdout_logfile_maxbytes=0
   stderr_logfile=/dev/stderr
   stderr_logfile_maxbytes=0

   [program:nginx]
   command=nginx -g "daemon off;"
   autostart=true
   autorestart=true
   stdout_logfile=/dev/stdout
   stdout_logfile_maxbytes=0
   stderr_logfile=/dev/stderr
   stderr_logfile_maxbytes=0
   ```

3. **Create `nginx-render.conf`**:
   ```nginx
   server {
       listen 10000;
       server_name _;
       root /usr/share/nginx/html;
       index index.html;

       location / {
           try_files $uri $uri/ /index.html;
       }

       location /api {
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_cache_bypass $http_upgrade;
           proxy_buffering off;
       }
   }
   ```

4. **On Render, set Dockerfile path to**: `Dockerfile.render`

---

### For Railway.app:

1. **Use your existing `docker-compose.yml`**
2. **Railway auto-detects it**
3. **Just add environment variables** in Railway dashboard
4. **Deploy!**

---

## 🚀 Quick Start: Render.com (Recommended)

### Step-by-Step:

1. **Create GitHub repo and push your code**

2. **Go to https://render.com** and sign up

3. **New → Web Service**:
   - Connect GitHub
   - Select your repo
   - Settings:
     - **Name**: `japanese-chatbot`
     - **Environment**: `Docker`
     - **Dockerfile Path**: `Dockerfile.render` (or create it)
     - **Region**: Asia Pacific (Singapore) or closest to Japan

4. **Environment Variables**:
   ```
   OPENAI_API_KEY=your_key_here
   HOST=0.0.0.0
   PORT=10000
   ```

5. **Create Web Service** and wait for deployment

6. **Your chatbot is live!** 🎉

---

## 📊 Comparison

| Platform | Free Tier | Docker Support | Ease of Use | Best For |
|----------|-----------|----------------|-------------|----------|
| **Render.com** | ✅ 750 hrs/month | ✅ Yes | ⭐⭐⭐⭐⭐ | Beginners |
| **Railway.app** | ✅ $5 credit/month | ✅ Yes (Compose) | ⭐⭐⭐⭐⭐ | Docker Compose |
| **Fly.io** | ✅ 3 VMs | ✅ Yes | ⭐⭐⭐⭐ | Advanced users |
| **Oracle Cloud** | ✅ Always free | ✅ Yes | ⭐⭐⭐ | Full control |

---

## 💡 Recommendations

**For beginners**: Use **Render.com** - it's the easiest
**For Docker Compose**: Use **Railway.app** - supports your existing setup
**For maximum control**: Use **Oracle Cloud** - free forever VPS

---

## 🔧 Troubleshooting

### Render.com:
- **Slow startup?** First request after sleep takes ~30 seconds
- **Build fails?** Check Dockerfile path in settings
- **Can't access?** Wait for build to complete (blue → green)

### Railway.app:
- **Services not starting?** Check environment variables
- **Port errors?** Railway auto-assigns ports

### General:
- **Check logs** in the platform dashboard
- **Verify environment variables** are set
- **Test locally first** before deploying

---

## ✅ Next Steps

1. Choose a platform (Render.com recommended for beginners)
2. Push code to GitHub
3. Deploy using the platform's dashboard
4. Share your URL with people in Japan!

**Your chatbot will be accessible from anywhere in the world!** 🌍

