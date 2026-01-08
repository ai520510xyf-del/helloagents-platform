#!/bin/bash

# HelloAgents Platform - Deployment Script
# This script handles deployment to various environments

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
VERSION="${VERSION:-latest}"
REGISTRY="${REGISTRY:-ghcr.io}"
NAMESPACE="${NAMESPACE:-helloagents}"

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

Deploy HelloAgents Platform to specified environment

Options:
    -e, --environment ENV    Target environment (staging|production) [default: staging]
    -v, --version VERSION    Docker image version [default: latest]
    -r, --registry REGISTRY  Container registry [default: ghcr.io]
    -n, --namespace NS       Namespace/repository [default: helloagents]
    -h, --help              Show this help message

Examples:
    $0 -e staging
    $0 -e production -v v1.0.0
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        -n|--namespace)
            NAMESPACE="$2"
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

log_info "Starting deployment to $ENVIRONMENT environment"
log_info "Version: $VERSION"
log_info "Registry: $REGISTRY"

# Pre-deployment checks
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if required tools are installed
    for tool in docker kubectl aws; do
        if ! command -v $tool &> /dev/null; then
            log_error "$tool is not installed. Please install it first."
            exit 1
        fi
    done

    log_info "All prerequisites met"
}

# Backup current deployment
backup_deployment() {
    log_info "Creating backup of current deployment..."

    BACKUP_DIR="$PROJECT_ROOT/backups/$ENVIRONMENT/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"

    # Save current deployment state
    kubectl get all -n $ENVIRONMENT -o yaml > "$BACKUP_DIR/deployment-state.yaml" 2>/dev/null || true

    log_info "Backup saved to: $BACKUP_DIR"
}

# Deploy to Kubernetes
deploy_to_kubernetes() {
    log_info "Deploying to Kubernetes cluster..."

    # Set kubectl context
    kubectl config use-context "$ENVIRONMENT-cluster"

    # Update image tags
    kubectl set image deployment/backend-deployment \
        backend=$REGISTRY/$NAMESPACE/backend:$VERSION \
        -n $ENVIRONMENT

    kubectl set image deployment/frontend-deployment \
        frontend=$REGISTRY/$NAMESPACE/frontend:$VERSION \
        -n $ENVIRONMENT

    # Wait for rollout to complete
    log_info "Waiting for deployment to complete..."
    kubectl rollout status deployment/backend-deployment -n $ENVIRONMENT
    kubectl rollout status deployment/frontend-deployment -n $ENVIRONMENT

    log_info "Deployment completed successfully"
}

# Deploy to AWS ECS
deploy_to_ecs() {
    log_info "Deploying to AWS ECS..."

    # Update ECS service
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

    log_info "ECS deployment completed successfully"
}

# Run smoke tests
run_smoke_tests() {
    log_info "Running smoke tests..."

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

    log_info "All smoke tests passed"
}

# Rollback deployment
rollback_deployment() {
    log_error "Deployment failed. Initiating rollback..."

    # Rollback Kubernetes deployment
    kubectl rollout undo deployment/backend-deployment -n $ENVIRONMENT
    kubectl rollout undo deployment/frontend-deployment -n $ENVIRONMENT

    log_info "Rollback completed"
}

# Main deployment flow
main() {
    check_prerequisites
    backup_deployment

    # Deploy based on orchestration platform
    if kubectl cluster-info &> /dev/null; then
        deploy_to_kubernetes
    else
        deploy_to_ecs
    fi

    # Run post-deployment tests
    if ! run_smoke_tests; then
        rollback_deployment
        exit 1
    fi

    log_info "🎉 Deployment to $ENVIRONMENT completed successfully!"
}

# Run main function
main
