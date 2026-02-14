#!/bin/bash
set -e

# 1. Configurar Puerto de Nginx (Railway asigna $PORT aleatorio)
echo "Configuring Nginx to listen on port $PORT..."
sed -i "s/PORT_PLACEHOLDER/$PORT/g" /etc/nginx/nginx.conf

# 2. Exportar Frontend Estático (Build Time)
# Esto genera los archivos HTML/JS en .web/_static
echo "Building Frontend..."
reflex export --frontend-only --no-zip

# 3. Iniciar Backend en segundo plano
echo "Starting Reflex Backend..."
reflex run --env prod --backend-only --loglevel info &

# 4. Esperar a que el backend arranque (opcional, Nginx reintentará)
sleep 5

# 5. Iniciar Nginx en primer plano (bloqueante)
echo "Starting Nginx..."
nginx -g "daemon off;"
