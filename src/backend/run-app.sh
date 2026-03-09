#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_ACTIVATE="${SCRIPT_DIR}/.venv/bin/activate"

if [[ ! -f "${VENV_ACTIVATE}" ]]; then
  echo "[run-app] No se encontro entorno virtual en src/backend/.venv"
  echo "[run-app] Ejecuta:"
  echo "  python3 -m venv src/backend/.venv"
  echo "  source src/backend/.venv/bin/activate"
  echo "  pip install -r src/backend/requirements.txt"
  exit 1
fi

# shellcheck disable=SC1091
source "${VENV_ACTIVATE}"

cd "${SCRIPT_DIR}"

export DEBUG="${DEBUG:-false}"
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8000}"
export RELOAD="${RELOAD:-true}"

if [[ "${RELOAD}" == "true" ]]; then
  exec uvicorn app.main:app --host "${HOST}" --port "${PORT}" --reload
else
  exec uvicorn app.main:app --host "${HOST}" --port "${PORT}"
fi
