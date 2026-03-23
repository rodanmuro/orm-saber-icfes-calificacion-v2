estado: done
prioridad: media
sprint: S6
owner: por_definir

# ACT_0049 - Persistencia y pruebas de contenido con imagen en items

## Objetivo tecnico
Asegurar que el backend y frontend preserven correctamente contenido con imagenes en el JSON de enunciado/opciones y validar casos de regresion.

## Tareas implementables
- [x] Ajustar validaciones del payload para aceptar nodos de imagen en `statement` y `options`.
- [x] Confirmar lectura/escritura de contenido enriquecido al consultar y editar item.
- [x] Crear pruebas de API para item con contenido mixto (texto + imagen).
- [x] Crear prueba de integracion frontend-backend del flujo crear->listar->consultar item con imagen.
- [x] Documentar limitaciones iniciales (tamano, formato, fallback).

## Evidencias esperadas
- Pruebas backend y/o integracion en verde para items con imagen.
- Evidencia de roundtrip de contenido enriquecido sin perdida.
- Nota tecnica de limites actuales de imagen.

## Criterio de terminado
El sistema conserva de forma consistente los datos de items con imagenes en todo el ciclo de vida basico (crear, consultar, editar).

## Evidencia de cierre
- Persistencia validada en base de datos para `statement_doc` y `options_doc` con nodos de imagen.
- Pruebas de API/integracion ejecutadas para prevenir regresiones de roundtrip.
- Verificacion manual en frontend confirmando que al recargar el item se mantiene el contenido visual.
