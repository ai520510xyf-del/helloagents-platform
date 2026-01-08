# CI/CD Pipeline Guide

## Overview

This guide documents the complete CI/CD pipeline setup for the HelloAgents Platform, including GitHub Actions workflows, Docker configurations, and deployment procedures.

## Table of Contents

- [Architecture](#architecture)
- [GitHub Actions Workflows](#github-actions-workflows)
- [Docker Configuration](#docker-configuration)
- [Deployment Process](#deployment-process)
- [Environment Management](#environment-management)
- [Rollback Procedures](#rollback-procedures)
- [Monitoring and Health Checks](#monitoring-and-health-checks)
- [Best Practices](#best-practices)

## Architecture

### CI/CD Pipeline Flow

```
Code Push → CI Tests → Docker Build → Security Scan → Deploy → Health Check
     ↓          ↓            ↓              ↓            ↓           ↓
  GitHub    Test.yml   docker-build.yml   Trivy     deploy.yml   Smoke Tests
```

### Environments

- **Development**: Local development with Docker Compose
- **Staging**: Pre-production testing environment
- **Production**: Live production environment

## GitHub Actions Workflows

### 1. CI Workflow (`.github/workflows/ci.yml`)

Triggers on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

Jobs:
- **backend-tests**: Runs Python tests with coverage
- **frontend-lint**: ESLint checks
- **frontend-tests**: React/Vite tests with coverage
- **frontend-build**: Production build verification
- **test-summary**: Aggregated test results

### 2. Docker Build Workflow (`.github/workflows/docker-build.yml`)

Triggers on:
- Tags matching `v*.*.*`
- Manual workflow dispatch

Jobs:
- **build-backend**: Build and push backend Docker image
- **build-frontend**: Build and push frontend Docker image
- **security-scan**: Trivy vulnerability scanning
- **build-summary**: Build status report

Features:
- Multi-architecture builds (amd64, arm64)
- GitHub Container Registry (ghcr.io)
- Build cache optimization
- SBOM generation

### 3. Deploy Workflow (`.github/workflows/deploy.yml`)

Triggers on:
- Successful Docker build completion
- Manual workflow dispatch

Jobs:
- **deploy-staging**: Deploy to staging environment
- **deploy-production**: Deploy to production (manual approval)
- **post-deployment-tests**: Integration and E2E tests

Features:
- Blue/Green deployment strategy
- Automatic rollback on failure
- Health checks and smoke tests
- ECS and Kubernetes support

## Docker Configuration

### Backend Dockerfile

**Location**: `backend/Dockerfile`

**Features**:
- Multi-stage build (builder + production)
- Python 3.11 slim base image
- Virtual environment isolation
- Non-root user execution
- Health check included
- Optimized layer caching

**Build Command**:
```bash
docker build -t helloagents-backend:latest ./backend
```

**Image Size Optimization**:
- Stage 1 (Builder): ~500MB
- Stage 2 (Production): ~200MB
- Final image: ~200MB

### Frontend Dockerfile

**Location**: `frontend/Dockerfile`

**Features**:
- Multi-stage build (builder + nginx)
- Node 18 Alpine for building
- Nginx Alpine for serving
- Custom nginx configuration
- Non-root user execution
- Gzip compression enabled

**Build Command**:
```bash
docker build -t helloagents-frontend:latest ./frontend
```

**Image Size Optimization**:
- Stage 1 (Builder): ~800MB
- Stage 2 (Nginx): ~50MB
- Final image: ~50MB

### .dockerignore Files

Both backend and frontend have `.dockerignore` files to exclude:
- Development dependencies
- Test files and coverage reports
- Git metadata
- IDE configurations
- Documentation
- Temporary files

**Benefits**:
- Faster build times
- Smaller context size
- Improved security (no secrets)

## Docker Compose Configuration

### Production Setup (`docker-compose.yml`)

Services:
- **backend**: FastAPI application (port 8000)
- **frontend**: Nginx with React app (port 80)
- **postgres**: PostgreSQL 16 database (port 5432)
- **redis**: Redis 7 cache (port 6379)
- **nginx**: Reverse proxy (port 8080, optional)

Usage:
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Start with nginx proxy
docker-compose --profile production up -d
```

### Development Setup (`docker-compose.dev.yml`)

Features:
- Hot reload enabled
- Volume mounts for live code changes
- Debug mode enabled
- Development ports exposed

Usage:
```bash
# Start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Frontend only (Vite dev server)
docker-compose -f docker-compose.dev.yml up frontend
```

## Deployment Process

### Automated Deployment

#### Staging Deployment

1. Push code to `main` or `develop`
2. CI tests run automatically
3. On tag push (`v*.*.*`), Docker images are built
4. Images are scanned for vulnerabilities
5. Automatic deployment to staging
6. Smoke tests run
7. Notification sent

#### Production Deployment

1. Manual approval required
2. Create backup of current deployment
3. Blue/Green deployment strategy
4. Health checks during rollout
5. Post-deployment verification
6. Automatic rollback on failure

### Manual Deployment

Using deployment script:

```bash
# Deploy to staging
./scripts/deployment/deploy.sh -e staging -v v1.0.0

# Deploy to production
./scripts/deployment/deploy.sh -e production -v v1.0.0
```

### Deployment Scripts

#### 1. Deploy Script (`scripts/deployment/deploy.sh`)

Features:
- Environment validation
- Prerequisites checking
- Backup creation
- Kubernetes and ECS support
- Smoke tests
- Automatic rollback

Options:
```bash
-e, --environment ENV    Target environment (staging|production)
-v, --version VERSION    Docker image version
-r, --registry REGISTRY  Container registry
-n, --namespace NS       Namespace/repository
```

#### 2. Rollback Script (`scripts/deployment/rollback.sh`)

Features:
- Rollback to previous deployment
- Revision-based rollback
- Health verification
- Production confirmation

Options:
```bash
-e, --environment ENV    Target environment
-r, --revision REVISION  Number of revisions to rollback
```

Usage:
```bash
# Rollback to previous version
./scripts/deployment/rollback.sh -e production

# Rollback to specific revision
./scripts/deployment/rollback.sh -e production -r 2
```

#### 3. Health Check Script (`scripts/deployment/health-check.sh`)

Features:
- Backend health check
- Frontend availability check
- Database connectivity check
- Response time monitoring
- SSL certificate validation
- Container/Pod status check
- Health report generation

Usage:
```bash
# Check staging health
./scripts/deployment/health-check.sh -e staging

# Check production health
./scripts/deployment/health-check.sh -e production
```

## Environment Management

### Environment Variables

#### Backend Environment Variables

Required:
- `ANTHROPIC_API_KEY`: Anthropic API key
- `OPENAI_API_KEY`: OpenAI API key
- `DATABASE_URL`: Database connection string

Optional:
- `ENVIRONMENT`: Environment name (development|staging|production)
- `LOG_LEVEL`: Logging level (DEBUG|INFO|WARNING|ERROR)
- `CORS_ORIGINS`: Allowed CORS origins

#### Frontend Environment Variables

Required:
- `VITE_API_URL`: Backend API URL

Optional:
- `VITE_WS_URL`: WebSocket URL

### Secrets Management

GitHub Secrets required:
- `DOCKERHUB_USERNAME`: Docker Hub username
- `DOCKERHUB_TOKEN`: Docker Hub access token
- `CODECOV_TOKEN`: Codecov upload token
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_REGION`: AWS region

Kubernetes Secrets:
```bash
# Create secret
kubectl create secret generic app-secrets \
  --from-literal=database-url=postgresql://... \
  --from-literal=anthropic-api-key=... \
  -n production
```

## Rollback Procedures

### Automatic Rollback

Triggers:
- Deployment failure
- Health check failure
- High error rate detection

Process:
1. Detect failure condition
2. Log rollback initiation
3. Revert to previous deployment
4. Verify health checks
5. Send notification

### Manual Rollback

Using rollback script:
```bash
# Quick rollback (to previous version)
./scripts/deployment/rollback.sh -e production

# Rollback to specific revision
kubectl rollout history deployment/backend-deployment -n production
./scripts/deployment/rollback.sh -e production -r 3
```

Using kubectl:
```bash
# View rollout history
kubectl rollout history deployment/backend-deployment -n production

# Rollback to previous
kubectl rollout undo deployment/backend-deployment -n production

# Rollback to specific revision
kubectl rollout undo deployment/backend-deployment --to-revision=2 -n production
```

## Monitoring and Health Checks

### Health Check Endpoints

Backend:
- `/health`: Basic health check
- `/health/db`: Database connectivity check

Frontend:
- `/health`: Nginx health check

### Monitoring Metrics

Key metrics to monitor:
- Deployment success rate
- Rollback frequency
- Response time
- Error rate
- Container restart count
- Resource utilization

### Alerting

Configure alerts for:
- Deployment failures
- Health check failures
- High error rates
- SSL certificate expiry
- Resource exhaustion

## Best Practices

### Docker Best Practices

1. **Use Multi-stage Builds**: Reduce final image size
2. **Run as Non-root User**: Improve security
3. **Use Specific Tags**: Avoid `latest` in production
4. **Optimize Layer Caching**: Order Dockerfile commands appropriately
5. **Use .dockerignore**: Exclude unnecessary files

### CI/CD Best Practices

1. **Run Tests in Parallel**: Faster CI pipeline
2. **Cache Dependencies**: Speed up builds
3. **Use Concurrency Control**: Cancel outdated workflows
4. **Set Timeout Limits**: Prevent hanging jobs
5. **Generate Artifacts**: Save build outputs and reports

### Deployment Best Practices

1. **Blue/Green Deployment**: Zero-downtime deployments
2. **Canary Releases**: Gradual rollout to production
3. **Automated Rollback**: Quick recovery from failures
4. **Health Checks**: Verify deployment success
5. **Backup Before Deploy**: Enable quick rollback

### Security Best Practices

1. **Scan Images**: Use Trivy for vulnerability scanning
2. **Use Secrets Management**: Never hardcode secrets
3. **Least Privilege**: Minimal container permissions
4. **Network Policies**: Restrict inter-service communication
5. **Regular Updates**: Keep base images and dependencies updated

## Troubleshooting

### Common Issues

#### 1. Docker Build Fails

**Symptoms**: Build fails with dependency errors

**Solution**:
```bash
# Clear Docker build cache
docker builder prune -a

# Rebuild without cache
docker build --no-cache -t helloagents-backend:latest ./backend
```

#### 2. Deployment Timeout

**Symptoms**: Deployment exceeds time limit

**Solution**:
- Check pod/container logs
- Verify resource limits
- Check health check endpoints
- Review application startup time

#### 3. Health Check Failures

**Symptoms**: Health checks fail after deployment

**Solution**:
```bash
# Check service status
kubectl get pods -n production

# View logs
kubectl logs -f deployment/backend-deployment -n production

# Describe pod for events
kubectl describe pod <pod-name> -n production
```

#### 4. Image Pull Errors

**Symptoms**: Cannot pull Docker images

**Solution**:
- Verify registry credentials
- Check image tag exists
- Verify network connectivity
- Check registry permissions

## Performance Metrics

### Build Performance

- Backend Docker build: ~3-5 minutes
- Frontend Docker build: ~5-7 minutes
- CI test suite: ~5-10 minutes
- Total pipeline time: ~15-20 minutes

### Deployment Performance

- Staging deployment: ~5 minutes
- Production deployment: ~10-15 minutes (with checks)
- Rollback time: ~2-3 minutes

## Continuous Improvement

### Regular Tasks

- Review and optimize Dockerfiles (monthly)
- Update base images (monthly)
- Review and update dependencies (bi-weekly)
- Analyze build performance (weekly)
- Review deployment metrics (weekly)
- Update documentation (as needed)

### Future Enhancements

- [ ] Implement canary deployments
- [ ] Add A/B testing support
- [ ] Enhance monitoring and alerting
- [ ] Add performance testing in CI
- [ ] Implement feature flags
- [ ] Add cost optimization analysis

## Support and Resources

### Documentation

- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)

### Team Contacts

- DevOps Lead: devops@helloagents.com
- On-call Support: oncall@helloagents.com

---

**Last Updated**: 2026-01-08
**Maintained by**: DevOps Team
