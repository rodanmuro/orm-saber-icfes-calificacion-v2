estado: done
prioridad: alta
sprint: S2
owner: codex

# ACT_0007 - Carga local de imagen y metadatos de plantilla

## Objetivo tecnico
Implementar el modulo de entrada local para cargar foto de plantilla diligenciada y su `template.json` asociado con validaciones de integridad basica.

## Tareas implementables
- [x] Crear modulo de carga de imagen desde ruta local.
- [x] Crear loader de metadatos de plantilla para lectura OMR.
- [x] Validar presencia de `template_id`, `version`, `question_items`, `bubbles`, `aruco_markers`.
- [x] Definir errores controlados para archivo faltante, formato invalido y metadata incompleta.

## Evidencias esperadas
- Modulo en `src/backend` para carga de imagen+metadata:
  - `src/backend/app/modules/omr_reader/loader.py`
  - `src/backend/app/modules/omr_reader/contracts.py`
  - `src/backend/app/modules/omr_reader/errors.py`
- CLI local de validacion:
  - `src/backend/app/modules/omr_reader/scripts/validate_read_input.py`
- Documentacion de uso en:
  - `src/backend/README.md`

## Criterio de terminado
El flujo recibe imagen+metadata validas y retorna estructuras listas para procesamiento OMR sin dependencias externas.
