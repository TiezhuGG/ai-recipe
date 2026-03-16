#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

bash "${SCRIPT_DIR}/deploy-docker.sh"
bash "${SCRIPT_DIR}/health-check.sh"
