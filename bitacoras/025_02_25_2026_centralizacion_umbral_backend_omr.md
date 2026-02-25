# Bitacora 025_02_25_2026 12:25:34 centralizacion_umbral_backend_omr

## Que fue lo que se hizo
- Se analizo el archivo `src/backend/data/input/mobile_uploads/mobile_20260225_114814_d3ce2fcb.auxiliary.ratios.csv` para entender por que aparecian valores repetidos en `top_1_ratio` y por que algunos casos quedaban como ambiguos.
- Se confirmo que los valores entre filas 79 y 128 pertenecen a columnas auxiliares con `status=ambiguous` y que `top_1_ratio` se repite por diseno (registro por fila candidata, no por decision final de columna).
- Se localizaron las reglas de seleccion de ganador por mayor ratio en:
  - `src/backend/app/modules/omr_reader/result_builder.py`
  - `src/backend/app/modules/omr_reader/auxiliary_blocks.py`
- Se ajustaron umbrales por defecto para lectura OMR clasica:
  - `marked_threshold` a `0.4`.
  - `unmarked_threshold` a `0.18`.
- Se centralizo la decision de umbrales en backend, eliminando dependencia del frontend:
  - Se agregaron settings en `src/backend/app/core/config.py`:
    - `omr_marked_threshold`
    - `omr_unmarked_threshold`
  - El endpoint `src/backend/app/api/v1/endpoints/omr_read.py` ahora usa solo thresholds de `settings`.
  - `src/backend/app/modules/omr_reader/api_service.py` usa defaults tomados de `settings`.
  - En `src/frontend/src/services/omrRead.js` se elimino el envio de `marked_threshold` y `unmarked_threshold` en `FormData`.
- Se valido sintaxis con `py_compile` en archivos backend modificados.

## Para que se hizo
- Evitar que thresholds enviados desde cliente sobreescriban reglas de negocio del backend.
- Asegurar una sola fuente de verdad para umbrales de clasificacion OMR.
- Reducir falsos positivos en bloques auxiliares al elevar el criterio de marcado.

## Que problemas se presentaron
- Existia inconsistencia de umbrales entre capas:
  - Frontend enviaba `marked_threshold=0.12`.
  - Backend tenia defaults distintos en endpoint/servicio/clasificador.
- Esa diferencia causaba resultados confusos: burbujas con ratios bajos podian aparecer como marcadas por configuracion heredada desde el front.
- La lectura de CSV auxiliar inducia confusion porque repetia `top_1_ratio` por cada fila candidata dentro de la misma columna.

## Como se resolvieron
- Se rastreo el flujo completo de umbrales desde frontend hasta clasificador OMR.
- Se unifico la configuracion del backend con parametros explicitos en `settings` y consumo directo en endpoint/servicio.
- Se retiro el envio de thresholds desde frontend para evitar sobrescrituras no controladas.
- Se verifico con inspeccion de `.result.json` que los casos reportados quedaban en `status=ambiguous`, aunque existiera `value` candidato por regla de maximo ratio.
- Se documentaron los puntos de codigo donde se decide ganador por `max(fill_ratio)` para preparar cambios de regla posteriores (si se decide no seleccionar ganador cuando hay ambiguedad).

## Que continua
- Definir y aplicar regla de negocio para casos ambiguos: cuando `status=ambiguous`, evaluar si `value` debe devolverse como `null` en lugar de candidato.
- Considerar un CSV auxiliar "colapsado por columna" (una fila por columna) para analitica y calibracion de umbrales.
- Ejecutar nueva ronda de pruebas deterministicas con fotos recientes y comparar disminucion de falsos positivos.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
