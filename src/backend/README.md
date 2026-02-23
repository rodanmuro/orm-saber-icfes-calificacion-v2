# Backend FastAPI

## Requisitos
- Python 3.11+

## Inicializacion
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r src/backend/requirements.txt
```

## Ejecutar API
```bash
uvicorn app.main:app --reload --app-dir src/backend
```

## Health check
- `GET /api/v1/health`

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
  --metadata src/backend/data/output/template_basica_omr_v1.json
```

## Alinear foto usando ArUco + homografia
Genera una imagen corregida al plano de la plantilla:

```bash
python -m app.modules.omr_reader.scripts.align_photo \
  --image src/backend/data/input/foto.jpg \
  --metadata src/backend/data/output/template_basica_omr_v1.json \
  --output-image src/backend/data/output/foto_alineada.png
```
