#!/usr/bin/env bash
set -euo pipefail

# Orquestador local para levantar/parar toda la stack en src/
# Servicios:
# - backend (FastAPI)            :8001
# - frontend_web (Vite)          :5173
# - frontend_results (Vite)      :5174
# - frontend (Expo)              :8081 (por defecto Expo)
#
# Uso:
#   scripts/src_stack.sh start
#   scripts/src_stack.sh stop
#   scripts/src_stack.sh restart
#   scripts/src_stack.sh status
#   scripts/src_stack.sh mobile
#   scripts/src_stack.sh attach
#   scripts/src_stack.sh logs backend
#
# Nota: requiere dependencias ya instaladas en cada subproyecto.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${ROOT_DIR}/.run/src_stack"
LOG_DIR="${RUN_DIR}/logs"
PID_DIR="${RUN_DIR}/pids"

is_sourced() {
  [[ "${BASH_SOURCE[0]}" != "$0" ]]
}

safe_exit() {
  local code="${1:-0}"
  if is_sourced; then
    return "${code}"
  fi
  exit "${code}"
}

mkdir -p "${LOG_DIR}" "${PID_DIR}"

service_pid_file() {
  local name="$1"
  echo "${PID_DIR}/${name}.pid"
}

service_log_file() {
  local name="$1"
  echo "${LOG_DIR}/${name}.log"
}

is_running() {
  local name="$1"
  local pid_file
  pid_file="$(service_pid_file "${name}")"
  local fallback_pattern=""
  case "${name}" in
    backend) fallback_pattern="uvicorn.*0.0.0.0:8001|run-app-postgres.sh" ;;
    frontend_web) fallback_pattern="vite.*5173" ;;
    frontend_results) fallback_pattern="vite.*5174" ;;
    frontend_expo) fallback_pattern="expo.*start" ;;
  esac

  if [[ ! -f "${pid_file}" ]]; then
    if [[ -n "${fallback_pattern}" ]]; then
      local detected_pid
      detected_pid="$(pgrep -f "${fallback_pattern}" | tail -n 1 || true)"
      if [[ -n "${detected_pid}" ]]; then
        echo "${detected_pid}" > "${pid_file}"
      else
        return 1
      fi
    else
      return 1
    fi
  fi
  local pid
  pid="$(cat "${pid_file}")"
  if [[ -z "${pid}" ]]; then
    return 1
  fi
  if ps -p "${pid}" >/dev/null 2>&1; then
    local cmdline
    cmdline="$(ps -p "${pid}" -o args= 2>/dev/null || true)"
    case "${name}" in
      backend)
        [[ "${cmdline}" == *"run-app-postgres.sh"* || "${cmdline}" == *"uvicorn"* || "${cmdline}" == *"python -m uvicorn"* ]] && return 0
        ;;
      frontend_web)
        [[ "${cmdline}" == *"vite"* || "${cmdline}" == *"npm run dev"* || "${cmdline}" == *"node"* ]] && return 0
        ;;
      frontend_results)
        [[ "${cmdline}" == *"vite"* || "${cmdline}" == *"npm run dev"* || "${cmdline}" == *"node"* ]] && return 0
        ;;
      frontend_expo)
        [[ "${cmdline}" == *"expo"* || "${cmdline}" == *"npm run start"* ]] && return 0
        ;;
    esac
    # PID existe pero no corresponde al servicio esperado
    rm -f "${pid_file}"
    return 1
  fi

  # Fallback: el PID pudo cambiar (npm/vite reloader). Reintentar por patron.
  if [[ -n "${fallback_pattern}" ]]; then
    local detected_pid
    detected_pid="$(pgrep -f "${fallback_pattern}" | tail -n 1 || true)"
    if [[ -n "${detected_pid}" ]]; then
      echo "${detected_pid}" > "${pid_file}"
      return 0
    fi
  fi

  rm -f "${pid_file}"
  return 1
}

start_service() {
  local name="$1"
  local cmd="$2"
  local workdir="$3"

  if is_running "${name}"; then
    echo "[SKIP] ${name} ya esta corriendo (pid $(cat "$(service_pid_file "${name}")"))"
    return 0
  fi

  local log_file
  log_file="$(service_log_file "${name}")"
  : > "${log_file}"

  (
    cd "${workdir}"
    nohup bash -lc "${cmd}" >> "${log_file}" 2>&1 &
    echo $! > "$(service_pid_file "${name}")"
  )

  sleep 1
  if is_running "${name}"; then
    echo "[OK] ${name} iniciado (pid $(cat "$(service_pid_file "${name}")"))"
    echo "     log: ${log_file}"
  else
    echo "[ERR] ${name} no inicio. Revisa log: ${log_file}"
    return 1
  fi
}

stop_service() {
  local name="$1"
  local pid_file
  pid_file="$(service_pid_file "${name}")"
  local fallback_pattern=""
  case "${name}" in
    backend) fallback_pattern="uvicorn.*0.0.0.0:8001|run-app-postgres.sh" ;;
    frontend_web) fallback_pattern="vite.*5173|npm run dev.*5173" ;;
    frontend_results) fallback_pattern="vite.*5174|npm run dev.*5174" ;;
    frontend_expo) fallback_pattern="expo.*start|npm run start.*--lan" ;;
  esac

  if [[ ! -f "${pid_file}" ]]; then
    echo "[SKIP] ${name} no tiene PID registrado"
    return 0
  fi

  local pid
  pid="$(cat "${pid_file}")"
  if [[ -z "${pid}" ]]; then
    rm -f "${pid_file}"
    echo "[SKIP] ${name} PID vacio"
    return 0
  fi

  if ps -p "${pid}" >/dev/null 2>&1; then
    kill "${pid}" >/dev/null 2>&1 || true
    sleep 1
    if ps -p "${pid}" >/dev/null 2>&1; then
      kill -9 "${pid}" >/dev/null 2>&1 || true
    fi
    echo "[OK] ${name} detenido"
  else
    echo "[SKIP] ${name} ya estaba detenido"
  fi

  # Limpieza extra si quedaron hijos/procesos hermanos vivos.
  if [[ -n "${fallback_pattern}" ]]; then
    pkill -f "${fallback_pattern}" >/dev/null 2>&1 || true
  fi

  rm -f "${pid_file}"
}

status_service() {
  local name="$1"
  if is_running "${name}"; then
    echo "[RUNNING] ${name} pid=$(cat "$(service_pid_file "${name}")")"
  else
    echo "[STOPPED] ${name}"
  fi
}

start_all() {
  start_service "backend" "source .venv/bin/activate && ./run-app-postgres.sh" "${ROOT_DIR}/src/backend"
  start_service "frontend_web" "npm run dev -- --host 0.0.0.0 --port 5173" "${ROOT_DIR}/src/frontend_web"
  start_service "frontend_results" "npm run dev -- --host 0.0.0.0 --port 5174" "${ROOT_DIR}/src/frontend_results"
  start_service "frontend_expo" "npm run start -- --lan" "${ROOT_DIR}/src/frontend"

  echo ""
  echo "Stack iniciada."
  echo "- Backend API      : http://<IP_LAN>:8001"
  echo "- Frontend Web     : http://<IP_LAN>:5173"
  echo "- Frontend Results : http://<IP_LAN>:5174"
  echo "- Expo Dev Server  : puerto por defecto Expo (ver log)"
  echo ""
  echo "Logs en: ${LOG_DIR}"
}

mobile_qr() {
  # Detener expo en background para evitar conflicto de puerto y mostrar QR en foreground.
  stop_service "frontend_expo" >/dev/null 2>&1 || true
  echo "[INFO] Abriendo Expo en foreground (con QR)..."
  echo "[INFO] Para salir de Expo: Ctrl+C"
  (
    cd "${ROOT_DIR}/src/frontend"
    unset CI
    npm run start -- --lan
  )
}

stop_all() {
  stop_service "frontend_expo"
  stop_service "frontend_results"
  stop_service "frontend_web"
  stop_service "backend"
}

status_all() {
  status_service "backend"
  status_service "frontend_web"
  status_service "frontend_results"
  status_service "frontend_expo"
}

show_logs() {
  local target="${1:-}"
  if [[ -z "${target}" ]]; then
    echo "Uso: $0 logs <backend|frontend_web|frontend_results|frontend_expo>"
    exit 1
  fi
  local log_file
  log_file="$(service_log_file "${target}")"
  if [[ ! -f "${log_file}" ]]; then
    echo "No existe log para ${target}: ${log_file}"
    exit 1
  fi
  tail -n 120 "${log_file}"
}

attach_logs() {
  echo "[INFO] Logs en vivo (backend/frontend_web/frontend_results/frontend_expo)."
  echo "[INFO] Formato: <servicio> HH:MM:SS: <mensaje>"
  echo "[INFO] Nota: el QR de Expo NO aparece en attach (tail de logs). Usa: ./scripts/start_all.sh mobile"
  echo "[INFO] Salir: Ctrl+C"

  stream_one_log() {
    local service="$1"
    local log_file="$2"
    local color_reset="\033[0m"
    local color_service="\033[1;37m"
    case "${service}" in
      backend) color_service="\033[1;34m" ;;          # azul
      frontend_web) color_service="\033[1;32m" ;;     # verde
      frontend_results) color_service="\033[1;35m" ;; # magenta
      frontend_expo) color_service="\033[1;33m" ;;    # amarillo
    esac
    stdbuf -oL tail -n 40 -F "${log_file}" 2>/dev/null | \
      awk -v svc="${service}" -v csvc="${color_service}" -v creset="${color_reset}" \
        '{ print csvc svc creset " " strftime("%H:%M:%S") ": " $0; fflush(); }'
  }

  stream_one_log "backend" "$(service_log_file "backend")" &
  local p1=$!
  stream_one_log "frontend_web" "$(service_log_file "frontend_web")" &
  local p2=$!
  stream_one_log "frontend_results" "$(service_log_file "frontend_results")" &
  local p3=$!
  stream_one_log "frontend_expo" "$(service_log_file "frontend_expo")" &
  local p4=$!

  trap 'kill ${p1} ${p2} ${p3} ${p4} >/dev/null 2>&1 || true' INT TERM
  wait ${p1} ${p2} ${p3} ${p4}
}

ACTION="${1:-}"
if [[ -z "${ACTION}" ]]; then
  ACTION="start"
fi

case "${ACTION}" in
  start)
    start_all
    ;;
  stop)
    stop_all
    ;;
  restart)
    stop_all
    start_all
    ;;
  status)
    status_all
    ;;
  mobile)
    mobile_qr
    ;;
  attach)
    attach_logs
    ;;
  logs)
    show_logs "${2:-}"
    ;;
  *)
    echo "Uso: $0 {start|stop|restart|status|mobile|attach|logs <servicio>}"
    safe_exit 1
    ;;
esac
