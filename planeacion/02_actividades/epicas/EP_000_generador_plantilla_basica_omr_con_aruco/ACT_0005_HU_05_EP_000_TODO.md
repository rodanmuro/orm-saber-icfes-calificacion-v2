estado: todo
prioridad: alta
sprint: S1
owner: por_definir

# ACT_0005 - Exportar metadatos de plantilla como fuente de verdad

## Objetivo tecnico
Implementar exportacion de metadatos (`template.json` o equivalente) desacoplada del renderer visual, con esquema consistente y validable.

## Tareas implementables
- [ ] Definir esquema minimo: pagina, ArUco, bloque principal, burbujas, version de plantilla.
- [ ] Implementar `metadata_exporter` independiente del backend de render.
- [ ] Asegurar correspondencia 1:1 entre elementos renderizados y metadatos.
- [ ] Agregar validacion de esquema (campos requeridos/tipos).

## Evidencias esperadas
- Archivo de metadatos generado por ejecucion.
- Validacion automatica basica del esquema en comando local.

## Criterio de terminado
El archivo de metadatos describe por completo la geometria necesaria para lectura OMR sin inferencias manuales.
