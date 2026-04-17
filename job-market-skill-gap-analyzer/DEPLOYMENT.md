# Deployment Guide

This guide covers deploying the SkillScope backend API to various cloud platforms using GitHub Actions.

## Prerequisites

- GitHub repository with code
- Docker Hub or GitHub Container Registry access
- Cloud provider account (AWS, GCP, Azure, or DigitalOcean)
- Domain name (optional but recommended)

## Table of Contents

1. [Docker Deployment](#docker-deployment)
2. [AWS Deployment](#aws-deployment)
3. [Google Cloud Platform](#google-cloud-platform)
4. [Azure Deployment](#azure-deployment)
5. [DigitalOcean](#digitalocean)
6. [Environment Variables](#environment-variables)
7. [GitHub Actions Setup](#github-actions-setup)

## Docker Deployment

### Local Docker Testing

```bash
# Build the image
docker build -t skillscope-api .

# Run container
docker run -d -p 8000:8000 \
  --name skillscope-api \
  -v $(pwd)/data:/app/data \
  skillscope-api

# Check logs
docker logs skillscope-api

# Test health endpoint
curl http://localhost:8000/health
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

## AWS Deployment

### Option 1: AWS ECS (Elastic Container Service)

#### Setup

1. **Create ECR Repository**
```bash
aws ecr create-repository --repository-name skillscope-api
```

2. **Create ECS Cluster**
```bash
aws ecs create-cluster --cluster-name skillscope-cluster
```

3. **Create Task Definition**
```json
{
  "family": "skillscope-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [{
    "name": "api",
    "image": "YOUR_ECR_REPO/skillscope-api:latest",
    "portMappings": [{
      "containerPort": 8000,
      "protocol": "tcp"
    }],
    "environment": [
      {"name": "ENVIRONMENT", "value": "production"}
    ]
  }]
}
```

4. **Configure GitHub Secrets**
```bash
# Add to GitHub repository secrets:
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION
```

5. **Deploy** - Push to main branch triggers automatic deployment

### Option 2: AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p docker skillscope-api

# Create environment
eb create skillscope-prod

# Deploy
eb deploy
```

## Google Cloud Platform

### Cloud Run Deployment

#### Setup

1. **Enable Cloud Run API**
```bash
gcloud services enable run.googleapis.com
```

2. **Create Service Account**
```bash
gcloud iam service-accounts create skillscope-deployer \
  --display-name="SkillScope Deployer"

# Generate key
gcloud iam service-accounts keys create key.json \
  --iam-account=skillscope-deployer@PROJECT_ID.iam.gserviceaccount.com
```

3. **Configure GitHub Secrets**
```bash
# Add to GitHub repository secrets:
GCP_PROJECT_ID
GCP_SA_KEY  # Contents of key.json
```

4. **Deploy via GitHub Actions**

Uncomment the GCP section in `.github/workflows/deploy.yml`:

```yaml
- name: Deploy to Cloud Run
  run: |
    gcloud run deploy skillscope-api \
      --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/skillscope-api:latest \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated
```

### Manual Deployment

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/skillscope-api

# Deploy
gcloud run deploy skillscope-api \
  --image gcr.io/PROJECT_ID/skillscope-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Azure Deployment

### Azure Container Instances

#### Setup

1. **Create Resource Group**
```bash
az group create --name skillscope-rg --location eastus
```

2. **Create Service Principal**
```bash
az ad sp create-for-rbac --name skillscope-deployer \
  --role contributor \
  --scopes /subscriptions/SUBSCRIPTION_ID/resourceGroups/skillscope-rg \
  --sdk-auth
```

3. **Configure GitHub Secrets**
```bash
# Add to GitHub repository secrets:
AZURE_CREDENTIALS  # Output from previous command
```

4. **Deploy**

Uncomment Azure section in `.github/workflows/deploy.yml`

### Azure App Service

```bash
# Create App Service plan
az appservice plan create \
  --name skillscope-plan \
  --resource-group skillscope-rg \
  --is-linux \
  --sku B1

# Create web app
az webapp create \
  --resource-group skillscope-rg \
  --plan skillscope-plan \
  --name skillscope-api \
  --deployment-container-image-name skillscope-api:latest
```

## DigitalOcean

### App Platform

#### Setup

1. **Install doctl**
```bash
# macOS
brew install doctl

# Linux
snap install doctl
```

2. **Authenticate**
```bash
doctl auth init
```

3. **Create App**

Create `app.yaml`:
```yaml
name: skillscope-api
services:
- name: api
  github:
    repo: your-username/skillscope
    branch: main
    deploy_on_push: true
  dockerfile_path: Dockerfile
  http_port: 8000
  instance_count: 1
  instance_size_slug: basic-xxs
  routes:
  - path: /
```

4. **Deploy**
```bash
doctl apps create --spec app.yaml
```

## Environment Variables

### Required Variables

```bash
# Application
ENVIRONMENT=production
LOG_LEVEL=info

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Database (if using)
DB_HOST=your-db-host
DB_PORT=5432
DB_NAME=skillscope
DB_USER=skillscope_user
DB_PASSWORD=secure_password

# Storage
DATA_DIR=/app/data
```

### Setting in GitHub Actions

```yaml
env:
  ENVIRONMENT: production
  LOG_LEVEL: info
```

### Setting in Cloud Platforms

**AWS ECS:**
```json
"environment": [
  {"name": "ENVIRONMENT", "value": "production"}
]
```

**GCP Cloud Run:**
```bash
gcloud run deploy skillscope-api \
  --set-env-vars ENVIRONMENT=production,LOG_LEVEL=info
```

**Azure:**
```bash
az webapp config appsettings set \
  --resource-group skillscope-rg \
  --name skillscope-api \
  --settings ENVIRONMENT=production LOG_LEVEL=info
```

## GitHub Actions Setup

### 1. Enable GitHub Actions

Repository → Settings → Actions → Allow all actions

### 2. Configure Secrets

Repository → Settings → Secrets and variables → Actions → New repository secret

Required secrets depend on your cloud provider (see sections above).

### 3. Workflow Files

Located in `.github/workflows/`:
- `ci.yml` - Runs on PRs (tests, linting)
- `deploy.yml` - Deploys on push to main
- `package-extension.yml` - Packages Chrome extension on tags

### 4. Trigger Deployment

```bash
# Push to main branch
git push origin main

# Or manually trigger
# GitHub → Actions → Deploy → Run workflow
```

## Custom Domain Setup

### Cloud Run (GCP)

```bash
# Map domain
gcloud run domain-mappings create \
  --service skillscope-api \
  --domain api.skillscope.app \
  --region us-central1
```

### AWS ECS with ALB

1. Create Application Load Balancer
2. Configure target group
3. Add HTTPS listener with SSL certificate
4. Update Route 53 DNS records

### Azure App Service

```bash
az webapp config hostname add \
  --webapp-name skillscope-api \
  --resource-group skillscope-rg \
  --hostname api.skillscope.app
```

## SSL/HTTPS Setup

All modern cloud platforms provide free SSL certificates:

- **AWS**: AWS Certificate Manager
- **GCP**: Managed SSL certificates
- **Azure**: App Service Managed Certificates
- **DigitalOcean**: Free Let's Encrypt certificates

## Monitoring & Logging

### AWS CloudWatch

```bash
# View logs
aws logs tail /ecs/skillscope-api --follow
```

### GCP Cloud Logging

```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

### Azure Monitor

```bash
# Stream logs
az webapp log tail --name skillscope-api --resource-group skillscope-rg
```

## Scaling

### Auto-scaling Configuration

**Cloud Run (GCP):**
```bash
gcloud run services update skillscope-api \
  --min-instances 0 \
  --max-instances 10
```

**ECS (AWS):**
Configure auto-scaling in ECS service settings

**Azure:**
```bash
az appservice plan update \
  --name skillscope-plan \
  --resource-group skillscope-rg \
  --number-of-workers 3
```

## Cost Optimization

- **Use free tiers**: Most providers offer free tiers
- **Auto-scaling**: Scale down during low traffic
- **Reserved instances**: For consistent traffic
- **Spot instances**: For batch jobs
- **CDN**: Cache static assets

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs CONTAINER_ID

# Test locally
docker run -it --rm skillscope-api sh
```

### Health Check Failing

```bash
# Test health endpoint
curl -v http://YOUR_URL/health

# Check container logs
```

### Database Connection Issues

- Verify connection string
- Check security group/firewall rules
- Test from container: `docker exec -it CONTAINER ping DB_HOST`

## Next Steps

1. Set up monitoring and alerts
2. Configure backup strategy
3. Implement CI/CD best practices
4. Set up staging environment
5. Configure CDN for static assets
6. Implement rate limiting
7. Set up error tracking (Sentry, Rollbar)

## Support

For deployment issues:
- Check GitHub Actions logs
- Review cloud provider documentation
- Open GitHub issue with deployment details
