# Semanario EduTicTac · recogida de Telegram

Primera pieza del semanario: un bot dedicado recoge los mensajes de `@edutictac`
y `@portaledu`, además de las publicaciones del canal `@cv_tic` cuando el bot
tenga acceso a él, para preparar una edición semanal en castellano y
valenciano/catalán.
Ningún mensaje se publica automáticamente. La redacción y los borradores de
WordPress se incorporarán después de probar la recogida con el bot real.

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
El servicio solo recoge datos; no escribe en WordPress ni envía mensajes.

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
