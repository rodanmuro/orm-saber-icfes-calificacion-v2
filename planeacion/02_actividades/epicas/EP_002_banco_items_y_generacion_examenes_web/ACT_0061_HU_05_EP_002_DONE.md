estado: done
prioridad: media
sprint: S8
owner: por_definir

# ACT_0061 - Layout dashboard full-width y sidebar sticky en frontend web

## Objetivo tecnico
Reorganizar la interfaz del modulo web de items hacia un layout tipo dashboard, maximizando ancho util y manteniendo navegacion lateral fija durante scroll.

## Tareas implementables
- [ ] Eliminar limite estricto de ancho del contenedor principal para trabajar en full-width.
- [ ] Estructurar layout con dos zonas: sidebar lateral y contenido principal.
- [ ] Implementar sidebar sticky (`position: sticky`) con comportamiento estable en scroll largo.
- [ ] Ajustar distribucion responsiva para pantallas medianas y pequenas.
- [ ] Verificar que las vistas de edicion/listado/builder sigan operativas tras el refactor visual.
- [ ] Ejecutar validacion de build frontend y prueba manual de navegacion.

## Evidencias esperadas
- Vista de dashboard que aprovecha casi todo el ancho de la pantalla.
- Sidebar navegable y fijo durante scroll.
- Evidencia de no-regresion funcional en vistas principales.

## Criterio de terminado
La interfaz web queda optimizada para uso operativo continuo en desktop, sin perder compatibilidad en resoluciones menores.

