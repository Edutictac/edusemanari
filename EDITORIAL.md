# Diseño editorial del semanario

## Decisiones confirmadas

- Fuentes iniciales: grupos públicos `@edutictac` y `@portaledu`, y canal
  público `@cv_tic` cuando el bot tenga acceso a sus publicaciones.
- Periodicidad: semanal, zona `Europe/Madrid`.
- Ediciones: castellano y valenciano/catalán.
- Destino: web estática propia (Hugo) en EduTicTac Pages,
  `https://pages.edutictac.es/Edutictac/edusemanari/`.
- Secciones: las comunicaciones del canal oficial van a secciones propias
  (LliureX, Aules, ITACA, normativa, formación, programas) y se presentan aparte
  de lo que surge en los grupos de la comunidad.
- Control: el sistema prepara borradores; una persona del equipo editorial los revisa antes de publicar.
- Avisos en Telegram: solo después de que el número esté publicado.

## Secuencia propuesta

1. **Cierre:** exportar la semana de lunes 00:00 a domingo 23:59. Guardar la
   exportación en una carpeta privada y purgarla después del periodo de revisión.
2. **Selección:** Claude elige hasta cinco temas a partir de los mensajes. Cada
   propuesta conserva los enlaces exactos de Telegram que la originaron.
3. **Fuentes:** extraer y abrir los enlaces externos originales. Un mensaje del
   grupo es una pista; no demuestra que el producto funcione ni que la noticia
   sea cierta. Si falta fuente primaria accesible, el tema queda fuera.
4. **Redacción:** Claude escribe piezas breves en castellano, con un registro de
   afirmaciones y el enlace que respalda cada una.
5. **Revisión independiente:** otra sesión de Claude recibe los mensajes y las
   fuentes originales, sin el contexto del redactor. Elimina afirmaciones que
   no pueda confirmar y rechaza la pieza si queda sin sustancia.
6. **Traducción:** una tercera sesión prepara valenciano/catalán a partir del
   texto revisado. Los enlaces y datos se comparan con la versión aprobada.
7. **Borrador web:** escribir ambas versiones en `web/content/numeros/AAAA-MM-DD/`
   con `draft: true`, en una rama propia del número.
8. **Aprobación:** revisión humana del número, las fuentes, las imágenes y la
   privacidad. Aprobar es quitar `draft: true`, fusionar la rama y ejecutar
   `scripts/publish-pages.sh`; solo entonces enviar un aviso breve a
   los grupos o canales autorizados.

## Reglas de publicación

- Enlazar la conversación pública y las fuentes consultadas al pie de cada
  pieza. Evitar atribuir opiniones a participantes sin su consentimiento.
- No incluir nombres, alias, fotos ni capturas de mensajes de participantes en
  el texto del semanario. Nombrar a quien creó un recurso propio solo cuando su
  atribución sea pública y pertinente.
- Distinguir «la web afirma que ofrece X» de «X funciona». La segunda frase
  exige una prueba propia, que esta primera versión no hace.
- No convertir discusiones, rumores o mensajes promocionales en noticias por
  el hecho de que aparezcan repetidos.
- Si una fuente no abre, cambia o contradice el borrador, retirar la
  afirmación. Si un mensaje se borró, retirarlo de la selección.
- Ofrecer un canal visible para correcciones y retiradas.

## Estado de implementación

La recogida y exportación están implementadas. Faltan los módulos de
selección, verificación, redacción, traducción, escritura del borrador del
número y publicación de avisos. La web (maqueta, secciones y script de
publicación) está preparada. No hay publicación automática activa.
