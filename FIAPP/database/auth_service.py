from firebase_admin import auth, db


class AuthService:
    """
    Maneja autenticación y registro de usuarios con Firebase Auth y DB.
    """

    def register_user(self, email, password, role):
        user = auth.create_user(email=email, password=password)
        ref = db.reference(f"usuarios/{user.uid}")
        ref.set({
            "email": email,
            "rol": role
        })
        return user.uid

    def get_user_role(self, uid):
        ref = db.reference(f"usuarios/{uid}/rol")
        return ref.get()

    def list_users(self):
        ref = db.reference("usuarios")
        return ref.get() or {}

    def delete_user(self, uid):
        auth.delete_user(uid)
        db.reference(f"usuarios/{uid}").delete()
