# Bitacora 068_04_29_2026 22:47:58 orquestador_start_all_logs_colores

## Que fue lo que se hizo
- Se robustecio el orquestador local `scripts/start_all.sh` para inicializar y supervisar toda la stack (`backend`, `frontend_web`, `frontend_results`, `frontend` Expo) con comandos consistentes: `start`, `stop`, `restart`, `status`, `logs`, `attach` y `mobile`.
- Se mejoro la deteccion de procesos vivos por PID y por patron para evitar falsos negativos con procesos `npm/vite/expo` que cambian de PID durante recargas.
- Se agrego limpieza adicional al detener servicios (`pkill` por patron) para evitar procesos huerfanos.
- Se agrego compatibilidad segura para ejecucion con `source` (sin cerrar la terminal) y accion por defecto `start` cuando no se pasa argumento.
- Se agrego modo `attach` para ver logs en vivo combinados, con prefijo por servicio y timestamp por linea.
- Se agregaron colores ANSI en `attach` para identificar rapidamente cada servicio (estilo `docker compose`).
- Se agrego modo `mobile` para abrir Expo en foreground con QR (sin reiniciar backend ni frontends web), deteniendo unicamente Expo en background para liberar el puerto.
- Se ajusto el flujo de Expo para evitar `--non-interactive` (incompatible en la version instalada) y mantener modo interactivo al mostrar QR.
- Se mantuvieron/actualizaron ajustes de entorno y conectividad LAN ya implementados en:
  - `src/backend/app/core/config.py`
  - `src/backend/app/main.py`
  - `src/backend/.env.example`
  - `src/frontend_results/src/api/studentPortalApi.js`
  - `src/frontend_results/vite.config.js`
  - `src/frontend_web/vite.config.js`
- Se continuaron ajustes de analiticas en:
  - `src/frontend_web/src/components/AnalyticsPanel.jsx`
- Tambien se actualizaron instrucciones en:
  - `README.md`

## Para que se hizo
- Reducir friccion operativa al iniciar todo el ecosistema del proyecto desde un unico comando.
- Evitar errores de arranque por PIDs stale y por diferencias entre procesos lanzados por `npm`, `vite` y `expo`.
- Mejorar trazabilidad en tiempo real de logs, con identificacion visual rapida de servicio.
- Separar claramente dos necesidades: logs unificados (`attach`) y QR de Expo (`mobile`).

## Que problemas se presentaron
- `frontend_web` y otros servicios podian arrancar correctamente, pero el script reportaba error por validacion de PID/cmdline demasiado estricta.
- Ejecutar `source ./scripts/start_all.sh` sin argumentos podia terminar la shell con `exit code 1`.
- Expo fallaba en arranque automatizado cuando se forzaba `--non-interactive` y/o `CI=1` en este entorno.
- En modo `attach`, el usuario esperaba ver QR, pero ese modo solo transmite logs (no TTY interactivo de Expo).

## Como se resolvieron
- Se reescribio la validacion `is_running` para:
  - aceptar firmas de proceso reales (`vite`, `npm run dev`, `node`, `expo`, `uvicorn`);
  - realizar fallback con `pgrep -f` cuando el PID inicial cambia.
- Se ajusto `stop_service` para limpieza complementaria por patron, evitando residuos.
- Se incorporo `safe_exit` para que el script no cierre la terminal cuando se ejecuta con `source`.
- Se establecio accion por defecto `start`, eliminando el fallo por invocacion sin argumentos.
- Se remplazo estrategia de Expo no interactivo por:
  - arranque normal en background para stack completa (`start`);
  - arranque interactivo dedicado para QR (`mobile`).
- Se implemento `attach` con `tail -F` concurrente por servicio + prefijo de nombre + hora y colores ANSI.
- Se dejo nota explicita en `attach`: para QR se debe usar `mobile`.

## Que continua
- Documentar en README ejemplos completos de flujo recomendado:
  - `start` -> `attach` -> `mobile` (cuando se requiera QR).
- Agregar una opcion futura `health` para verificar puertos/respuesta HTTP de cada servicio.
- Evaluar persistir una configuracion de colores (activar/desactivar) para terminales sin soporte ANSI.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
