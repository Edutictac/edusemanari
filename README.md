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
   permisos de administración ni de publicación, y es el mismo bot el que
   enviará el aviso de cada número publicado. En el canal Telegram puede
   exigir que sea administrador para recibir las publicaciones. Los
   administradores deben comunicar a la comunidad que sus mensajes pueden
   servir para elaborar el semanario y que recibirán un aviso cuando salga
   la edición.
4. Guardar el token fuera del repositorio, en `pass`. Nunca enviarlo por chat
   ni ponerlo como argumento de un comando.
5. Crear un entorno: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
6. Copiar `config.example.json` a `config.json` y escribir el nombre del bot
   en `bot_username` y la ruta de `pass` en `token_pass_entry`. En
   `announce_groups` van los grupos que reciben el aviso de cada edición;
   `@cv_tic` no se incluye porque es un canal de avisos, no un grupo del
   proyecto. `site_url` es la dirección pública de la web.
   `config.json` está excluido de Git.
7. Arrancar con `.venv/bin/python -m semanario.collect --config config.json`.
   El proceso lee el token en memoria desde `pass`, verifica la identidad del
   bot y comprueba que la privacidad esté desactivada antes de escuchar.

Para ejecución permanente en este equipo, la unidad `systemd/edusemanari-collector.service`
puede enlazarse en `~/.config/systemd/user/` y activarse con `systemctl --user`.
El servicio de recogida solo recoge datos; no publica en la web ni envía
mensajes. El aviso de cada edición lo envía el script de publicación.

El bot solo recibe mensajes **desde que entra en los grupos**. Telegram no
ofrece el historial anterior a un bot. Al arrancar, esta aplicación confirma
por `getMe` que el token pertenece al bot esperado, si se configura su nombre.

## Exportar una semana

`.venv/bin/python -m semanario.export_week --config config.json --week 2026-11-02`

La fecha es el lunes que identifica el número, en `Europe/Madrid`. Cada edición
recoge desde el domingo anterior a las 00:00, justo donde cerró la anterior,
hasta el sábado a las 23:59; el domingo se publica. Así lo que se habla el
domingo entra en la edición siguiente y no se pierde ningún día. El comando
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

### Aviso a los grupos

Al terminar de publicar, el mismo script avisa en los grupos de
`announce_groups` (hoy `@edutictac` y `@portaledu`). Antes de enviar comprueba
que la URL del número responde; espera hasta 5 minutos a que Pages refresque la
caché. El aviso se envía una sola vez por número y grupo; si se republica para
corregir algo, no se repite. Para publicar sin avisar:

`scripts/publish-pages.sh --no-announce`

Para forzar un número concreto o probar el texto sin enviarlo:

```
scripts/publish-pages.sh --week 2026-11-02
.venv/bin/python -m semanario.announce --config config.json --week 2026-11-02 --dry-run
```

El aviso no sale hasta que el número deja de ser un borrador. El canal
`@cv_tic` no recibe avisos. Si la publicación termina pero el aviso falla
(por ejemplo, porque la web tarda más de 5 minutos), se puede repetir sin
volver a publicar:

`.venv/bin/python -m semanario.announce --config config.json --week 2026-11-02`

### Avisos adaptados a cada grupo

Cada edición puede incluir `web/content/numeros/AAAA-MM-DD/avisos.json`, con
un perfil `general` y perfiles en `grupos` identificados por el nombre de Telegram
sin `@` (por ejemplo, `aules`, `comunitat_lliurex` o `portaledu`). Cada perfil
contiene `es` y `va`, con una `intro` y entre uno y tres `puntos`.

Son resúmenes editoriales revisables, basados en las piezas del número: Aules
prioriza Aules; LliureX, LliureX y software libre; Portaledu, gestión de la web del
centro. No es necesario rellenar tres puntos si solo hay una novedad relevante.
Los grupos sin perfil específico usan el resumen general. Los números antiguos
sin `avisos.json` conservan el aviso bilingüe sencillo.

El mensaje añade automáticamente número, fecha de publicación y enlace al número
completo. `announce_language` permite elegir `es` (por defecto) o `va` en
`config.json`. No modifica los destinatarios: siguen siendo solo los de
`announce_groups`. `--dry-run` muestra por separado el texto de cada grupo sin
leer credenciales ni enviar mensajes. Todos los textos se validan antes de enviar
el primero, incluido el límite de Telegram. Se conserva la protección contra
avisos repetidos por número y grupo.

### Estructura de un número

Cada número es una carpeta `web/content/numeros/AAAA-MM-DD/` con la fecha del
lunes que identifica la edición. La edición cubre del domingo anterior al
sábado y se publica el domingo siguiente (lunes + 6 días); la web muestra ese
periodo:

- `_index.md` y `_index.va.md`: `numero`, `date`, `draft`, editorial opcional
  en el cuerpo y lista `breves` (`texto` en Markdown y `url` opcional).
- Una pieza por fichero (`slug.md` y `slug.va.md`) con `title`, `entradilla`,
  `secciones`, `weight`, `destacado`, `fuentes` (`titulo`, `url`, `medio`) y
  `conversacion` (enlaces `https://t.me/...`).

La portada muestra primero la pieza destacada y las novedades oficiales, y después
la selección de las comunidades y los breves agrupados. Campos opcionales:

- `accion`: consejo práctico que sustituye al resumen repetido de la destacada.
- `oficial: false`: identifica una aportación comunitaria aunque pertenezca a una
  sección como Aules o LliureX. La procedencia explícita prevalece sobre la sección.
- `grupo_breve`: `gestion`, `aula` o `software`; sin este campo, se muestra en
  «Más breves».
- `desde` y `hasta` en el índice del número: permiten rotular un periodo excepcional
  sin llamarlo semana.

### Secciones

Las secciones viven en `web/content/secciones/<slug>/_index{,.va}.md` con
`title`, `weight` y `oficial`. Cada una tiene su página y su RSS.

- Oficiales (`oficial: true`): `lliurex`, `aules`, `itaca`, `normativa`,
  `formacion`, `programas`. Pensadas para lo que comunica el canal `@cv_tic`.
  En la portada se agrupan en el bloque «Novedades oficiales».
- De las comunidades: `ia`, `herramientas`, `aula`, `debates`. Forman la
  portada principal; la pieza con `destacado: true` abre el número.

Para añadir una sección basta con crear su carpeta con los dos `_index`.

### Fuentes

La lista pública de fuentes está en `web/data/fuentes.yaml` y se muestra en
«Cómo lo hacemos» y en el pie de todas las páginas. Para incorporar una fuente
nueva de Telegram hay que hacer dos cosas: añadirla en `groups` de
`config.json` (y meter el bot en el grupo o canal) y añadir su bloque en
`fuentes.yaml` con la descripción en los dos idiomas.

### Tipografía

Fraunces (titulares), Source Serif 4 (texto) y Public Sans (rótulos), servidas
desde `web/static/fonts/`, todas con licencia SIL Open Font License 1.1.
