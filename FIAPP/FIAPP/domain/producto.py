class Producto:
    def __init__(self, nombre, precio, stock, imagen_url=None, proveedor=None):
        self.nombre = nombre
        self.precio = precio
        self.stock = stock
        self.imagen_url = imagen_url  # URL relativa a /static/productos/...
        self.proveedor = proveedor  # Nombre o ID del proveedor

    def to_dict(self):
        data = {
            "nombre": self.nombre,
            "precio": self.precio,
            "stock": self.stock
        }
        if self.imagen_url:
            data["imagen_url"] = self.imagen_url
        if self.proveedor:
            data["proveedor"] = self.proveedor
        return data
