# HU_010 - Migracion de esquema y datos base desde SQLite (EP_004)

## Trazabilidad
- Epica asociada: `EP_004_migracion_persistencia_postgresql.md`
- Dependencias: HU_009 completada.

## Historia de usuario
**Como** equipo tecnico  
**Quiero** portar el esquema y los datos base de trabajo desde SQLite hacia PostgreSQL  
**Para** continuar el desarrollo funcional sin perder contexto operativo.

## Criterios de aceptacion
1. Las entidades principales (teacher, item, exam, exam_item, exam_version, omr_attempt, etc.) existen en PostgreSQL con integridad referencial.
2. Hay un procedimiento reproducible para cargar datos semilla o dummies necesarios de desarrollo.
3. El backend puede consultar y persistir datos en PostgreSQL con el mismo contrato funcional actual.
4. Se valida que relaciones y restricciones clave queden preservadas.
5. Queda documentada la estrategia para cargas iniciales y reinicios de entorno.

## Evidencia esperada
- Esquema desplegado en PostgreSQL.
- Script/proceso de seed funcional.
- Verificacion de datos de muestra visibles en tablas clave.

## Notas
- El objetivo en esta HU es continuidad de desarrollo, no migracion historica completa de produccion.
