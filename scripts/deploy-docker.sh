#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
# shellcheck source=./common.sh
. "${SCRIPT_DIR}/common.sh"

ensure_project_root
load_env

require_command docker
require_command curl
compose version >/dev/null

ENV_FILE=${ENV_FILE:-"${PROJECT_ROOT}/.env"}

if [ ! -f "${ENV_FILE}" ]; then
  if [ -f "${PROJECT_ROOT}/.env.example" ]; then
    cp "${PROJECT_ROOT}/.env.example" "${ENV_FILE}"
    log_warn "${ENV_FILE} was missing, so a template was copied from .env.example"
  fi

  log_error "Please review ${ENV_FILE} and fill in real values before deploying"
  exit 1
fi

required_vars=(
  POSTGRES_DB
  POSTGRES_USER
  POSTGRES_PASSWORD
  DATABASE_URL
  LLM_API_KEY
  LLM_BASE_URL
  MODEL_NAME
  SECRET_KEY
)

missing_vars=()
for var_name in "${required_vars[@]}"; do
  if [ -z "${!var_name:-}" ]; then
    missing_vars+=("${var_name}")
  fi
done

if [ "${#missing_vars[@]}" -gt 0 ]; then
  log_error "Missing required variables in ${ENV_FILE}: ${missing_vars[*]}"
  exit 1
fi

log_section "Validating Docker Compose configuration"
compose config >/dev/null

log_section "Building and starting containers"
compose up -d --build --remove-orphans

log_section "Waiting for services"
bash scripts/health-check.sh

log_section "Container status"
compose ps

log_section "Recent logs"
compose logs --tail=30 backend frontend db

log_info "Deployment finished"
log_info "Frontend: http://localhost"
log_info "Backend:  http://localhost:8000"
