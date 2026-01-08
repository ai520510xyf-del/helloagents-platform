# Deployment Checklist

## Pre-Deployment Checklist

### Code Quality

- [ ] All tests passing locally
- [ ] Code coverage meets threshold (≥75%)
- [ ] Linting and formatting checks pass
- [ ] No console.log or debug statements in production code
- [ ] Code reviewed and approved
- [ ] All merge conflicts resolved

### Configuration

- [ ] Environment variables configured (see [ENVIRONMENT_SETUP.md](./ENVIRONMENT_SETUP.md))
  - [ ] Copy `.env.example` to `.env`
  - [ ] Set `ANTHROPIC_API_KEY` (required)
  - [ ] Set `POSTGRES_PASSWORD` (required, minimum 12 chars)
  - [ ] Set optional API keys if needed
  - [ ] Run `./scripts/check-env.sh` to validate
- [ ] Secrets updated in GitHub Secrets
- [ ] Database migrations prepared (if any)
- [ ] API versions updated (if changed)
- [ ] Feature flags configured
- [ ] CORS settings verified

### Testing

- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Performance tests completed
- [ ] Security scan passed
- [ ] Load testing completed (for major changes)

### Documentation

- [ ] README updated
- [ ] API documentation updated
- [ ] CHANGELOG updated
- [ ] Version number bumped
- [ ] Migration guide created (if breaking changes)

### Dependencies

- [ ] Dependencies updated and audited
- [ ] Security vulnerabilities addressed
- [ ] License compliance verified
- [ ] Package lock files committed

## Deployment Checklist

### Staging Deployment

- [ ] Create deployment tag (`v*.*.*`)
- [ ] Verify CI pipeline passes
- [ ] Monitor Docker image build
- [ ] Check security scan results
- [ ] Verify automatic deployment to staging
- [ ] Run smoke tests
- [ ] Check application logs
- [ ] Verify all features working
- [ ] Test critical user flows
- [ ] Performance monitoring review

### Production Deployment

#### Before Deployment

- [ ] Staging deployment successful
- [ ] Stakeholder approval obtained
- [ ] Deployment window scheduled
- [ ] Rollback plan prepared
- [ ] Team notified of deployment
- [ ] On-call engineer identified
- [ ] Customer notification prepared (if needed)
- [ ] Maintenance mode page ready (if needed)

#### During Deployment

- [ ] Start deployment workflow
- [ ] Monitor deployment progress
- [ ] Watch for errors in logs
- [ ] Verify health checks passing
- [ ] Monitor error rates
- [ ] Check response times
- [ ] Verify database connectivity
- [ ] Test critical endpoints

#### After Deployment

- [ ] All health checks passing
- [ ] Smoke tests successful
- [ ] No error rate spikes
- [ ] Performance metrics normal
- [ ] Database queries performing well
- [ ] External integrations working
- [ ] User acceptance testing completed
- [ ] Team notified of successful deployment
- [ ] Customer notification sent (if applicable)
- [ ] Deployment documented

## Post-Deployment Checklist

### Monitoring (First 1 Hour)

- [ ] Monitor application logs
- [ ] Check error tracking (Sentry)
- [ ] Monitor response times
- [ ] Check database performance
- [ ] Monitor CPU and memory usage
- [ ] Verify cron jobs running
- [ ] Check background task queues

### Monitoring (First 24 Hours)

- [ ] Review application metrics
- [ ] Check user feedback
- [ ] Monitor error trends
- [ ] Review performance metrics
- [ ] Check for unexpected behavior
- [ ] Verify scheduled tasks executed
- [ ] Monitor API usage patterns

### Verification

- [ ] All critical features working
- [ ] No new errors or warnings
- [ ] Performance within acceptable range
- [ ] User reports reviewed
- [ ] Analytics data flowing
- [ ] Third-party integrations stable

### Documentation

- [ ] Update deployment log
- [ ] Document any issues encountered
- [ ] Update runbooks if needed
- [ ] Share deployment summary with team
- [ ] Update project status

## Rollback Checklist

### When to Rollback

Rollback immediately if:
- [ ] Critical features not working
- [ ] Error rate > 5%
- [ ] Response time > 2x baseline
- [ ] Database connectivity issues
- [ ] Security vulnerability discovered
- [ ] Data corruption detected

### Rollback Procedure

- [ ] Notify team of rollback
- [ ] Execute rollback script or workflow
- [ ] Verify rollback completion
- [ ] Run health checks
- [ ] Monitor error rates
- [ ] Verify critical features working
- [ ] Document rollback reason
- [ ] Create incident report
- [ ] Schedule post-mortem

## Environment-Specific Checks

### Staging Environment

- [ ] Database seeded with test data
- [ ] Test API keys configured
- [ ] Feature flags enabled appropriately
- [ ] Logging level set to DEBUG
- [ ] Performance monitoring enabled
- [ ] Test user accounts created

### Production Environment

- [ ] Production API keys configured
- [ ] Feature flags configured
- [ ] Logging level set to INFO/WARNING
- [ ] Performance monitoring enabled
- [ ] Backup systems verified
- [ ] SSL certificates valid
- [ ] CDN cache invalidated (if needed)
- [ ] Database backups recent

## Emergency Contacts

### On-Call Roster

- Primary: [Name] - [Contact]
- Secondary: [Name] - [Contact]
- Escalation: [Name] - [Contact]

### Vendor Contacts

- AWS Support: [Support Link]
- Database Provider: [Support Link]
- CDN Provider: [Support Link]

## Quick Commands

### Deployment

```bash
# Deploy to staging
./scripts/deployment/deploy.sh -e staging -v v1.0.0

# Deploy to production
./scripts/deployment/deploy.sh -e production -v v1.0.0
```

### Health Checks

```bash
# Run health check
./scripts/deployment/health-check.sh -e production

# Check specific service
curl https://api.helloagents.com/health
```

### Rollback

```bash
# Rollback production
./scripts/deployment/rollback.sh -e production

# Rollback to specific version
./scripts/deployment/rollback.sh -e production -r 2
```

### Logs

```bash
# View backend logs
kubectl logs -f deployment/backend-deployment -n production

# View frontend logs
kubectl logs -f deployment/frontend-deployment -n production

# View all logs
kubectl logs -f -l app=helloagents -n production
```

## Notes

- Always deploy to staging first
- Never deploy on Fridays or before holidays
- Keep deployment windows short (< 30 minutes)
- Have rollback plan ready
- Monitor for at least 1 hour after deployment
- Document all issues and learnings

---

**Last Updated**: 2026-01-08
**Version**: 1.0.0
