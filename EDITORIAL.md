# Diseño editorial del semanario

## Decisiones confirmadas

- Fuentes iniciales: grupos públicos `@edutictac` y `@portaledu`, y canal
  público `@cv_tic` cuando el bot tenga acceso a sus publicaciones.
- Periodicidad: semanal, zona `Europe/Madrid`.
- Ediciones: castellano y valenciano/catalán.
- Destino: web estática propia (Hugo) en EduTicTac Pages,
  `https://pages.edutictac.es/Edutictac/edusemanari/`.
- Secciones: los avisos contrastados en las webs de los servicios educativos
  van a secciones propias y se distinguen de las experiencias y debates de la
  comunidad. `@cv_tic` es un canal no oficial, aunque difunda avisos de Conselleria.
- Control: el sistema prepara borradores; una persona del equipo editorial los revisa antes de publicar.
- Avisos en Telegram: solo después de que el número esté publicado.

## Secuencia propuesta

1. **Cierre:** exportar desde el domingo 00:00, donde cerró la edición
   anterior, hasta el sábado 23:59. La edición se publica el domingo. Guardar
   la exportación en una carpeta privada y purgarla después del periodo de
   revisión.
2. **Selección:** recoger la mayoría de los temas educativos relevantes tratados
   en los grupos, agrupar las conversaciones repetidas y dar a cada tema el espacio
   adecuado: pieza principal, breve o resumen de dudas y debate. Incluir siempre
   las novedades de EduTicTac. La falta de un enlace externo no excluye un tema.
   Cada propuesta conserva, cuando exista, el enlace a la conversación original.
3. **Fuentes:** abrir las fuentes externas cuando las haya y priorizar las
   originales. Se admite una fuente secundaria identificada o la propia
   conversación pública para resumir experiencias, dudas, recursos, opiniones
   y avisos compartidos. Un mensaje demuestra que el tema se ha planteado;
   no demuestra que una herramienta funcione ni que una afirmación sea cierta.
   Si no hay fuente externa o no es accesible, atribuir la información al grupo
   o al medio y explicar qué no se ha podido comprobar. Si no hay enlace al
   mensaje, indicar la comunidad y el contexto sin inventar una URL.
4. **Redacción:** escribir piezas breves en castellano, diferenciando datos
   contrastados, información atribuida y dudas u opiniones de la comunidad.
   Registrar la procedencia y los límites de cada afirmación.
5. **Revisión independiente:** otra sesión de Claude recibe los mensajes y las
   fuentes disponibles, sin el contexto del redactor. Corrige o retira las
   afirmaciones presentadas como hechos sin respaldo y comprueba que las
   experiencias, dudas y avisos no contrastados estén atribuidos con claridad.
6. **Traducción:** una tercera sesión prepara valenciano/catalán a partir del
   texto revisado. Los enlaces y datos se comparan con la versión aprobada.
7. **Borrador web:** escribir ambas versiones en `web/content/numeros/AAAA-MM-DD/`
   con `draft: true`, en una rama propia del número.
8. **Aprobación:** revisión humana del número, las fuentes, las imágenes y la
   privacidad. Aprobar es quitar `draft: true`, fusionar la rama y ejecutar
   `scripts/publish-pages.sh`. El script publica la web y, solo cuando la URL
   responde, envía un aviso breve a los grupos participantes de
   `announce_groups`: `@edutictac`, `@portaledu`, `@aules`,
   `@comunitat_lliurex` y el canal `@cv_tic`. Cada destino recibe su resumen
   temático. Un mismo número no se avisa dos veces en el mismo destino.

## Reglas de publicación

- Enlazar la conversación pública y las fuentes consultadas cuando estén
  disponibles. Si falta un enlace, identificar la procedencia y explicar la
  limitación. Evitar atribuir opiniones a participantes sin su consentimiento.
- No incluir nombres, alias, fotos ni capturas de mensajes de participantes en
  el texto del semanario. Nombrar a quien creó un recurso propio solo cuando su
  atribución sea pública y pertinente.
- Distinguir «la web afirma que ofrece X» de «X funciona». La segunda frase
  exige una prueba propia, que esta primera versión no hace.
- No convertir discusiones o rumores en noticias por el hecho de aparecer
  repetidos. Las novedades de EduTicTac sí se incluyen siempre, con un tono
  informativo y sin exagerar lo que ofrecen.
- La actualidad tecnológica de interés para el profesorado, especialmente la de
  software libre, puede entrar como breve.
- Si una fuente no abre, buscar otra referencia o presentar el tema como
  información atribuida pendiente de contraste. Si contradice el borrador,
  corregirlo. Si un mensaje se borró, retirar lo que dependa solo de él.
- La cobertura amplia no implica reproducir todos los mensajes: se agrupan
  repeticiones y se excluyen datos personales, mensajes sin interés educativo,
  ataques personales y publicidad sin contenido útil. Los rumores no se
  presentan como hechos; una duda puede recogerse como pregunta abierta.
- Los avisos de difusión se adaptan a la temática de cada grupo: fecha de
  publicación, introducción breve, entre uno y tres puntos pertinentes y enlace
  al número completo. Se preparan en castellano y valenciano en `avisos.json`
  junto al número y se revisan antes de enviarlos. No se rellenan con novedades
  ajenas al grupo si hay menos material; se conservan las atribuciones y límites
  de las piezas originales.
- Ofrecer un canal visible para correcciones y retiradas.

## Estado de implementación

La recogida y exportación están implementadas. Faltan los módulos de
selección, verificación, redacción, traducción, escritura del borrador del
número y publicación de avisos. La web (maqueta, secciones y script de
publicación) está preparada. No hay publicación automática activa.
