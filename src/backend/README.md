# Backend FastAPI

## Requisitos
- Python 3.10+

## Inicializacion
```bash
python3 -m venv src/backend/.venv
source src/backend/.venv/bin/activate
pip install -r src/backend/requirements.txt
```

## PostgreSQL local (sin Docker)
1. Iniciar servicio PostgreSQL local:
```bash
sudo systemctl start postgresql
sudo systemctl status postgresql
```

2. Crear usuario/base para el proyecto (una sola vez):
```bash
sudo -u postgres psql
```
Luego en `psql`:
```sql
CREATE ROLE administrador WITH LOGIN PASSWORD '12345678';
ALTER ROLE administrador CREATEDB;
CREATE DATABASE omr_app OWNER administrador;
GRANT ALL PRIVILEGES ON DATABASE omr_app TO administrador;
```

3. Configurar `.env` en `src/backend/.env` (puedes copiar desde `.env.example`):
```bash
DATABASE_URL="postgresql+psycopg://administrador:12345678@localhost:5432/omr_app"
```

4. Verificar conectividad backend -> DB:
```bash
cd src/backend
source .venv/bin/activate
DEBUG=false PYTHONPATH=. python3 scripts/check_database_connection.py
```

## Ejecutar API
```bash
cd src/backend
./run-app.sh
```

Nota: el entorno virtual oficial vive en `src/backend/.venv`.

## Detener PostgreSQL local
```bash
sudo systemctl stop postgresql
```

## Health check
- `GET /api/v1/health`

## Estado de persistencia (importante para onboarding)
- Motor objetivo actual: PostgreSQL local/entorno (`DATABASE_URL`).
- Esquema actual del proyecto: definido en modelos SQLAlchemy + migraciones SQL en `src/backend/migrations`.
- Estado de migraciones versionadas:
  - Alembic: integrado como mecanismo operativo de arranque (`upgrade head`).
  - Migracion base inicial: `src/backend/alembic/versions/20260310_0001_initial_schema.py`.
- En cada arranque de API, el backend ejecuta migraciones pendientes antes de atender requests.
- Comando de verificacion de conexion backend -> DB:
```bash
cd src/backend
source .venv/bin/activate
DEBUG=false PYTHONPATH=. python3 scripts/check_database_connection.py
```

## Comandos Alembic (backend)
Aplicar migraciones pendientes:
```bash
cd src/backend
source .venv/bin/activate
alembic upgrade head
```

Crear una nueva migracion:
```bash
cd src/backend
source .venv/bin/activate
alembic revision -m "descripcion_cambio"
```

Revertir una migracion:
```bash
cd src/backend
source .venv/bin/activate
alembic downgrade -1
```

Validar esquema de PostgreSQL (tablas, unique, FKs basicas):
```bash
cd src/backend
source .venv/bin/activate
DATABASE_URL="postgresql+psycopg://administrador:12345678@localhost:5432/omr_app" \
DEBUG=false PYTHONPATH=. python3 scripts/validate_postgres_schema.py
```

Seed dummy de examen (40 preguntas):
```bash
cd src/backend
source .venv/bin/activate
DATABASE_URL="postgresql+psycopg://administrador:12345678@localhost:5432/omr_app" \
DEBUG=false PYTHONPATH=. python3 scripts/seed_dummy_exam_40.py
```

Reseed oficial de dataset base (docente + 40 preguntas + examen + version V001):
```bash
cd src/backend
source .venv/bin/activate
DATABASE_URL="postgresql+psycopg://administrador:12345678@localhost:5432/omr_app" \
DEBUG=false PYTHONPATH=. python3 scripts/reseed_dummy_dataset.py
```

Verificar dataset dummy cargado:
```bash
cd src/backend
source .venv/bin/activate
DATABASE_URL="postgresql+psycopg://administrador:12345678@localhost:5432/omr_app" \
DEBUG=false PYTHONPATH=. python3 scripts/verify_dummy_dataset.py
```

## Calificacion OMR (modo integracion)
- `POST /api/v1/omr/read-photo`
- Si se envia `teacher_id` y el OMR detecta `exam_identifier`, el backend intenta resolver examen por `teacher_id + exam_code` y agrega bloque `grading` en la respuesta.
- Cada lectura persiste un intento OMR con detalle por pregunta y devuelve `diagnostics.attempt_id`.
- Consulta de intento: `GET /api/v1/omr/attempts/{attempt_id}`.

## Banco de items y examenes (API)
- Items:
  - `POST /api/v1/items`
  - `GET /api/v1/items`
  - `GET /api/v1/items/{item_id}`
  - `PUT /api/v1/items/{item_id}`
- Examenes:
  - `POST /api/v1/exams`
  - `GET /api/v1/exams`
  - `GET /api/v1/exams/{exam_id}`
  - `POST /api/v1/exams/{exam_id}/items`
  - `DELETE /api/v1/exams/{exam_id}/items/{item_id}`
  - `POST /api/v1/exams/{exam_id}/versions/publish`
  - `GET /api/v1/exams/{exam_id}/versions`
  - `GET /api/v1/exams/{exam_id}/versions/{version_id}`
  - `GET /api/v1/exams/{exam_id}/answer-key`

## Asistente IA (OpenAI / Groq)
Selector de proveedor por variable de entorno:

```bash
AI_PROVIDER=openai   # o groq
```

Variables para OpenAI:
```bash
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5.1
OPENAI_TIMEOUT_SECONDS=60
OPENAI_MAX_RETRIES=4
OPENAI_RETRY_BACKOFF_SECONDS=1.0
```

Variables para Groq:
```bash
GROQ_API_KEY=...
GROQ_MODEL=meta-llama/llama-4-scout-17b-16e-instruct
GROQ_TIMEOUT_SECONDS=60
GROQ_MAX_RETRIES=4
GROQ_RETRY_BACKOFF_SECONDS=1.0
```

Notas:
- Endpoint de generación: `POST /api/v1/ai/generate-item`
- El contrato de salida (`statement_doc`, `options_doc`, `correct_answer`) es el mismo para ambos proveedores.
- Costo/tarifas automáticas solo se calculan con valores OpenAI en este momento; en Groq se reportan en `0.0` por defecto.

## Assets de items (editor web)
- Upload de imagen: `POST /api/v1/assets/images` (multipart campo `image`)
- Tipos permitidos: `png`, `jpeg`, `webp`
- URL de salida servida en: `/assets/item_assets/<filename>`

## Arquitectura del generador de plantillas
Modulos base (`src/backend/app/modules/template_generator`):
- `config_loader`: lectura y validacion de configuracion externa (JSON/YAML).
- `geometry`: funciones puras para area imprimible y validaciones geometricas.
- `layout_engine`: orquestacion geometrica y validaciones de limites.
- `aruco_renderer`: calculo de posicionamiento de marcadores ArUco.
- `bubble_layout`: calculo de grillas OMR e IDs deterministas.
- `template_renderer`: salida visual PDF de la plantilla.
- `metadata_exporter`: salida estructurada JSON (fuente de verdad de layout).
- `pipeline`: composicion desacoplada de todo el flujo.

Dependencias (direccion unica):
- `config_loader` -> `contracts`
- `geometry` -> `contracts`
- `layout_engine` -> `contracts`, `geometry`, `aruco_renderer`, `bubble_layout`
- `pipeline` -> `config_loader`, `layout_engine`, `template_renderer`, `metadata_exporter`

## Contratos parametrizables
El archivo de configuracion define:
- `page_config`
- `aruco_config`
- `block_config`
- `bubble_config`
- `output_config`

Notas de `aruco_config`:
- `dictionary_name` validado contra diccionarios ArUco soportados.
- `ids` validados por rango segun diccionario.
- `corner_inset_mm` y `corner_offsets_mm` para mover cada marcador por esquina.
- Render PDF con marcadores ArUco reales (OpenCV ArUco), no solo placeholders.

Notas de `bubble_config`:
- `group_id` debe ser unico por grupo.
- IDs de burbuja deterministas con formato `GROUP_ROW_COL` (ej: `G01_00_03`).
- Validaciones activas para burbujas fuera del bloque o solapadas.
- Etiquetas internas por columna (`A/B/C/D` o personalizadas con `column_labels`).
- Estilo de etiqueta configurable con `label_style` (gris claro y tamano de fuente).
- `num_questions` parametrizable por grupo (si se define, prevalece sobre `rows`).
- Numeracion de preguntas por fila configurable con `question_number_style`.
- Separacion numero -> primera burbuja por centros en `question_number_style.center_gap_mm`.
- Salida estructurada `question_items` (unidad logica de pregunta con numero + opciones).
- Metadata incluye `aruco_dictionary_name` para trazabilidad de deteccion.

Base de ejemplo:
- `src/backend/config/template.base.json`

## Generar plantilla base
```bash
python -m app.modules.template_generator.scripts.generate_template \
  --config src/backend/config/template.base.json \
  --output-dir src/backend/data/output
```

## Generacion reproducible multi-configuracion
Comando unico para generar y validar varias configuraciones:

```bash
python -m app.modules.template_generator.scripts.generate_templates_batch \
  --configs \
    src/backend/config/template.base.json \
    src/backend/config/template.single_column_20.json \
    src/backend/config/template.two_columns_24.json \
  --output-dir src/backend/data/output
```

Opcional:
- `--fail-fast` para detenerse en la primera configuracion invalida.

## Validar entrada local de lectura OMR
Valida imagen + metadata antes de correr deteccion/lectura:

```bash
python -m app.modules.omr_reader.scripts.validate_read_input \
  --image /ruta/foto_diligenciada.jpg \
  --metadata src/backend/data/output/template_basica_omr_v2_wireframe.json
```

## Alinear foto usando ArUco + homografia
Genera una imagen corregida al plano de la plantilla:

```bash
python -m app.modules.omr_reader.scripts.align_photo \
  --image src/backend/data/input/foto.jpg \
  --metadata src/backend/data/output/template_basica_omr_v2_wireframe.json \
  --output-image src/backend/data/output/foto_alineada.png
```

## Clasificar burbujas y generar JSON por pregunta
Corre alineacion + lectura de ROI y exporta:
- `questions`: resultado por pregunta y opcion (`marcada`/`no_marcada`/`ambigua`)
- `quality_summary`: conteos globales basicos
- `bubbles`: detalle por burbuja (debug)

```bash
python -m app.modules.omr_reader.scripts.classify_bubbles \
  --image src/backend/data/input/foto.jpg \
  --metadata src/backend/data/output/template_basica_omr_v2_wireframe.json \
  --output-json src/backend/data/output/foto_bubbles.json
```

## Endpoint API para leer foto subida (ACT_0014)
Recibe una foto por `multipart/form-data` y retorna JSON OMR por pregunta.

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/omr/read-photo" \
  -F "photo=@src/backend/data/input/diligenciadas/foto_001.jpeg" \
  -F "metadata_path=data/output/template_basica_omr_v2_wireframe.json"
```

Parametros opcionales en form-data:
- `px_per_mm` (default `10.0`)
- `marked_threshold` (default `0.45`)
- `unmarked_threshold` (default `0.35`)

Notas:
- El backend valida calidad geometrica minima de captura; si la perspectiva es extrema o la hoja ocupa muy poco, devuelve error controlado (HTTP 400).
