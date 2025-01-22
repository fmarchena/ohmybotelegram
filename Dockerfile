FROM python:3.9

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos necesarios al contenedor
COPY script.py /app/extract_env.py
COPY .env /app/.env

# Instalar las dependencias necesarias
RUN pip install docker python-dotenv requests

# Definir el comando de inicio del contenedor
CMD ["python", "/app/extract_env.py"]