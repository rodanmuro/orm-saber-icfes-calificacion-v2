# HU_006 - Generacion de version de examen con barajado (EP_002)

## Trazabilidad
- Epica asociada: `EP_002_banco_items_y_generacion_examenes_web.md`
- Referencia de dominio: `bitacoras/028_02_28_2026_planeacion_decisiones_arquitectura_entidades_docente_examen.md`

## Historia de usuario
**Como** docente  
**Quiero** generar versiones de un examen con orden de preguntas y/o opciones barajadas  
**Para** evitar examenes identicos entre estudiantes y reducir copia.

## Criterios de aceptacion
1. Puedo crear un examen y asociar preguntas desde el banco de items.
2. Puedo publicar una version de examen inmutable para aplicacion.
3. La version puede variar orden de preguntas y/o orden de opciones por pregunta.
4. El sistema conserva trazabilidad del mapeo de respuestas correctas despues del barajado.
5. Dos versiones del mismo examen pueden coexistir sin perder consistencia de calificacion.

## Evidencia esperada
- Modelo de datos para `exam`, `exam_item`, `exam_version`, `exam_version_item`.
- Endpoints para crear examen, asociar items y publicar version.
- Evidencia de dos versiones del mismo examen con diferente orden/mapeo.

## Notas
- La version publicada es la unidad valida de aplicacion y posterior calificacion OMR.
