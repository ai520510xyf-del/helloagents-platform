#!/bin/bash
# HelloAgents Platform - PostgreSQL Migration Script
# Description: Migrate from SQLite to PostgreSQL with zero data loss
# Author: DB Architect
# Version: 1.0.0

set -e  # Exit on error
set -u  # Exit on undefined variable

# ====================================
# Configuration
# ====================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

# SQLite Configuration
SQLITE_DB="${SQLITE_DB:-$BACKEND_DIR/helloagents.db}"

# PostgreSQL Configuration (from environment or defaults)
PG_HOST="${PG_HOST:-localhost}"
PG_PORT="${PG_PORT:-5432}"
PG_DB="${PG_DB:-helloagents_prod}"
PG_USER="${PG_USER:-helloagents_user}"
PG_PASSWORD="${PG_PASSWORD:-}"

# Backup Configuration
BACKUP_DIR="$BACKEND_DIR/backups/$(date +%Y%m%d_%H%M%S)"
CSV_DIR="$BACKUP_DIR/csv"
LOG_FILE="$BACKUP_DIR/migration.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ====================================
# Functions
# ====================================

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

check_prerequisites() {
    log "Checking prerequisites..."

    # Check SQLite
    if ! command -v sqlite3 &> /dev/null; then
        log_error "sqlite3 not found. Please install sqlite3."
        exit 1
    fi

    # Check PostgreSQL client
    if ! command -v psql &> /dev/null; then
        log_error "psql not found. Please install PostgreSQL client."
        exit 1
    fi

    # Check SQLite database exists
    if [ ! -f "$SQLITE_DB" ]; then
        log_error "SQLite database not found: $SQLITE_DB"
        exit 1
    fi

    # Check PostgreSQL password
    if [ -z "$PG_PASSWORD" ]; then
        log_error "PG_PASSWORD environment variable not set"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

test_postgresql_connection() {
    log "Testing PostgreSQL connection..."

    export PGPASSWORD="$PG_PASSWORD"
    if psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d postgres -c '\q' 2>/dev/null; then
        log_success "PostgreSQL connection successful"
    else
        log_error "Cannot connect to PostgreSQL"
        exit 1
    fi
}

backup_sqlite() {
    log "Creating SQLite backup..."
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$CSV_DIR"

    # 1. Binary backup
    cp "$SQLITE_DB" "$BACKUP_DIR/helloagents_backup.db"
    log_success "Binary backup created: $BACKUP_DIR/helloagents_backup.db"

    # 2. SQL dump
    sqlite3 "$SQLITE_DB" ".dump" | gzip > "$BACKUP_DIR/sqlite_dump.sql.gz"
    log_success "SQL dump created: $BACKUP_DIR/sqlite_dump.sql.gz"

    # 3. Database stats
    sqlite3 "$SQLITE_DB" <<EOF > "$BACKUP_DIR/stats_before.txt"
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL SELECT 'lessons', COUNT(*) FROM lessons
UNION ALL SELECT 'user_progress', COUNT(*) FROM user_progress
UNION ALL SELECT 'code_submissions', COUNT(*) FROM code_submissions
UNION ALL SELECT 'chat_messages', COUNT(*) FROM chat_messages;
EOF

    log "Database statistics before migration:"
    cat "$BACKUP_DIR/stats_before.txt" | tee -a "$LOG_FILE"
}

export_sqlite_data() {
    log "Exporting SQLite data to CSV..."

    # Export all tables to CSV
    sqlite3 "$SQLITE_DB" <<EOF
.headers on
.mode csv
.output $CSV_DIR/users.csv
SELECT * FROM users;
.output $CSV_DIR/lessons.csv
SELECT * FROM lessons;
.output $CSV_DIR/user_progress.csv
SELECT * FROM user_progress;
.output $CSV_DIR/code_submissions.csv
SELECT * FROM code_submissions;
.output $CSV_DIR/chat_messages.csv
SELECT * FROM chat_messages;
.quit
EOF

    # Count exported records
    for table in users lessons user_progress code_submissions chat_messages; do
        count=$(($(wc -l < "$CSV_DIR/${table}.csv") - 1))  # Subtract header
        log "Exported $count records from $table"
    done

    log_success "Data export completed"
}

create_postgresql_schema() {
    log "Creating PostgreSQL schema..."

    export PGPASSWORD="$PG_PASSWORD"

    # Check if schema script exists
    SCHEMA_FILE="$SCRIPT_DIR/create_tables_postgresql.sql"
    if [ ! -f "$SCHEMA_FILE" ]; then
        log_error "Schema file not found: $SCHEMA_FILE"
        exit 1
    fi

    # Create schema
    psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -f "$SCHEMA_FILE" 2>&1 | tee -a "$LOG_FILE"

    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log_success "Schema created successfully"
    else
        log_error "Failed to create schema"
        exit 1
    fi
}

import_data_to_postgresql() {
    log "Importing data to PostgreSQL..."

    export PGPASSWORD="$PG_PASSWORD"

    psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" <<EOF 2>&1 | tee -a "$LOG_FILE"
-- Disable triggers and constraints for faster import
SET session_replication_role = 'replica';

-- Import data
\COPY users (id, username, full_name, settings, created_at, updated_at, last_login) FROM '$CSV_DIR/users.csv' WITH CSV HEADER;
\COPY lessons (id, chapter_number, lesson_number, title, content, starter_code, extra_data, created_at, updated_at) FROM '$CSV_DIR/lessons.csv' WITH CSV HEADER;
\COPY user_progress (id, user_id, lesson_id, completed, current_code, cursor_position, started_at, completed_at, last_accessed) FROM '$CSV_DIR/user_progress.csv' WITH CSV HEADER;
\COPY code_submissions (id, user_id, lesson_id, code, output, status, execution_time, submitted_at) FROM '$CSV_DIR/code_submissions.csv' WITH CSV HEADER;
\COPY chat_messages (id, user_id, lesson_id, role, content, extra_data, created_at) FROM '$CSV_DIR/chat_messages.csv' WITH CSV HEADER;

-- Re-enable triggers and constraints
SET session_replication_role = 'origin';

-- Update sequences to match max IDs
SELECT setval('users_id_seq', COALESCE((SELECT MAX(id) FROM users), 1), true);
SELECT setval('lessons_id_seq', COALESCE((SELECT MAX(id) FROM lessons), 1), true);
SELECT setval('user_progress_id_seq', COALESCE((SELECT MAX(id) FROM user_progress), 1), true);
SELECT setval('code_submissions_id_seq', COALESCE((SELECT MAX(id) FROM code_submissions), 1), true);
SELECT setval('chat_messages_id_seq', COALESCE((SELECT MAX(id) FROM chat_messages), 1), true);
EOF

    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log_success "Data import completed"
    else
        log_error "Failed to import data"
        exit 1
    fi
}

create_indexes() {
    log "Creating indexes..."

    export PGPASSWORD="$PG_PASSWORD"

    INDEX_FILE="$SCRIPT_DIR/create_indexes_postgresql.sql"
    if [ ! -f "$INDEX_FILE" ]; then
        log_error "Index file not found: $INDEX_FILE"
        exit 1
    fi

    psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -f "$INDEX_FILE" 2>&1 | tee -a "$LOG_FILE"

    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log_success "Indexes created successfully"
    else
        log_error "Failed to create indexes"
        exit 1
    fi
}

verify_data_integrity() {
    log "Verifying data integrity..."

    export PGPASSWORD="$PG_PASSWORD"

    # Get PostgreSQL stats
    psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -t <<EOF > "$BACKUP_DIR/stats_after.txt"
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL SELECT 'lessons', COUNT(*) FROM lessons
UNION ALL SELECT 'user_progress', COUNT(*) FROM user_progress
UNION ALL SELECT 'code_submissions', COUNT(*) FROM code_submissions
UNION ALL SELECT 'chat_messages', COUNT(*) FROM chat_messages;
EOF

    log "Database statistics after migration:"
    cat "$BACKUP_DIR/stats_after.txt" | tee -a "$LOG_FILE"

    # Compare counts
    log "Comparing record counts..."

    diff_output=$(diff "$BACKUP_DIR/stats_before.txt" "$BACKUP_DIR/stats_after.txt" | grep -v '^---' | grep -v '^+++' | grep -v '^@@' || true)

    if [ -z "$diff_output" ]; then
        log_success "Data integrity verified - all record counts match"
    else
        log_error "Data integrity check failed - record counts mismatch:"
        echo "$diff_output" | tee -a "$LOG_FILE"
        exit 1
    fi
}

generate_migration_report() {
    log "Generating migration report..."

    REPORT_FILE="$BACKUP_DIR/MIGRATION_REPORT.md"

    cat > "$REPORT_FILE" <<EOF
# PostgreSQL Migration Report

**Migration Date**: $(date +'%Y-%m-%d %H:%M:%S')
**Migration Duration**: $(($(date +%s) - $START_TIME)) seconds

## Migration Summary

### Source Database (SQLite)
- **Database File**: $SQLITE_DB
- **Database Size**: $(du -h "$SQLITE_DB" | cut -f1)

### Target Database (PostgreSQL)
- **Host**: $PG_HOST:$PG_PORT
- **Database**: $PG_DB
- **User**: $PG_USER

## Data Statistics

### Before Migration (SQLite)
\`\`\`
$(cat "$BACKUP_DIR/stats_before.txt")
\`\`\`

### After Migration (PostgreSQL)
\`\`\`
$(cat "$BACKUP_DIR/stats_after.txt")
\`\`\`

## Backup Location
- **Backup Directory**: $BACKUP_DIR
- **SQLite Backup**: $BACKUP_DIR/helloagents_backup.db
- **SQL Dump**: $BACKUP_DIR/sqlite_dump.sql.gz
- **CSV Export**: $CSV_DIR/

## Next Steps

1. Update application configuration:
   \`\`\`bash
   export DATABASE_URL="postgresql://$PG_USER:***@$PG_HOST:$PG_PORT/$PG_DB"
   \`\`\`

2. Restart application:
   \`\`\`bash
   cd $BACKEND_DIR
   systemctl restart helloagents  # or your startup command
   \`\`\`

3. Monitor application logs:
   \`\`\`bash
   tail -f /var/log/helloagents/app.log
   \`\`\`

4. Verify API endpoints:
   \`\`\`bash
   curl http://localhost:8000/api/v1/health
   \`\`\`

## Rollback Instructions

If you need to rollback to SQLite:

\`\`\`bash
# 1. Stop application
systemctl stop helloagents

# 2. Restore SQLite database
cp $BACKUP_DIR/helloagents_backup.db $SQLITE_DB

# 3. Remove DATABASE_URL from environment
unset DATABASE_URL

# 4. Restart application
systemctl start helloagents
\`\`\`

---

**Migration Status**: ✅ SUCCESS
EOF

    log_success "Migration report generated: $REPORT_FILE"
}

# ====================================
# Main Migration Flow
# ====================================

main() {
    START_TIME=$(date +%s)

    echo ""
    echo "======================================"
    echo "HelloAgents PostgreSQL Migration"
    echo "======================================"
    echo ""

    # Step 1: Prerequisites
    check_prerequisites
    test_postgresql_connection

    # Step 2: Backup SQLite
    backup_sqlite

    # Step 3: Export data
    export_sqlite_data

    # Step 4: Create PostgreSQL schema
    create_postgresql_schema

    # Step 5: Import data
    import_data_to_postgresql

    # Step 6: Create indexes
    create_indexes

    # Step 7: Verify data integrity
    verify_data_integrity

    # Step 8: Generate report
    generate_migration_report

    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))

    echo ""
    echo "======================================"
    echo "✅ Migration Completed Successfully!"
    echo "======================================"
    echo "Duration: ${DURATION} seconds"
    echo "Backup: $BACKUP_DIR"
    echo "Report: $BACKUP_DIR/MIGRATION_REPORT.md"
    echo ""
    echo "Next Steps:"
    echo "1. Update DATABASE_URL in your .env file"
    echo "2. Restart your application"
    echo "3. Monitor logs and verify functionality"
    echo ""
}

# Run migration
main "$@"
