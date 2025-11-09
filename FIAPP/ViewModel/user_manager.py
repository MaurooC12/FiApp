from database.auth_service import AuthService


class Administrador:
    def __init__(self):
        self.auth = AuthService()

    def crear_usuario(self, email, password, rol):
        try:
            uid = self.auth.register_user(email, password, rol)
            print(f"✅ Usuario '{email}' creado con rol '{rol}' (UID: {uid})")
        except Exception as e:
            print(f"❌ Error creando usuario: {e}")

    def listar_usuarios(self):
        usuarios = self.auth.list_users()
        try: 
            print("\n=== Lista de usuarios ===")
            for uid, data in usuarios.items():
                print(f"- UID: {uid} | Email: {data['email']} | Rol: {data['rol']}")
        except Exception as e:
            print(f"❌ Error listando usuarios: {e}")
            if not usuarios:
                print("No hay usuarios registrados.")
        return
       
    def eliminar_usuario(self, uid):
        try:
            self.auth.delete_user(uid)
            print(f"🗑️ Usuario {uid} eliminado correctamente.")
        except Exception as e:
            print(f"❌ Error eliminando usuario: {e}")
