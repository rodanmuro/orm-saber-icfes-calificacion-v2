estado: done
prioridad: alta
sprint: S2
owner: codex

# ACT_0015 - Pantalla Expo de captura y envio de foto

## Objetivo tecnico
Implementar flujo minimo Expo para capturar foto y enviarla al endpoint backend OMR.

## Tareas implementables
- [x] Configurar permisos de camara en Expo.
- [x] Crear pantalla de captura manual de foto.
- [x] Implementar envio HTTP multipart al endpoint OMR.
- [x] Mostrar estados de carga y errores de comunicacion.
- [x] Ejecutar prueba real con captura y envio desde celular en LAN.

## Evidencias esperadas
- Pantalla y servicio movil:
  - `src/frontend/App.js`
  - `src/frontend/src/services/omrRead.js`
  - `src/frontend/src/config/api.js`
  - `src/frontend/.env.example`
  - `src/frontend/README.md`
- Dependencia:
  - `src/frontend/package.json` (`expo-image-picker`)

## Cierre breve
Se completo captura+envio desde Expo hacia backend local con respuesta OMR utilizable en pruebas e2e.

## Criterio de terminado
Desde la app Expo se captura y envia una foto real al backend local sin pasos manuales intermedios.
