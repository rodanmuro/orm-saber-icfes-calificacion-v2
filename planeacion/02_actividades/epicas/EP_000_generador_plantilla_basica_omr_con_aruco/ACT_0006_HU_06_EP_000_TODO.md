estado: todo
prioridad: alta
sprint: S1
owner: por_definir

# ACT_0006 - Comando reproducible y validacion multi-configuracion

## Objetivo tecnico
Exponer un comando unico de generacion y validar parametrizacion ejecutando el pipeline con multiples configuraciones sin cambios de codigo.

## Tareas implementables
- [ ] Implementar CLI/script de entrada unica para generar plantilla + metadatos.
- [ ] Definir manejo de errores controlado para config invalida.
- [ ] Crear al menos 2 configuraciones adicionales de prueba (ademas de la base).
- [ ] Ejecutar pipeline con cada config y comparar consistencia estructural de salidas.
- [ ] Documentar comando y ejemplos de uso.

## Evidencias esperadas
- Comando documentado en `README` tecnico o doc de ejecucion.
- Salidas de plantilla/metadatos para varias configuraciones.
- Registro de validacion de reproducibilidad por configuracion.

## Criterio de terminado
El mismo comando genera correctamente plantillas variantes solo cambiando config, demostrando escalabilidad y ausencia de hardcode critico.
