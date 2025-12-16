# Requirements Document

## Introduction

This document outlines the requirements for deploying a multi-service voice agent application to Azure App Service from a single GitHub repository. The application consists of three Python-based services (FastAPI backend, Django persistence service, and Flask frontend) that must be deployed as separate Azure App Services while maintaining their interconnected functionality.

## Glossary

- **FastAPI_Service**: The Backend service that orchestrates LiveKit voice agent sessions, handles STT/LLM/TTS pipeline
- **Django_Service**: The django_persistence service that provides authentication, user profiles, and conversation history storage
- **Flask_Service**: The flask_frontend service that serves the web UI and handles user interactions
- **Azure_App_Service**: Azure's platform-as-a-service offering for hosting web applications
- **GitHub_Actions**: CI/CD automation platform integrated with GitHub repositories
- **Startup_Command**: The command Azure App Service executes to start the Python application
- **Application_Settings**: Environment variables configured in Azure App Service
- **Deployment_Path**: The subdirectory within the repository that contains a specific service's code

## Requirements

### Requirement 1

**User Story:** As a DevOps engineer, I want to deploy all three services from a single GitHub repository, so that I can maintain code consistency and simplify version control

#### Acceptance Criteria

1. WHEN the repository is pushed to GitHub, THE Repository SHALL contain all three service directories (Backend, django_persistence, flask_frontend) in the root
2. THE Repository SHALL include a .gitignore file that excludes virtual environments, .env files, and Python cache files
3. THE Repository SHALL include a README with deployment instructions
4. WHERE each service has local .env files, THE Repository SHALL NOT include these files in version control

### Requirement 2

**User Story:** As a developer, I want each service to have proper startup scripts for Azure, so that Azure App Service can correctly initialize and run each Python application

#### Acceptance Criteria

1. THE FastAPI_Service SHALL include a startup.sh script that installs dependencies and starts uvicorn
2. THE Django_Service SHALL include a startup.sh script that installs dependencies, runs migrations, and starts gunicorn
3. THE Flask_Service SHALL include a startup.sh script that installs dependencies and starts gunicorn
4. WHEN Azure App Service starts a service, THE Startup_Command SHALL execute the corresponding startup.sh script
5. THE Startup_Command SHALL bind to the port specified by Azure's PORT environment variable

### Requirement 3

**User Story:** As a developer, I want each service to have production-ready requirements files, so that Azure can install all necessary dependencies

#### Acceptance Criteria

1. THE FastAPI_Service SHALL include a requirements.txt with all production dependencies including uvicorn, fastapi, and livekit-agents
2. THE Django_Service SHALL include a requirements.txt with all production dependencies including django, djangorestframework, gunicorn, and psycopg2-binary
3. THE Flask_Service SHALL include a requirements.txt with all production dependencies including flask and gunicorn
4. WHERE a service requires a production WSGI server, THE requirements.txt SHALL include gunicorn
5. THE requirements.txt files SHALL NOT include development-only dependencies

### Requirement 4

**User Story:** As a DevOps engineer, I want GitHub Actions workflows to automatically deploy each service to Azure, so that deployments are automated and consistent

#### Acceptance Criteria

1. THE Repository SHALL include a .github/workflows directory with three deployment workflow files
2. WHEN code is pushed to the main branch, THE GitHub_Actions SHALL trigger deployment workflows for all three services
3. THE GitHub_Actions SHALL deploy the FastAPI_Service from the Backend directory to its Azure App Service
4. THE GitHub_Actions SHALL deploy the Django_Service from the django_persistence directory to its Azure App Service
5. THE GitHub_Actions SHALL deploy the Flask_Service from the flask_frontend directory to its Azure App Service
6. WHERE deployment requires authentication, THE GitHub_Actions SHALL use Azure publish profiles stored as GitHub secrets

### Requirement 5

**User Story:** As a system administrator, I want environment variables configured in Azure App Service, so that sensitive credentials are not stored in the repository

#### Acceptance Criteria

1. THE FastAPI_Service SHALL read configuration from Application_Settings including LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET, and API keys for AI providers
2. THE Django_Service SHALL read configuration from Application_Settings including SECRET_KEY, ALLOWED_HOSTS, and CORS_ALLOWED_ORIGINS
3. THE Flask_Service SHALL read configuration from Application_Settings including FASTAPI_BASE_URL, DJANGO_API_URL, and SECRET_KEY
4. WHEN a service starts, THE Application_Settings SHALL override any default configuration values
5. THE Application_Settings SHALL include production URLs for inter-service communication

### Requirement 6

**User Story:** As a developer, I want the Django service to use Azure Database for PostgreSQL, so that conversation data persists reliably in production

#### Acceptance Criteria

1. THE Django_Service SHALL support PostgreSQL database connections via DATABASE_URL environment variable
2. WHEN Django_Service starts, THE Startup_Command SHALL run database migrations automatically
3. THE Django_Service SHALL include psycopg2-binary in requirements.txt for PostgreSQL connectivity
4. WHERE DATABASE_URL is not provided, THE Django_Service SHALL fall back to SQLite for local development
5. THE Django_Service SHALL configure database connection pooling for production workloads

### Requirement 7

**User Story:** As a developer, I want proper CORS configuration for production, so that the frontend can communicate with both backend services

#### Acceptance Criteria

1. THE FastAPI_Service SHALL configure CORS_ORIGINS to include the Flask_Service production URL
2. THE Django_Service SHALL configure CORS_ALLOWED_ORIGINS to include both FastAPI_Service and Flask_Service production URLs
3. WHEN a service receives a cross-origin request, THE Service SHALL validate the origin against the configured allowed origins
4. THE CORS configuration SHALL allow credentials for session-based authentication
5. THE CORS configuration SHALL be configurable via Application_Settings

### Requirement 8

**User Story:** As a developer, I want inter-service URLs configured correctly, so that services can communicate with each other in production

#### Acceptance Criteria

1. THE Flask_Service SHALL configure FASTAPI_BASE_URL to point to the FastAPI_Service production URL
2. THE Flask_Service SHALL configure DJANGO_API_URL to point to the Django_Service production URL
3. THE FastAPI_Service SHALL configure DJANGO_BASE_URL to point to the Django_Service production URL
4. WHEN a service makes an inter-service API call, THE Service SHALL use HTTPS protocol for production URLs
5. THE inter-service URLs SHALL be configurable via Application_Settings

### Requirement 9

**User Story:** As a developer, I want health check endpoints configured, so that Azure can monitor service availability

#### Acceptance Criteria

1. THE FastAPI_Service SHALL expose a /health endpoint that returns HTTP 200 when healthy
2. THE Django_Service SHALL expose a health check endpoint that returns HTTP 200 when healthy
3. THE Flask_Service SHALL expose a health check endpoint that returns HTTP 200 when healthy
4. WHEN Azure App Service performs a health check, THE Service SHALL respond within 5 seconds
5. THE health check endpoints SHALL verify critical dependencies (database connectivity for Django)

### Requirement 10

**User Story:** As a DevOps engineer, I want deployment documentation, so that I can set up and maintain the Azure infrastructure

#### Acceptance Criteria

1. THE Repository SHALL include a DEPLOYMENT.md file with step-by-step Azure setup instructions
2. THE DEPLOYMENT.md SHALL document how to create three Azure App Services
3. THE DEPLOYMENT.md SHALL document all required Application_Settings for each service
4. THE DEPLOYMENT.md SHALL document how to configure GitHub Actions secrets
5. THE DEPLOYMENT.md SHALL document how to set up Azure Database for PostgreSQL
6. THE DEPLOYMENT.md SHALL include troubleshooting steps for common deployment issues

### Requirement 11

**User Story:** As a developer, I want static files served correctly in production, so that the Flask frontend displays properly

#### Acceptance Criteria

1. THE Flask_Service SHALL configure static file serving for production
2. WHEN Flask_Service runs in production, THE Service SHALL serve CSS and JavaScript files from the static directory
3. THE Flask_Service SHALL set appropriate cache headers for static assets
4. THE Flask_Service SHALL use WhiteNoise or similar middleware for efficient static file serving
5. THE static file configuration SHALL work with Azure App Service's file system

### Requirement 12

**User Story:** As a security engineer, I want production security settings enabled, so that the application is secure in production

#### Acceptance Criteria

1. THE Django_Service SHALL set DEBUG=False in production Application_Settings
2. THE Django_Service SHALL set SESSION_COOKIE_SECURE=True in production Application_Settings
3. THE Django_Service SHALL configure ALLOWED_HOSTS to include only the production domain
4. THE Flask_Service SHALL set SESSION_COOKIE_SECURE=True in production
5. WHEN services communicate, THE Services SHALL use HTTPS for all inter-service requests
