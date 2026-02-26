# OMR Saber ICFES Calificacion v2

Proyecto para generar plantillas OMR con ArUco, capturar fotos desde celular y leer respuestas marcadas en backend.

## Estructura
- `src/backend`: API FastAPI, generador de plantillas, pipeline de lectura OMR.
- `src/frontend`: app Expo para prueba LAN, captura y envio de foto.
- `planeacion`: epicas, historias y actividades.
- `bitacoras`: registro cronologico de avances y pruebas.

## Arquitectura

### Backend (FastAPI)
- API REST en `src/backend/app/api/v1`.
- Modulo `template_generator`: pipeline de configuracion y compilacion de plantilla.
- Modulo `omr_reader`: flujo de lectura:
  1. decodifica imagen,
  2. detecta ArUco y alinea por homografía,
  3. preprocesa (modo robusto opcional),
  4. calcula `fill_ratio` por burbuja,
  5. construye resultado por pregunta.
- Salidas de trazabilidad:
  - JSON de lectura por subida (`*.result.json`),
  - artefactos de debug (`aligned` y `binary_inv`) cuando se activan.

### Pipeline de plantilla v2 (actual)
- `src/backend/config/template.basica_omr_v2.json`: configuracion base editable.
- `src/backend/app/modules/template_generator/scripts/generate_wireframe_metadata.py`:
  compila geometria operativa y genera `src/backend/data/output/template_basica_omr_v2_wireframe.json`.
- `src/backend/app/modules/template_generator/scripts/generate_pdf_from_metadata.py`:
  renderiza PDF desde el metadata wireframe.
- Lectura OMR backend:
  - usa `settings.omr_default_metadata_path` (actual: `data/output/template_basica_omr_v2_wireframe.json`).
  - mismo metadata para render y para calificar (coherencia runtime).

### Frontend (Expo Go)
- App React Native mínima en `src/frontend`.
- Flujo:
  1. prueba health LAN,
  2. toma foto con cámara del celular,
  3. normaliza orientación EXIF,
  4. envía `multipart/form-data` al endpoint OMR,
  5. muestra resumen y payload JSON.

## Estado actual (resumen)
- Generacion de plantilla OMR parametrizable (PDF + metadata JSON).
- Lectura OMR desde foto con alineacion ArUco.
- Flujo movil (Expo) para tomar foto y enviarla al backend.
- Regla actual de seleccion por pregunta:
  - umbral base `marked_threshold=0.4`,
  - `unmarked_threshold=0.18`,
  - si varias opciones superan umbral, se selecciona la de mayor ratio.
- Guardado de evidencia:
  - fotos subidas: `src/backend/data/input/mobile_uploads/`
  - artefactos debug (alineada/binaria): `src/backend/data/output/debug_preprocess/`

## Inicio rapido

### 1) Backend
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r src/backend/requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir src/backend
```

### 2) Frontend
```bash
cd src/frontend
cp .env.example .env
# editar EXPO_PUBLIC_API_BASE_URL con la IP local de tu PC
npm install
npm start
```

## Endpoints principales
- Health: `GET /api/v1/health`
- Lectura foto OMR: `POST /api/v1/omr/read-photo`

Campos clave de `read-photo` (multipart):
- `photo`
- `metadata_path` (ej: `data/output/template_basica_omr_v1.json`)
- `robust_mode` (recomendado: `true`)

Nota: `marked_threshold` y `unmarked_threshold` ya no se controlan desde frontend; son decision de backend via `settings`.

## Documentacion detallada
- Backend: `src/backend/README.md`
- Frontend: `src/frontend/README.md`
- Arquitectura de pipeline de plantilla: `bitacoras/026_02_26_2026_arquitecura_pipeline_plantilla_v2_deuda_tecnica.md`

## Notas de trabajo
- Umbrales actuales centralizados en backend:
  - `omr_marked_threshold=0.4`
  - `omr_unmarked_threshold=0.18`

## Estilo de desarrollo (agentes)
- Se trabaja por epicas/historias/actividades con trazabilidad en `planeacion/`.
- Cada avance relevante se registra en `bitacoras/` con evidencias, problemas y siguientes pasos.
- Se usa automatizacion con agentes para:
  - aplicar cambios incrementales,
  - ejecutar pruebas,
  - registrar decisiones tecnicas y deuda.

## Dificultades encontradas
- Sensibilidad a condiciones reales de captura:
  - iluminacion desigual y reflejos,
  - inclinacion/perspectiva extrema,
  - marcas tenues de lapiz.
- Casos observados:
  - preguntas sin detectar aun estando marcadas visualmente,
  - falsos positivos al bajar demasiado umbral,
  - fallos por ArUco incompleto en algunas capturas.
- Mitigaciones ya aplicadas:
  - `robust_mode` de preprocesamiento,
  - guardado de artefactos de debug,
  - calibracion empirica de umbral y regla de mayor ratio.

## Deuda tecnica actual
1. Manejo formal de multiple marca del estudiante (no consolidar automaticamente como valida).
2. Regla anti-marca-espuria (punto/trazo pequeno no intencional).
3. Politica robusta de “sin respuesta” para casos limite de baja calidad.
4. Dashboard frontend de correccion manual con imagen procesada para revisar ambiguedades.
5. Proceso formal de calibracion estadistica de umbrales (no solo tanteo visual).
