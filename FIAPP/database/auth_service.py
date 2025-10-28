from database.firebase_config import db

class AuthService:
    def __init__(self):
        self.ref_usuarios = db.reference("usuarios")

    def crear_usuario(self, uid, nombre, email, rol="cliente"):
        """Crea un nuevo usuario con un rol."""
        self.ref_usuarios.child(uid).set({
            "nombre": nombre,
            "email": email,
            "rol": rol
        })
        print(f"✅ Usuario '{nombre}' creado como {rol}")

    def obtener_rol(self, uid):
        """Devuelve el rol del usuario."""
        data = self.ref_usuarios.child(uid).get()
        return data.get("rol") if data else None

    def cambiar_rol(self, uid, nuevo_rol):
        """Cambia el rol del usuario (solo admin)."""
        self.ref_usuarios.child(uid).update({"rol": nuevo_rol})
        print(f"🔄 Rol de {uid} actualizado a {nuevo_rol}")
