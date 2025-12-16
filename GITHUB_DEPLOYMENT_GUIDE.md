# GitHub Deployment Setup Guide

Your Azure resources are created and configured! Now let's set up automatic deployment from GitHub.

## What's Already Done ✅

- ✅ 3 App Services created (voice-agent-django, voice-agent-fastapi, voice-agent-flask)
- ✅ Environment variables configured
- ✅ Startup commands set
- ✅ GitHub Actions workflows ready
- ✅ Publish profiles downloaded

## Next Steps - Add GitHub Secrets

### 1. Go to Your GitHub Repository
Navigate to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`

### 2. Add These 3 Secrets

Click "New repository secret" for each:

#### Secret 1: AZURE_DJANGO_PUBLISH_PROFILE
- Name: `AZURE_DJANGO_PUBLISH_PROFILE`
- Value: Copy the entire content from `django-publish-profile.xml`

#### Secret 2: AZURE_FASTAPI_PUBLISH_PROFILE
- Name: `AZURE_FASTAPI_PUBLISH_PROFILE`
- Value: Copy the entire content from `fastapi-publish-profile.xml`

#### Secret 3: AZURE_FLASK_PUBLISH_PROFILE
- Name: `AZURE_FLASK_PUBLISH_PROFILE`
- Value: Copy the entire content from `flask-publish-profile.xml`

### 3. Deploy!

Once secrets are added:

```bash
git add .
git commit -m "Configure Azure deployment"
git push origin main
```

GitHub Actions will automatically deploy all 3 services!

## Monitor Deployment

Watch the deployment progress:
- Go to your GitHub repo → Actions tab
- You'll see 3 workflows running

## Your App URLs

After deployment completes (5-10 minutes):

- **Flask Frontend**: https://voice-agent-flask.azurewebsites.net
- **FastAPI Backend**: https://voice-agent-fastapi.azurewebsites.net
- **Django API**: https://voice-agent-django.azurewebsites.net

## Health Check Endpoints

Verify services are running:
- https://voice-agent-flask.azurewebsites.net/health
- https://voice-agent-fastapi.azurewebsites.net/health
- https://voice-agent-django.azurewebsites.net/health/

## Troubleshooting

If deployment fails:
1. Check GitHub Actions logs
2. Check Azure App Service logs in Azure Portal
3. Verify all environment variables are set correctly

## Environment Variables Already Set

All services have their environment variables configured:
- LiveKit credentials
- OpenAI API key
- Deepgram API key
- Cartesia API key
- CORS settings
- Service URLs

You're ready to deploy! 🚀
