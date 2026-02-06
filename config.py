import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8519041982:AAG9y3iaC9S9nk2bOo5rkI1-OMcXgsavG2o")
ADMIN_ID = int(os.getenv("ADMIN_ID", "6667062973"))

# Validar configuración
if not BOT_TOKEN or BOT_TOKEN == "8519041982:AAG9y3iaC9S9nk2bOo5rkI1-OMcXgsavG2o":
    print("⚠️  ADVERTENCIA: Estás usando un token público. Esto es INSECURO.")
    print("⚠️  Por favor, crea un nuevo bot con @BotFather y usa un token privado.")
