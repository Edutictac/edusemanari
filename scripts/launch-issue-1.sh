#!/usr/bin/env bash
set -euo pipefail
export GIT_TERMINAL_PROMPT=0
export GIT_SSH_COMMAND="ssh -o BatchMode=yes -o ConnectTimeout=15"
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"
if [[ "$(git branch --show-current)" != main || -n "$(git status --porcelain)" ]]; then
  echo "Lanzamiento detenido: main debe estar limpia y revisada." >&2
  exit 1
fi
.venv/bin/python -m semanario.announce --config config.json --week 2026-11-02 --dry-run --wait 0 >/dev/null
# Comprobar la credencial antes de publicar, sin mostrarla.
.venv/bin/python -c 'from semanario.storage import load_config; from semanario.telegram import read_token; c=load_config("config.json"); read_token(c["token_pass_entry"])'
git push origin main
git push edutictac main
scripts/publish-pages.sh --week 2026-11-02
