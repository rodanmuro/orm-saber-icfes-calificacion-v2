# EP_001 - Lectura movil local OMR a JSON

## Objetivo tecnico
Implementar un flujo de lectura local desde celular que tome una captura de la plantilla basica, detecte burbujas marcadas/no marcadas y produzca un JSON de resultados sin enviar informacion a API.

## Alcance
- Captura de imagen desde celular (modo manual inicial).
- Deteccion de marcadores ArUco en la imagen capturada.
- Correccion de perspectiva (homografia) hacia el plano de plantilla.
- Evaluacion de burbujas definidas en metadatos de la plantilla.
- Generacion local de JSON con estado por burbuja.

## Fuera de alcance
- Envio de imagen o resultados a backend/API.
- Calculo de puntaje o calificacion de examen.
- Identificacion de estudiante/examen.
- OCR de texto manuscrito.

## Entregables verificables
- Modulo de captura y procesamiento local en app movil.
- Parser/cargador de metadatos de plantilla.
- Motor de decision de burbuja marcada/no marcada por ROI.
- JSON de salida con estructura minima:
  - `template_id` (o version),
  - `timestamp`,
  - `bubbles`: lista de objetos `{id, estado}` donde `estado` es `marcada` o `no_marcada`,
  - metadatos de calidad basicos (por ejemplo confianza o umbral aplicado).

## Restricciones tecnicas
- El procesamiento de lectura ocurre localmente en el dispositivo.
- El estado de cada burbuja se basa en umbral o criterio documentado y reproducible.
- Debe existir tolerancia basica a inclinacion mediante ArUco + homografia.

## Criterios de aceptacion
1. Con una captura valida donde se ven los 4 ArUco, el sistema genera JSON local sin dependencia de red.
2. El JSON contiene todas las burbujas esperadas segun la plantilla cargada.
3. Cada burbuja aparece exactamente una vez con estado `marcada` o `no_marcada`.
4. Si faltan marcadores ArUco o la captura no es util, el flujo retorna error controlado (sin cierre inesperado).
5. Se documenta un caso de prueba manual con evidencia de salida JSON.
