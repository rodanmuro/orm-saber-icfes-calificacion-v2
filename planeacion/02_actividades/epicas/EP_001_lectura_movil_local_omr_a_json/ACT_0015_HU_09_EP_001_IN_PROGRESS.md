estado: in_progress
prioridad: alta
sprint: S2
owner: codex

# ACT_0015 - Pantalla Expo de captura y envio de foto

## Objetivo tecnico
Implementar en Expo el flujo minimo para abrir camara, capturar imagen y enviarla al endpoint backend.

## Tareas implementables
- [x] Configurar permisos de camara en Expo.
- [x] Crear pantalla de captura manual de foto.
- [x] Implementar envio HTTP de imagen al endpoint backend OMR.
- [x] Mostrar estado de envio/carga y errores de comunicacion.
- [ ] Ejecutar prueba real desde celular capturando hoja y enviandola al backend LAN.

## Evidencias esperadas
- Pantalla funcional en app Expo para capturar y enviar foto:
  - `src/frontend/App.js`
- Servicio de envio multipart al endpoint OMR:
  - `src/frontend/src/services/omrRead.js`
- Configuracion de URL/metadata por entorno:
  - `src/frontend/.env.example`
  - `src/frontend/src/config/api.js`
- Dependencia de captura:
  - `src/frontend/package.json` (`expo-image-picker`)
- Documentacion de uso:
  - `src/frontend/README.md`
- Pendiente: evidencia de request exitoso con foto real desde celular.

## Criterio de terminado
Desde la app Expo se captura y envia una foto real al backend local sin pasos manuales intermedios.
