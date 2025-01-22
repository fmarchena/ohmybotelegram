import docker
import os
import requests
import time
import re
from dotenv import load_dotenv

# Cargar las variables desde el archivo .env
load_dotenv()

# Obtener las variables de entorno
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = os.getenv("TELEGRAM_API_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # Asegúrate de configurarlo
CONTAINER_NAME = os.getenv("CONTAINER_NAME")
SOURCE_PATH = os.getenv("SOURCE_PATH")
DEST_PATH = os.getenv("DEST_PATH")

# Almacenar el último valor conocido del JWT_SECRET
previous_jwt_secret = '-'

def extract_env_file():
    """ Extrae el archivo .env del contenedor Docker. """
    print("Extrayendo el archivo .env del contenedor...")
    print(f"Contenedor: {CONTAINER_NAME}")
    print(f"Origen: {SOURCE_PATH}")
    print(f"Destino: {DEST_PATH}")

    try:
        client = docker.from_env()
        container = client.containers.get(CONTAINER_NAME)

        bits, _ = container.get_archive(SOURCE_PATH)

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

    print("Leyendo el valor de JWT_SECRET...")

    if os.path.exists(DEST_PATH):
        with open(DEST_PATH, 'r') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                print(line)

                if line.startswith('JWT_SECRET='):
                    current_jwt_secret = line.split('=')[1]

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

def escape_markdown_v2(text):
    """ Escapa caracteres especiales para enviar texto en MarkdownV2 a Telegram. """
    escape_chars = r"\_*[]()~`>#+-=|{}.!<>"
    return re.sub(r"([{}])".format(re.escape(escape_chars)), r"\\\1", text)

def send_telegram_alert(new_secret):
    """ Envía una notificación a Telegram cuando cambia el JWT_SECRET. """
    escaped_secret = escape_markdown_v2(new_secret)
    message = f"⚠️ *Alerta:* El valor de `JWT_SECRET` ha cambiado.\n\n*Nuevo valor:*\n`{escaped_secret}`\n\n*Código de seguridad:* `{WEBHOOK_SECRET}`"

    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "MarkdownV2"
    }

    try:
        response = requests.post(TELEGRAM_API_URL, data=data)
        if response.status_code == 200:
            print("Notificación de cambio enviada a Telegram.")
        else:
            print(f"Error al enviar notificación a Telegram: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con Telegram: {e}")

def monitor_changes():
    """ Bucle para monitorear cambios cada 5 minutos. """
    while True:
        if extract_env_file():
            read_jwt_secret()
        print("Esperando 5 minutos para la próxima verificación...")
        time.sleep(300)  # 300 segundos = 5 minutos

if __name__ == "__main__":
    monitor_changes()
