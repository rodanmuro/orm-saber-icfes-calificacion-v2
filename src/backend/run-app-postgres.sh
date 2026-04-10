#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_ACTIVATE="${SCRIPT_DIR}/.venv/bin/activate"

if [[ ! -f "${VENV_ACTIVATE}" ]]; then
  echo "[run-app-postgres] No se encontro entorno virtual en src/backend/.venv"
  echo "[run-app-postgres] Ejecuta:"
  echo "  python3 -m venv src/backend/.venv"
  echo "  source src/backend/.venv/bin/activate"
  echo "  pip install -r src/backend/requirements.txt"
  exit 1
fi

# shellcheck disable=SC1091
source "${VENV_ACTIVATE}"

cd "${SCRIPT_DIR}"

export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg://administrador:12345678@localhost:5432/omr_app}"
export DEBUG="${DEBUG:-false}"
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8001}"
export RELOAD="${RELOAD:-true}"

if [[ "${RELOAD}" == "true" ]]; then
  exec uvicorn app.main:app --host "${HOST}" --port "${PORT}" --reload
else
  exec uvicorn app.main:app --host "${HOST}" --port "${PORT}"
fi
