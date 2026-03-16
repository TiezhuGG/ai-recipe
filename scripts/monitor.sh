#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
# shellcheck source=./common.sh
. "${SCRIPT_DIR}/common.sh"

ensure_project_root
load_env

TAIL_LINES=${TAIL_LINES:-5}
BACKUP_DIR=${BACKUP_DIR:-"${PROJECT_ROOT}/backups"}

echo "=========================================="
echo "AI Recipe Generator Monitoring"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="
echo

if command -v docker >/dev/null 2>&1; then
  log_section "Docker services"
  compose ps || true
  echo

  log_section "Container resource usage"
  docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}' || true
  echo
fi

log_section "System resource usage"
if command -v free >/dev/null 2>&1; then
  free -h
else
  log_warn "Command not available: free"
fi

if command -v df >/dev/null 2>&1; then
  df -h /
else
  log_warn "Command not available: df"
fi
echo

log_section "HTTP health"
BACKEND_URL=${BACKEND_URL:-"http://localhost:8000/health"}
FRONTEND_URL=${FRONTEND_URL:-"http://localhost/nginx-health"}

if curl -fsS --max-time 10 "${BACKEND_URL}" >/dev/null 2>&1; then
  log_info "backend healthy"
else
  log_error "backend unhealthy"
fi

if curl -fsS --max-time 10 "${FRONTEND_URL}" >/dev/null 2>&1; then
  log_info "frontend healthy"
else
  log_error "frontend unhealthy"
fi
echo

if command -v docker >/dev/null 2>&1 && compose_service_exists db && compose_service_running db; then
  log_section "Database status"
  compose exec -T db pg_isready -U "${POSTGRES_USER:-recipe_user}" -d "${POSTGRES_DB:-recipe_db}" || true
  echo
fi

log_section "Recent application logs"
if command -v docker >/dev/null 2>&1 && compose_service_exists backend; then
  compose logs --tail="${TAIL_LINES}" backend frontend || true
else
  log_warn "Docker Compose services not detected, skipping container logs"
fi
echo

log_section "Network listeners"
if command -v ss >/dev/null 2>&1; then
  ss -tuln | grep -E ':(80|443|8000|5432)\s' || true
elif command -v netstat >/dev/null 2>&1; then
  netstat -tuln | grep -E ':(80|443|8000|5432)\s' || true
else
  log_warn "Neither ss nor netstat is available"
fi
echo

log_section "Backup files"
if [ -d "${BACKUP_DIR}" ]; then
  ls -lh "${BACKUP_DIR}" | tail -n +1
else
  log_warn "Backup directory does not exist yet: ${BACKUP_DIR}"
fi

