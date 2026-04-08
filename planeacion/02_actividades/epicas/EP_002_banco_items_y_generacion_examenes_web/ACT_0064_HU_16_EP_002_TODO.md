estado: todo
prioridad: alta
sprint: S9
owner: por_definir

# ACT_0064 - Backend de exportacion PDF por version publicada

## Objetivo tecnico
Implementar el flujo backend para generar un PDF imprimible del cuadernillo de preguntas desde una version publicada de examen, conservando orden y trazabilidad de version.

## Tareas implementables
- [ ] Definir contrato API para exportacion PDF de version publicada.
- [ ] Implementar servicio de render PDF (A4) consumiendo `exam`, `exam_version` y `exam_version_item`.
- [ ] Resolver render de contenido enriquecido base (texto, imagenes, tablas y ecuaciones en modo compatible).
- [ ] Agregar encabezado con trazabilidad (`exam_code`, `version_code`, `seed_shuffle`, fecha de generacion).
- [ ] Exponer endpoint de descarga (`application/pdf`) sin persistencia adicional.
- [ ] Agregar pruebas de integracion backend del endpoint (caso exitoso y errores por version no encontrada/no publicada).

## Evidencias esperadas
- Endpoint operativo que retorna PDF valido.
- PDF consistente con el orden de preguntas de la version publicada.
- Pruebas backend en verde para contratos principales de exportacion.

## Criterio de terminado
El backend puede exportar cualquier version publicada a PDF imprimible, sin modificar datos del examen.
El alcance de esta actividad corresponde al cuadernillo de preguntas (no a la hoja OMR de respuestas).
