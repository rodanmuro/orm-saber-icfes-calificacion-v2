# Bitacora 049_03_26_2026 10:07:58 dashboard_ancho_completo_y_menu_compacto

## Que fue lo que se hizo
- Se evoluciono el frontend a un layout tipo dashboard para usar casi todo el ancho disponible de la pagina.
- Se reorganizo `App.jsx` para trabajar con dos zonas principales:
  - Sidebar lateral (navegacion de pestañas).
  - Main content (topbar, formulario/listado y builder de examenes).
- Se ajustaron estilos globales para eliminar el limite de `max-width: 1200px` y pasar a distribucion full-width.
- Se dejo el menu lateral izquierdo fijo durante scroll (`position: sticky`, `top: 0`, `height: 100vh`, `overflow-y: auto`).
- Se compacto la barra de herramientas del editor rico:
  - Botones mas pequenos y con tooltips.
  - Abreviaciones visuales para acciones frecuentes.
  - Menu desplegable para herramientas de tabla (en vez de ocupar una fila completa de botones).
- Se corrigio un problema de texto IA con escapes tipo LaTeX en texto normal (ejemplo `gr\\'afico`) para convertirlo a acentos correctos en salida de borrador.
- Se agrego prueba automatizada para validar la normalizacion de acentos escapados.
- Se diagnostico y corrigio el problema estructural del sandbox local:
  - Causa: `bwrap 0.6.1` sin soporte de `--argv0`.
  - Mitigacion aplicada: wrapper local `~/.local/bin/bwrap` para compatibilidad con runtime actual.
- Archivos modificados relevantes:
  - `src/frontend_web/src/App.jsx`
  - `src/frontend_web/src/styles.css`
  - `src/frontend_web/src/components/RichTextEditor.jsx`
  - `src/backend/app/modules/item_ai_assistant/service.py`
  - `src/backend/tests/test_item_ai_assistant_service.py`

## Para que se hizo
- Mejorar el aprovechamiento de espacio en pantalla para trabajo operativo real (edicion de items, tablas, imagenes y revision de listados).
- Reducir friccion visual del editor, evitando toolbar extensa y poco compacta.
- Mantener disponibilidad del menu principal al hacer scroll en sesiones largas.
- Incrementar calidad del texto generado por IA al corregir escapes de acentos que afectaban UX.
- Eliminar la friccion operativa del sandbox para reducir interrupciones por solicitudes de permisos innecesarias.

## Que problemas se presentaron
- La interfaz estaba limitada por ancho maximo y no se comportaba como dashboard.
- El toolbar del editor ocupaba demasiado espacio horizontal y vertical.
- Se detectaron salidas IA con secuencias escapadas en lugar de caracteres acentuados.
- El sandbox fallaba con `bwrap: Unknown option --argv0`, obligando a usar permisos elevados con frecuencia.

## Como se resolvieron
- Se reestructuro la composicion visual en `App.jsx` y se aplicaron clases de dashboard en `styles.css`.
- Se definieron estilos de sidebar fija y main flexible, con comportamiento responsive para pantallas pequenas.
- Se rediseno la toolbar del editor con controles compactos y submenu para acciones de tabla.
- En backend se agrego normalizacion de escapes de acento en nodos de texto y test de regresion.
- Se diagnostico version de `bwrap` y se confirmo incompatibilidad con `--argv0`; se aplico wrapper de compatibilidad en `~/.local/bin/bwrap`.
- Verificaciones ejecutadas:
  - `cd src/frontend_web && npm run build` (multiple veces, exitoso)
  - `cd src/backend && source .venv/bin/activate && DEBUG=false pytest -q tests/test_item_ai_assistant_service.py` (exitoso)

## Que continua
- Refinar visualmente el dashboard (jerarquia tipografica, espaciado y consistencia entre tarjetas).
- Evaluar un modo de toolbar aun mas minimalista para pantallas pequenas.
- Definir si el sidebar tendra modulos adicionales (OMR, reportes, configuracion) o se mantiene enfocado en items/examenes.
- Agregar pruebas frontend (si aplica) para interacciones de toolbar y layout responsivo.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
