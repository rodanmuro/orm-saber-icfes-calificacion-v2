# Bitacora 067_04_28_2026 16:04:03 documentacion_backup_restauracion_drive

## Que fue lo que se hizo
- Se documento formalmente el flujo de backup/restauracion en `src/backend/README.md`.
- Se agrego en la documentacion:
  - Que se respalda y por que (DB, `mobile_uploads`, `item_assets`, templates de output).
  - Que se excluye y por que (`debug_preprocess`, codigo fuente, etc.).
  - Ubicacion remota institucional en Drive (`gdrive-institucional:CEVU2026/OMR_BACKUPS`).
  - Estructura interna del archivo comprimido (`omr_backup_<timestamp>/...`) para restauracion transparente.
  - Comandos manuales completos de backup (creacion de paquete + `pg_dump -Fc` + subida por `rclone`).
  - Comandos de restauracion despues de clonar repo (descarga, descompresion, copias a rutas esperadas y `pg_restore`).
  - Checklist de verificacion posterior a restauracion.
- Se agrego referencia desde `README.md` raiz hacia la seccion de backup del backend.
- Se implemento script operativo `src/backend/scripts/backup_produccion_hoy.sh` para ejecutar el backup completo con un comando.
- Se extendio `src/backend/README.md` con la seccion `Script automatico de backup (recomendado)`, incluyendo uso basico y variables (`RCLONE_REMOTE`, `UPLOAD_REMOTE`, `DATABASE_URL`).

## Para que se hizo
- Reducir riesgo operacional ante falla del PC local.
- Dejar una guia reproducible y auditada para recuperar plataforma y datos sin ambiguedad.
- Asegurar que cualquier restauracion posterior respete rutas y estructura esperada por el backend.

## Que problemas se presentaron
- Riesgo de confusion entre archivos de produccion y artefactos de depuracion.
- Falta de claridad inicial sobre la estructura exacta interna del backup comprimido.

## Como se resolvieron
- Se separo explicitamente que entra/no entra en el backup con justificacion tecnica.
- Se fijo una convencion de estructura dentro del `.tar.gz` para hacer restauracion determinista.
- Se incluyeron comandos concretos de copia a rutas de runtime para evitar restauraciones parciales o inconsistentes.
- Se materializo la automatizacion en script shell para evitar errores manuales repetitivos al ejecutar respaldos de clase.

## Que continua
- Programar opcionalmente ejecucion periodica (cron) usando `backup_produccion_hoy.sh`.
- Agregar version corta de runbook de recuperacion para uso en contingencia durante clase.
- Definir politica de retencion (diaria/semanal/mensual) en carpeta institucional.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
