# Production Setup Guide

This guide covers setting up The Cognisphere for production deployment on Render.com and GitHub Pages.

## Environment Variables

### Required Environment Variables

Set these environment variables in your production environment:

#### Backend (Render.com)

```bash
# Environment
ENVIRONMENT=production

# CORS Configuration
CORS_ORIGINS=https://zaydbashir.github.io,https://zaydbashir.github.io/the-cognisphere

# Authentication (Optional but Recommended)
API_KEY=your-secure-api-key-here
REQUIRE_AUTH=true

# LLM Configuration (if using OpenAI)
OPENAI_API_KEY=your-openai-api-key

# Neo4j Configuration (if using Neo4j)
NEO4J_URI=bolt://your-neo4j-instance:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-neo4j-password
```

#### Frontend (GitHub Pages)

```bash
# API URL
VITE_API_URL=https://cognisphere-backend.onrender.com
```

## Render.com Backend Setup

### 1. Create Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `cognisphere-backend`
   - **Environment**: `Docker`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Dockerfile Path**: `backend/Dockerfile`

### 2. Set Environment Variables

In Render.com dashboard, go to **Environment** tab and add:

```
ENVIRONMENT=production
CORS_ORIGINS=https://zaydbashir.github.io,https://zaydbashir.github.io/the-cognisphere
API_KEY=<generate-a-secure-random-key>
REQUIRE_AUTH=true
```

**Generate a secure API key:**
```bash
# Generate a secure random API key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Configure Health Check

- **Health Check Path**: `/healthz`
- **Health Check Interval**: `60 seconds`

### 4. Deploy

Render will automatically deploy when you push to `main` branch.

## GitHub Pages Frontend Setup

### 1. Configure Environment Variables

Create `.env.production` file in `frontend/` directory:

```bash
VITE_API_URL=https://cognisphere-backend.onrender.com
```

### 2. Update Vite Configuration

The `vite.config.ts` already has the correct base path for GitHub Pages:

```typescript
base: "/the-cognisphere/"
```

### 3. Build and Deploy

The GitHub Actions workflow automatically:
- Builds the frontend
- Deploys to GitHub Pages
- Sets up HTTPS automatically

## HTTPS Configuration

### GitHub Pages

GitHub Pages automatically provides HTTPS for all sites:
- ✅ HTTPS enabled by default
- ✅ Automatic certificate management
- ✅ HTTP to HTTPS redirect

### Render.com

Render.com automatically provides HTTPS:
- ✅ HTTPS enabled by default
- ✅ Automatic certificate management
- ✅ Custom domain support

### Custom Domain Setup (Optional)

If using a custom domain:

1. **Render.com**:
   - Go to your service settings
   - Add custom domain
   - Update DNS records as instructed
   - HTTPS automatically configured

2. **Update CORS_ORIGINS**:
   ```bash
   CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

## Authentication Setup

### Enable Authentication

1. **Generate API Key**:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Set Environment Variables**:
   ```bash
   API_KEY=your-generated-key-here
   REQUIRE_AUTH=true
   ```

3. **Use API Key in Requests**:
   ```bash
   curl -H "Authorization: Bearer your-api-key" \
        https://cognisphere-backend.onrender.com/simulation/status
   ```

### Frontend Integration

Update your frontend API client to include the API key:

```typescript
// frontend/src/api/client.ts
const API_KEY = import.meta.env.VITE_API_KEY;

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
  },
});
```

## Security Checklist

Before going to production:

- [ ] `ENVIRONMENT=production` is set
- [ ] `CORS_ORIGINS` is configured with your frontend URLs
- [ ] `API_KEY` is set and secure (if using authentication)
- [ ] `REQUIRE_AUTH=true` is set (if using authentication)
- [ ] HTTPS is enabled (automatic on Render and GitHub Pages)
- [ ] All sensitive data is in environment variables
- [ ] No hardcoded credentials in code
- [ ] Health check endpoint is configured
- [ ] Error messages don't leak internal details
- [ ] Dependencies are up to date

## Monitoring

### Health Checks

- **Backend**: `https://cognisphere-backend.onrender.com/healthz`
- **Frontend**: Automatically monitored by GitHub Pages

### Logs

- **Render.com**: View logs in dashboard
- **GitHub Actions**: View workflow logs

## Troubleshooting

### CORS Errors

If you see CORS errors:
1. Check `CORS_ORIGINS` includes your frontend URL
2. Ensure `ENVIRONMENT=production` is set
3. Verify frontend URL matches exactly (including protocol)

### Authentication Errors

If authentication fails:
1. Check `API_KEY` is set correctly
2. Verify `REQUIRE_AUTH=true` is set
3. Ensure API key is included in request headers
4. Check API key format: `Authorization: Bearer <key>`

### Deployment Issues

If deployment fails:
1. Check Render.com logs
2. Verify Dockerfile is correct
3. Check environment variables are set
4. Verify health check endpoint works

## Example Production Configuration

### render.yaml

```yaml
services:
  - type: web
    name: cognisphere-backend
    env: docker
    dockerfilePath: ./backend/Dockerfile
    dockerContext: ./backend
    healthCheckPath: /healthz
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: CORS_ORIGINS
        value: https://zaydbashir.github.io,https://zaydbashir.github.io/the-cognisphere
      - key: API_KEY
        generateValue: true
      - key: REQUIRE_AUTH
        value: true
```

## Support

For issues or questions:
- Check [SECURITY.md](./SECURITY.md) for security best practices
- Review [README.md](./README.md) for general documentation
- Open an issue on GitHub

