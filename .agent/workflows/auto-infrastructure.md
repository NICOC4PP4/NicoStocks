---
description: Habilita la ejecución automática de comandos de infraestructura para el proyecto SmartFolio.
---

// turbo-all

Este flujo de trabajo permite que Antigravity ejecute comandos de gcloud, docker y mantenimiento sin pedir confirmación constante, agilizando la configuración del MCP de Stitch y el despliegue.

1. Ejecutar comandos de configuración de Google Cloud SDK.
2. Actualizar archivos de configuración del sistema (.env, mcp_config.json).
3. Reiniciar contenedores Docker si es necesario.
