import docker
import os

def extract_env_file(container_name, source_path, destination_path):
    try:
        # Conectar al socket de Docker
        client = docker.from_env()

        # Obtener el contenedor
        container = client.containers.get(container_name)
        
        # Extraer el archivo desde el contenedor
        bits, stat = container.get_archive(source_path)

        # Guardar el archivo localmente
        with open(destination_path, 'wb') as f:
            for chunk in bits:
                f.write(chunk)

        print(f"Archivo extraído con éxito en: {destination_path}")
    
    except docker.errors.NotFound:
        print(f"El contenedor '{container_name}' no fue encontrado.")
    except Exception as e:
        print(f"Error durante la extracción: {e}")

if __name__ == "__main__":
    CONTAINER_NAME = "JWT_SECRET"  # Nombre del contenedor con el .env
    SOURCE_PATH = "/var/www/html/.env"  # Ruta dentro del contenedor
    DEST_PATH = "/root/.env"  # Ruta donde guardar el archivo localmente

    extract_env_file(CONTAINER_NAME, SOURCE_PATH, DEST_PATH)

    # Leer el archivo extraído para verificar el token
    if os.path.exists(DEST_PATH):
        with open(DEST_PATH, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith('JWT_SECRET='):
                    print(f"JWT_SECRET encontrado: {line.strip()}")
 