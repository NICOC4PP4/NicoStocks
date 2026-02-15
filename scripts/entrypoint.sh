#!/bin/bash

# 1. Configurar Puerto de Nginx (Railway asigna $PORT aleatorio)
echo "=== SmartFolio Entrypoint ==="
echo "PORT=$PORT"
echo "API_URL=$API_URL"
sed -i "s/PORT_PLACEHOLDER/$PORT/g" /etc/nginx/nginx.conf

# 2. Debug: verificar que los archivos estáticos existen
echo "--- Static files check ---"
ls -la /app/.web/build/client/ 2>&1 || echo "ERROR: /app/.web/build/client/ NOT FOUND"
ls -la /app/.web/build/client/assets/ 2>&1 | head -5 || echo "ERROR: assets/ NOT FOUND"
echo "--- End check ---"

# 3. Inyectar API_URL en Runtime (non-fatal)
if [ -z "$API_URL" ]; then
  echo "WARNING: API_URL not set, defaulting to localhost:8000"
  REAL_API_URL="http://localhost:8000"
else
  echo "Injecting API_URL: $API_URL"
  REAL_API_URL="$API_URL"
fi

echo "Replacing placeholder in static files..."
find /app/.web/build/client -type f -name "*.js" -exec sed -i "s|http://API_URL_PLACEHOLDER|$REAL_API_URL|g" {} + 2>/dev/null || echo "WARNING: find/sed failed (non-fatal)"

# 4. Iniciar Backend en segundo plano
echo "Starting Reflex Backend..."
reflex run --env prod --backend-only --loglevel info &

# 5. Esperar a que el backend arranque
sleep 5

# 6. Verificar configuración de Nginx
echo "Testing Nginx config..."
nginx -t 2>&1

# 7. Iniciar Nginx en primer plano (bloqueante)
echo "Starting Nginx on port $PORT..."
nginx -g "daemon off;"
