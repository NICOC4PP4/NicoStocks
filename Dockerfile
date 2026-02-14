# Usar imagen base ligera de Python 3.11
FROM python:3.11-slim

# Evitar que Python escriba archivos .pyc y buffering
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Instalar dependencias del sistema necesarias para Reflex y Node.js
# Reflex necesita Node.js para el frontend y unzip/curl para setup
# Instalar Nginx además de las dependencias anteriores
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    git \
    nodejs \
    npm \
    nginx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements
COPY scripts/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código y configuraciones
COPY . .
COPY nginx.conf /etc/nginx/nginx.conf

# Permisos de ejecución
RUN chmod +x scripts/entrypoint.sh

# Exponer el puerto variable (documentación solamente, Railway lo ignora e inyecta $PORT)
EXPOSE 8080

# Usar el script orquestador
CMD ["./scripts/entrypoint.sh"]
