estado: todo
prioridad: alta
sprint: S2
owner: por_definir

# ACT_0012 - CLI unica para lectura local fin a fin

## Objetivo tecnico
Exponer un comando unico de ejecucion local que reciba imagen+template y produzca JSON de resultados OMR.

## Tareas implementables
- [ ] Implementar CLI que orqueste carga, alineacion, lectura y exportacion.
- [ ] Validar argumentos requeridos y manejo de errores controlado.
- [ ] Permitir parametrizacion de umbral/config sin cambios de codigo.
- [ ] Documentar comando con ejemplos reales de uso.

## Evidencias esperadas
- Script CLI en `src/backend`.
- Ejecucion local demostrable de punta a punta con salida JSON.

## Criterio de terminado
El comando corre de forma reproducible para distintas fotos validas y reporta errores claros en entradas invalidas.
