estado: todo
prioridad: alta
sprint: S4
owner: por_definir

# ACT_0044 - Portabilidad de esquema de dominio a PostgreSQL

## Objetivo tecnico
Validar y ajustar tipos, constraints y relaciones del esquema actual para compatibilidad completa con PostgreSQL.

## Tareas implementables
- [ ] Revisar entidades y constraints del dominio actual en motor PostgreSQL.
- [ ] Ajustar tipos de columna (JSON, fechas, booleanos, textos) segun comportamiento esperado.
- [ ] Validar indices y unicidad de claves de negocio (`teacher_id + exam_code`, etc.).
- [ ] Confirmar integridad referencial en flujos de insercion/actualizacion.

## Evidencias esperadas
- Esquema completo creado sin errores en PostgreSQL.
- Relaciones y constraints funcionando segun reglas de negocio.
- Registro de ajustes de compatibilidad aplicados.

## Criterio de terminado
El modelo de datos actual queda estable y consistente en PostgreSQL.
