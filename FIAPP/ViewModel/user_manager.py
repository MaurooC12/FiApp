from database.auth_service import AuthService


class Administrador:
    def __init__(self):
        self.auth = AuthService()

    def crear_usuario(self, email, password, rol,user_id):
        try:
            uid = self.auth.register_user(email, password, rol,user_id)
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
        return usuarios
       
    def eliminar_usuario(self, uid):
        try:
            self.auth.delete_user(uid)
            print(f"🗑️ Usuario {uid} eliminado correctamente.")
            return True
        except Exception as e:
            print(f"❌ Error eliminando usuario: {e}")
            return False