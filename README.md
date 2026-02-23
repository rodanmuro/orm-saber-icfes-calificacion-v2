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
- Modulo `template_generator`: genera plantilla PDF y metadata JSON (fuente de verdad geométrica).
- Modulo `omr_reader`: flujo de lectura:
  1. decodifica imagen,
  2. detecta ArUco y alinea por homografía,
  3. preprocesa (modo robusto opcional),
  4. calcula `fill_ratio` por burbuja,
  5. construye resultado por pregunta.
- Salidas de trazabilidad:
  - JSON de lectura por subida (`*.result.json`),
  - artefactos de debug (`aligned` y `binary_inv`) cuando se activan.

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
  - umbral base `marked_threshold=0.12`,
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
- `marked_threshold` (actual calibrado: `0.12`)
- `unmarked_threshold` (actual: `0.08`)
- `robust_mode` (recomendado: `true`)

## Documentacion detallada
- Backend: `src/backend/README.md`
- Frontend: `src/frontend/README.md`

## Notas de trabajo
- El umbral `0.12` fue calibrado empiricamente por tanteo visual sobre imagenes reales.

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
