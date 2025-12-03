class Proveedor:
    """Modelo de dominio para Proveedor.

    Ahora incluye `propietario_id` para identificar al tendero que lo creó.
    """

    def __init__(self, id, nombre, contacto=None, email=None, propietario_id=None):
        self.id = id
        self.nombre = nombre
        self.contacto = contacto
        self.email = email
        self.propietario_id = propietario_id

    def to_dict(self):
        """Convierte el proveedor a diccionario para guardar en BD."""
        data = {
            "id": self.id,
            "nombre": self.nombre,
            "contacto": self.contacto,
            "email": self.email
        }
        if self.propietario_id:
            data["propietario_id"] = self.propietario_id
        return data

    @staticmethod
    def from_dict(data):
        """Crea un Proveedor desde un diccionario."""
        return Proveedor(
            id=data.get("id"),
            nombre=data.get("nombre"),
            contacto=data.get("contacto"),
            email=data.get("email"),
            propietario_id=data.get("propietario_id")
        )
