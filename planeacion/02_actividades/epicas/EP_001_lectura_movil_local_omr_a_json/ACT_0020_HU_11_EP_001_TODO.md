estado: todo
prioridad: media
sprint: S2
owner: por_definir

# ACT_0020 - Reporte de benchmark por lote para EP_001

## Objetivo tecnico
Consolidar metricas de rendimiento de lectura por imagen para seguimiento de calidad en EP_001.

## Tareas implementables
- [ ] Definir esquema de benchmark (accuracy por imagen, promedio global, rechazos ArUco, ambiguas, vacias).
- [ ] Automatizar generacion de reporte sobre conjunto `mobile_uploads`.
- [ ] Exportar reporte en formato reutilizable (JSON/CSV) para bitacoras y decisiones.
- [ ] Documentar criterio de aceptacion minimo para continuar a siguiente fase.

## Evidencias esperadas
- Archivo de benchmark con resultados por imagen.
- Resumen ejecutivo con metricas globales.

## Criterio de terminado
Se dispone de un benchmark reproducible que permite medir progreso entre iteraciones de robustez.
