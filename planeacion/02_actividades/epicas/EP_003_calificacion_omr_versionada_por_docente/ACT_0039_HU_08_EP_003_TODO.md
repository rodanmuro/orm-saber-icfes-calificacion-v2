estado: todo
prioridad: media
sprint: S4
owner: por_definir

# ACT_0039 - Persistencia de artefactos y consulta de auditoria

## Objetivo tecnico
Registrar y consultar artefactos tecnicos por intento OMR (imagen y salidas de trazabilidad) para soporte de revision y auditoria operativa.

## Tareas implementables
- [ ] Definir entidad `omr_attempt_artifact` con tipo, ruta y metadatos de integridad.
- [ ] Registrar artefactos producidos por pipeline (`result.json`, `ratios.csv`, `auxiliary.ratios.csv`, imagen).
- [ ] Exponer endpoint de consulta de artefactos por intento.
- [ ] Estandarizar nomenclatura de tipos de artefacto para consumo de cliente.
- [ ] Validar disponibilidad de artefactos en escenarios de exito y error controlado.

## Evidencias esperadas
- Persistencia de artefactos vinculada a cada intento.
- Consulta estructurada de evidencias para auditoria.
- Evidencia de rutas y checksums almacenados por intento.

## Criterio de terminado
Cada intento OMR tiene evidencias tecnicas consultables y trazables para soporte de revision posterior.
