#!/usr/bin/env bash

set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_PORT="${MAPI_BACKEND_PORT:-8000}"
FRONTEND_PORT="${MAPI_FRONTEND_PORT:-5173}"
HOST="${MAPI_HOST:-0.0.0.0}"
PIDS=()

usage() {
  cat <<EOF
Avvia backend e frontend di Mapi RAG.

Uso:
  ./start.sh

Variabili opzionali:
  MAPI_HOST             Host di ascolto (default: 0.0.0.0)
  MAPI_BACKEND_PORT     Porta FastAPI (default: 8000)
  MAPI_FRONTEND_PORT    Porta Vite (default: 5173)
EOF
}

cleanup() {
  local pid
  trap - EXIT INT TERM
  for pid in "${PIDS[@]}"; do
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
  done
  for pid in "${PIDS[@]}"; do
    wait "$pid" 2>/dev/null || true
  done
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

if [[ $# -gt 0 ]]; then
  usage >&2
  exit 2
fi

if [[ -x "$ROOT_DIR/.tools/node/bin/node" ]]; then
  export PATH="$ROOT_DIR/.tools/node/bin:$PATH"
fi

for command_name in uv npm; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    printf 'Errore: comando richiesto non trovato: %s\n' "$command_name" >&2
    exit 1
  fi
done

if [[ ! -d "$ROOT_DIR/frontend/node_modules" ]]; then
  printf 'Errore: dipendenze frontend assenti. Esegui npm install in frontend/.\n' >&2
  exit 1
fi

if [[ ! -f "$ROOT_DIR/.env" && ! -f "$ROOT_DIR/backend/.env" ]]; then
  printf 'Avviso: file .env assente; la generazione DeepSeek non sara disponibile.\n' >&2
fi

trap cleanup EXIT
trap 'exit 130' INT TERM

(
  cd "$ROOT_DIR/backend"
  UV_CACHE_DIR="$ROOT_DIR/.uv-cache" exec uv run uvicorn app.main:app \
    --reload --host "$HOST" --port "$BACKEND_PORT"
) &
PIDS+=("$!")

(
  cd "$ROOT_DIR/frontend"
  exec npm run dev -- --host "$HOST" --port "$FRONTEND_PORT"
) &
PIDS+=("$!")

printf '\nMapi RAG in avvio:\n'
printf '  Applicazione: http://localhost:%s\n' "$FRONTEND_PORT"
printf '  API:          http://localhost:%s/docs\n' "$BACKEND_PORT"
printf 'Premi Ctrl+C per arrestare entrambi i processi.\n\n'

set +e
wait -n "${PIDS[@]}"
STATUS=$?
set -e

if [[ $STATUS -ne 0 && $STATUS -ne 130 ]]; then
  printf 'Un processo si e arrestato con codice %s; arresto l intero ambiente.\n' "$STATUS" >&2
fi
exit "$STATUS"
