# AGENTS.md · EduSemanari

Semanario bilingüe (castellano y valenciano) a partir de comunidades docentes de Telegram.

## Estructura

- `semanario/`: recogida (`collect.py`), almacenamiento SQLite (`storage.py`) y exportación semanal (`export_week.py`).
- `web/`: web Hugo. Contenido en `web/content/`, plantillas en `web/layouts/`, estilos en `web/assets/css/`.
- `scripts/publish-pages.sh`: publica la web en EduTicTac Pages (rama `pages` del remoto Forgejo `edutictac`).
- `systemd/edusemanari-collector.service`: unidad de usuario enlazada con `systemctl --user link`.

## Comandos

- Pruebas: `python3 -m unittest discover -s tests -v`.
- Vista previa: `hugo server -D --source web`.
- Compilación: `hugo --source web --minify`.

## Reglas

- Nunca mostrar el token del bot ni pasarlo como argumento. Vive en `pass`.
- `config.json`, `*.sqlite3*` y `exports/` contienen datos privados: no imprimirlos ni versionarlos.
- No publicar nada sin aprobación humana. Todo número nuevo se crea con `draft: true`.
- Seguir `EDITORIAL.md`: contrastar cada dato en su fuente, sin nombres ni alias de participantes.
- Toda pieza y todo texto de interfaz existen en los dos idiomas (`*.md` y `*.va.md`, `i18n/es.toml` y `i18n/va.toml`). Valenciano normativo con formas de la AVL (`esta`, `servix`, `vore`).
- El número 0 (`web/content/numeros/2026-10-26/`) es una muestra hecha solo con avisos de portal.edu.gva.es y sigue en borrador hasta su aprobación.
