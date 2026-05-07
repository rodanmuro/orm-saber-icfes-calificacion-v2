# Bitacora 069_05_07_2026 11:10:06 validacion_reordenamiento_manual

## Que fue lo que se hizo
- Se revisaron los logs del backend para el error `500` al guardar el reordenamiento manual de una version de examen (`PATCH /api/v1/exams/{exam_id}/versions/{version_id}/reorder`).
- Se identifico el fallo en `src/backend/app/api/v1/endpoints/exams.py`: colision temporal de la restriccion unica `uq_exam_version_item_qnum` al reasignar `question_number` en una sola fase.
- Se implemento renumeracion en dos fases en el endpoint de reorder:
  - Fase 1: mover temporalmente los `question_number` a un rango alto.
  - Fase 2: reasignar `1..N` en el nuevo orden.
- Se agrego manejo de `IntegrityError` con `rollback` y respuesta `409` controlada.
- Se valido sintaxis del backend (`py_compile`).
- Se ejecutaron consultas en PostgreSQL para verificar que en `exam_version_id=7` no se cambiaron `item_id`, solo el orden de las preguntas.
- Se hizo validacion manual contra dos exportes CSV (antes/despues) y se confirmo consistencia de clave por `item_id`.

## Para que se hizo
- El objetivo fue dejar funcional y estable el reordenamiento manual de preguntas barajadas, sin romper la clave OMR ni cambiar los items asociados.

## Que problemas se presentaron
- Error `500 Internal Server Error` al guardar el orden.
- La causa real fue una violacion de unicidad durante `commit`, por duplicados temporales en `(exam_version_id, question_number)`.
- Hubo confusion inicial en comparacion manual por mezclar listados de versiones distintas, lo que daba la impresion de cambio de `item_id`.

## Como se resolvieron
- Se aplico estrategia transaccional segura de reordenamiento en dos pasos para eliminar colisiones temporales de `question_number`.
- Se reforzo el endpoint con control explicito de `IntegrityError` para evitar errores 500 no manejados.
- Se verifico en BD el estado de `exam_version_item` para `version_id=7`, confirmando:
  - mismo set de 40 `item_id`
  - misma respuesta correcta por `item_id`
  - solo cambio de posicion (`question_number`).

## Que continua
- Agregar prueba automatizada backend del endpoint de reorder para cubrir:
  - preservacion de set de `item_id`
  - preservacion de `correct_answer_mapped` por `item_id`
  - actualizacion correcta de `answer_key_json` tras reorder.
- Mantener uso de export CSV para verificacion operativa rapida por parte del docente.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
