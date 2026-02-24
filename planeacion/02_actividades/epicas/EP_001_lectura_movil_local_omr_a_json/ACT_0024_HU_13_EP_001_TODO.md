estado: todo
prioridad: media
sprint: S2
owner: por_definir

# ACT_0024 - Modo de ejecucion alterno y trazabilidad de motor activo

## Objetivo tecnico
Permitir ejecutar backend en modo `classic` o `gemini` de forma explicita y trazable por solicitud.

## Tareas implementables
- [ ] Exponer en logs el motor activo por cada lectura.
- [ ] Agregar al resultado tecnico/campos de debug el motor utilizado.
- [ ] Documentar variables de entorno necesarias para cada motor.
- [ ] Definir politica de fallback por configuracion (sin fallback o fallback a classic).

## Evidencias esperadas
- Logs y salida tecnica con identificacion de motor.
- Documento corto de operacion para cambiar motor sin tocar codigo.

## Criterio de terminado
Es posible alternar motores en ejecucion y auditar claramente que motor proceso cada imagen.
