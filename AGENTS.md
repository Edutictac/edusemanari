# AGENTS.md · EduSetmanari

Semanario bilingüe (castellano y valenciano) a partir de comunidades docentes de Telegram.

## Estructura

- `semanario/`: recogida (`collect.py`), almacenamiento SQLite (`storage.py`) y exportación semanal (`export_week.py`).
- `web/`: web Hugo. Contenido en `web/content/`, plantillas en `web/layouts/`, estilos en `web/assets/css/`.
- `scripts/publish-pages.sh`: publica la web en EduTicTac Pages (rama `pages` del remoto Forgejo `edutictac`) y avisa en los grupos participantes.
- `semanario/announce.py`: envía el aviso de una edición publicada a `announce_groups` (`@edutictac`, `@portaledu`, `@aules`, `@comunitat_lliurex` y `@cv_tic`).
- `systemd/edusemanari-collector.service`: unidad de usuario enlazada con `systemctl --user link`.

## Comandos

- Pruebas: `python3 -m unittest discover -s tests -v`.
- Vista previa con buscador: `scripts/preview.sh` (compila, genera el índice de Pagefind y sirve `web/public`).
- Vista previa de contenido: `hugo server -D --source web`.
- Compilación: `hugo --source web --minify`.
- Índice del buscador: `npx --yes pagefind@1.6.0 --site web/public` (tras compilar en `web/public`).
- Aviso sin enviar: `.venv/bin/python -m semanario.announce --config config.json --week AAAA-MM-DD --dry-run`.

## Reglas

- Nunca mostrar el token del bot ni pasarlo como argumento. Vive en `pass`.
- `config.json`, `*.sqlite3*` y `exports/` contienen datos privados: no imprimirlos ni versionarlos.
- No publicar nada sin aprobación humana. Todo número nuevo se crea con `draft: true`.
- Cada edición recoge desde el domingo 00:00, donde cerró la anterior, hasta el sábado 23:59, y se publica el domingo. Lo que se habla el domingo entra en la edición siguiente; no se pierde ningún día.
- El aviso de una edición se envía solo después de publicar la web y solo a `announce_groups`; `@cv_tic` también recibe su aviso por autorización del usuario. No repetir avisos ya enviados sin `--force`.
- Seguir `EDITORIAL.md`: cubrir la mayoría de temas educativos relevantes, aunque no tengan enlace externo; distinguir hechos contrastados de experiencias, dudas y avisos atribuidos. Sin nombres ni alias de participantes al resumir conversaciones. Al presentar obras o programas, citar su autoría pública comprobada (persona, seudónimo o equipo) y enlazar el recurso de forma visible, también en los avisos.
- Toda pieza y todo texto de interfaz existen en los dos idiomas (`*.md` y `*.va.md`, `i18n/es.toml` y `i18n/va.toml`). Valenciano normativo con formas de la AVL (`esta`, `servix`, `vore`).
- El número 0 (`web/content/numeros/2026-10-26/`) es una muestra hecha solo con avisos de portal.edu.gva.es, aprobada el 2026-11-03.
