class Local:
    def __init__(self, nombre, propietario_id):
        self.nombre = nombre
        self.propietario_id = propietario_id
        self.productos = {} 
        self.clientes = {}  

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "propietario_id": self.propietario_id,
            "productos": self.productos,
            "clientes": self.clientes
        }

    def local_create(self):
        return {
            "nombre": self.nombre,
            "propietario_id": self.propietario_id
            
        }