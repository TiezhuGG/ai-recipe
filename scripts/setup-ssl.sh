#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
# shellcheck source=./common.sh
. "${SCRIPT_DIR}/common.sh"

ensure_project_root

if [ "${EUID}" -ne 0 ]; then
  log_error "Run this script with sudo or as root"
  exit 1
fi

require_command nginx
require_command certbot

DOMAIN=${1:-${DOMAIN:-}}
EMAIL=${2:-${EMAIL:-}}
FRONTEND_UPSTREAM=${FRONTEND_UPSTREAM:-127.0.0.1:8080}
BACKEND_UPSTREAM=${BACKEND_UPSTREAM:-127.0.0.1:8000}

if [ -z "${DOMAIN}" ] || [ -z "${EMAIL}" ]; then
  log_error "Usage: sudo ./scripts/setup-ssl.sh <domain> <email>"
  log_warn "This script assumes your frontend is reachable at ${FRONTEND_UPSTREAM} and backend at ${BACKEND_UPSTREAM}"
  exit 1
fi

if grep -Eq '"80:80"|127\.0\.0\.1:80:80' docker-compose.yml 2>/dev/null; then
  log_warn "Your current docker-compose frontend mapping still occupies host port 80."
  log_warn "Host nginx cannot listen on 80/443 until you remap the frontend container to 127.0.0.1:8080:80 or similar."
  log_warn "After adjusting docker-compose.yml, rerun this script."
  exit 1
fi

cat > /etc/nginx/sites-available/recipe-app <<EOF
server {
    listen 80;
    server_name ${DOMAIN};

    location / {
        proxy_pass http://${FRONTEND_UPSTREAM};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/ {
        proxy_pass http://${BACKEND_UPSTREAM}/api/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_buffering off;
        proxy_read_timeout 300s;
    }

    location /uploads/ {
        proxy_pass http://${BACKEND_UPSTREAM}/uploads/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /health {
        proxy_pass http://${BACKEND_UPSTREAM}/health;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /docs {
        proxy_pass http://${BACKEND_UPSTREAM}/docs;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /redoc {
        proxy_pass http://${BACKEND_UPSTREAM}/redoc;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /openapi.json {
        proxy_pass http://${BACKEND_UPSTREAM}/openapi.json;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/recipe-app /etc/nginx/sites-enabled/recipe-app
nginx -t
systemctl reload nginx

certbot --nginx -d "${DOMAIN}" --non-interactive --agree-tos --email "${EMAIL}" --redirect
certbot renew --dry-run

log_info "SSL setup completed for https://${DOMAIN}"

