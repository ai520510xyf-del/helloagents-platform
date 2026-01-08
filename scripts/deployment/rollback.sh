#!/bin/bash

# HelloAgents Platform - Rollback Script
# This script handles rollback to previous deployment

set -e  # Exit on error
set -o pipefail  # Exit on pipe failure

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Default values
ENVIRONMENT="${ENVIRONMENT:-staging}"
REVISION="${REVISION:-0}"  # 0 means rollback to previous, N means rollback N revisions

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

Rollback HelloAgents Platform to previous deployment

Options:
    -e, --environment ENV    Target environment (staging|production) [default: staging]
    -r, --revision REVISION  Number of revisions to rollback [default: 0 (previous)]
    -h, --help              Show this help message

Examples:
    $0 -e staging
    $0 -e production -r 2
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -r|--revision)
            REVISION="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(staging|production)$ ]]; then
    log_error "Invalid environment: $ENVIRONMENT. Must be 'staging' or 'production'"
    exit 1
fi

log_warning "Starting rollback for $ENVIRONMENT environment"

# Confirmation for production
if [ "$ENVIRONMENT" = "production" ]; then
    log_warning "⚠️  You are about to rollback PRODUCTION environment!"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        log_info "Rollback cancelled"
        exit 0
    fi
fi

# Rollback Kubernetes deployment
rollback_kubernetes() {
    log_info "Rolling back Kubernetes deployment..."

    # Set kubectl context
    kubectl config use-context "$ENVIRONMENT-cluster"

    # Rollback deployments
    if [ "$REVISION" -eq 0 ]; then
        kubectl rollout undo deployment/backend-deployment -n $ENVIRONMENT
        kubectl rollout undo deployment/frontend-deployment -n $ENVIRONMENT
    else
        kubectl rollout undo deployment/backend-deployment --to-revision=$REVISION -n $ENVIRONMENT
        kubectl rollout undo deployment/frontend-deployment --to-revision=$REVISION -n $ENVIRONMENT
    fi

    # Wait for rollback to complete
    log_info "Waiting for rollback to complete..."
    kubectl rollout status deployment/backend-deployment -n $ENVIRONMENT
    kubectl rollout status deployment/frontend-deployment -n $ENVIRONMENT

    log_info "Kubernetes rollback completed"
}

# Rollback ECS deployment
rollback_ecs() {
    log_info "Rolling back AWS ECS deployment..."

    # Get previous task definition
    BACKEND_TASK_DEF=$(aws ecs describe-services \
        --cluster helloagents-$ENVIRONMENT \
        --services backend-service \
        --region us-east-1 \
        --query 'services[0].taskDefinition' \
        --output text)

    FRONTEND_TASK_DEF=$(aws ecs describe-services \
        --cluster helloagents-$ENVIRONMENT \
        --services frontend-service \
        --region us-east-1 \
        --query 'services[0].taskDefinition' \
        --output text)

    log_info "Current task definitions:"
    log_info "  Backend: $BACKEND_TASK_DEF"
    log_info "  Frontend: $FRONTEND_TASK_DEF"

    # Trigger rollback by forcing new deployment
    aws ecs update-service \
        --cluster helloagents-$ENVIRONMENT \
        --service backend-service \
        --force-new-deployment \
        --region us-east-1

    aws ecs update-service \
        --cluster helloagents-$ENVIRONMENT \
        --service frontend-service \
        --force-new-deployment \
        --region us-east-1

    # Wait for services to stabilize
    log_info "Waiting for services to stabilize..."
    aws ecs wait services-stable \
        --cluster helloagents-$ENVIRONMENT \
        --services backend-service frontend-service \
        --region us-east-1

    log_info "ECS rollback completed"
}

# Verify rollback
verify_rollback() {
    log_info "Verifying rollback..."

    if [ "$ENVIRONMENT" = "staging" ]; then
        BACKEND_URL="https://staging-api.helloagents.com"
        FRONTEND_URL="https://staging.helloagents.com"
    else
        BACKEND_URL="https://api.helloagents.com"
        FRONTEND_URL="https://helloagents.com"
    fi

    # Test backend health
    if curl -f -s "$BACKEND_URL/health" > /dev/null; then
        log_info "Backend health check: PASSED"
    else
        log_error "Backend health check: FAILED"
        return 1
    fi

    # Test frontend
    if curl -f -s "$FRONTEND_URL" > /dev/null; then
        log_info "Frontend health check: PASSED"
    else
        log_error "Frontend health check: FAILED"
        return 1
    fi

    log_info "Rollback verification passed"
}

# Main rollback flow
main() {
    # Rollback based on orchestration platform
    if kubectl cluster-info &> /dev/null; then
        rollback_kubernetes
    else
        rollback_ecs
    fi

    # Verify rollback
    if ! verify_rollback; then
        log_error "Rollback verification failed. Manual intervention required!"
        exit 1
    fi

    log_info "✅ Rollback to previous version completed successfully!"
}

# Run main function
main
