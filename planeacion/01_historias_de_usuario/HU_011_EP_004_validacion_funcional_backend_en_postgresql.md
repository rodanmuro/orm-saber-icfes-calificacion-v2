# HU_011 - Validacion funcional backend en PostgreSQL (EP_004)

## Trazabilidad
- Epica asociada: `EP_004_migracion_persistencia_postgresql.md`
- Dependencias: HU_009 y HU_010 completadas.

## Historia de usuario
**Como** equipo tecnico  
**Quiero** validar los flujos backend de banco de items, examenes/versiones y calificacion OMR sobre PostgreSQL  
**Para** asegurar que la migracion no rompe el comportamiento esperado.

## Criterios de aceptacion
1. Endpoints clave de items/exams/versiones responden correctamente sobre PostgreSQL.
2. El flujo de lectura y persistencia OMR mantiene contratos y trazabilidad existentes.
3. Pruebas automaticas criticas se ejecutan exitosamente con PostgreSQL.
4. Se identifican y corrigen diferencias de comportamiento entre SQLite y PostgreSQL.
5. Se documentan limites conocidos o deudas tecnicas remanentes tras la validacion.

## Evidencia esperada
- Suite de pruebas backend clave ejecutada contra PostgreSQL.
- Registro de resultados E2E basicos para EP_002 y EP_003.
- Documentacion de observaciones y ajustes necesarios.

## Notas
- Esta HU cierra la base tecnica para seguir roadmap funcional sobre PostgreSQL.
