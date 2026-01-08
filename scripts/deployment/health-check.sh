#!/bin/bash

# HelloAgents Platform - Health Check Script
# This script performs comprehensive health checks

set -e  # Exit on error
set -o pipefail  # Exit on pipe failure

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="${ENVIRONMENT:-staging}"

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

Perform health checks on HelloAgents Platform

Options:
    -e, --environment ENV    Target environment (staging|production) [default: staging]
    -h, --help              Show this help message

Examples:
    $0 -e staging
    $0 -e production
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
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

log_info "Starting health checks for $ENVIRONMENT environment"

# Set URLs based on environment
if [ "$ENVIRONMENT" = "staging" ]; then
    BACKEND_URL="https://staging-api.helloagents.com"
    FRONTEND_URL="https://staging.helloagents.com"
else
    BACKEND_URL="https://api.helloagents.com"
    FRONTEND_URL="https://helloagents.com"
fi

# Backend health check
check_backend_health() {
    log_info "Checking backend health..."

    # Basic health endpoint
    if response=$(curl -s -w "\n%{http_code}" "$BACKEND_URL/health"); then
        status_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | head -n-1)

        if [ "$status_code" -eq 200 ]; then
            log_info "✅ Backend health check: PASSED (HTTP $status_code)"
            echo "Response: $body"
        else
            log_error "❌ Backend health check: FAILED (HTTP $status_code)"
            return 1
        fi
    else
        log_error "❌ Backend health check: CONNECTION FAILED"
        return 1
    fi

    # Database health check
    if response=$(curl -s -w "\n%{http_code}" "$BACKEND_URL/health/db"); then
        status_code=$(echo "$response" | tail -n1)
        if [ "$status_code" -eq 200 ]; then
            log_info "✅ Database health check: PASSED"
        else
            log_warning "⚠️  Database health check: FAILED (HTTP $status_code)"
        fi
    fi
}

# Frontend health check
check_frontend_health() {
    log_info "Checking frontend health..."

    if response=$(curl -s -w "\n%{http_code}" "$FRONTEND_URL"); then
        status_code=$(echo "$response" | tail -n1)

        if [ "$status_code" -eq 200 ]; then
            log_info "✅ Frontend health check: PASSED (HTTP $status_code)"
        else
            log_error "❌ Frontend health check: FAILED (HTTP $status_code)"
            return 1
        fi
    else
        log_error "❌ Frontend health check: CONNECTION FAILED"
        return 1
    fi
}

# API response time check
check_response_time() {
    log_info "Checking API response time..."

    response_time=$(curl -o /dev/null -s -w '%{time_total}\n' "$BACKEND_URL/health")
    response_time_ms=$(echo "$response_time * 1000" | bc)

    log_info "Response time: ${response_time_ms}ms"

    if (( $(echo "$response_time > 2.0" | bc -l) )); then
        log_warning "⚠️  High response time detected"
    else
        log_info "✅ Response time is acceptable"
    fi
}

# SSL certificate check
check_ssl_certificate() {
    log_info "Checking SSL certificate..."

    if [ "$ENVIRONMENT" = "production" ]; then
        expiry_date=$(echo | openssl s_client -servername helloagents.com -connect helloagents.com:443 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)

        if [ -n "$expiry_date" ]; then
            expiry_epoch=$(date -j -f "%b %d %H:%M:%S %Y %Z" "$expiry_date" "+%s" 2>/dev/null || date -d "$expiry_date" "+%s" 2>/dev/null)
            current_epoch=$(date "+%s")
            days_until_expiry=$(( ($expiry_epoch - $current_epoch) / 86400 ))

            log_info "SSL certificate expires in $days_until_expiry days"

            if [ $days_until_expiry -lt 30 ]; then
                log_warning "⚠️  SSL certificate expires soon!"
            else
                log_info "✅ SSL certificate is valid"
            fi
        fi
    fi
}

# Container/Pod status check
check_container_status() {
    log_info "Checking container/pod status..."

    if kubectl cluster-info &> /dev/null; then
        # Kubernetes environment
        kubectl config use-context "$ENVIRONMENT-cluster" 2>/dev/null || true

        # Check pod status
        pods=$(kubectl get pods -n $ENVIRONMENT -o json 2>/dev/null)
        if [ -n "$pods" ]; then
            running_pods=$(echo "$pods" | grep -c '"phase":"Running"' || true)
            log_info "Running pods: $running_pods"

            # Check for failed pods
            failed_pods=$(echo "$pods" | grep -c '"phase":"Failed"' || true)
            if [ "$failed_pods" -gt 0 ]; then
                log_warning "⚠️  Found $failed_pods failed pods"
            fi
        fi
    else
        log_info "Not in a Kubernetes environment, skipping pod checks"
    fi
}

# Generate health report
generate_report() {
    log_info "Generating health report..."

    cat > health-report-$ENVIRONMENT-$(date +%Y%m%d_%H%M%S).txt <<EOF
HelloAgents Platform Health Report
Environment: $ENVIRONMENT
Generated at: $(date)

Backend URL: $BACKEND_URL
Frontend URL: $FRONTEND_URL

Health Checks:
- Backend: $1
- Frontend: $2
- Response Time: $3
- SSL Certificate: $4
- Container Status: $5

EOF

    log_info "Health report saved"
}

# Main health check flow
main() {
    local backend_status="UNKNOWN"
    local frontend_status="UNKNOWN"
    local response_time_status="UNKNOWN"
    local ssl_status="UNKNOWN"
    local container_status="UNKNOWN"

    # Run all checks
    if check_backend_health; then
        backend_status="PASSED"
    else
        backend_status="FAILED"
    fi

    if check_frontend_health; then
        frontend_status="PASSED"
    else
        frontend_status="FAILED"
    fi

    check_response_time
    response_time_status="CHECKED"

    if [ "$ENVIRONMENT" = "production" ]; then
        check_ssl_certificate
        ssl_status="CHECKED"
    else
        ssl_status="SKIPPED"
    fi

    check_container_status
    container_status="CHECKED"

    # Generate report
    generate_report "$backend_status" "$frontend_status" "$response_time_status" "$ssl_status" "$container_status"

    # Overall status
    if [ "$backend_status" = "PASSED" ] && [ "$frontend_status" = "PASSED" ]; then
        log_info "🎉 All critical health checks passed!"
        exit 0
    else
        log_error "❌ Some health checks failed!"
        exit 1
    fi
}

# Run main function
main
