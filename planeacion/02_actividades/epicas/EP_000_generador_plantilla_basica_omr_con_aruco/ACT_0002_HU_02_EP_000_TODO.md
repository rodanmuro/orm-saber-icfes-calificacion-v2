estado: todo
prioridad: alta
sprint: S1
owner: por_definir

# ACT_0002 - Integrar ArUco en esquinas de forma configurable

## Objetivo tecnico
Generar y ubicar 4 ArUco en esquinas logicas usando parametros configurables de diccionario, tamano y offset.

## Tareas implementables
- [ ] Parametrizar `aruco_dictionary`, IDs permitidos y `marker_size`.
- [ ] Parametrizar offsets por esquina respecto a margenes.
- [ ] Implementar validacion para evitar ArUco fuera del area imprimible.
- [ ] Exponer coordenadas finales de ArUco para metadatos.

## Evidencias esperadas
- Plantilla visual con 4 ArUco visibles.
- Coordenadas de ArUco disponibles para exportacion.

## Criterio de terminado
El sistema permite cambiar diccionario/tamano/offset de ArUco por config y mantiene 4 marcadores validos en la salida.
