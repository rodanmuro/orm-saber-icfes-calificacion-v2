# Bitacora 005_02_23_2026 09:09:25 customizacion_burbujas_question_item

## Que fue lo que se hizo
- Se amplió la customizacion de burbujas para soportar contenido y estilo parametrizable desde configuracion:
  - Etiquetas internas por columna (ejemplo `A/B/C/D`), con posibilidad de usar valores personalizados.
  - Estilo de etiqueta (`label_style`) configurable: gris, fuente y tamano.
- Se incorporo numeracion de preguntas por fila con parametros configurables:
  - cantidad de preguntas por grupo (`num_questions`),
  - numero inicial (`question_start_number`),
  - separacion entre centro del numero y centro de primera burbuja (`center_gap_mm`),
  - estilo de numero (`question_number_style`).
- Se implemento la nueva entidad `QuestionItem` como unidad logica de pregunta, agrupando:
  - numero de pregunta,
  - posicion del numero,
  - opciones (burbujas) asociadas.
- Se mantuvo compatibilidad hacia atras en JSON:
  - permanecen `bubbles` y `question_numbers`,
  - se agrega `question_items` como estructura adicional.
- Se regeneraron artefactos actualizados:
  - `src/backend/output/template_basica_omr_v1.pdf`
  - `src/backend/output/template_basica_omr_v1.json`

Archivos principales modificados/creados:
- `src/backend/app/modules/template_generator/contracts.py`
- `src/backend/app/modules/template_generator/bubble_layout.py`
- `src/backend/app/modules/template_generator/layout_engine.py`
- `src/backend/app/modules/template_generator/template_renderer.py`
- `src/backend/config/template.base.json`
- `src/backend/tests/test_bubble_layout.py`
- `src/backend/tests/test_pipeline.py`
- `src/backend/README.md`

## Para que se hizo
- Modelar la pregunta como unidad de dominio reutilizable para futuras fases de lectura OMR.
- Permitir variaciones de plantilla sin tocar logica central (letras, numeros, estilos, cantidad de preguntas).
- Preparar una salida estructurada mas semantica para backend y movil.

## Que problemas se presentaron
- Ajustes menores de pruebas al migrar de una salida basada en listas sueltas a una salida enriquecida con `QuestionItem`.
- Un test inicial no contemplaba correctamente la cantidad real de numeracion por filas en el caso configurado.

## Como se resolvieron
- Se actualizaron tests para validar tanto compatibilidad (`bubbles`, `question_numbers`) como el nuevo modelo (`question_items`).
- Se corrigieron expectativas de pruebas segun la configuracion real de filas/preguntas.
- Se agregaron pruebas de capacidad fisica para verificar si una cantidad de preguntas cabe o excede el alto util del bloque.

## Que continua
- Consolidar cierre formal de `ACT_0004`/`ACT_0005` segun trazabilidad documental pendiente.
- Evaluar mejoras de render para etiquetas internas (autoajuste si texto crece).
- Preparar el paso hacia lectura local de respuestas, aprovechando `QuestionItem` como unidad de evaluacion.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
