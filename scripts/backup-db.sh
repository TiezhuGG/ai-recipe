#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
# shellcheck source=./common.sh
. "${SCRIPT_DIR}/common.sh"

ensure_project_root
load_env

BACKUP_DIR=${BACKUP_DIR:-"${PROJECT_ROOT}/backups"}
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-7}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/recipe_db_${TIMESTAMP}.sql"

mkdir -p "${BACKUP_DIR}"

if command -v docker >/dev/null 2>&1 && compose_service_exists db && compose_service_running db; then
  log_section "Creating PostgreSQL backup from Docker"
  compose exec -T db pg_dump -U "${POSTGRES_USER:-recipe_user}" -d "${POSTGRES_DB:-recipe_db}" > "${BACKUP_FILE}"
else
  log_section "Creating PostgreSQL backup from local connection"
  require_command pg_dump
  PGPASSWORD="${POSTGRES_PASSWORD:-}" pg_dump \
    -h "${DB_HOST:-localhost}" \
    -p "${DB_PORT:-5432}" \
    -U "${POSTGRES_USER:-recipe_user}" \
    -d "${POSTGRES_DB:-recipe_db}" > "${BACKUP_FILE}"
fi

gzip -f "${BACKUP_FILE}"
find "${BACKUP_DIR}" -name 'recipe_db_*.sql.gz' -mtime +"${RETENTION_DAYS}" -delete

log_info "Backup created: ${BACKUP_FILE}.gz"
log_info "Retention cleanup finished: ${RETENTION_DAYS} days"

