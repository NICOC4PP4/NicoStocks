# Usar imagen base ligera de Python 3.11
FROM python:3.11-slim

# Evitar que Python escriba archivos .pyc y buffering
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Instalar dependencias del sistema necesarias para Reflex y Node.js
# Reflex necesita Node.js para el frontend y unzip/curl para setup
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements primero para aprovechar caché de Docker
COPY scripts/requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Inicializar Reflex (Opcional si ya existe estructura, comentado para evitar fallo)
# RUN reflex init


# Exponer puertos: 3000 (Frontend), 8000 (Backend)
EXPOSE 3000
EXPOSE 8000

# Comando por defecto para desarrollo
CMD ["reflex", "run", "--env", "dev", "--backend-host", "0.0.0.0"]
