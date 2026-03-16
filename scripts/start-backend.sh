#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
# shellcheck source=./common.sh
. "${SCRIPT_DIR}/common.sh"

BACKEND_DIR="${PROJECT_ROOT}/backend"
ENV_FILE=${ENV_FILE:-"${BACKEND_DIR}/.env"}

cd "${BACKEND_DIR}"

require_command python

if [ ! -d ".venv" ]; then
  log_section "Creating local virtual environment"
  python -m venv .venv
fi

# shellcheck disable=SC1091
. .venv/bin/activate

log_section "Installing backend dependencies"
python -m pip install -r requirements.txt

if [ ! -f "${ENV_FILE}" ] && [ -f ".env.example" ]; then
  cp .env.example "${ENV_FILE}"
  log_warn "Created ${ENV_FILE} from backend/.env.example. Review it before using production credentials."
fi

set -a
if [ -f "${ENV_FILE}" ]; then
  # shellcheck disable=SC1090
  . "${ENV_FILE}"
fi
set +a

mkdir -p uploads logs

log_section "Initializing database"
python -c 'from app.core.database import init_db; init_db()'

log_section "Starting FastAPI server"
exec uvicorn main:app \
  --host "${BACKEND_HOST:-0.0.0.0}" \
  --port "${BACKEND_PORT:-8000}" \
  --reload
