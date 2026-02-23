estado: todo
prioridad: alta
sprint: S2
owner: por_definir

# ACT_0014 - Endpoint backend para recepcion de foto y lectura OMR

## Objetivo tecnico
Exponer en FastAPI un endpoint que reciba foto desde movil y retorne JSON de lectura por pregunta.

## Tareas implementables
- [ ] Definir contrato de request/response para carga de imagen y referencia de template.
- [ ] Implementar endpoint multipart para recibir archivo de foto.
- [ ] Orquestar pipeline actual (carga, alineacion, clasificacion, armado de JSON) dentro del endpoint.
- [ ] Retornar errores controlados con mensajes legibles para casos invalidos.

## Evidencias esperadas
- Endpoint implementado en `src/backend`.
- Ejecucion demostrable que recibe una imagen y devuelve JSON de resultados.

## Criterio de terminado
Desde cliente externo se puede enviar una foto al backend y recibir respuesta OMR estructurada o error claro.
