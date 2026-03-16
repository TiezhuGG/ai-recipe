#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
# shellcheck source=./common.sh
. "${SCRIPT_DIR}/common.sh"

ensure_project_root
load_env

require_command npm

cd "${PROJECT_ROOT}/frontend"

log_section "Installing frontend dependencies"
npm ci

log_section "Building frontend"
npm run build

log_info "Frontend build completed: ${PROJECT_ROOT}/frontend/dist"

