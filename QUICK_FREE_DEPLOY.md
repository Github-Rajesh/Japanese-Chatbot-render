# Quick Guide: Deploy for Free (5 Minutes)

Deploy your chatbot for **FREE** so anyone in Japan (or anywhere) can access it!

## 🎯 Easiest Method: Render.com (Recommended)

### Step 1: Push to GitHub (2 minutes)

```bash
# On your local machine
git init
git add .
git commit -m "Initial commit"

# Create a new repo on GitHub.com, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Render.com (3 minutes)

1. **Go to https://render.com** and sign up (free)

2. **Click "New" → "Web Service"**

3. **Connect GitHub** and select your repository

4. **Configure**:
   - **Name**: `japanese-chatbot` (or any name)
   - **Environment**: `Docker`
   - **Dockerfile Path**: `Dockerfile.render`
   - **Region**: Asia Pacific (Singapore) - closest to Japan

5. **Add Environment Variables**:
   - Click "Environment" tab
   - Add: `OPENAI_API_KEY` = `your_openai_api_key`
   - Add: `HOST` = `0.0.0.0`
   - **Note**: Render automatically sets `PORT` (usually 10000)

6. **Click "Create Web Service"**

7. **Wait 5-10 minutes** for first build

8. **Done!** Your chatbot is live at: `https://your-app-name.onrender.com`

### Share Your URL!

Anyone in Japan (or anywhere) can now access your chatbot at your Render URL!

---

## 🚂 Alternative: Railway.app (Supports Docker Compose)

### Step 1: Push to GitHub (same as above)

### Step 2: Deploy on Railway

1. **Go to https://railway.app** and sign up (GitHub login)

2. **Click "New Project" → "Deploy from GitHub repo"**

3. **Select your repository**

4. **Add Environment Variables**:
   - `OPENAI_API_KEY` = `your_openai_api_key`

5. **Railway auto-detects `docker-compose.yml`** and deploys!

6. **Your chatbot is live** at: `https://your-app.up.railway.app`

---

## 📝 Notes

- **Render.com**: Free tier sleeps after 15 min inactivity (wakes on request)
- **Railway.app**: $5 free credit/month (usually enough for small apps)
- **Both**: Free SSL (HTTPS), custom domain support
- **Both**: Auto-deploy on git push

---

## ✅ What You Get

- ✅ Free hosting
- ✅ HTTPS (secure)
- ✅ Accessible from anywhere
- ✅ Auto-deploys on code changes
- ✅ No credit card required (for Render free tier)

---

## 🆘 Troubleshooting

**Build fails?**
- Check Dockerfile path is correct
- Verify all files are in GitHub repo
- Check Render/Railway logs

**Can't access?**
- Wait for build to complete (green = ready)
- Check environment variables are set
- Try the health endpoint: `https://your-app.onrender.com/health`

**Need help?**
- Check platform logs in dashboard
- Verify `.env` variables are set in platform
- Test locally first

---

**That's it! Your chatbot is now live and free!** 🎉

