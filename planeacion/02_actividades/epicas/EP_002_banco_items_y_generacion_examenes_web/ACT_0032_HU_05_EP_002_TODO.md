estado: todo
prioridad: alta
sprint: S4
owner: por_definir

# ACT_0032 - Modelo backend base para banco de items y actores academicos

## Objetivo tecnico
Definir e implementar el modelo inicial de datos para docentes, estudiantes e items, habilitando persistencia estructurada y versionable para el banco de preguntas.

## Tareas implementables
- [ ] Definir entidades base `teacher`, `student`, `item` y sus restricciones de unicidad.
- [ ] Crear migraciones iniciales de base de datos para dichas entidades.
- [ ] Exponer modelos/DTOs de lectura y escritura para items en backend.
- [ ] Implementar validaciones minimas de consistencia de pregunta (opciones A/B/C/D + respuesta correcta).
- [ ] Incluir campos curriculares basicos opcionales (estandar/competencia) en modo lite.

## Evidencias esperadas
- Migraciones aplicables en entorno local.
- Estructura de modelos en backend versionada en repositorio.
- Pruebas basicas de creacion y consulta de items.

## Criterio de terminado
El backend puede persistir y consultar items con estructura valida y metadatos curriculares basicos opcionales.
