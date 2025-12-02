from firebase_admin import db
import hashlib
from database import local_auth_db


class AuthService:
    def __init__(self, use_local=False):
        # use_local: si True, guarda/lee en archivo local en vez de Firebase (útil para debugging)
        self.use_local = use_local
    
    def _hash_password(self, password):
        """Hash simple de contraseña."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, email, password, user_id):
        """Registra usuario en BD (sin rol; se asigna después)."""
        print(f"[REGISTER] Iniciando registro para {email}")
        
        if not email or not password or not user_id:
            raise ValueError("Email, contraseña y usuario son requeridos")
        
        email_key = hashlib.md5(email.lower().encode()).hexdigest()
        print(f"[REGISTER] email_key: {email_key}")

        # Verificar si ya existe
        if self.use_local:
            existing = local_auth_db.get_user_by_email(email)
        else:
            existing = db.reference(f"usuarios/{email_key}").get()

        if existing:
            print(f"[REGISTER] Email ya existe")
            raise ValueError("El email ya está registrado")

        # Guardar (sin rol inicial)
        password_hash = self._hash_password(password)
        data = {
            "email": email,
            "password_hash": password_hash,
            "user_id": user_id,
            "tipo_usuario": None  # Se asigna después
        }
        print(f"[REGISTER] Guardando: {data}")
        if self.use_local:
            local_auth_db.create_user(email, password, user_id, None)
        else:
            db.reference(f"usuarios/{email_key}").set(data)

        print(f"[REGISTER] ✓ Registro exitoso")
        return user_id

    def login_user(self, email, password):
        """Autentica usuario contra BD; devuelve email y tipo_usuario (puede ser None)."""
        print(f"[LOGIN] Intentando login para {email}")
        
        if not email or not password:
            print(f"[LOGIN] Email o password vacío")
            return None, None
        
        try:
            email_key = hashlib.md5(email.lower().encode()).hexdigest()
            print(f"[LOGIN] Buscando usuario: {email_key}")

            if self.use_local:
                user_data = local_auth_db.get_user_by_email(email)
            else:
                user_data = db.reference(f"usuarios/{email_key}").get()

            print(f"[LOGIN] user_data: {user_data}")
            
            if not user_data:
                print(f"[LOGIN] Usuario no encontrado")
                return None, None
            
            stored_hash = user_data.get("password_hash")
            provided_hash = self._hash_password(password)
            
            if stored_hash != provided_hash:
                print(f"[LOGIN] Contraseña incorrecta")
                return None, None
            
            tipo_usuario = user_data.get("tipo_usuario")
            user_id = user_data.get("user_id")
            print(f"[LOGIN] ✓ Login exitoso, tipo: {tipo_usuario}, user_id: {user_id}")
            return user_id, tipo_usuario
        except Exception as e:
            print(f"[LOGIN] Error: {e}")
            return None, None

    def get_user_by_email(self, email):
        """Obtiene usuario por email."""
        email_key = hashlib.md5(email.lower().encode()).hexdigest()
        return db.reference(f"usuarios/{email_key}").get()
    
    def set_user_type(self, email, tipo_usuario):
        """Asigna el tipo de usuario (tendero/cliente) después del registro."""
        if tipo_usuario not in ('tendero', 'cliente'):
            raise ValueError("tipo_usuario debe ser 'tendero' o 'cliente'")
        email_key = hashlib.md5(email.lower().encode()).hexdigest()
        db.reference(f"usuarios/{email_key}").update({"tipo_usuario": tipo_usuario})
        print(f"[AUTH] Tipo de usuario asignado: {email} -> {tipo_usuario}")

    def list_users(self):
        """Lista todos los usuarios."""
        return db.reference("usuarios").get() or {}

    def delete_user(self, email):
        """Elimina usuario."""
        email_key = hashlib.md5(email.lower().encode()).hexdigest()
        db.reference(f"usuarios/{email_key}").delete()
