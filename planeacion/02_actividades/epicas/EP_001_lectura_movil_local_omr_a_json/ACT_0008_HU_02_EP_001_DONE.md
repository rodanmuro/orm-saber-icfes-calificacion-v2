estado: done
prioridad: alta
sprint: S2
owner: codex

# ACT_0008 - Deteccion ArUco y correccion de perspectiva

## Objetivo tecnico
Implementar deteccion de los 4 ArUco y homografia para normalizar fotos al plano de plantilla.

## Tareas implementables
- [x] Implementar detector ArUco configurable segun `aruco_dictionary_name`.
- [x] Mapear esquinas detectadas a la geometria esperada de plantilla.
- [x] Aplicar transformacion de perspectiva y obtener imagen corregida.
- [x] Definir errores controlados para deteccion insuficiente o geometria inconsistente.

## Evidencias esperadas
- Modulo de alineacion en `src/backend`:
  - `src/backend/app/modules/omr_reader/alignment.py`
- CLI para generar imagen corregida:
  - `src/backend/app/modules/omr_reader/scripts/align_photo.py`
- Errores especificos de etapa:
  - `src/backend/app/modules/omr_reader/errors.py`
- Contrato de salida de alineacion:
  - `src/backend/app/modules/omr_reader/contracts.py`
- Documentacion de uso:
  - `src/backend/README.md`

## Criterio de terminado
Con foto valida, se obtiene imagen alineada; con foto invalida, el sistema retorna error legible sin cierre inesperado.
