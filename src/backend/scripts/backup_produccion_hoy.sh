#!/usr/bin/env bash
set -euo pipefail

# Backup operativo OMR (produccion del dia):
# - PostgreSQL dump custom (-Fc)
# - mobile_uploads del dia
# - item_assets completo
# - templates de data/output
# - subida opcional con rclone

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
STAMP="${STAMP:-$(date +%Y%m%d_%H%M%S)}"
TMP_DIR="${TMP_DIR:-/tmp}"
BACKUP_ROOT="${TMP_DIR}/omr_backup_${STAMP}"
ARCHIVE_PATH="${TMP_DIR}/omr_backup_${STAMP}.tar.gz"

# Remote destino por defecto (puedes sobreescribir por variable de entorno)
RCLONE_REMOTE="${RCLONE_REMOTE:-gdrive-institucional:CEVU2026/OMR_BACKUPS}"

# Activa/desactiva subida remota
UPLOAD_REMOTE="${UPLOAD_REMOTE:-true}"

# URL de PostgreSQL (si no viene, se usa la del proyecto)
DATABASE_URL="${DATABASE_URL:-postgresql://administrador:12345678@localhost:5432/omr_app}"

echo "[INFO] PROJECT_ROOT=${PROJECT_ROOT}"
echo "[INFO] BACKUP_ROOT=${BACKUP_ROOT}"
echo "[INFO] ARCHIVE_PATH=${ARCHIVE_PATH}"
echo "[INFO] RCLONE_REMOTE=${RCLONE_REMOTE}"
echo "[INFO] UPLOAD_REMOTE=${UPLOAD_REMOTE}"

mkdir -p "${BACKUP_ROOT}/data_input_mobile_uploads_today" \
         "${BACKUP_ROOT}/data_input_item_assets" \
         "${BACKUP_ROOT}/data_output_templates"

echo "[INFO] Copiando mobile_uploads del dia..."
find "${PROJECT_ROOT}/src/backend/data/input/mobile_uploads" -maxdepth 1 -type f -daystart -mtime 0 -print0 \
  | xargs -r -0 -I{} cp -a "{}" "${BACKUP_ROOT}/data_input_mobile_uploads_today/"

echo "[INFO] Copiando item_assets..."
cp -a "${PROJECT_ROOT}/src/backend/data/input/item_assets/." "${BACKUP_ROOT}/data_input_item_assets/"

echo "[INFO] Copiando templates output..."
find "${PROJECT_ROOT}/src/backend/data/output" -maxdepth 1 -type f \
  \( -name 'template*.pdf' -o -name 'template*.json' -o -name 'template_basica_omr_v2_wireframe.pdf' -o -name 'template_basica_omr_v2_wireframe.json' \) \
  -print0 | xargs -r -0 -I{} cp -a "{}" "${BACKUP_ROOT}/data_output_templates/"

echo "[INFO] Generando dump PostgreSQL..."
pg_dump -Fc "${DATABASE_URL}" -f "${BACKUP_ROOT}/omr_app_${STAMP}.dump"

cat > "${BACKUP_ROOT}/README_BACKUP.txt" << EOF
Backup OMR - corte ${STAMP}
Incluye:
- PostgreSQL dump custom (-Fc)
- data/input/mobile_uploads (solo archivos del dia)
- data/input/item_assets
- data/output templates (.pdf/.json)
Excluye:
- data/output/debug_preprocess
- data/output/aligned
- codigo fuente (ya en GitHub)
EOF

echo "[INFO] Comprimiendo..."
cd "${TMP_DIR}"
tar -czf "$(basename "${ARCHIVE_PATH}")" "$(basename "${BACKUP_ROOT}")"

echo "[INFO] Archivo generado:"
ls -lh "${ARCHIVE_PATH}"

if [[ "${UPLOAD_REMOTE}" == "true" ]]; then
  echo "[INFO] Subiendo a remoto..."
  rclone mkdir "${RCLONE_REMOTE}"
  rclone copyto "${ARCHIVE_PATH}" "${RCLONE_REMOTE}/$(basename "${ARCHIVE_PATH}")" --progress
  echo "[INFO] Subida completada: ${RCLONE_REMOTE}/$(basename "${ARCHIVE_PATH}")"
else
  echo "[INFO] UPLOAD_REMOTE=false -> se omite subida remota"
fi

echo "[INFO] Backup finalizado OK"
