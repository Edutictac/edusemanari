# EduSemanari

Primera pieza del semanario: un bot dedicado recoge los mensajes de `@edutictac`
y `@portaledu`, además de las publicaciones del canal `@cv_tic` cuando el bot
tenga acceso a él, para preparar una edición semanal en castellano y
valenciano/catalán.
Ningún mensaje se publica automáticamente: cada número se prepara como borrador
y solo se publica después de una revisión humana.

El proyecto tiene dos partes:

- `semanario/`: recogida de Telegram y exportación semanal (Python).
- `web/`: la web del semanario (Hugo), que se publica en EduTicTac Pages:
  `https://pages.edutictac.es/Edutictac/edusemanari/`.

## Preparación

1. Crear un bot **nuevo** con `@BotFather` (`/newbot`). No reutilizar los bots
   que ya gestionan avisos o publicaciones.
2. En `@BotFather`, usar `/setprivacy` y elegir **Disable** para este bot.
3. Añadir el bot a `@edutictac`, `@portaledu` y al canal `@cv_tic`. En los grupos no requiere
   permisos de administración ni de publicación. En el canal Telegram puede
   exigir que sea administrador para recibir las publicaciones. Los
   administradores deben comunicar a la comunidad que sus mensajes pueden
   servir para elaborar el semanario.
4. Guardar el token fuera del repositorio, en `pass`. Nunca enviarlo por chat
   ni ponerlo como argumento de un comando.
5. Crear un entorno: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
6. Copiar `config.example.json` a `config.json` y escribir el nombre del bot
   en `bot_username` y la ruta de `pass` en `token_pass_entry`.
   `config.json` está excluido de Git.
7. Arrancar con `.venv/bin/python -m semanario.collect --config config.json`.
   El proceso lee el token en memoria desde `pass`, verifica la identidad del
   bot y comprueba que la privacidad esté desactivada antes de escuchar.

Para ejecución permanente en este equipo, la unidad `systemd/edusemanari-collector.service`
puede enlazarse en `~/.config/systemd/user/` y activarse con `systemctl --user`.
El servicio solo recoge datos; no publica en la web ni envía mensajes.

El bot solo recibe mensajes **desde que entra en los grupos**. Telegram no
ofrece el historial anterior a un bot. Al arrancar, esta aplicación confirma
por `getMe` que el token pertenece al bot esperado, si se configura su nombre.

## Exportar una semana

`.venv/bin/python -m semanario.export_week --config config.json --week 2026-11-02`

La fecha es el lunes que inicia la semana, en `Europe/Madrid`. El comando
escribe JSON a stdout, con texto, fecha, grupo y enlace al mensaje original.
Para guardar el fichero, redirigirlo a una ruta privada; el contenido puede
contener datos personales de la conversación.

## Datos y límites

- Solo se admiten mensajes de las fuentes configuradas. No se guarda el
  identificador, nombre ni alias de quien escribe.
- Se guardan texto y pies de foto, no archivos, imágenes, contactos ni otros
  adjuntos. Los mensajes editados actualizan la copia local.
- El bot no recibe avisos fiables de todos los mensajes borrados. Antes de
  publicar, la redacción deberá volver a abrir el enlace original.
- Cada arranque elimina mensajes con más de 35 días. No se registra el contenido
  de los mensajes en la salida del proceso.
- Los enlaces a mensajes funcionan si la fuente sigue siendo pública. El bot
  puede funcionar en grupos privados, pero esta configuración inicial exige
  nombres públicos para evitar enlazar mensajes que los lectores no pueden ver.

## Pruebas

`python3 -m unittest discover -s tests -v`

## Web

Hugo extended (probado con 0.131). Castellano en la raíz y valenciano en `/va/`.

- Vista previa con borradores: `hugo server -D --source web`.
- Compilación de producción: `hugo --source web --minify`. Los números y piezas
  con `draft: true` no se incluyen.
- Publicación: `scripts/publish-pages.sh`. Compila y sube el resultado a la rama
  `pages` del remoto `edutictac` (Forgejo). Se niega a publicar si `web/` tiene
  cambios sin commit. EduTicTac Pages guarda en caché la rama que sirve
  durante 5 minutos y el contenido durante 1 minuto: un cambio puede tardar
  ese tiempo en verse.

### Estructura de un número

Cada número es una carpeta `web/content/numeros/AAAA-MM-DD/` con la fecha del
lunes de la semana:

- `_index.md` y `_index.va.md`: `numero`, `date`, `draft`, editorial opcional
  en el cuerpo y lista `breves` (`texto` en Markdown y `url` opcional).
- Una pieza por fichero (`slug.md` y `slug.va.md`) con `title`, `entradilla`,
  `secciones`, `weight`, `destacado`, `fuentes` (`titulo`, `url`, `medio`) y
  `conversacion` (enlaces `https://t.me/...`).

### Secciones

Las secciones viven en `web/content/secciones/<slug>/_index{,.va}.md` con
`title`, `weight` y `oficial`. Cada una tiene su página y su RSS.

- Oficiales (`oficial: true`): `lliurex`, `aules`, `itaca`, `normativa`,
  `formacion`, `programas`. Pensadas para lo que comunica el canal `@cv_tic`.
  En la portada se agrupan en el bloque «Novedades oficiales».
- De las comunidades: `ia`, `herramientas`, `aula`, `debates`. Forman la
  portada principal; la pieza con `destacado: true` abre el número.

Para añadir una sección basta con crear su carpeta con los dos `_index`.

### Tipografía

Fraunces (titulares), Source Serif 4 (texto) y Public Sans (rótulos), servidas
desde `web/static/fonts/`, todas con licencia SIL Open Font License 1.1.
