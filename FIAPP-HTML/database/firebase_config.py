import os
import firebase_admin
from firebase_admin import credentials , db
from dotenv import load_dotenv

load_dotenv()


def init_firebase():
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    db_url = os.getenv("FIREBASE_DB_URL")

    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {"databaseURL": db_url})

    print("✅ Firebase inicializado correctamente.\n")
