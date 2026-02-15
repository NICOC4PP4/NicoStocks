#!/bin/bash
set -e

# 1. Configurar Puerto de Nginx (Railway asigna $PORT aleatorio)
echo "Configuring Nginx to listen on port $PORT..."
sed -i "s/PORT_PLACEHOLDER/$PORT/g" /etc/nginx/nginx.conf

# 2. Inyectar API_URL en Runtime
# Reemplazamos el placeholder del build por la variable de entorno real de Railway
if [ -z "$API_URL" ]; then
  echo "WARNING: API_URL not set, defaulting to localhost:8000"
  REAL_API_URL="http://localhost:8000"
else
  echo "Injecting API_URL: $API_URL"
  REAL_API_URL="$API_URL"
fi

echo "Replacing placeholder in static files..."
find .web/build/client -type f -name "*.js" -exec sed -i "s|http://API_URL_PLACEHOLDER|$REAL_API_URL|g" {} +

# 3. Iniciar Backend en segundo plano
echo "Starting Reflex Backend..."
reflex run --env prod --backend-only --loglevel info &

# 4. Esperar a que el backend arranque (opcional, Nginx reintentará)
sleep 5

# 5. Iniciar Nginx en primer plano (bloqueante)
echo "Starting Nginx..."
nginx -g "daemon off;"
