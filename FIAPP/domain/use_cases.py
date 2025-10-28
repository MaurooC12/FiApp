from domain.producto import Producto
from database.db_service import DBService


class UseCases:
    def __init__(self):
        self.db = DBService()

    # --- CRUD de Productos ---
    def crear_producto(self, local_id, nombre, precio, stock):
        producto = Producto(nombre, precio, stock)
        key = self.db.add_producto(local_id, producto.to_dict())
        print(f"✅ Producto '{nombre}' agregado con ID: {key}")

    def listar_productos(self, local_id):
        productos = self.db.get_productos(local_id)
        if not productos:
            print("No hay productos en este local.")
            return
        for pid, p in productos.items():
            print(f"[{pid}] {p['nombre']} - ${p['precio']} (Stock: {p['stock']})")

    def actualizar_producto(self, local_id, producto_id, nombre=None, precio=None, stock=None):
        data = {}
        if nombre:
            data["nombre"] = nombre
        if precio:
            data["precio"] = precio
        if stock:
            data["stock"] = stock
        self.db.update_producto(local_id, producto_id, data)
        print("✅ Producto actualizado correctamente.")

    def eliminar_producto(self, local_id, producto_id):
        self.db.delete_producto(local_id, producto_id)
        print("🗑️ Producto eliminado.")

    # --- Clientes / Deudas ---
    def registrar_cliente(self, local_id, cliente_id, cliente_data):
        self.db.add_cliente_a_local(local_id, cliente_id, cliente_data)
        print(f"✅ Cliente añadido al local {local_id}.")

    def listar_clientes(self, local_id):
        clientes = self.db.get_clientes(local_id)
        if not clientes:
            print("No hay clientes en este local.")
            return
        for cid, c in clientes.items():
            print(f"- {c['nombre']} ({c['email']}) | Deuda: ${c.get('deuda', 0)}")

    def registrar_deuda(self, local_id, cliente_id, monto):
        self.db.registrar_deuda(local_id, cliente_id, monto)
        print(f"💰 Deuda de ${monto} añadida al cliente {cliente_id}.")
