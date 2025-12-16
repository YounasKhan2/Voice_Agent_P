# Azure Deployment Checklist

Use this checklist to ensure all steps are completed for a successful deployment.

## Pre-Deployment

### Azure Account Setup
- [ ] Azure account created with active subscription
- [ ] Azure CLI installed and configured
- [ ] Logged in to Azure CLI (`az login`)
- [ ] Subscription selected (`az account set`)

### External Services
- [ ] LiveKit account created (Cloud or self-hosted)
- [ ] LiveKit WebSocket URL obtained (wss://)
- [ ] LiveKit API key and secret obtained
- [ ] OpenAI API key obtained
- [ ] Deepgram API key obtained (optional)
- [ ] Cartesia API key obtained (optional)

### Repository Setup
- [ ] Code pushed to GitHub repository
- [ ] Repository is accessible
- [ ] All local changes committed

## Azure Resources Creation

### Resource Group
- [ ] Resource group created (`wanderbot-rg`)
- [ ] Location selected (e.g., `eastus`)

### Database
- [ ] PostgreSQL Flexible Server created
- [ ] Database name: `wanderbot`
- [ ] Admin username saved
- [ ] Admin password saved (secure location)
- [ ] Firewall rule created (Allow Azure Services)
- [ ] Connection string saved

### App Service Plan
- [ ] App Service Plan created
- [ ] SKU selected (B1 minimum)
- [ ] Linux runtime selected

### App Services
- [ ] Django service created (`wanderbot-django`)
- [ ] FastAPI service created (`wanderbot-fastapi`)
- [ ] Flask service created (`wanderbot-flask`)
- [ ] Python 3.11 runtime configured for all
- [ ] Startup commands configured for all

## Environment Variables Configuration

### Django Service (`wanderbot-django`)
- [ ] `SECRET_KEY` - Random 50+ character string
- [ ] `DEBUG` - Set to "False"
- [ ] `ALLOWED_HOSTS` - Service domain name
- [ ] `DATABASE_URL` - PostgreSQL connection string
- [ ] `ALLOW_INGEST_TOKEN` - Random token (save for FastAPI)
- [ ] `SESSION_COOKIE_AGE` - 1209600 (14 days)
- [ ] `SESSION_COOKIE_SECURE` - "True"
- [ ] `CORS_ALLOWED_ORIGINS` - Flask and FastAPI URLs

### FastAPI Service (`wanderbot-fastapi`)
- [ ] `LIVEKIT_URL` - WebSocket URL (wss://)
- [ ] `LIVEKIT_API_KEY` - LiveKit API key
- [ ] `LIVEKIT_API_SECRET` - LiveKit API secret
- [ ] `OPENAI_API_KEY` - OpenAI API key
- [ ] `DEEPGRAM_API_KEY` - Deepgram API key (optional)
- [ ] `CARTESIA_API_KEY` - Cartesia API key (optional)
- [ ] `SYSTEM_PROMPT` - Default agent prompt
- [ ] `CORS_ORIGINS` - Flask service URL
- [ ] `DJANGO_BASE_URL` - Django service URL
- [ ] `INGEST_TOKEN` - Same as Django's ALLOW_INGEST_TOKEN
- [ ] `STT_PROVIDER` - "deepgram" or "openai"
- [ ] `TTS_PROVIDER` - "openai" or "cartesia"
- [ ] `LLM_PROVIDER` - "openai"
- [ ] `TTS_VOICE` - "alloy" or preferred voice

### Flask Service (`wanderbot-flask`)
- [ ] `SECRET_KEY` - Random 50+ character string
- [ ] `FASTAPI_BASE_URL` - FastAPI service URL
- [ ] `DJANGO_API_URL` - Django service URL with /api
- [ ] `LIVEKIT_URL` - LiveKit WebSocket URL (wss://)
- [ ] `DEFAULT_ROOM` - "quickstart"
- [ ] `SYSTEM_PROMPT` - Default agent prompt

## GitHub Actions Setup

### Publish Profiles
- [ ] Django publish profile downloaded
- [ ] FastAPI publish profile downloaded
- [ ] Flask publish profile downloaded

### GitHub Secrets
- [ ] `AZURE_DJANGO_APP_NAME` added
- [ ] `AZURE_DJANGO_PUBLISH_PROFILE` added
- [ ] `AZURE_FASTAPI_APP_NAME` added
- [ ] `AZURE_FASTAPI_PUBLISH_PROFILE` added
- [ ] `AZURE_FLASK_APP_NAME` added
- [ ] `AZURE_FLASK_PUBLISH_PROFILE` added

## Deployment

### Code Deployment
- [ ] All changes committed to git
- [ ] Code pushed to main branch
- [ ] GitHub Actions workflows triggered
- [ ] Django deployment successful
- [ ] FastAPI deployment successful
- [ ] Flask deployment successful

### Deployment Verification
- [ ] Django logs checked (no errors)
- [ ] FastAPI logs checked (no errors)
- [ ] Flask logs checked (no errors)
- [ ] All services started successfully

## Post-Deployment

### Database Setup
- [ ] Database migrations run successfully
- [ ] Django superuser created
- [ ] Admin panel accessible

### Health Checks
- [ ] Django health endpoint responds: `/health/`
- [ ] FastAPI health endpoint responds: `/health`
- [ ] Flask health endpoint responds: `/health`

### Functional Testing
- [ ] Flask frontend loads successfully
- [ ] User can access signup page
- [ ] User can create account
- [ ] User can login
- [ ] User can access chat interface
- [ ] Voice conversation works
- [ ] Conversation history saves
- [ ] User profile accessible
- [ ] User preferences work
- [ ] Logout works

### Security Verification
- [ ] All services use HTTPS
- [ ] Session cookies are secure
- [ ] CORS configured correctly
- [ ] Database uses SSL
- [ ] No secrets in logs
- [ ] Admin panel requires authentication

## Optional Enhancements

### Custom Domain
- [ ] Custom domain purchased
- [ ] DNS configured
- [ ] Custom domain added to Flask service
- [ ] SSL certificate configured
- [ ] HTTPS redirect enabled

### Monitoring
- [ ] Application Insights enabled
- [ ] Log Analytics workspace created
- [ ] Alerts configured for errors
- [ ] Alerts configured for high CPU
- [ ] Alerts configured for high memory
- [ ] Dashboard created

### Backup & Recovery
- [ ] Database backup configured
- [ ] Backup retention policy set
- [ ] Recovery plan documented
- [ ] Disaster recovery tested

### Performance
- [ ] Auto-scaling rules configured
- [ ] CDN configured for static files
- [ ] Database connection pooling verified
- [ ] Response times acceptable

### CI/CD Improvements
- [ ] Staging environment created
- [ ] Automated tests added
- [ ] Deployment approval workflow
- [ ] Rollback procedure documented

## Documentation

- [ ] Deployment guide reviewed
- [ ] Environment variables documented
- [ ] Architecture diagram created
- [ ] Runbook created for operations
- [ ] Troubleshooting guide updated

## Sign-Off

### Deployment Team
- [ ] Developer sign-off
- [ ] DevOps sign-off
- [ ] Security review completed
- [ ] Product owner approval

### Production Readiness
- [ ] All checklist items completed
- [ ] Production credentials secured
- [ ] Support team notified
- [ ] Monitoring dashboard shared
- [ ] Incident response plan in place

---

## Notes

Use this section to track any issues, decisions, or important information during deployment:

```
Date: _______________
Deployed by: _______________
Azure Subscription: _______________
Resource Group: _______________

Django URL: _______________
FastAPI URL: _______________
Flask URL: _______________

Issues encountered:
- 
- 
- 

Resolutions:
- 
- 
- 

Next steps:
- 
- 
- 
```

---

**Deployment Status:** [ ] Not Started | [ ] In Progress | [ ] Completed | [ ] Failed

**Production Go-Live Date:** _______________
