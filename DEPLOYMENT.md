# Azure Deployment Guide - Voice Agent Application

This guide provides step-by-step instructions for deploying the Voice Agent application to Azure App Service from a single GitHub repository.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Azure Resources Setup](#azure-resources-setup)
4. [GitHub Configuration](#github-configuration)
5. [Environment Variables](#environment-variables)
6. [Deployment](#deployment)
7. [Post-Deployment Configuration](#post-deployment-configuration)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:

- **Azure Account** with an active subscription ([Sign up for free](https://azure.microsoft.com/free/))
- **GitHub Account** with this repository
- **Azure CLI** installed ([Installation guide](https://docs.microsoft.com/cli/azure/install-azure-cli))
- **LiveKit Account** (Cloud or self-hosted) with API credentials
- **OpenAI API Key** (or other AI provider keys)

---

## Architecture Overview

The application consists of three Python services:

1. **Flask Frontend** (Port 5173) - Web UI for user interactions
2. **FastAPI Backend** (Port 8000) - Voice agent orchestration with LiveKit
3. **Django Persistence** (Port 9000) - Authentication and data storage

Each service will be deployed as a separate Azure App Service, with a shared PostgreSQL database.

---

## Azure Resources Setup

### Step 1: Login to Azure

```bash
az login
```

### Step 2: Create Resource Group

```bash
az group create \
  --name wanderbot-rg \
  --location eastus
```

### Step 3: Create Azure Database for PostgreSQL

```bash
# Create PostgreSQL Flexible Server
az postgres flexible-server create \
  --resource-group wanderbot-rg \
  --name wanderbot-db \
  --location eastus \
  --admin-user dbadmin \
  --admin-password <YourSecurePassword> \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32 \
  --version 14 \
  --public-access 0.0.0.0

# Create database
az postgres flexible-server db create \
  --resource-group wanderbot-rg \
  --server-name wanderbot-db \
  --database-name wanderbot

# Allow Azure services to access the database
az postgres flexible-server firewall-rule create \
  --resource-group wanderbot-rg \
  --name wanderbot-db \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

**Save the connection string:**
```
postgresql://dbadmin:<YourSecurePassword>@wanderbot-db.postgres.database.azure.com:5432/wanderbot?sslmode=require
```

### Step 4: Create App Service Plan

```bash
az appservice plan create \
  --name wanderbot-plan \
  --resource-group wanderbot-rg \
  --location eastus \
  --sku B1 \
  --is-linux
```

### Step 5: Create App Services

#### Django Persistence Service
```bash
az webapp create \
  --resource-group wanderbot-rg \
  --plan wanderbot-plan \
  --name wanderbot-django \
  --runtime "PYTHON:3.11" \
  --startup-file "bash startup.sh"
```

#### FastAPI Backend
```bash
az webapp create \
  --resource-group wanderbot-rg \
  --plan wanderbot-plan \
  --name wanderbot-fastapi \
  --runtime "PYTHON:3.11" \
  --startup-file "bash startup.sh"
```

#### Flask Frontend
```bash
az webapp create \
  --resource-group wanderbot-rg \
  --plan wanderbot-plan \
  --name wanderbot-flask \
  --runtime "PYTHON:3.11" \
  --startup-file "bash startup.sh"
```

**Note:** Replace `wanderbot-django`, `wanderbot-fastapi`, and `wanderbot-flask` with your desired app names. These must be globally unique.

---

## GitHub Configuration

### Step 1: Get Publish Profiles

Download the publish profile for each App Service:

```bash
# Django
az webapp deployment list-publishing-profiles \
  --resource-group wanderbot-rg \
  --name wanderbot-django \
  --xml > django-publish-profile.xml

# FastAPI
az webapp deployment list-publishing-profiles \
  --resource-group wanderbot-rg \
  --name wanderbot-fastapi \
  --xml > fastapi-publish-profile.xml

# Flask
az webapp deployment list-publishing-profiles \
  --resource-group wanderbot-rg \
  --name wanderbot-flask \
  --xml > flask-publish-profile.xml
```

### Step 2: Add GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add the following secrets:

1. **AZURE_DJANGO_APP_NAME**: `wanderbot-django`
2. **AZURE_DJANGO_PUBLISH_PROFILE**: Contents of `django-publish-profile.xml`
3. **AZURE_FASTAPI_APP_NAME**: `wanderbot-fastapi`
4. **AZURE_FASTAPI_PUBLISH_PROFILE**: Contents of `fastapi-publish-profile.xml`
5. **AZURE_FLASK_APP_NAME**: `wanderbot-flask`
6. **AZURE_FLASK_PUBLISH_PROFILE**: Contents of `flask-publish-profile.xml`

---

## Environment Variables

### Django Persistence Service

Configure in Azure Portal → App Service → Configuration → Application settings:

```bash
az webapp config appsettings set \
  --resource-group wanderbot-rg \
  --name wanderbot-django \
  --settings \
    SECRET_KEY="<generate-random-secret-key>" \
    DEBUG="False" \
    ALLOWED_HOSTS="wanderbot-django.azurewebsites.net" \
    DATABASE_URL="postgresql://dbadmin:<password>@wanderbot-db.postgres.database.azure.com:5432/wanderbot?sslmode=require" \
    ALLOW_INGEST_TOKEN="<generate-random-token>" \
    SESSION_COOKIE_AGE="1209600" \
    SESSION_COOKIE_SECURE="True" \
    CORS_ALLOWED_ORIGINS="https://wanderbot-flask.azurewebsites.net,https://wanderbot-fastapi.azurewebsites.net"
```

### FastAPI Backend

```bash
az webapp config appsettings set \
  --resource-group wanderbot-rg \
  --name wanderbot-fastapi \
  --settings \
    LIVEKIT_URL="<your-livekit-wss-url>" \
    LIVEKIT_API_KEY="<your-livekit-api-key>" \
    LIVEKIT_API_SECRET="<your-livekit-api-secret>" \
    OPENAI_API_KEY="<your-openai-api-key>" \
    DEEPGRAM_API_KEY="<your-deepgram-api-key>" \
    CARTESIA_API_KEY="<your-cartesia-api-key>" \
    SYSTEM_PROMPT="You are a friendly travel assistant." \
    CORS_ORIGINS="https://wanderbot-flask.azurewebsites.net" \
    DJANGO_BASE_URL="https://wanderbot-django.azurewebsites.net" \
    INGEST_TOKEN="<same-token-as-django>" \
    STT_PROVIDER="deepgram" \
    TTS_PROVIDER="openai" \
    LLM_PROVIDER="openai" \
    TTS_VOICE="alloy"
```

### Flask Frontend

```bash
az webapp config appsettings set \
  --resource-group wanderbot-rg \
  --name wanderbot-flask \
  --settings \
    SECRET_KEY="<generate-random-secret-key>" \
    FASTAPI_BASE_URL="https://wanderbot-fastapi.azurewebsites.net" \
    DJANGO_API_URL="https://wanderbot-django.azurewebsites.net/api" \
    LIVEKIT_URL="<your-livekit-wss-url>" \
    DEFAULT_ROOM="quickstart" \
    SYSTEM_PROMPT="You are a friendly travel assistant."
```

**Important Notes:**
- Replace all `<placeholders>` with actual values
- Replace `wanderbot-*` with your actual App Service names
- Use `https://` for production URLs
- Generate secure random strings for SECRET_KEY and INGEST_TOKEN

---

## Deployment

### Option 1: Automatic Deployment via GitHub Actions

1. Push your code to the `main` branch:
```bash
git add .
git commit -m "Prepare for Azure deployment"
git push origin main
```

2. GitHub Actions will automatically deploy all three services

3. Monitor deployment progress:
   - Go to GitHub repository → Actions tab
   - Watch the deployment workflows

### Option 2: Manual Deployment via Azure CLI

#### Deploy Django Service
```bash
cd django_persistence
zip -r ../django.zip .
cd ..
az webapp deployment source config-zip \
  --resource-group wanderbot-rg \
  --name wanderbot-django \
  --src django.zip
```

#### Deploy FastAPI Service
```bash
cd Backend
zip -r ../fastapi.zip .
cd ..
az webapp deployment source config-zip \
  --resource-group wanderbot-rg \
  --name wanderbot-fastapi \
  --src fastapi.zip
```

#### Deploy Flask Service
```bash
cd flask_frontend
zip -r ../flask.zip .
cd ..
az webapp deployment source config-zip \
  --resource-group wanderbot-rg \
  --name wanderbot-flask \
  --src flask.zip
```

---

## Post-Deployment Configuration

### Step 1: Run Database Migrations

The startup script automatically runs migrations, but you can verify:

```bash
az webapp ssh --resource-group wanderbot-rg --name wanderbot-django
python manage.py migrate
```

### Step 2: Create Django Superuser

```bash
az webapp ssh --resource-group wanderbot-rg --name wanderbot-django
python manage.py createsuperuser
```

### Step 3: Test Health Endpoints

```bash
# Django
curl https://wanderbot-django.azurewebsites.net/admin/

# FastAPI
curl https://wanderbot-fastapi.azurewebsites.net/health

# Flask
curl https://wanderbot-flask.azurewebsites.net/
```

### Step 4: Configure Custom Domain (Optional)

```bash
# Add custom domain
az webapp config hostname add \
  --resource-group wanderbot-rg \
  --webapp-name wanderbot-flask \
  --hostname www.yourdomain.com

# Enable HTTPS
az webapp config ssl bind \
  --resource-group wanderbot-rg \
  --name wanderbot-flask \
  --certificate-thumbprint <thumbprint> \
  --ssl-type SNI
```

---

## Troubleshooting

### View Application Logs

```bash
# Django logs
az webapp log tail --resource-group wanderbot-rg --name wanderbot-django

# FastAPI logs
az webapp log tail --resource-group wanderbot-rg --name wanderbot-fastapi

# Flask logs
az webapp log tail --resource-group wanderbot-rg --name wanderbot-flask
```

### Enable Application Insights

```bash
az monitor app-insights component create \
  --app wanderbot-insights \
  --location eastus \
  --resource-group wanderbot-rg

# Link to App Services
az webapp config appsettings set \
  --resource-group wanderbot-rg \
  --name wanderbot-django \
  --settings APPLICATIONINSIGHTS_CONNECTION_STRING="<connection-string>"
```

### Common Issues

#### Issue: "Module not found" errors
**Solution:** Ensure all dependencies are in `requirements.txt` and the startup script runs `pip install`

#### Issue: Database connection fails
**Solution:** 
- Verify DATABASE_URL is correct
- Check firewall rules allow Azure services
- Ensure PostgreSQL server is running

#### Issue: CORS errors in browser
**Solution:**
- Verify CORS_ALLOWED_ORIGINS includes all service URLs
- Use HTTPS URLs in production
- Check CORS_ALLOW_CREDENTIALS is True

#### Issue: Session cookies not working
**Solution:**
- Set SESSION_COOKIE_SECURE=True in production
- Ensure all services use HTTPS
- Verify CORS_ALLOW_CREDENTIALS is True

#### Issue: Startup script not executing
**Solution:**
- Check startup command in App Service configuration
- Verify script has execute permissions
- Review deployment logs for errors

### Restart Services

```bash
az webapp restart --resource-group wanderbot-rg --name wanderbot-django
az webapp restart --resource-group wanderbot-rg --name wanderbot-fastapi
az webapp restart --resource-group wanderbot-rg --name wanderbot-flask
```

---

## Cost Estimation

Monthly costs (approximate):

- **App Service Plan (B1)**: ~$13/month
- **PostgreSQL Flexible Server (B1ms)**: ~$15/month
- **Application Insights**: ~$5/month (basic)
- **Total**: ~$33/month

For production workloads, consider upgrading to:
- App Service Plan: S1 (~$70/month)
- PostgreSQL: GP_Gen5_2 (~$100/month)

---

## Security Best Practices

1. **Use Azure Key Vault** for secrets management
2. **Enable HTTPS** for all services
3. **Configure Azure Front Door** for CDN and WAF
4. **Set up Azure AD** for authentication
5. **Enable diagnostic logging** for all services
6. **Use Managed Identities** instead of connection strings where possible
7. **Implement rate limiting** on API endpoints
8. **Regular security updates** for dependencies

---

## Monitoring and Maintenance

### Set Up Alerts

```bash
# CPU usage alert
az monitor metrics alert create \
  --name high-cpu \
  --resource-group wanderbot-rg \
  --scopes /subscriptions/<subscription-id>/resourceGroups/wanderbot-rg/providers/Microsoft.Web/sites/wanderbot-django \
  --condition "avg Percentage CPU > 80" \
  --description "Alert when CPU exceeds 80%"
```

### Backup Database

```bash
# Manual backup
az postgres flexible-server backup create \
  --resource-group wanderbot-rg \
  --name wanderbot-db \
  --backup-name manual-backup-$(date +%Y%m%d)
```

### Update Application

1. Make changes to code
2. Commit and push to GitHub
3. GitHub Actions automatically deploys
4. Monitor deployment in Actions tab

---

## Additional Resources

- [Azure App Service Documentation](https://docs.microsoft.com/azure/app-service/)
- [Azure Database for PostgreSQL](https://docs.microsoft.com/azure/postgresql/)
- [GitHub Actions for Azure](https://docs.microsoft.com/azure/developer/github/github-actions)
- [LiveKit Documentation](https://docs.livekit.io/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)

---

## Support

For issues or questions:
- **Azure Support**: [Azure Portal](https://portal.azure.com)
- **GitHub Issues**: Create an issue in this repository
- **LiveKit Community**: [LiveKit Slack](https://livekit.io/community)

---

## Next Steps

After successful deployment:

1. ✅ Test all user flows (signup, login, voice chat)
2. ✅ Configure monitoring and alerts
3. ✅ Set up automated backups
4. ✅ Implement CI/CD improvements
5. ✅ Add custom domain and SSL
6. ✅ Optimize performance and scaling
7. ✅ Document API endpoints
8. ✅ Set up staging environment

---

**Congratulations!** Your Voice Agent application is now deployed to Azure! 🎉
