# 🚀 Deploying to Render.com

This guide will help you deploy the Earring Generator to Render.com for free!

## Prerequisites

1. **GitHub Account** - Your code needs to be in a GitHub repository
2. **Render.com Account** - Sign up at https://render.com (free)

## Step-by-Step Deployment

### 1. Push Your Code to GitHub

```bash
# If not already a git repo with remote
git remote add origin https://github.com/YOUR_USERNAME/earring_generator.git
git add .
git commit -m "Ready for deployment"
git push -u origin main
```

### 2. Deploy on Render

#### Option A: Automatic Deployment (Recommended)

1. Go to https://render.com/deploy
2. Click **"New Blueprint Instance"**
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml` and set everything up!
5. Click **"Create Blueprint"**
6. Wait 5-10 minutes for deployment (installing Python packages takes time)

#### Option B: Manual Deployment

**Backend:**
1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo
4. Configure:
   - **Name:** `earring-generator-api`
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT app:app`
   - **Instance Type:** `Free`
5. Add Environment Variable:
   - `USE_VECTOR_GENERATOR` = `true`
6. Click **"Create Web Service"**

**Frontend:**
1. Click **"New +"** → **"Static Site"**
2. Connect your GitHub repo
3. Configure:
   - **Name:** `earring-generator-frontend`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`
4. Add Environment Variable:
   - `VITE_API_URL` = `https://earring-generator-api.onrender.com`
   (Use the URL from your backend service)
5. Click **"Create Static Site"**

### 3. Connect Frontend to Backend

After both services are deployed:

1. Go to your **frontend service** settings
2. Under **"Rewrites and Redirects"**, add:
   - **Source:** `/api/*`
   - **Destination:** `https://earring-generator-api.onrender.com/api/*`
   - **Action:** `Rewrite`

### 4. Access Your App

Your frontend will be available at:
```
https://earring-generator-frontend.onrender.com
```

## Important Notes

### Free Tier Limitations
- ✅ **750 hours/month** of compute time (plenty for personal use)
- ⚠️ **Services sleep after 15 minutes** of inactivity
- ⚠️ **First request after sleep takes 30-60 seconds** to wake up
- ✅ **No cold starts** once awake
- ✅ **Automatic SSL/HTTPS**

### Performance Tips
1. **Keep the service awake** - Use a service like UptimeRobot (free) to ping your app every 14 minutes
2. **First load is slow** - Backend needs to wake up and load Python packages
3. **3D preview generation** - Takes 2-5 seconds (normal, generating real mesh)

## Updating Your Deployment

Render automatically deploys when you push to GitHub:

```bash
git add .
git commit -m "Updated patterns"
git push
```

Render will automatically rebuild and redeploy (takes 5-10 minutes).

## Troubleshooting

### Backend won't start
- Check logs in Render dashboard
- Verify all dependencies in `requirements.txt`
- Make sure Python version is 3.10+

### Frontend can't reach backend
- Check CORS is enabled in `app.py` (already done)
- Verify API URL in frontend environment variables
- Check rewrite rules are set correctly

### Out of memory (512MB limit)
- Vector-based approach should fit easily
- If issues, consider upgrading to paid tier ($7/month)

## Cost

**Free Forever** for:
- Personal projects
- Low-moderate traffic
- 750 hours/month compute

**Upgrade to paid ($7/month)** for:
- No sleep/instant responses
- More memory (1GB+)
- Priority support

## Support

If you run into issues:
1. Check Render logs in dashboard
2. Review this guide
3. Check Render docs: https://render.com/docs

Happy deploying! 🎨✨
