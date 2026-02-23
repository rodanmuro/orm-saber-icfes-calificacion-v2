estado: todo
prioridad: alta
sprint: S1
owner: por_definir

# ACT_0004 - Generar burbujas OMR parametrizadas con IDs estables

## Objetivo tecnico
Implementar grilla de burbujas basada en configuracion (filas, columnas, spacing, radio) garantizando IDs deterministas.

## Tareas implementables
- [ ] Definir `bubble_config` (estructura de grupos, filas/columnas, radio, separaciones).
- [ ] Implementar algoritmo de distribucion dentro del bloque principal.
- [ ] Definir estrategia de IDs estables (ej: prefijo + indice determinista).
- [ ] Validar que todas las burbujas queden dentro del bloque.

## Evidencias esperadas
- Plantilla con conjunto de burbujas dibujadas.
- Lista estructurada de burbujas con ID y geometria.

## Criterio de terminado
Con misma configuracion se obtienen exactamente los mismos IDs y coordenadas de burbujas en ejecuciones consecutivas.
