# Azure Deployment Quick Start Guide

This is a condensed guide for deploying the Voice Agent application to Azure. For detailed instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Prerequisites Checklist

- [ ] Azure account with active subscription
- [ ] GitHub account with this repository
- [ ] Azure CLI installed
- [ ] LiveKit credentials (URL, API key, API secret)
- [ ] OpenAI API key (or other AI provider keys)

## Quick Deployment Steps

### 1. Create Azure Resources (5 minutes)

```bash
# Login
az login

# Create resource group
az group create --name wanderbot-rg --location eastus

# Create PostgreSQL database
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

# Create App Service Plan
az appservice plan create \
  --name wanderbot-plan \
  --resource-group wanderbot-rg \
  --location eastus \
  --sku B1 \
  --is-linux

# Create three App Services
az webapp create --resource-group wanderbot-rg --plan wanderbot-plan --name wanderbot-django --runtime "PYTHON:3.11" --startup-file "bash startup.sh"
az webapp create --resource-group wanderbot-rg --plan wanderbot-plan --name wanderbot-fastapi --runtime "PYTHON:3.11" --startup-file "bash startup.sh"
az webapp create --resource-group wanderbot-rg --plan wanderbot-plan --name wanderbot-flask --runtime "PYTHON:3.11" --startup-file "bash startup.sh"
```

### 2. Configure Environment Variables (10 minutes)

#### Django Service
```bash
az webapp config appsettings set \
  --resource-group wanderbot-rg \
  --name wanderbot-django \
  --settings \
    SECRET_KEY="<random-50-char-string>" \
    DEBUG="False" \
    ALLOWED_HOSTS="wanderbot-django.azurewebsites.net" \
    DATABASE_URL="postgresql://dbadmin:<password>@wanderbot-db.postgres.database.azure.com:5432/wanderbot?sslmode=require" \
    ALLOW_INGEST_TOKEN="<random-token>" \
    SESSION_COOKIE_SECURE="True" \
    CORS_ALLOWED_ORIGINS="https://wanderbot-flask.azurewebsites.net,https://wanderbot-fastapi.azurewebsites.net"
```

#### FastAPI Service
```bash
az webapp config appsettings set \
  --resource-group wanderbot-rg \
  --name wanderbot-fastapi \
  --settings \
    LIVEKIT_URL="<wss://your-livekit-url>" \
    LIVEKIT_API_KEY="<key>" \
    LIVEKIT_API_SECRET="<secret>" \
    OPENAI_API_KEY="<key>" \
    DEEPGRAM_API_KEY="<key>" \
    CARTESIA_API_KEY="<key>" \
    CORS_ORIGINS="https://wanderbot-flask.azurewebsites.net" \
    DJANGO_BASE_URL="https://wanderbot-django.azurewebsites.net" \
    INGEST_TOKEN="<same-as-django>"
```

#### Flask Service
```bash
az webapp config appsettings set \
  --resource-group wanderbot-rg \
  --name wanderbot-flask \
  --settings \
    SECRET_KEY="<random-50-char-string>" \
    FASTAPI_BASE_URL="https://wanderbot-fastapi.azurewebsites.net" \
    DJANGO_API_URL="https://wanderbot-django.azurewebsites.net/api" \
    LIVEKIT_URL="<wss://your-livekit-url>"
```

### 3. Setup GitHub Actions (5 minutes)

1. Get publish profiles:
```bash
az webapp deployment list-publishing-profiles --resource-group wanderbot-rg --name wanderbot-django --xml > django-profile.xml
az webapp deployment list-publishing-profiles --resource-group wanderbot-rg --name wanderbot-fastapi --xml > fastapi-profile.xml
az webapp deployment list-publishing-profiles --resource-group wanderbot-rg --name wanderbot-flask --xml > flask-profile.xml
```

2. Add GitHub Secrets (Repository → Settings → Secrets):
   - `AZURE_DJANGO_APP_NAME`: `wanderbot-django`
   - `AZURE_DJANGO_PUBLISH_PROFILE`: Contents of `django-profile.xml`
   - `AZURE_FASTAPI_APP_NAME`: `wanderbot-fastapi`
   - `AZURE_FASTAPI_PUBLISH_PROFILE`: Contents of `fastapi-profile.xml`
   - `AZURE_FLASK_APP_NAME`: `wanderbot-flask`
   - `AZURE_FLASK_PUBLISH_PROFILE`: Contents of `flask-profile.xml`

### 4. Deploy (2 minutes)

```bash
git add .
git commit -m "Deploy to Azure"
git push origin main
```

GitHub Actions will automatically deploy all three services!

### 5. Post-Deployment (5 minutes)

```bash
# Create Django superuser
az webapp ssh --resource-group wanderbot-rg --name wanderbot-django
python manage.py createsuperuser
exit

# Test endpoints
curl https://wanderbot-django.azurewebsites.net/health/
curl https://wanderbot-fastapi.azurewebsites.net/health
curl https://wanderbot-flask.azurewebsites.net/health

# Open your app
open https://wanderbot-flask.azurewebsites.net/
```

## Environment Variables Reference

### Required for All Services
- `SECRET_KEY`: Random 50+ character string
- `DEBUG`: Set to "False" in production

### Django Specific
- `DATABASE_URL`: PostgreSQL connection string
- `ALLOWED_HOSTS`: Your domain name
- `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed origins
- `ALLOW_INGEST_TOKEN`: Random token for FastAPI authentication

### FastAPI Specific
- `LIVEKIT_URL`: WebSocket URL (wss://)
- `LIVEKIT_API_KEY`: LiveKit API key
- `LIVEKIT_API_SECRET`: LiveKit API secret
- `OPENAI_API_KEY`: OpenAI API key
- `DJANGO_BASE_URL`: Django service URL
- `INGEST_TOKEN`: Same as Django's ALLOW_INGEST_TOKEN

### Flask Specific
- `FASTAPI_BASE_URL`: FastAPI service URL
- `DJANGO_API_URL`: Django API URL (with /api suffix)
- `LIVEKIT_URL`: LiveKit WebSocket URL

## Troubleshooting

### View Logs
```bash
az webapp log tail --resource-group wanderbot-rg --name wanderbot-django
az webapp log tail --resource-group wanderbot-rg --name wanderbot-fastapi
az webapp log tail --resource-group wanderbot-rg --name wanderbot-flask
```

### Restart Services
```bash
az webapp restart --resource-group wanderbot-rg --name wanderbot-django
az webapp restart --resource-group wanderbot-rg --name wanderbot-fastapi
az webapp restart --resource-group wanderbot-rg --name wanderbot-flask
```

### Common Issues

**Database connection fails:**
- Check DATABASE_URL format
- Verify firewall rules allow Azure services
- Ensure password is URL-encoded

**CORS errors:**
- Verify all URLs use https:// in production
- Check CORS_ALLOWED_ORIGINS includes all service URLs
- Ensure CORS_ALLOW_CREDENTIALS is True

**Session cookies not working:**
- Set SESSION_COOKIE_SECURE=True
- Use HTTPS for all services
- Check CORS configuration

## Cost Estimate

- App Service Plan (B1): ~$13/month
- PostgreSQL (B1ms): ~$15/month
- Total: ~$28/month

## Next Steps

1. ✅ Test signup and login
2. ✅ Test voice conversation
3. ✅ Configure custom domain
4. ✅ Set up monitoring alerts
5. ✅ Enable Application Insights
6. ✅ Configure auto-scaling

## Support

- Full guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- Azure docs: https://docs.microsoft.com/azure/app-service/
- GitHub Issues: Create an issue in this repository

---

**Total deployment time: ~30 minutes** ⏱️
