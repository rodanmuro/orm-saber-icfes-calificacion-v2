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
- `config_loader`: lectura y validacion de configuracion externa JSON.
- `layout_engine`: orquestacion geometrica y validaciones de limites.
- `aruco_renderer`: calculo de posicionamiento de marcadores ArUco.
- `bubble_layout`: calculo de grillas OMR e IDs deterministas.
- `template_renderer`: salida visual PDF de la plantilla.
- `metadata_exporter`: salida estructurada JSON (fuente de verdad de layout).
- `pipeline`: composicion desacoplada de todo el flujo.

Dependencias (direccion unica):
- `config_loader` -> `contracts`
- `layout_engine` -> `contracts`, `aruco_renderer`, `bubble_layout`
- `pipeline` -> `config_loader`, `layout_engine`, `template_renderer`, `metadata_exporter`

## Contratos parametrizables
El archivo de configuracion define:
- `page_config`
- `aruco_config`
- `block_config`
- `bubble_config`
- `output_config`

Base de ejemplo:
- `src/backend/config/template.base.json`

## Generar plantilla base
```bash
python -m app.modules.template_generator.scripts.generate_template \
  --config src/backend/config/template.base.json \
  --output-dir src/backend/output
```
