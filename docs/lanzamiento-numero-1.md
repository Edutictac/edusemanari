# Lanzamiento del número 1

Fecha recomendada: domingo 15 de noviembre de 2026, a las 10:00 (Europe/Madrid).
Es una recomendación editorial; no hay una tarea de lanzamiento programada.

## Preparación comprobada

- Edición especial del 1 al 14 de noviembre; fecha de publicación: 15 de noviembre.
- Identificador técnico y URL: `2026-11-02`. No sustituirlo por la fecha de publicación.
- Avisos específicos en `web/content/numeros/2026-11-02/avisos.json`, en castellano y valenciano.
- Destinatarios locales: EduTicTac, Portaledu, Aules, Comunitat LliureX y el canal CvTIC (`@cv_tic`).
- Idioma de envío configurado: castellano (`announce_language: es`).
- Permisos del bot comprobados en los cuatro grupos y el canal; ningún aviso del número 1 enviado.
- Kora se incluye como breve atribuido a Computer Hoy, sin dar por comprobada su disponibilidad, con el criterio editorial ampliado. La explicación de los estados de Appsedu se integra en la noticia del catálogo.

## Última revisión del cierre

El sábado termina a las 23:59. Antes de lanzar el domingo, revisar si los últimos
mensajes aportan novedades que deban incorporarse. La segunda semana se exporta
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
