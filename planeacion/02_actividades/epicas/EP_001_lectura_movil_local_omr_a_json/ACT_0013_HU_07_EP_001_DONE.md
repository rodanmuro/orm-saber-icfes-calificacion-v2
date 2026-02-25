estado: done
prioridad: alta
sprint: S2
owner: codex

# ACT_0013 - Prueba de conectividad LAN app Expo -> backend local

## Objetivo tecnico
Validar conectividad real desde celular en LAN hacia backend local por IP.

## Tareas implementables
- [x] Crear pantalla minima en Expo para probar endpoint `health`.
- [x] Parametrizar IP/puerto del backend sin hardcode.
- [x] Ejecutar prueba real desde celular en LAN y registrar resultado.
- [x] Documentar checklist de red local (WiFi, puerto, firewall).

## Evidencias esperadas
- Frontend de conectividad y configuracion:
  - `src/frontend/App.js`
  - `src/frontend/src/config/api.js`
  - `src/frontend/src/services/health.js`
  - `src/frontend/.env.example`
  - `src/frontend/README.md`
- Prueba e2e LAN ejecutada exitosamente.

## Cierre breve
Se verifico comunicacion celular->backend en LAN con respuesta correcta del endpoint de salud y flujo repetible por configuracion de IP.

## Criterio de terminado
La app Expo obtiene respuesta del backend por IP local en prueba real de LAN.
