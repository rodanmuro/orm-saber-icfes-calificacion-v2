# HU_016 - Exportacion de examen por version (PDF/DOCX) (EP_002)

## Trazabilidad
- Epica asociada: `EP_002_banco_items_y_generacion_examenes_web.md`
- Dependencias: `HU_006`.

## Historia de usuario
**Como** docente  
**Quiero** exportar una version publicada de examen a formatos de salida (PDF y DOCX)  
**Para** aplicar la prueba en aula con cuadernillo trazable y contar con una salida tabular para revision, separado de la hoja OMR de respuestas.

## Criterios de aceptacion
1. Solo se puede exportar una version ya publicada del examen.
2. PDF y DOCX incluyen: titulo del examen, codigo de examen, version, preguntas y opciones en el orden de la version publicada.
3. El PDF/DOCX preserva contenido enriquecido base de los items (texto, imagenes, ecuaciones y tablas) dentro de limites de impresion.
4. La exportacion mantiene trazabilidad: `exam_id`, `exam_code`, `version_id`, `version_code`, `seed_shuffle`.
5. El docente puede descargar desde frontend:
   - PDF del cuadernillo.
   - DOCX del cuadernillo.
6. La exportacion no altera la version publicada ni el banco de items (operacion de solo lectura).
7. Ante errores de exportacion, el sistema devuelve mensaje claro y no bloquea el flujo de armado.

## Evidencia esperada
- Endpoints backend funcionales para exportar una version a PDF y DOCX.
- Descarga de PDF y DOCX desde frontend en la seccion de armado de examen.
- Evidencia de que dos versiones distintas generan PDFs consistentes con su orden/mapeo.

## Notas
- PDF es el formato primario de aplicacion; DOCX se ofrece como salida editable complementaria.
- El criterio de calidad prioriza estabilidad de impresion en PDF sobre fidelidad pixel-perfect en formatos editables.
- Esta HU corresponde al cuadernillo/cuestionario de preguntas; la hoja OMR se gestiona en el flujo de plantilla y lectura OMR.
