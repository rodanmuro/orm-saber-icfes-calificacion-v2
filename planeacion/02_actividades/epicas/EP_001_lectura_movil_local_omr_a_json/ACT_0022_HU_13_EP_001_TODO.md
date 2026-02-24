estado: todo
prioridad: alta
sprint: S2
owner: por_definir

# ACT_0022 - Contrato comun de lector OMR y estrategia de motor

## Objetivo tecnico
Desacoplar el backend para soportar multiples motores de lectura (`classic` y `gemini`) bajo un contrato unico.

## Tareas implementables
- [ ] Definir interfaz/contrato del lector (entrada, salida y errores).
- [ ] Adaptar motor clasico actual a la interfaz sin cambiar su comportamiento.
- [ ] Implementar selector por configuracion (`OMR_READER_BACKEND`).
- [ ] Mantener endpoint y esquema JSON de salida sin cambios.

## Evidencias esperadas
- Nuevo modulo de contrato/estrategia en backend.
- Prueba minima que confirme que `classic` sigue funcionando por la nueva interfaz.

## Criterio de terminado
El backend puede resolver el lector por configuracion y responder con el contrato existente usando `classic`.
