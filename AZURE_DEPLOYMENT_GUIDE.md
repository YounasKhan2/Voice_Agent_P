# Azure Deployment Guide for WanderBot Voice Agent

This guide walks you through deploying your multi-service voice agent application to Azure.

## Architecture Overview

Your application consists of:
1. **Flask Frontend** (Port 5173) - Web UI
2. **FastAPI Backend** (Port 8000) - Voice agent logic with LiveKit
3. **Django API** (Port 9000) - Authentication & data persistence
4. **PostgreSQL Database** - User data and conversation history
5. **LiveKit Server** - Real-time voice communication

---

## Deployment Strategy

### Option 1: Azure Container Apps (Recommended)
Best for microservices architecture with automatic scaling.

### Option 2: Azure App Service
Simpler setup, good for getting started quickly.

### Option 3: Azure Kubernetes Service (AKS)
Most flexible, best for production at scale.

---

## Prerequisites

1. **Azure Account** - [Sign up here](https://azure.microsoft.com/free/)
2. **Azure CLI** - Install from [here](https://docs.microsoft.com/cli/azure/install-azure-cli)
3. **Docker** - Install from [here](https://docs.docker.com/get-docker/)
4. **Git** - For version control

---

## Step-by-Step Deployment (Azure Container Apps)

### 1. Prepare Your Application

#### Create Dockerfiles for Each Service

**Flask Frontend Dockerfile** (`flask_frontend/Dockerfile`):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5173

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5173", "--workers", "4", "app:app"]
```

**FastAPI Backend Dockerfile** (`Backend/Dockerfile`):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Django API Dockerfile** (`django_persistence/Dockerfile`):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 9000

# Run migrations and start server
CMD python manage.py migrate && \
    gunicorn --bind 0.0.0.0:9000 --workers 4 config.wsgi:application
```

#### Create Requirements Files

Make sure each service has a `requirements.txt` file with all dependencies.

---

### 2. Set Up Azure Resources

#### Login to Azure
```bash
az login
```

#### Create Resource Group
```bash
az group create \
  --name wanderbot-rg \
  --location eastus
```

#### Create Azure Container Registry (ACR)
```bash
az acr create \
  --resource-group wanderbot-rg \
  --name wanderbotacr \
  --sku Basic \
  --admin-enabled true
```

#### Get ACR Credentials
```bash
az acr credential show --name wanderbotacr
```

---

### 3. Build and Push Docker Images

#### Login to ACR
```bash
az acr login --name wanderbotacr
```

#### Build and Push Flask Frontend
```bash
cd flask_frontend
docker build -t wanderbotacr.azurecr.io/flask-frontend:latest .
docker push wanderbotacr.azurecr.io/flask-frontend:latest
```

#### Build and Push FastAPI Backend
```bash
cd ../Backend
docker build -t wanderbotacr.azurecr.io/fastapi-backend:latest .
docker push wanderbotacr.azurecr.io/fastapi-backend:latest
```

#### Build and Push Django API
```bash
cd ../django_persistence
docker build -t wanderbotacr.azurecr.io/django-api:latest .
docker push wanderbotacr.azurecr.io/django-api:latest
```

---

### 4. Create Azure Database for PostgreSQL

```bash
az postgres flexible-server create \
  --resource-group wanderbot-rg \
  --name wanderbot-db \
  --location eastus \
  --admin-user dbadmin \
  --admin-password <YourSecurePassword> \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32 \
  --version 14
```

#### Create Database
```bash
az postgres flexible-server db create \
  --resource-group wanderbot-rg \
  --server-name wanderbot-db \
  --database-name wanderbot
```

#### Configure Firewall (Allow Azure Services)
```bash
az postgres flexible-server firewall-rule create \
  --resource-group wanderbot-rg \
  --name wanderbot-db \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

---

### 5. Deploy LiveKit Server

You have two options:

#### Option A: Use LiveKit Cloud (Easiest)
1. Sign up at [LiveKit Cloud](https://cloud.livekit.io/)
2. Create a project
3. Get your WebSocket URL and API credentials

#### Option B: Self-host on Azure Container Apps
```bash
az containerapp create \
  --name livekit-server \
  --resource-group wanderbot-rg \
  --environment wanderbot-env \
  --image livekit/livekit-server:latest \
  --target-port 7880 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3
```

---

### 6. Create Container Apps Environment

```bash
az containerapp env create \
  --name wanderbot-env \
  --resource-group wanderbot-rg \
  --location eastus
```

---

### 7. Deploy Container Apps

#### Deploy Django API
```bash
az containerapp create \
  --name django-api \
  --resource-group wanderbot-rg \
  --environment wanderbot-env \
  --image wanderbotacr.azurecr.io/django-api:latest \
  --target-port 9000 \
  --ingress external \
  --registry-server wanderbotacr.azurecr.io \
  --registry-username <ACR_USERNAME> \
  --registry-password <ACR_PASSWORD> \
  --env-vars \
    "DATABASE_URL=postgresql://dbadmin:<password>@wanderbot-db.postgres.database.azure.com:5432/wanderbot" \
    "SECRET_KEY=<your-secret-key>" \
    "DEBUG=False" \
    "ALLOWED_HOSTS=*" \
  --min-replicas 1 \
  --max-replicas 3
```

#### Deploy FastAPI Backend
```bash
az containerapp create \
  --name fastapi-backend \
  --resource-group wanderbot-rg \
  --environment wanderbot-env \
  --image wanderbotacr.azurecr.io/fastapi-backend:latest \
  --target-port 8000 \
  --ingress external \
  --registry-server wanderbotacr.azurecr.io \
  --registry-username <ACR_USERNAME> \
  --registry-password <ACR_PASSWORD> \
  --env-vars \
    "LIVEKIT_URL=<your-livekit-url>" \
    "LIVEKIT_API_KEY=<your-api-key>" \
    "LIVEKIT_API_SECRET=<your-api-secret>" \
    "OPENAI_API_KEY=<your-openai-key>" \
  --min-replicas 1 \
  --max-replicas 5
```

#### Deploy Flask Frontend
```bash
az containerapp create \
  --name flask-frontend \
  --resource-group wanderbot-rg \
  --environment wanderbot-env \
  --image wanderbotacr.azurecr.io/flask-frontend:latest \
  --target-port 5173 \
  --ingress external \
  --registry-server wanderbotacr.azurecr.io \
  --registry-username <ACR_USERNAME> \
  --registry-password <ACR_PASSWORD> \
  --env-vars \
    "FASTAPI_BASE_URL=https://fastapi-backend.<region>.azurecontainerapps.io" \
    "DJANGO_API_URL=https://django-api.<region>.azurecontainerapps.io/api" \
    "LIVEKIT_URL=<your-livekit-url>" \
    "SECRET_KEY=<your-secret-key>" \
  --min-replicas 1 \
  --max-replicas 3
```

---

### 8. Configure Custom Domain (Optional)

```bash
# Add custom domain
az containerapp hostname add \
  --hostname www.wanderbot.com \
  --resource-group wanderbot-rg \
  --name flask-frontend

# Bind SSL certificate
az containerapp hostname bind \
  --hostname www.wanderbot.com \
  --resource-group wanderbot-rg \
  --name flask-frontend \
  --environment wanderbot-env \
  --validation-method CNAME
```

---

## Environment Variables Summary

### Flask Frontend
- `FASTAPI_BASE_URL` - FastAPI backend URL
- `DJANGO_API_URL` - Django API URL
- `LIVEKIT_URL` - LiveKit WebSocket URL
- `SECRET_KEY` - Flask secret key

### FastAPI Backend
- `LIVEKIT_URL` - LiveKit server URL
- `LIVEKIT_API_KEY` - LiveKit API key
- `LIVEKIT_API_SECRET` - LiveKit API secret
- `OPENAI_API_KEY` - OpenAI API key

### Django API
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Django secret key
- `DEBUG` - Set to False in production
- `ALLOWED_HOSTS` - Your domain names

---

## Cost Estimation (Monthly)

- **Container Apps** (3 apps): ~$50-100
- **PostgreSQL Flexible Server**: ~$15-30
- **Container Registry**: ~$5
- **LiveKit Cloud**: ~$0-50 (depending on usage)
- **Total**: ~$70-185/month

---

## Monitoring and Logging

### Enable Application Insights
```bash
az monitor app-insights component create \
  --app wanderbot-insights \
  --location eastus \
  --resource-group wanderbot-rg
```

### View Logs
```bash
# View Flask logs
az containerapp logs show \
  --name flask-frontend \
  --resource-group wanderbot-rg \
  --follow

# View Django logs
az containerapp logs show \
  --name django-api \
  --resource-group wanderbot-rg \
  --follow
```

---

## CI/CD with GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Azure

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Login to Azure
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Login to ACR
      run: az acr login --name wanderbotacr
    
    - name: Build and push Flask
      run: |
        cd flask_frontend
        docker build -t wanderbotacr.azurecr.io/flask-frontend:${{ github.sha }} .
        docker push wanderbotacr.azurecr.io/flask-frontend:${{ github.sha }}
    
    - name: Deploy Flask to Container Apps
      run: |
        az containerapp update \
          --name flask-frontend \
          --resource-group wanderbot-rg \
          --image wanderbotacr.azurecr.io/flask-frontend:${{ github.sha }}
```

---

## Security Best Practices

1. **Use Azure Key Vault** for secrets
2. **Enable HTTPS** for all services
3. **Configure CORS** properly
4. **Use Managed Identities** instead of passwords
5. **Enable Azure DDoS Protection**
6. **Set up Azure Front Door** for CDN and WAF

---

## Troubleshooting

### Check Container App Status
```bash
az containerapp show \
  --name flask-frontend \
  --resource-group wanderbot-rg
```

### View Recent Logs
```bash
az containerapp logs show \
  --name flask-frontend \
  --resource-group wanderbot-rg \
  --tail 100
```

### Restart Container App
```bash
az containerapp revision restart \
  --name flask-frontend \
  --resource-group wanderbot-rg
```

---

## Next Steps

1. Set up monitoring and alerts
2. Configure auto-scaling rules
3. Implement backup strategy for database
4. Set up staging environment
5. Configure CDN for static assets

---

## Useful Resources

- [Azure Container Apps Documentation](https://docs.microsoft.com/azure/container-apps/)
- [Azure Database for PostgreSQL](https://docs.microsoft.com/azure/postgresql/)
- [LiveKit Documentation](https://docs.livekit.io/)
- [Azure CLI Reference](https://docs.microsoft.com/cli/azure/)

---

## Support

For issues or questions:
- Azure Support: [Azure Portal](https://portal.azure.com)
- LiveKit Support: [LiveKit Community](https://livekit.io/community)
- OpenAI Support: [OpenAI Help Center](https://help.openai.com)
