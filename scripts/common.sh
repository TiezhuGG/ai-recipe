#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "${SCRIPT_DIR}/.." && pwd)

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
  echo -e "${GREEN}[INFO]${NC} $*"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $*" >&2
}

log_section() {
  echo -e "${BLUE}==>${NC} $*"
}

ensure_project_root() {
  cd "${PROJECT_ROOT}"
}

require_command() {
  local command_name=$1
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    log_error "Missing required command: ${command_name}"
    exit 1
  fi
}

compose() {
  if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    docker compose "$@"
    return
  fi

  if command -v docker-compose >/dev/null 2>&1; then
    docker-compose "$@"
    return
  fi

  log_error "Neither 'docker compose' nor 'docker-compose' is available"
  exit 1
}

load_env() {
  local env_file=${1:-"${PROJECT_ROOT}/.env"}

  if [ -f "${env_file}" ]; then
    set -a
    # shellcheck disable=SC1090
    . "${env_file}"
    set +a
  fi
}

wait_for_http_ok() {
  local url=$1
  local timeout_seconds=${2:-60}
  local label=${3:-$1}
  local elapsed=0

  while [ "${elapsed}" -lt "${timeout_seconds}" ]; do
    if curl -fsS --max-time 5 "${url}" >/dev/null 2>&1; then
      log_info "${label} is reachable: ${url}"
      return 0
    fi

    sleep 2
    elapsed=$((elapsed + 2))
  done

  log_warn "Timed out while waiting for ${label}: ${url}"
  return 1
}

compose_service_exists() {
  local service_name=$1
  compose config --services 2>/dev/null | grep -Fxq "${service_name}"
}

compose_service_running() {
  local service_name=$1
  compose ps --services --status running 2>/dev/null | grep -Fxq "${service_name}"
}
