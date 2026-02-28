# Bitacora 027_02_28_2026 10:29:42 seccion13_modulo_banco_items

## Que fue lo que se hizo
- Se actualizo el documento fundacional en `planeacion/descripcion_fundacional_proyecto.md` agregando la **Seccion 13** para el modulo de creacion de preguntas (banco de items).
- Se incorporo una definicion tecnica del alcance del modulo: editor estructurado, opciones por pregunta, manejo de imagenes, manejo de ecuaciones y exportacion de examen.
- Se registro el criterio no funcional minimo de esta fase: **versionado de items**.
- Se dejo explicitamente documentado que queda pendiente definir el contrato con OMR para:
  - mapeo de `correct_answer`,
  - mapeo del orden de preguntas hacia `exam_identifier`/plantilla.

## Para que se hizo
- Alinear la evolucion del proyecto con una arquitectura de plataforma integral (creacion + aplicacion + calificacion).
- Evitar ambiguedad futura sobre el alcance del banco de preguntas y su integracion con OMR.
- Mantener consistencia con el enfoque tecnico del documento fundacional.

## Que problemas se presentaron
- El resumen original tenia partes con lenguaje comercial y faltaba una forma normativa para incorporarlo al fundacional.
- No estaba explicito, dentro del fundacional, el punto de contrato tecnico pendiente entre modulo de preguntas y modulo OMR.

## Como se resolvieron
- Se redacto la nueva seccion con tono tecnico/normativo, eliminando lenguaje comercial.
- Se estructuro la seccion en subapartados claros (alcance, frontend de autoria, modelo de datos, assets/ecuaciones, criterio no funcional, integracion con OMR, relacion con arquitectura general).
- Se incluyo el pendiente de contrato como requisito explicito para iteraciones siguientes.

## Que continua
- Definir el contrato tecnico formal entre banco de items y OMR (mapa `correct_answer`, orden, version de examen).
- Crear historias de usuario y actividades para implementacion incremental del modulo de banco de items.
- Establecer validaciones minimas de consistencia entre examen generado y plantilla OMR usada en calificacion.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
