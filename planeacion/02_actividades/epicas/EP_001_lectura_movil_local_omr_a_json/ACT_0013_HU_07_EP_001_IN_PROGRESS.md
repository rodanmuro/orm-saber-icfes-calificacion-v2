estado: in_progress
prioridad: alta
sprint: S2
owner: codex

# ACT_0013 - Prueba de conectividad LAN app Expo -> backend local

## Objetivo tecnico
Validar que el celular en la misma red local puede consumir el endpoint `health` del backend por IP local.

## Tareas implementables
- [x] Crear pantalla minima en Expo para probar `ping`/consulta a endpoint `health`.
- [x] Parametrizar IP y puerto del backend para no hardcodear entorno.
- [ ] Ejecutar prueba real desde celular en LAN y registrar resultado.
- [x] Documentar checklist de red local (misma WiFi, puerto, firewall) para repetibilidad.

## Evidencias esperadas
- Codigo de prueba de conectividad en frontend movil:
  - `src/frontend/App.js`
  - `src/frontend/src/config/api.js`
  - `src/frontend/src/services/health.js`
- Configuracion de entorno y guia de ejecucion:
  - `src/frontend/.env.example`
  - `src/frontend/README.md`
- Evidencia pendiente de respuesta satisfactoria del endpoint de salud en prueba LAN real.

## Criterio de terminado
La app Expo obtiene respuesta del backend por IP local en al menos una prueba real dentro de la LAN.
