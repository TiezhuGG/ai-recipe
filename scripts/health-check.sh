#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
# shellcheck source=./common.sh
. "${SCRIPT_DIR}/common.sh"

ensure_project_root
load_env

require_command curl

BACKEND_URL=${BACKEND_URL:-"http://localhost:8081/health"}
FRONTEND_URL=${FRONTEND_URL:-"http://localhost:8081/nginx-health"}
DB_HOST=${DB_HOST:-"localhost"}
DB_PORT=${DB_PORT:-"5432"}
BACKEND_WAIT_SECONDS=${BACKEND_WAIT_SECONDS:-120}
FRONTEND_WAIT_SECONDS=${FRONTEND_WAIT_SECONDS:-60}
DB_WAIT_SECONDS=${DB_WAIT_SECONDS:-60}
BACKEND_CONTAINER_NAME=${BACKEND_CONTAINER_NAME:-recipe-backend}
FRONTEND_CONTAINER_NAME=${FRONTEND_CONTAINER_NAME:-recipe-frontend}
DB_CONTAINER_NAME=${DB_CONTAINER_NAME:-recipe-db}

check_http() {
  local url=$1
  local label=$2
  local timeout_seconds=$3

  if wait_for_http_ok "${url}" "${timeout_seconds}" "${label}"; then
    log_info "${label} is healthy: ${url}"
  else
    log_error "${label} check failed: ${url}"
    return 1
  fi
}

check_compose_health() {
  local service_name=$1
  local timeout_seconds=$2
  local elapsed=0

  while [ "${elapsed}" -lt "${timeout_seconds}" ]; do
    local container_id
    container_id=$(compose ps -q "${service_name}" 2>/dev/null | head -n 1)

    if [ -n "${container_id}" ]; then
      local status
      status=$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "${container_id}" 2>/dev/null || true)

      case "${status}" in
        healthy|running)
          log_info "${service_name} is healthy (${status})"
          return 0
          ;;
        unhealthy|exited|dead)
          log_error "${service_name} became unhealthy (${status})"
          return 1
          ;;
      esac
    fi

    sleep 2
    elapsed=$((elapsed + 2))
  done

  log_warn "Timed out while waiting for ${service_name} container health"
  return 1
}

check_container_health() {
  local container_name=$1
  local timeout_seconds=$2
  local elapsed=0

  while [ "${elapsed}" -lt "${timeout_seconds}" ]; do
    local status
    status=$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "${container_name}" 2>/dev/null || true)

    case "${status}" in
      healthy|running)
        log_info "${container_name} is healthy (${status})"
        return 0
        ;;
      unhealthy|exited|dead)
        log_error "${container_name} became unhealthy (${status})"
        return 1
        ;;
    esac

    sleep 2
    elapsed=$((elapsed + 2))
  done

  log_warn "Timed out while waiting for ${container_name} container health"
  return 1
}

container_exists() {
  local container_name=$1
  docker inspect "${container_name}" >/dev/null 2>&1
}

if command -v docker >/dev/null 2>&1; then
  if container_exists "${BACKEND_CONTAINER_NAME}"; then
    check_container_health "${BACKEND_CONTAINER_NAME}" "${BACKEND_WAIT_SECONDS}"
  elif compose_service_exists backend; then
    check_compose_health backend "${BACKEND_WAIT_SECONDS}"
  else
    log_error "backend container/service not found (expected ${BACKEND_CONTAINER_NAME})"
    exit 1
  fi
else
  check_http "${BACKEND_URL}" "backend" "${BACKEND_WAIT_SECONDS}"
fi

if command -v docker >/dev/null 2>&1; then
  if container_exists "${FRONTEND_CONTAINER_NAME}"; then
    check_container_health "${FRONTEND_CONTAINER_NAME}" "${FRONTEND_WAIT_SECONDS}"
  elif compose_service_exists frontend; then
    check_compose_health frontend "${FRONTEND_WAIT_SECONDS}"
  else
    log_error "frontend container/service not found (expected ${FRONTEND_CONTAINER_NAME})"
    exit 1
  fi
else
  check_http "${FRONTEND_URL}" "frontend" "${FRONTEND_WAIT_SECONDS}"
fi

if command -v docker >/dev/null 2>&1; then
  if container_exists "${DB_CONTAINER_NAME}"; then
    check_container_health "${DB_CONTAINER_NAME}" "${DB_WAIT_SECONDS}"
    if docker exec "${DB_CONTAINER_NAME}" pg_isready -U "${POSTGRES_USER:-recipe_user}" -d "${POSTGRES_DB:-recipe_db}" >/dev/null 2>&1; then
      log_info "database is healthy inside Docker"
    else
      log_error "database health check failed inside Docker"
      exit 1
    fi
  elif compose_service_exists db; then
    check_compose_health db "${DB_WAIT_SECONDS}"
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
    log_error "database container/service not found (expected ${DB_CONTAINER_NAME})"
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
