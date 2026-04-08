# HU_016 - Exportacion de examen imprimible en PDF (EP_002)

## Trazabilidad
- Epica asociada: `EP_002_banco_items_y_generacion_examenes_web.md`
- Dependencias: `HU_006`.

## Historia de usuario
**Como** docente  
**Quiero** exportar una version publicada de examen a PDF imprimible  
**Para** aplicar la prueba en aula mediante un cuadernillo de preguntas estable y trazable, separado de la hoja OMR de respuestas.

## Criterios de aceptacion
1. Solo se puede exportar una version ya publicada del examen.
2. El PDF incluye: titulo del examen, codigo de examen, version, preguntas y opciones en el orden de la version publicada.
3. El PDF preserva contenido enriquecido de los items (texto, imagenes, ecuaciones y tablas) dentro de limites de impresion A4.
4. La exportacion mantiene trazabilidad: `exam_id`, `exam_code`, `version_id`, `version_code`, `seed_shuffle`.
5. El docente puede descargar el PDF desde frontend con una accion explicita.
6. La exportacion no altera la version publicada ni el banco de items (operacion de solo lectura).
7. Ante errores de render, el sistema devuelve mensaje claro y no bloquea el flujo de armado.

## Evidencia esperada
- Endpoint backend funcional para exportar una version a PDF.
- Descarga de PDF desde frontend en la seccion de armado de examen.
- Evidencia de que dos versiones distintas generan PDFs consistentes con su orden/mapeo.

## Notas
- PDF es el formato primario de aplicacion; `DOCX` queda fuera de alcance inicial.
- El criterio de calidad prioriza estabilidad de impresion sobre edicion posterior.
- Esta HU corresponde al cuadernillo/cuestionario de preguntas; la hoja OMR se gestiona en el flujo de plantilla y lectura OMR.
