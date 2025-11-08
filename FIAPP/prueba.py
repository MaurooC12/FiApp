import firebase_admin
from firebase_admin import credentials, auth
from database.auth_service import AuthService
import os
from dotenv import load_dotenv
from database.firebase_config import init_firebase
load_dotenv()

# Usar las mismas variables que el resto del proyecto
'''cred_path = os.getenv("FIREBASE_CREDENTIAL_JSON")
db_url = os.getenv("FIREBASE_DATABASE_URL")

if not cred_path:
    raise RuntimeError("FIREBASE_CREDENTIAL_JSON no está definido en .env")

cred = credentials.Certificate(cred_path)
if db_url:
    firebase_admin.initialize_app(cred, {"databaseURL": db_url})
else:
    firebase_admin.initialize_app(cred)
'''
init_firebase()
# Crear usuario
authe = AuthService()
uid = authe.register_user(
    email="estoesunex@correo.com",
    password="micontrasña",
    role= "admin"
)
print("✅ Usuario creado:", uid)

# Obtener info
user_info = auth.get_user(uid)
print("📧 Email:", user_info.email)

# Actualizar
auth.update_user(uid, display_name="Nuevo Nombre")
print("✏️ Usuario actualizado.")

# Para eliminar, descomenta si lo deseas:
# auth.delete_user(uid)
# print("🗑️ Usuario eliminado.")
