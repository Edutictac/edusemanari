#!/usr/bin/env bash
set -euo pipefail

# Compila la web con Hugo y la publica en la rama `pages` del remoto Forgejo.
# EduTicTac Pages la sirve en https://pages.edutictac.es/Edutictac/edusemanari/
# Los números con `draft: true` no se publican: aprobar un número es quitar esa línea.
remote="${PAGES_REMOTE:-edutictac}"
announce=1
week=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-announce) announce=0; shift ;;
    --week) week="${2:-}"; shift 2 ;;
    *) echo "Opción desconocida: $1" >&2; exit 1 ;;
  esac
done
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
build_dir="$(mktemp -d)"
pages_dir="$(mktemp -d)"
cleanup() {
  rm -rf "$build_dir"
  git -C "$project_dir" worktree remove --force "$pages_dir" 2>/dev/null || rm -rf "$pages_dir"
}
trap cleanup EXIT

cd "$project_dir"
if [[ -n "$(git status --porcelain -- web)" ]]; then
  echo "Hay cambios sin commit en web/. Haz commit antes de publicar." >&2
  exit 1
fi

python_bin="$project_dir/.venv/bin/python"
announce_args=(--config config.json --wait 300)
if [[ -n "$week" ]]; then
  announce_args+=(--week "$week")
fi
if [[ "$announce" == 1 ]]; then
  if [[ ! -x "$python_bin" ]]; then
    echo "No encuentro .venv/bin/python para preparar el aviso a los grupos." >&2
    exit 1
  fi
  if ! "$python_bin" -m semanario.announce "${announce_args[@]}" --dry-run --wait 0 >/dev/null; then
    echo "No se publica: el número no está listo para avisar (¿sigue en borrador?)." >&2
    exit 1
  fi
fi

hugo --source web --gc --minify --destination "$build_dir"

if command -v npx >/dev/null 2>&1; then
  npx --yes pagefind@1.6.0 --site "$build_dir" >/dev/null
else
  echo "Aviso: Pagefind no está disponible; el buscador no se regenerará." >&2
fi

git fetch "$remote" pages 2>/dev/null || true
rmdir "$pages_dir"
git worktree add --detach "$pages_dir" HEAD >/dev/null
cd "$pages_dir"
git rm -rf . >/dev/null 2>&1 || true
cp -R "$build_dir/." .
touch .nojekyll
git add -A
git -c user.name="EduTicTac Pages" -c user.email="pages@edutictac.es" \
  commit -q -m "Publish EduSetmanari $(git -C "$project_dir" rev-parse --short HEAD)"
expected="$(git rev-parse --verify -q "refs/remotes/$remote/pages" || true)"
if [[ -n "$expected" ]]; then
  git push "--force-with-lease=refs/heads/pages:$expected" "$remote" HEAD:refs/heads/pages
else
  git push "$remote" HEAD:refs/heads/pages
fi

echo "Publicado en https://pages.edutictac.es/Edutictac/edusemanari/"
cd "$project_dir"

if [[ "$announce" == 1 ]]; then
  if ! "$python_bin" -m semanario.announce "${announce_args[@]}"; then
    echo "La web se publicó, pero el aviso a los grupos falló." >&2
    exit 1
  fi
fi
