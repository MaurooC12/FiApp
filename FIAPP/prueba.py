import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Crear usuario
user = auth.create_user(
    email="ejemplo@correo.com",
    password="miClave123",
    display_name="Ejemplo Usuario"
)
print("✅ Usuario creado:", user.uid)

# Obtener info
user_info = auth.get_user(user.uid)
print("📧 Email:", user_info.email)

# Actualizar
auth.update_user(user.uid, display_name="Nuevo Nombre")
print("✏️ Usuario actualizado.")

# Eliminar
# auth.delete_user(user.uid)
# print("🗑️ Usuario eliminado.")
