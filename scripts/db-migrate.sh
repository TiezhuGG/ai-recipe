#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
# shellcheck source=./common.sh
. "${SCRIPT_DIR}/common.sh"

ensure_project_root
load_env

MODE=${1:-auto}
PYTHON_CODE='from app.core.database import init_db; init_db(); print("Database initialization completed")'

run_local_migration() {
  log_section "Running local database initialization"
  cd "${PROJECT_ROOT}/backend"

  if [ -d ".venv" ]; then
    # shellcheck disable=SC1091
    . .venv/bin/activate
  elif [ -d "venv" ]; then
    # shellcheck disable=SC1091
    . venv/bin/activate
  fi

  require_command python
  python -c "${PYTHON_CODE}"
}

run_docker_migration() {
  log_section "Running database initialization inside Docker"
  require_command docker
  compose version >/dev/null

  compose up -d db

  if compose_service_running backend; then
    compose exec -T backend python -c "${PYTHON_CODE}"
  else
    compose run --rm backend python -c "${PYTHON_CODE}"
  fi
}

case "${MODE}" in
  docker)
    run_docker_migration
    ;;
  local)
    run_local_migration
    ;;
  auto)
    if command -v docker >/dev/null 2>&1 \
      && compose_service_exists backend \
      && (compose_service_running backend || compose_service_running db); then
      run_docker_migration
    else
      run_local_migration
    fi
    ;;
  *)
    log_error "Unsupported mode: ${MODE}. Use auto, docker, or local."
    exit 1
    ;;
esac

log_info "Database migration finished"
