#!/usr/bin/env bash

set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_PORT="${MAPI_BACKEND_PORT:-8000}"
FRONTEND_PORT="${MAPI_FRONTEND_PORT:-5173}"
HOST="${MAPI_HOST:-0.0.0.0}"
PIDS=()
BOOTSTRAP_TMP=""

usage() {
  cat <<EOF
Avvia backend e frontend di Mapi RAG.
Installa automaticamente le dipendenze mancanti dai lockfile.
Installa uv, Node.js e npm mancanti in .tools/ (senza sudo).

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
  if [[ -n "$BOOTSTRAP_TMP" ]]; then
    rm -rf -- "$BOOTSTRAP_TMP"
  fi
}

download() {
  if command -v curl >/dev/null 2>&1; then
    curl --fail --location --silent --show-error --retry 3 "$1" --output "$2"
  elif command -v wget >/dev/null 2>&1; then
    wget -q "$1" -O "$2"
  else
    printf 'Errore: serve curl o wget per scaricare gli strumenti mancanti.\n' >&2
    return 1
  fi
}

node_ready() {
  command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1 &&
    node -e 'const [major, minor] = process.versions.node.split(".").map(Number); process.exit((major === 20 && minor >= 19) || (major === 22 && minor >= 12) || major > 22 ? 0 : 1)' &&
    npm --version >/dev/null 2>&1
}

install_node() {
  local platform arch archive checksum actual_checksum
  case "$(uname -s)" in
    Linux) platform=linux ;;
    Darwin) platform=darwin ;;
    *) printf 'Errore: installazione automatica Node supportata su Linux e macOS.\n' >&2; return 1 ;;
  esac
  case "$(uname -m)" in
    x86_64|amd64) arch=x64 ;;
    aarch64|arm64) arch=arm64 ;;
    *) printf 'Errore: architettura non supportata per Node (richiesti x64 o arm64).\n' >&2; return 1 ;;
  esac
  archive="node-v22.23.3-${platform}-${arch}.tar.gz"
  printf 'Installazione locale di Node.js 22.23.3 e npm...\n'
  download "https://nodejs.org/dist/v22.23.3/$archive" "$BOOTSTRAP_TMP/$archive"
  download 'https://nodejs.org/dist/v22.23.3/SHASUMS256.txt' "$BOOTSTRAP_TMP/SHASUMS256.txt"
  checksum="$(awk -v file="$archive" '$2 == file {print $1}' "$BOOTSTRAP_TMP/SHASUMS256.txt")"
  if command -v sha256sum >/dev/null 2>&1; then
    actual_checksum="$(sha256sum "$BOOTSTRAP_TMP/$archive")"
  elif command -v shasum >/dev/null 2>&1; then
    actual_checksum="$(shasum -a 256 "$BOOTSTRAP_TMP/$archive")"
  else
    printf 'Errore: serve sha256sum o shasum per verificare Node.\n' >&2
    return 1
  fi
  if [[ ! "$checksum" =~ ^[a-f0-9]{64}$ || "${actual_checksum%% *}" != "$checksum" ]]; then
    printf 'Errore: checksum del download Node non valido.\n' >&2
    return 1
  fi
  mkdir -p "$ROOT_DIR/.tools/node"
  tar -xzf "$BOOTSTRAP_TMP/$archive" -C "$ROOT_DIR/.tools/node" --strip-components=1
  hash -r
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

if [[ $# -gt 0 ]]; then
  usage >&2
  exit 2
fi

for port in "$BACKEND_PORT" "$FRONTEND_PORT"; do
  if [[ ! "$port" =~ ^[0-9]{1,5}$ ]] || (( 10#$port < 1 || 10#$port > 65535 )); then
    printf 'Errore: le porte devono essere numeri compresi tra 1 e 65535.\n' >&2
    exit 2
  fi
done
BACKEND_PORT="$((10#$BACKEND_PORT))"
FRONTEND_PORT="$((10#$FRONTEND_PORT))"
export MAPI_BACKEND_PORT="$BACKEND_PORT" MAPI_FRONTEND_PORT="$FRONTEND_PORT"

trap cleanup EXIT
trap 'exit 130' INT TERM

export PATH="$ROOT_DIR/.tools/uv:$ROOT_DIR/.tools/node/bin:$PATH"

if ! command -v uv >/dev/null 2>&1 || ! node_ready; then
  BOOTSTRAP_TMP="$(mktemp -d)"
fi

if ! command -v uv >/dev/null 2>&1; then
  printf 'Installazione locale di uv...\n'
  download 'https://astral.sh/uv/install.sh' "$BOOTSTRAP_TMP/uv-install.sh"
  UV_INSTALL_DIR="$ROOT_DIR/.tools/uv" UV_NO_MODIFY_PATH=1 sh "$BOOTSTRAP_TMP/uv-install.sh"
  hash -r
fi

if ! node_ready; then
  install_node
fi

for command_name in uv node npm; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    printf 'Errore: comando richiesto non trovato: %s\n' "$command_name" >&2
    exit 1
  fi
done

if ! node_ready; then
  printf 'Errore: Node.js o npm non funzionanti dopo l installazione.\n' >&2
  exit 1
fi

(
  cd "$ROOT_DIR/frontend"
  if [[ ! -d node_modules ]] || ! npm ls --all --include=dev --include=optional >/dev/null 2>&1; then
    printf 'Installazione delle dipendenze frontend dal lockfile...\n'
    npm ci --include=dev --include=optional
  fi
)

printf 'Verifica e sincronizzazione delle dipendenze backend...\n'
(
  cd "$ROOT_DIR/backend"
  UV_CACHE_DIR="$ROOT_DIR/.uv-cache" uv sync --locked
)

(
  cd "$ROOT_DIR/backend"
  UV_CACHE_DIR="$ROOT_DIR/.uv-cache" exec uv run --locked --no-sync uvicorn app.main:app \
    --reload --host "$HOST" --port "$BACKEND_PORT"
) &
PIDS+=("$!")

(
  cd "$ROOT_DIR/frontend"
  exec npm run dev -- --host "$HOST" --port "$FRONTEND_PORT" --strictPort
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
