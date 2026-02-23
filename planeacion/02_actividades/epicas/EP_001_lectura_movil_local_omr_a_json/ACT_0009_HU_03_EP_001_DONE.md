estado: done
prioridad: alta
sprint: S2
owner: codex

# ACT_0009 - Clasificacion de burbujas por ROI

## Objetivo tecnico
Implementar evaluacion de burbujas sobre imagen corregida para clasificar `marcada` o `no_marcada` con criterio reproducible.

## Tareas implementables
- [x] Implementar extraccion de ROI por burbuja usando metadatos de plantilla.
- [x] Definir metrica de relleno/oscurecimiento por ROI.
- [x] Implementar regla de umbral parametrizable para clasificacion binaria.
- [x] Gestionar estado ambiguo cuando se detecte borde de decision.

## Evidencias esperadas
- Modulo de lectura de burbujas:
  - `src/backend/app/modules/omr_reader/bubble_classifier.py`
- CLI local de clasificacion con salida JSON:
  - `src/backend/app/modules/omr_reader/scripts/classify_bubbles.py`
- Contrato de salida por burbuja:
  - `src/backend/app/modules/omr_reader/contracts.py`
- Documentacion de uso:
  - `src/backend/README.md`
- Pruebas automáticas:
  - `src/backend/tests/test_omr_bubble_classifier.py`

## Criterio de terminado
Todas las burbujas se evalúan exactamente una vez con clasificacion reproducible y trazable.
