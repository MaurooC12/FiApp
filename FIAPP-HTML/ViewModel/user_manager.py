from database.auth_service import AuthService


class Administrador:
    def __init__(self):
        self.auth = AuthService()

    def crear_usuario(self, email, password, user_id):
        """Crea usuario sin asignar tipo. El tipo se asigna después."""
        try:
            uid = self.auth.register_user(email, password, user_id)
            return {"success": True, "user_id": uid}
        except Exception as e:
            return {"error": str(e)}

    def asignar_tipo_usuario(self, email, tipo_usuario):
        """Asigna el tipo de usuario después del registro."""
        try:
            self.auth.set_user_type(email, tipo_usuario)
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}

    def listar_usuarios(self):
        usuarios = self.auth.list_users()
        return usuarios or {}
       
    def eliminar_usuario(self, uid):
        try:
            self.auth.delete_user(uid)
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}
