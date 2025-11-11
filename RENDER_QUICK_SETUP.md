# Render.com Quick Setup Guide

## Step-by-Step Setup (Based on Current Screen)

### Step 1: Select Repository
1. ✅ You can see `zaydabash / the-cognisphere` in the list
2. Click on `zaydabash / the-cognisphere` to select it

### Step 2: Configure Service Type
1. **Service Type**: Should already show "Web Service" (with globe icon)
2. If not, click the dropdown and select "Web Service"

### Step 3: Configure Service Name
1. **Name**: Enter `cognisphere-backend`
2. This will be your service name (e.g., `cognisphere-backend.onrender.com`)

### Step 4: Advanced Settings (Click "Advanced" if visible)

After selecting the repository, you'll need to configure:

#### Build & Deploy Settings:
- **Root Directory**: `backend`
- **Environment**: `Docker`
- **Dockerfile Path**: `backend/Dockerfile`
- **Docker Context**: `backend`
- **Build Command**: (leave empty)
- **Start Command**: (leave empty)

#### Environment Variables:
Click "Environment" or "Environment Variables" and add:

```
ENVIRONMENT=production
PORT=8000
LLM_MODE=mock
MEM_BACKEND=networkx
VEC_BACKEND=faiss
SIMULATION_SEED=42
SIMULATION_AGENTS=100
LOG_LEVEL=INFO
CORS_ORIGINS=https://zaydbashir.github.io,https://zaydbashir.github.io/the-cognisphere
REQUIRE_AUTH=false
```

#### Health Check:
- **Health Check Path**: `/healthz`
- **Health Check Interval**: `60` seconds

### Step 5: Deploy
1. Click **"Deploy Web Service"** button (bottom left)
2. Wait for deployment (5-10 minutes)
3. Render will build and deploy your service

### Step 6: Get Service Information

After deployment completes:

1. **Service URL**: 
   - Will be something like: `https://cognisphere-backend.onrender.com`
   - Note this URL down!

2. **Service ID**:
   - Go to service settings
   - Look for "Service ID" (looks like `srv-xxxxx`)
   - Copy this ID

3. **API Key**:
   - Go to Account Settings → API Keys
   - Create a new API key
   - Copy the key (you won't see it again!)

### Step 7: Configure GitHub Secrets

1. Go to your GitHub repository: `https://github.com/zaydabash/the-cognisphere`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add these three secrets:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `RENDER_API_KEY` | Your Render API key | `rnd_xxxxxxxxxxxxx` |
| `RENDER_SERVICE_ID` | Your service ID | `srv-xxxxxxxxxxxxx` |
| `RENDER_HEALTH_URL` | Health check URL | `https://cognisphere-backend.onrender.com/healthz` |

### Step 8: Test the Connection

1. **Test Health Endpoint**:
   ```bash
   curl https://cognisphere-backend.onrender.com/healthz
   # Should return: {"ok": true}
   ```

2. **Test API Docs**:
   - Visit: `https://cognisphere-backend.onrender.com/docs`
   - Should show FastAPI documentation

3. **Test Auto-Deployment**:
   - Make a small change and push to `main`
   - Check GitHub Actions tab
   - Should see "Deploy Backend (Render)" workflow running

## Quick Reference

### Service Configuration Summary:
- **Name**: `cognisphere-backend`
- **Repository**: `zaydabash/the-cognisphere`
- **Root Directory**: `backend`
- **Environment**: `Docker`
- **Dockerfile**: `backend/Dockerfile`
- **Health Check**: `/healthz`

### Environment Variables:
```
ENVIRONMENT=production
PORT=8000
LLM_MODE=mock
MEM_BACKEND=networkx
VEC_BACKEND=faiss
CORS_ORIGINS=https://zaydbashir.github.io,https://zaydbashir.github.io/the-cognisphere
REQUIRE_AUTH=false
```

### Expected URLs:
- **Service**: `https://cognisphere-backend.onrender.com`
- **Health Check**: `https://cognisphere-backend.onrender.com/healthz`
- **API Docs**: `https://cognisphere-backend.onrender.com/docs`

## Troubleshooting

### Service Won't Deploy
- Check if Dockerfile exists at `backend/Dockerfile`
- Verify environment variables are set
- Check Render logs for errors

### Health Check Fails
- Wait 5-10 minutes after deployment
- Verify `/healthz` endpoint exists in `backend/app.py`
- Check service logs in Render dashboard

### GitHub Actions Fails
- Verify all three secrets are set correctly
- Check `RENDER_SERVICE_ID` matches your service
- Verify `RENDER_API_KEY` has proper permissions

## Next Steps After Setup

1. ✅ Service deployed and running
2. ✅ GitHub secrets configured
3. ✅ Test health endpoint
4. ⏭️ Update frontend `VITE_API_URL` to your Render URL
5. ⏭️ Test full stack integration
6. ⏭️ Enable authentication (optional)

---

**You're almost there! Just complete the deployment and configure the secrets!**

