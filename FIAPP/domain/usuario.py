class Usuario:
    def __init__(self, uid, email, rol):
        self.uid = uid
        self.email = email
        self.rol = rol

    def to_dict(self):
        return {"uid": self.uid, "email": self.email, "rol": self.rol}

    def __repr__(self):
        return f"{self.email} ({self.rol})"
