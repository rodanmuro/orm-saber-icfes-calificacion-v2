# Bitacora 015_02_23_2026 15:45:49 avance_pruebas_omr_movil_robust_mode

## Que fue lo que se hizo
- Se conecto `robust_mode` de punta a punta para lectura OMR:
  - `src/backend/app/api/v1/endpoints/omr_read.py`
  - `src/backend/app/modules/omr_reader/api_service.py`
  - `src/frontend/src/services/omrRead.js`
- Se ajusto el test de servicio para incluir diagnostico de `robust_mode`:
  - `src/backend/tests/test_omr_api_service.py`
- Se creo un test de integracion por ruta local de imagen (sin simular frontend), con metricas de exactitud contra la clave de 30 respuestas:
  - `src/backend/tests/test_omr_integration_local_image.py`
- Se corrio el test de integracion con la ultima imagen en `mobile_uploads` usando el venv del proyecto.

## Para que se hizo
- Permitir evaluar rapidamente fotos reales tomadas con celular, usando el mismo pipeline del backend.
- Tener una forma repetible de medir calidad de lectura (exactitud, vacias, multiplemente marcadas) y no depender solo de revision manual.
- Dejar habilitada una ruta de mejora incremental (`robust_mode`) sin romper el flujo actual.

## Que problemas se presentaron
- En el entorno de ejecucion de herramientas no estaba disponible `cv2`, por lo que los tests fallaban al importar OpenCV.
- No habia salida a internet en ese entorno para instalar paquetes con `pip`.
- En pruebas reales, algunas fotos daban lecturas en blanco o con multiples marcas por iluminacion desigual, reflejos y perspectiva fuerte.
- La ultima imagen de prueba siguio siendo compleja para el pipeline aun con mejoras iniciales.

## Como se resolvieron
- Se detecto y uso el `venv` local del proyecto (`.venv`) donde ya estaba instalado OpenCV, y desde ahi se ejecuto el test de integracion.
- Se dejo el test parametrizable por variables de entorno para cambiar imagen y umbrales sin editar codigo:
  - `OMR_INTEGRATION_IMAGE_PATH`
  - `OMR_INTEGRATION_ROBUST_MODE`
  - `OMR_INTEGRATION_MARKED_THRESHOLD`
  - `OMR_INTEGRATION_UNMARKED_THRESHOLD`
  - `OMR_INTEGRATION_MIN_ACCURACY`
- Resultado medido sobre la ultima imagen:
  - `accuracy=53.33%`
  - `exact_matches=16/30`
  - `blank=5`
  - `multi=8`
- Con esto se confirmo que hay mejora instrumental de trazabilidad, pero aun falta robustez en preprocesamiento para condiciones de captura adversas.

## Que continua
- Implementar comparacion controlada por lotes sobre `mobile_uploads` (baseline vs robust_mode) y registrar tabla de mejoras por imagen.
- Incorporar preprocesamiento adicional configurable: normalizacion de iluminacion por canal, CLAHE con parametros ajustables, y/o umbral adaptativo por region.
- Agregar control explicito en frontend para activar/desactivar `robust_mode` en pruebas A/B.
- Definir criterio minimo de aceptacion para la siguiente iteracion (por ejemplo, exactitud >= 90% en set de fotos reales validado).
- Documentar recomendaciones operativas de captura para usuario final mientras se estabiliza el pipeline (angulo, luz, distancia y encuadre de marcadores).

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
