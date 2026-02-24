estado: blocked
prioridad: alta
sprint: S2
owner: por_definir

# ACT_0017 - Variante robusta adicional de preprocesamiento

## Objetivo tecnico
Incorporar una variante adicional de preprocesamiento (`CLAHE -> GaussianBlur(5x5) -> OTSU_INV`) para mejorar lectura en fotos reales.

## Tareas implementables
- [ ] Implementar nueva variante de preprocesado en modulo OMR reader.
- [ ] Permitir ejecucion controlada de la variante sin romper defaults actuales.
- [ ] Guardar artefactos debug de esta variante para inspeccion visual.
- [ ] Documentar parametros base usados en la variante.

## Evidencias esperadas
- Cambios en backend OMR reader con nueva ruta de preprocesado.
- Imagenes debug comparables (alineada/binaria) para al menos 2 capturas reales.

## Criterio de terminado
La nueva variante se ejecuta de forma reproducible y produce salida OMR valida sobre imagenes reales.

## Estado de pausa
- Actividad pausada temporalmente por priorizacion del enfoque de motor alterno LLM (Gemini).
- Se reactivara al cerrar HU_003 (ACT_0022+).
