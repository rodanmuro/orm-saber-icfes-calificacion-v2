estado: done
prioridad: alta
sprint: S1
owner: codex

# ACT_0006 - Comando reproducible y validacion multi-configuracion

## Objetivo tecnico
Exponer un comando unico de generacion y validar parametrizacion ejecutando el pipeline con multiples configuraciones sin cambios de codigo.

## Tareas implementables
- [x] Implementar CLI/script de entrada unica para generar plantilla + metadatos.
- [x] Definir manejo de errores controlado para config invalida.
- [x] Crear al menos 2 configuraciones adicionales de prueba (ademas de la base).
- [x] Ejecutar pipeline con cada config y comparar consistencia estructural de salidas.
- [x] Documentar comando y ejemplos de uso.

## Evidencias esperadas
- Script batch reproducible en:
  - `src/backend/app/modules/template_generator/scripts/generate_templates_batch.py`
- Validacion estructural de metadata en:
  - `src/backend/app/modules/template_generator/metadata_validation.py`
- Configuraciones adicionales:
  - `src/backend/config/template.single_column_20.json`
  - `src/backend/config/template.two_columns_24.json`
- Documentacion de comando multi-configuracion:
  - `src/backend/README.md`
- Tests automaticos de validacion:
  - `src/backend/tests/test_metadata_validation.py`

## Criterio de terminado
El mismo comando genera correctamente plantillas variantes solo cambiando config, demostrando escalabilidad y ausencia de hardcode critico.
