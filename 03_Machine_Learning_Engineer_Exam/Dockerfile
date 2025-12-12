# --- Etapa 1: Definir la Base ---
FROM python:3.10-slim

# --- Etapa 2: Instalar Software ---
# 'cron' sigue siendo necesario porque el entrypoint lo inicia
# 'procps' es útil para depurar (contiene 'printenv')
RUN apt-get update && apt-get install -y cron procps

# --- Etapa 3: Configurar el Entorno ---
WORKDIR /app
RUN mkdir data
RUN mkdir logs

# Copiar archivos de requisitos e instalar Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Etapa 4: Copiar la Aplicación y el Entrypoint ---
# Copiamos el script de Python
COPY task_1_script.py .

# ¡CAMBIO IMPORTANTE!
# 1. Copiamos nuestro nuevo script entrypoint
COPY entrypoint.sh /app/entrypoint.sh
# 2. (¡CRÍTICO!) Le damos permisos de ejecución
RUN chmod +x /app/entrypoint.sh



