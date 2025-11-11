# Render.com Connection Checklist

## Current Status

❌ **NOT CONNECTED** - The project has configuration files but no active Render service.

## Quick Setup Steps

### Step 1: Create Render Account (if needed)
1. Go to https://render.com
2. Sign up for a free account
3. Verify your email

### Step 2: Create Backend Service

1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository:
   - Select **"Build and deploy from a Git repository"**
   - Connect `zaydabash/the-cognisphere` repository
   - Authorize Render to access your GitHub account

4. Configure the service:
   - **Name**: `cognisphere-backend`
   - **Region**: `Oregon` (or closest to you)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `backend/Dockerfile`
   - **Docker Context**: `backend`
   - **Plan**: `Free`

5. Click **"Create Web Service"**

### Step 3: Set Environment Variables

In Render service settings, go to **Environment** tab and add:

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
API_KEY=<generate-a-secure-key>
REQUIRE_AUTH=false
```

**Generate API Key:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 4: Configure Health Check

In Render service settings:
- **Health Check Path**: `/healthz`
- **Health Check Interval**: `60` seconds

### Step 5: Get Service Information

After deployment, note:
1. **Service URL**: `https://cognisphere-backend.onrender.com` (or your custom name)
2. **Service ID**: Found in service settings (looks like `srv-xxxxx`)
3. **API Key**: Create in Account Settings → API Keys

### Step 6: Set GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Add these secrets:

| Secret Name | Value | Where to Get |
|-------------|-------|--------------|
| `RENDER_API_KEY` | Your Render API key | Render Dashboard → Account Settings → API Keys |
| `RENDER_SERVICE_ID` | Your service ID | Render service settings (e.g., `srv-xxxxx`) |
| `RENDER_HEALTH_URL` | Health check URL | `https://your-service.onrender.com/healthz` |

### Step 7: Test the Connection

1. Wait for Render to deploy (5-10 minutes)
2. Test health endpoint:
   ```bash
   curl https://cognisphere-backend.onrender.com/healthz
   # Should return: {"ok": true}
   ```
3. Check API docs:
   ```
   https://cognisphere-backend.onrender.com/docs
   ```

### Step 8: Verify Auto-Deployment

1. Push a change to `main` branch
2. Check GitHub Actions tab
3. Should see "Deploy Backend (Render)" workflow running
4. Check Render dashboard for deployment status

## Alternative: Use render.yaml (Blueprint)

If you prefer, you can use the `render.yaml` file:

1. Go to Render Dashboard
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will read `render.yaml` and create the service automatically

**Note**: You'll still need to:
- Set GitHub secrets for auto-deployment
- Get the service URL for frontend configuration

## Troubleshooting

### Service Not Deploying
- Check Render logs in dashboard
- Verify Dockerfile is correct
- Check environment variables are set
- Verify health check path is correct

### Health Check Failing
- Wait 5-10 minutes after deployment
- Check if service is running
- Verify `/healthz` endpoint exists
- Check service logs

### GitHub Actions Failing
- Verify all secrets are set
- Check `RENDER_SERVICE_ID` is correct
- Verify `RENDER_API_KEY` has permissions
- Check workflow logs for errors

### CORS Errors
- Verify `CORS_ORIGINS` includes your frontend URL
- Check `ENVIRONMENT=production` is set
- Verify frontend URL matches exactly

## Verification Checklist

- [ ] Render service created
- [ ] Service is deployed and running
- [ ] Health endpoint returns `{"ok": true}`
- [ ] API docs accessible at `/docs`
- [ ] GitHub secrets configured
- [ ] Auto-deployment working
- [ ] Frontend can connect to backend
- [ ] CORS configured correctly

## Next Steps

Once connected:
1. Update frontend `VITE_API_URL` to your Render URL
2. Test the full stack
3. Monitor logs in Render dashboard
4. Set up custom domain (optional)

## Support

If you need help:
1. Check Render service logs
2. Check GitHub Actions logs
3. Verify all configuration is correct
4. Review this checklist again

---

**Once you complete these steps, your project will be fully connected to Render!**

