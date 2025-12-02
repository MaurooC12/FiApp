class Usuario:
    """Modelo de usuario sin rol fijo. El tipo se asigna después del registro."""
    def __init__(self, uid, email, tipo_usuario=None):
        self.uid = uid
        self.email = email
        self.tipo_usuario = tipo_usuario  # 'tendero' o 'cliente'

    def to_dict(self):
        return {
            "uid": self.uid,
            "email": self.email,
            "tipo_usuario": self.tipo_usuario
        }

    def __repr__(self):
        tipo_str = f" ({self.tipo_usuario})" if self.tipo_usuario else " (sin asignar)"
        return f"{self.email}{tipo_str}"
