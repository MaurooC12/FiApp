from firebase_admin import auth, db


class AuthService:
    """
    Maneja autenticación y registro de usuarios con Firebase Auth y DB.
    """
    def __init__(self):
        self.ref = db.reference("/")
    
    def register_user(self, email, password, role ,user_id):
        user = auth.create_user(email=email, password=password)
        ref = self.ref.child(f"usuarios/{user_id}")
        ref.set({
            "email": email,
            "rol": role,
            "user_id": user_id  # Guarda el ID personalizado como dato adicional
        })
        alias_ref = self.ref.child(f"usuarios/{user_id}/alias")
        alias_ref.set(user.uid)
        return user_id  # NO Retorna el UID real de Firebase

    def get_user_role(self, uid):
        ref = db.reference(f"usuarios/{uid}/rol")
        return ref.get()

    def list_users(self):
        ref = db.reference("usuarios")
        return ref.get() or {}

    def delete_user(self, custom_id):
        alias_ref = self.ref.child(f"usuarios/{custom_id}/alias")
        uid = alias_ref.get()
        if not uid:
            print("⚠️ No se encontró usuario con ese ID personalizado.")
            return False
        
        try:
            auth.delete_user(uid)
            print("🗑️ Usuario eliminado de Firebase Auth.")
        except Exception as e:
            print(f"⚠️ Usuario no eliminado en Firebase Auth: {e}")
            return False
        
        try:
            user_ref = self.ref.child(f"usuarios/{custom_id}")
            user_ref.delete()
            print("🗑️ Datos del usuario eliminados de Firebase DB.")
        
        except Exception as e:
            print(f"⚠️ Datos del usuario no eliminados de Firebase DB: {e}")
            return False
        
        try:
            alias_ref.delete()
            print("🗑️ Alias eliminado de Firebase DB.")
            return True
        except Exception as e:
            print(f"⚠️ Alias no eliminado en Firebase DB: {e}")
            return False