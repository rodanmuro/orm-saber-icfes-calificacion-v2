estado: done
prioridad: alta
sprint: S1
owner: codex

# ACT_0004 - Generar burbujas OMR parametrizadas con IDs estables

## Objetivo tecnico
Implementar grilla de burbujas basada en configuracion (filas, columnas, spacing, radio) garantizando IDs deterministas.

## Tareas implementables
- [x] Definir `bubble_config` (estructura de grupos, filas/columnas, radio, separaciones).
- [x] Implementar algoritmo de distribucion dentro del bloque principal.
- [x] Definir estrategia de IDs estables (ej: prefijo + indice determinista).
- [x] Validar que todas las burbujas queden dentro del bloque.

## Evidencias esperadas
- Plantilla con conjunto de burbujas dibujadas en `src/backend/output/template_basica_omr_v1.pdf`.
- Lista estructurada de burbujas con ID y geometria en `src/backend/output/template_basica_omr_v1.json`.
- Validaciones y estrategia de IDs implementadas en:
  - `src/backend/app/modules/template_generator/bubble_layout.py`
  - `src/backend/app/modules/template_generator/contracts.py`
- Pruebas automaticas asociadas en:
  - `src/backend/tests/test_bubble_layout.py`

## Criterio de terminado
Con misma configuracion se obtienen exactamente los mismos IDs y coordenadas de burbujas en ejecuciones consecutivas.
