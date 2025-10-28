import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv
import os

# Cargar variables del archivo .env
load_dotenv()

# Obtener variables
cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
db_url = os.getenv("FIREBASE_DB_URL")

if not cred_path or not db_url:
    raise ValueError("❌ Configuración incompleta. Revisa tu archivo .env")

# Inicializar Firebase
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {
    "databaseURL": db_url
})
