#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
# shellcheck source=./common.sh
. "${SCRIPT_DIR}/common.sh"

ensure_project_root
load_env

require_command curl

BACKEND_URL=${BACKEND_URL:-"http://localhost:8000/health"}
FRONTEND_URL=${FRONTEND_URL:-"http://localhost/nginx-health"}
DB_HOST=${DB_HOST:-"localhost"}
DB_PORT=${DB_PORT:-"5432"}

check_http() {
  local url=$1
  local label=$2

  if curl -fsS --max-time 10 "${url}" >/dev/null 2>&1; then
    log_info "${label} is healthy: ${url}"
  else
    log_error "${label} check failed: ${url}"
    return 1
  fi
}

check_http "${BACKEND_URL}" "backend"
check_http "${FRONTEND_URL}" "frontend"

if command -v docker >/dev/null 2>&1 && compose_service_exists db; then
  if compose_service_running db; then
    if compose exec -T db pg_isready -U "${POSTGRES_USER:-recipe_user}" -d "${POSTGRES_DB:-recipe_db}" >/dev/null 2>&1; then
      log_info "database is healthy inside Docker"
    else
      log_error "database health check failed inside Docker"
      exit 1
    fi
  else
    log_warn "db service exists but is not currently running"
    exit 1
  fi
else
  log_warn "Docker database service not detected, skipping in-container pg_isready"
  if command -v pg_isready >/dev/null 2>&1; then
    if PGPASSWORD="${POSTGRES_PASSWORD:-}" pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${POSTGRES_USER:-recipe_user}" -d "${POSTGRES_DB:-recipe_db}" >/dev/null 2>&1; then
      log_info "database is reachable via pg_isready"
    else
      log_error "database pg_isready check failed"
      exit 1
    fi
  fi
fi

log_info "All health checks passed"

