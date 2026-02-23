# Bitacora 014_02_23_2026 15:06:27 ensayos_umbral_y_mejoras_robustez

## Que fue lo que se hizo
- Se realizaron ensayos manuales de lectura OMR desde celular enviando fotos reales al backend via endpoint `POST /api/v1/omr/read-photo`.
- Se evaluaron distintos valores de umbral para clasificacion de burbujas:
  - perfil mas sensible (`0.18 / 0.05`),
  - perfil intermedio,
  - perfil mas estricto (`0.26 / 0.10`).
- Se confirmo comportamiento no estable segun condiciones de iluminacion: en algunas tomas se perdian marcas de una zona y en otras aparecian multimarcas falsas.
- Se agrego trazabilidad operativa en backend:
  - guardado de imagen subida en `src/backend/data/input/mobile_uploads/`.
  - guardado de JSON por captura (`*.result.json`) con respuestas leidas por pregunta (`marked`, `ambiguous`, `blank`).
- Se ajusto log de backend para mostrar respuestas por pregunta en formato legible (`pregunta N: opcion`).
- Se mejoro visualizacion en frontend para revisar mejor la captura:
  - miniatura mas grande,
  - vista completa de la foto en modal.
- Se probo el efecto de compresion del lado movil y se ajusto temporalmente calidad de captura para comparativos.

Archivos clave modificados:
- `src/backend/app/api/v1/endpoints/omr_read.py`
- `src/backend/app/modules/omr_reader/api_service.py`
- `src/frontend/App.js`
- `src/frontend/src/services/omrRead.js`
- `src/backend/README.md`
- `.gitignore`

## Para que se hizo
- Identificar por evidencia real por que la lectura cambia entre tomas con misma plantilla.
- Dejar trazabilidad de cada prueba (imagen + resultado) para poder depurar y comparar ajustes.

## Que problemas se presentaron
- Alta sensibilidad a condiciones de luz/sombra y reflejo: en ciertas fotos se perdian burbujas marcadas.
- Cuando el umbral se hizo muy sensible, aparecieron falsos positivos (multimarca por pregunta).
- Inestabilidad local por zonas: columnas o bloques de preguntas se comportaban distinto en una misma foto.

## Como se resolvieron
- Se hicieron iteraciones controladas de umbral y se compararon resultados por pregunta.
- Se incorporo guardado automatico de evidencia por captura en backend para analizar casos fallidos y exitosos.
- Se mejoro la inspeccion visual en frontend para validar reflejos/claridad antes de enviar la foto.

## Que continua
- Mantener temporalmente un perfil de umbral base estable mientras se implementa robustez real.
- Implementar mejoras de backend para robustez fotometrica (por hacer):
  - Normalizacion de iluminacion previa a clasificacion.
  - Aumento de contraste local (CLAHE) sobre imagen alineada.
  - Binarizacion adaptativa local (no solo umbral global/Otsu).
  - Regla de decision por pregunta con opcion ganadora para reducir multimarcas falsas.
  - Modo `robust_mode` configurable para comparar pipeline actual vs pipeline robusto.
- Medir impacto de cada mejora con el set de capturas guardadas en `mobile_uploads`.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
