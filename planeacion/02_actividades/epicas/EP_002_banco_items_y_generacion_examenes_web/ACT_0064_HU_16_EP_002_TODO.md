estado: done
prioridad: alta
sprint: S9
owner: por_definir

# ACT_0064 - Backend de exportacion PDF/DOCX por version publicada

## Objetivo tecnico
Implementar el flujo backend para generar salidas PDF y DOCX del cuadernillo de preguntas desde una version publicada de examen, conservando orden y trazabilidad de version.

## Tareas implementables
- [x] Definir contrato API para exportacion PDF de version publicada.
- [x] Implementar servicio de render PDF consumiendo `exam`, `exam_version` y `exam_version_item`.
- [x] Resolver render de contenido enriquecido base (texto, imagenes, tablas y ecuaciones en modo compatible).
- [x] Agregar encabezado con trazabilidad (`exam_code`, `version_code`, `seed_shuffle`, fecha de generacion).
- [x] Exponer endpoint de descarga (`application/pdf`) sin persistencia adicional.
- [x] Exponer endpoint de descarga DOCX (`application/vnd.openxmlformats-officedocument.wordprocessingml.document`).
- [x] Agregar pruebas de integracion backend de exportacion (PDF/DOCX exitoso y errores por version no encontrada).

## Evidencias esperadas
- Endpoints operativos que retornan PDF y DOCX validos.
- Salidas consistentes con el orden de preguntas de la version publicada.
- Pruebas backend en verde para contratos principales de exportacion.

## Criterio de terminado
El backend puede exportar cualquier version publicada a PDF y DOCX, sin modificar datos del examen.
El alcance de esta actividad corresponde al cuadernillo de preguntas (no a la hoja OMR de respuestas).
