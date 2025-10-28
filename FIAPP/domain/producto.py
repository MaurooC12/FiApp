class Producto:
    def __init__(self, nombre, precio, stock):
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

    def to_dict(self):
        return {"nombre": self.nombre, "precio": self.precio, "stock": self.stock}
