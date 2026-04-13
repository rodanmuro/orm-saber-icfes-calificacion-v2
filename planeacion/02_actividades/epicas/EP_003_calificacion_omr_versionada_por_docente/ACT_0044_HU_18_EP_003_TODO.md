estado: todo
prioridad: media
sprint: S5
owner: por_definir

# ACT_0044 - Endpoint de listado de intentos calificados

## Objetivo tecnico
Exponer un endpoint que liste intentos OMR calificados con metadatos para el tablero web.

## Tareas implementables
- [ ] Definir contrato de listado (exam, version, estudiante, grupo, timestamp, estado).
- [ ] Incluir rutas a imagen/evidencias cuando existan.
- [ ] Implementar paginacion basica.
- [ ] Documentar el endpoint y ejemplos de respuesta.

## Evidencias esperadas
- Endpoint funcional probado con datos dummy.
- Respuesta consistente con el tablero web.

## Criterio de terminado
El frontend puede listar intentos calificados sin depender de consultas manuales.
