# Lanzamiento del número 1

Lanzamiento autorizado para el domingo 15 de noviembre de 2026, a las 10:00
(Europe/Madrid), mediante `edusemanari-issue-1.timer` (systemd de usuario).
Publicación anticipada de la web autorizada sin avisos; la difusión sigue a las 10:00.

## Preparación comprobada

- Edición especial del 1 al 14 de noviembre; fecha de publicación: 15 de noviembre.
- Identificador técnico y URL: `2026-11-02`. No sustituirlo por la fecha de publicación.
- Avisos específicos en `web/content/numeros/2026-11-02/avisos.json`, en castellano y valenciano.
- Destinatarios locales: EduTicTac, Portaledu, Aules, Comunitat LliureX y el canal CvTIC (`@cv_tic`).
- Idioma de envío configurado: valenciano (`announce_language: va`), por indicación expresa del usuario.
- Permisos del bot comprobados en los cuatro grupos y el canal; ningún aviso del número 1 enviado.
- Kora se incluye como breve atribuido a Computer Hoy y anunciado para 2027, con el criterio editorial ampliado. La explicación de los estados de Appsedu se integra en la noticia del catálogo.

## Última revisión del cierre

La tarea publica la versión revisada y guardada en Git; no añade contenido por
su cuenta. El sábado termina a las 23:59. Si se hace una última revisión editorial,
comprobar si los últimos mensajes aportan novedades que deban incorporarse. La segunda semana se exporta
con `--week 2026-11-09`; `2026-11-02` sigue siendo el identificador de publicación.
Las exportaciones son privadas: no imprimirlas ni versionarlas. Si se incorpora
contenido, actualizar los dos idiomas y los avisos afectados, verificar y guardar
los cambios en un nuevo commit.

## Lanzamiento manual

Desde la raíz del repositorio, revisar los cinco mensajes sin enviar:

```bash
.venv/bin/python -m semanario.announce --config config.json --week 2026-11-02 --dry-run --wait 0
```

Una vez aprobado el cierre, ejecutar estos pasos, deteniéndose ante cualquier error:

```bash
git push origin main
git push edutictac main
scripts/publish-pages.sh --week 2026-11-02
```

El último comando publica y después envía los avisos. No ejecutarlo para una
simple comprobación. Espera a que la URL responda y omite los grupos que ya
recibieron el aviso. No usar `--force` en un lanzamiento normal.

Si la web se publica pero falla algún aviso, reintentar solo el envío:

```bash
.venv/bin/python -m semanario.announce --config config.json --week 2026-11-02
```

Si se quiere actualizar la web antes de difundirla, publicar con `--no-announce`
y ejecutar el comando anterior a la hora elegida. La fecha mostrada en el aviso
procede del número, no del reloj del servidor.

## Tarea programada

Unidades de usuario: `systemd/edusemanari-issue-1.service` y
`systemd/edusemanari-issue-1.timer`. Es una ejecución única y persistente: si el
equipo está apagado a la hora prevista, se ejecutará al volver a estar disponible.
Debe estar encendido y conectado para cumplir la hora.

El servicio utiliza una credencial cifrada de systemd con caducidad, preparada
localmente; no requiere abrir `pass` durante el lanzamiento. El cifrado no se
versiona. `scripts/launch-issue-1.sh` comprueba que `main` esté limpia, valida los
avisos y la credencial, sube las fuentes y publica con los avisos habilitados.
La protección por número y destino evita reenviar los avisos ya completados.

Comprobar y cancelar la tarea:

```bash
systemctl --user list-timers edusemanari-issue-1.timer
systemctl --user disable --now edusemanari-issue-1.timer
```

Registro de ejecución:

```bash
journalctl --user -u edusemanari-issue-1.service
```
