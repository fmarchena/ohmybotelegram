FROM python:3.9

WORKDIR /app

# Copiar los archivos necesarios al contenedor
COPY script.py /app/extract_env.py
COPY .env /app/.env

# Instalar dependencias necesarias
RUN pip install docker python-dotenv requests

# Deshabilitar buffering para mostrar logs en tiempo real
ENV PYTHONUNBUFFERED=1

# Definir el comando de inicio del contenedor
CMD ["python", "/app/extract_env.py"]
