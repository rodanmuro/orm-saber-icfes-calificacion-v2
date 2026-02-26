estado: todo
prioridad: alta
sprint: S4
owner: por_definir

# ACT_0031 - Unificar fuente de verdad de plantilla v2

## Objetivo tecnico
Reducir la duplicidad conceptual entre `template.basica_omr_v2.json` (config base) y `template_basica_omr_v2_wireframe.json` (metadata runtime), definiendo una arquitectura mantenible para plantillas customizables.

## Tareas implementables
- [ ] Definir decision de arquitectura: fuente unica directa o compilacion formalizada.
- [ ] Documentar contrato de datos de plantilla (campos obligatorios y opcionales).
- [ ] Alinear scripts de generacion con contrato seleccionado.
- [ ] Garantizar que render PDF y lector OMR consuman la misma fuente runtime sin desvio.
- [ ] Agregar validaciones automaticas de coherencia geometrica (metadata vs PDF renderizado).
- [ ] Actualizar README y documentacion backend con flujo definitivo.

## Evidencias esperadas
- Documento de decision tecnica actualizado en `planeacion/`.
- Scripts ajustados en `src/backend/app/modules/template_generator/scripts/`.
- Pruebas/validaciones de coherencia agregadas en `src/backend/tests/`.
- Flujo reproducible de generacion y lectura para plantilla v2.

## Criterio de terminado
La arquitectura de plantillas queda definida, documentada y ejecutable sin ambiguedad sobre cual archivo es la fuente de verdad en runtime.
