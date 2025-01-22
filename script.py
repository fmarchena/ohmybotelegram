import docker
import os
import requests
import time
from dotenv import load_dotenv

# Cargar las variables desde el archivo .env
load_dotenv()

# Obtener las variables de entorno
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = os.getenv("TELEGRAM_API_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

# Variables de contenedor y archivo
CONTAINER_NAME = os.getenv("CONTAINER_NAME")
SOURCE_PATH = os.getenv("SOURCE_PATH")
DEST_PATH =  os.getenv("DEST_PATH")


previous_jwt_secret = None

def extract_env_file():
    """ Extrae el archivo .env del contenedor Docker. """
    try:
        client = docker.from_env()
        container = client.containers.get(CONTAINER_NAME)
        
        bits, stat = container.get_archive(SOURCE_PATH)

        with open(DEST_PATH, 'wb') as f:
            for chunk in bits:
                f.write(chunk)

        print(f"Archivo extraído con éxito en: {DEST_PATH}")
        return True

    except docker.errors.NotFound:
        print(f"El contenedor '{CONTAINER_NAME}' no fue encontrado.")
        return False
    except Exception as e:
        print(f"Error durante la extracción: {e}")
        return False

def read_jwt_secret():
    """ Lee el valor de JWT_SECRET del archivo .env extraído. """
    global previous_jwt_secret

    if os.path.exists(DEST_PATH):
        with open(DEST_PATH, 'r') as file:
            lines = file.readlines()
            for line in lines:
                print(line.strip())
                if line.startswith('JWT_SECRET='):
                    current_jwt_secret = line.strip().split('=')[1]

                    if previous_jwt_secret is None:
                        previous_jwt_secret = current_jwt_secret
                        print("JWT_SECRET inicializado.")
                    elif previous_jwt_secret != current_jwt_secret:
                        print("El JWT_SECRET ha cambiado.")
                        send_telegram_alert(current_jwt_secret)
                        previous_jwt_secret = current_jwt_secret
                    else:
                        print("No hay cambios en JWT_SECRET.")
    else:
        print("El archivo .env no se encontró.")

def send_telegram_alert(new_secret):
    """ Envía una notificación a Telegram cuando cambia el JWT_SECRET. """
    message = f"⚠️ Alerta: El valor de JWT_SECRET ha cambiado.\n\nNuevo valor:\n`{new_secret}`\n\nCódigo de seguridad: `{WEBHOOK_SECRET}`"
    data = {
        "chat_id": "YOUR_TELEGRAM_CHAT_ID",  # Reemplazar con tu ID de chat de Telegram
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(TELEGRAM_API_URL, data=data)
    if response.status_code == 200:
        print("Notificación de cambio enviada a Telegram.")
    else:
        print("Error al enviar notificación a Telegram:", response.text)

def monitor_changes():
    """ Bucle para monitorear cambios cada 10 minutos. """
    while True:
        if extract_env_file():
            read_jwt_secret()
        print("Esperando 10 minutos para la próxima verificación...")
        time.sleep(600)  # 600 segundos = 10 minutos

if __name__ == "__main__":
    monitor_changes()
