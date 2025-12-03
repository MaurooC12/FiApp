from firebase_admin import db
import hashlib
# from database import local_auth_db  # TODO: implementar si se necesita almacenamiento local


class AuthService:
    def __init__(self, use_local=False):
        # use_local: si True, guarda/lee en archivo local en vez de Firebase (útil para debugging)
        self.use_local = use_local
    
    def _hash_password(self, password):
        """Hash simple de contraseña."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def user_id_exists(self, user_id):
        """Verifica si un user_id ya existe en la BD."""
        try:
            usuarios = db.reference("usuarios").get() or {}
            for email_key, user_data in usuarios.items():
                if user_data.get("user_id") == user_id:
                    return True
            return False
        except Exception as e:
            print(f"[ERROR] al verificar user_id: {e}")
            return False
    
    def register_user(self, email, password, user_id):
        """Registra usuario en BD (sin rol; se asigna después)."""
        print(f"[REGISTER] Iniciando registro para {email}")
        
        if not email or not password or not user_id:
            raise ValueError("Email, contraseña y usuario son requeridos")
        
        email_key = hashlib.md5(email.lower().encode()).hexdigest()
        print(f"[REGISTER] email_key: {email_key}")

        # Verificar si ya existe el email
        existing = db.reference(f"usuarios/{email_key}").get()

        if existing:
            print(f"[REGISTER] Email ya existe")
            raise ValueError("El email ya está registrado")
        
        # Verificar si el user_id ya existe (VALIDACIÓN DE UNICIDAD)
        print(f"[REGISTER] Verificando unicidad de user_id: {user_id}")
        if self.user_id_exists(user_id):
            print(f"[REGISTER] user_id '{user_id}' ya está en uso")
            raise ValueError(f"El nombre de usuario '{user_id}' ya está en uso. Elige otro.")

        # Guardar (sin rol inicial)
        password_hash = self._hash_password(password)
        data = {
            "email": email,
            "password_hash": password_hash,
            "user_id": user_id,
            "tipo_usuario": None  # Se asigna después
        }
        print(f"[REGISTER] Guardando: {data}")
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
