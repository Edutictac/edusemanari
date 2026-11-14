#!/usr/bin/env bash
set -euo pipefail

# Compila la web, genera el índice del buscador y la sirve en local.
# Hugo server no incluye Pagefind, así que la vista previa se sirve desde web/public.
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
port="${PORT:-1313}"

cd "$project_dir"
hugo --source web --destination web/public --baseURL "http://localhost:${port}/" --gc --minify
npx --yes pagefind@1.6.0 --site web/public >/dev/null

echo "Vista previa en http://localhost:${port}/"
python3 -m http.server "$port" --directory web/public
