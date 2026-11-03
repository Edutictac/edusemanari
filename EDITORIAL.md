# Diseño editorial del semanario

## Decisiones confirmadas

- Fuentes iniciales: grupos públicos `@edutictac` y `@portaledu`, y canal
  público `@cv_tic` cuando el bot tenga acceso a sus publicaciones.
- Periodicidad: semanal, zona `Europe/Madrid`.
- Ediciones: castellano y valenciano/catalán.
- Destino: WordPress de `edutictac.es`, aprovechando su instalación multisite.
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
7. **WordPress:** subir ambas versiones como borradores, con una portada de
   número y enlaces entre idiomas. No usar `post_status=publish` en este flujo.
8. **Aprobación:** revisión humana del número, las fuentes, las imágenes y la
   privacidad. Publicar desde WordPress; solo entonces enviar un aviso breve a
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
selección, verificación, redacción, traducción, creación de borradores en
WordPress y publicación de avisos. No hay publicación automática activa.
