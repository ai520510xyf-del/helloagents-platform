#!/bin/bash
# HelloAgents Platform - PostgreSQL Backup Script
# Description: Automated backup with S3 sync and retention management
# Author: DB Architect
# Version: 1.0.0

set -e
set -u

# ====================================
# Configuration
# ====================================

# PostgreSQL Configuration
PG_HOST="${PG_HOST:-localhost}"
PG_PORT="${PG_PORT:-5432}"
PG_DB="${PG_DB:-helloagents_prod}"
PG_USER="${PG_USER:-helloagents_user}"
PG_PASSWORD="${PG_PASSWORD:-}"

# Backup Configuration
BACKUP_DIR="${BACKUP_DIR:-/var/backups/postgresql}"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/$DATE"
RETENTION_DAYS="${RETENTION_DAYS:-30}"

# S3 Configuration (optional)
S3_BUCKET="${S3_BUCKET:-}"
ENABLE_S3_SYNC="${ENABLE_S3_SYNC:-false}"

# Notification Configuration (optional)
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"
EMAIL_TO="${EMAIL_TO:-}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ====================================
# Functions
# ====================================

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

send_notification() {
    local status=$1
    local message=$2

    # Slack notification
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -X POST "$SLACK_WEBHOOK" \
            -H 'Content-Type: application/json' \
            -d "{\"text\":\"[$status] HelloAgents DB Backup\n$message\"}" \
            &>/dev/null || true
    fi

    # Email notification (requires mailx)
    if [ -n "$EMAIL_TO" ] && command -v mailx &> /dev/null; then
        echo "$message" | mailx -s "[$status] HelloAgents DB Backup" "$EMAIL_TO" || true
    fi
}

check_prerequisites() {
    log "Checking prerequisites..."

    # Check pg_dump
    if ! command -v pg_dump &> /dev/null; then
        log_error "pg_dump not found. Please install PostgreSQL client."
        exit 1
    fi

    # Check PostgreSQL password
    if [ -z "$PG_PASSWORD" ]; then
        log_error "PG_PASSWORD environment variable not set"
        exit 1
    fi

    # Create backup directory
    mkdir -p "$BACKUP_PATH"

    log_success "Prerequisites check passed"
}

test_connection() {
    log "Testing PostgreSQL connection..."

    export PGPASSWORD="$PG_PASSWORD"
    if psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -c '\q' 2>/dev/null; then
        log_success "Connection successful"
    else
        log_error "Cannot connect to PostgreSQL"
        send_notification "FAILED" "Cannot connect to PostgreSQL at $PG_HOST:$PG_PORT"
        exit 1
    fi
}

backup_custom_format() {
    log "Creating custom format backup (optimized for restore)..."

    export PGPASSWORD="$PG_PASSWORD"
    pg_dump -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" \
        -Fc \
        -Z 9 \
        -f "$BACKUP_PATH/full_backup.dump" \
        2>&1 | grep -v "^pg_dump: warning:" || true

    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        local size=$(du -h "$BACKUP_PATH/full_backup.dump" | cut -f1)
        log_success "Custom format backup created: $size"
    else
        log_error "Failed to create custom format backup"
        exit 1
    fi
}

backup_sql_format() {
    log "Creating SQL format backup (human-readable)..."

    export PGPASSWORD="$PG_PASSWORD"
    pg_dump -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" \
        --clean --if-exists \
        -f "$BACKUP_PATH/schema_and_data.sql" \
        2>&1 | grep -v "^pg_dump: warning:" || true

    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        gzip "$BACKUP_PATH/schema_and_data.sql"
        local size=$(du -h "$BACKUP_PATH/schema_and_data.sql.gz" | cut -f1)
        log_success "SQL format backup created: $size"
    else
        log_error "Failed to create SQL format backup"
        exit 1
    fi
}

backup_schema_only() {
    log "Creating schema-only backup..."

    export PGPASSWORD="$PG_PASSWORD"
    pg_dump -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" \
        --schema-only \
        -f "$BACKUP_PATH/schema_only.sql" \
        2>&1 | grep -v "^pg_dump: warning:" || true

    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log_success "Schema-only backup created"
    else
        log_warning "Failed to create schema-only backup (non-critical)"
    fi
}

export_statistics() {
    log "Exporting database statistics..."

    export PGPASSWORD="$PG_PASSWORD"
    psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" <<EOF > "$BACKUP_PATH/stats.txt"
-- Table row counts
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL SELECT 'lessons', COUNT(*) FROM lessons
UNION ALL SELECT 'user_progress', COUNT(*) FROM user_progress
UNION ALL SELECT 'code_submissions', COUNT(*) FROM code_submissions
UNION ALL SELECT 'chat_messages', COUNT(*) FROM chat_messages;

-- Database size
SELECT pg_size_pretty(pg_database_size('$PG_DB')) as database_size;

-- Table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as indexes_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Connection stats
SELECT
    state,
    COUNT(*) as connections
FROM pg_stat_activity
WHERE datname = '$PG_DB'
GROUP BY state;

-- Slow queries (top 10)
SELECT
    substring(query, 1, 100) as query_preview,
    calls,
    ROUND(total_exec_time::numeric / 1000, 2) as total_seconds,
    ROUND(mean_exec_time::numeric, 2) as avg_ms
FROM pg_stat_statements
WHERE dbid = (SELECT oid FROM pg_database WHERE datname = '$PG_DB')
ORDER BY mean_exec_time DESC
LIMIT 10;
EOF

    log_success "Statistics exported"
}

sync_to_s3() {
    if [ "$ENABLE_S3_SYNC" != "true" ]; then
        log "S3 sync disabled (set ENABLE_S3_SYNC=true to enable)"
        return 0
    fi

    if [ -z "$S3_BUCKET" ]; then
        log_warning "S3_BUCKET not set, skipping S3 sync"
        return 0
    fi

    if ! command -v aws &> /dev/null; then
        log_warning "AWS CLI not found, skipping S3 sync"
        return 0
    fi

    log "Syncing to S3: $S3_BUCKET..."

    aws s3 sync "$BACKUP_PATH" "$S3_BUCKET/postgresql/$DATE/" \
        --storage-class STANDARD_IA \
        --quiet

    if [ $? -eq 0 ]; then
        log_success "S3 sync completed"
    else
        log_warning "S3 sync failed (non-critical)"
    fi
}

cleanup_old_backups() {
    log "Cleaning up old backups (retention: $RETENTION_DAYS days)..."

    local deleted=0
    while IFS= read -r dir; do
        rm -rf "$dir"
        deleted=$((deleted + 1))
    done < <(find "$BACKUP_DIR" -type d -name "20*" -mtime +$RETENTION_DAYS 2>/dev/null)

    if [ $deleted -gt 0 ]; then
        log_success "Deleted $deleted old backup(s)"
    else
        log "No old backups to clean up"
    fi
}

generate_report() {
    log "Generating backup report..."

    local report_file="$BACKUP_PATH/BACKUP_REPORT.md"
    local duration=$(($(date +%s) - $START_TIME))

    cat > "$report_file" <<EOF
# PostgreSQL Backup Report

**Backup Date**: $(date +'%Y-%m-%d %H:%M:%S')
**Duration**: ${duration} seconds
**Status**: ✅ SUCCESS

## Database Information

- **Host**: $PG_HOST:$PG_PORT
- **Database**: $PG_DB
- **User**: $PG_USER

## Backup Files

\`\`\`
$(ls -lh "$BACKUP_PATH")
\`\`\`

## Database Statistics

\`\`\`
$(cat "$BACKUP_PATH/stats.txt")
\`\`\`

## Backup Location

- **Local**: $BACKUP_PATH
- **S3**: $S3_BUCKET/postgresql/$DATE/ (if enabled)

## Restore Instructions

### Method 1: Custom Format (Parallel Restore)

\`\`\`bash
export PGPASSWORD="your_password"
pg_restore -h localhost -p 5432 -U $PG_USER -d $PG_DB \\
    -j 4 \\
    --clean --if-exists \\
    $BACKUP_PATH/full_backup.dump
\`\`\`

### Method 2: SQL Format

\`\`\`bash
export PGPASSWORD="your_password"
gunzip -c $BACKUP_PATH/schema_and_data.sql.gz | \\
    psql -h localhost -p 5432 -U $PG_USER -d postgres
\`\`\`

---

**Next Backup**: $(date -d "+1 day" +'%Y-%m-%d 03:00:00')
EOF

    log_success "Report generated: $report_file"
}

# ====================================
# Main Backup Flow
# ====================================

main() {
    START_TIME=$(date +%s)

    echo ""
    echo "======================================"
    echo "PostgreSQL Backup Started"
    echo "======================================"
    echo ""

    # Check prerequisites
    check_prerequisites
    test_connection

    # Create backups
    backup_custom_format
    backup_sql_format
    backup_schema_only
    export_statistics

    # Sync to S3 (if enabled)
    sync_to_s3

    # Cleanup old backups
    cleanup_old_backups

    # Generate report
    generate_report

    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))

    echo ""
    echo "======================================"
    echo "✅ Backup Completed Successfully!"
    echo "======================================"
    echo "Duration: ${DURATION} seconds"
    echo "Location: $BACKUP_PATH"
    echo ""

    # Send success notification
    local backup_size=$(du -sh "$BACKUP_PATH" | cut -f1)
    send_notification "SUCCESS" "Backup completed in ${DURATION}s\nSize: $backup_size\nLocation: $BACKUP_PATH"
}

# Error handling
trap 'log_error "Backup failed at line $LINENO"; send_notification "FAILED" "Backup failed at line $LINENO"; exit 1' ERR

# Run backup
main "$@"
