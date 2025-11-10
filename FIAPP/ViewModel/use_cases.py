from domain.producto import Producto
from database.db_service import DBService
from domain.local import Local


class UseCases:
    def __init__(self):
        self.db = DBService()

    # --- CRUD de Productos ---
    def crear_producto(self, local_id, nombre, precio, stock,producto_id):
        producto = Producto(nombre, precio, stock)
        key = self.db.add_producto(local_id, producto.to_dict(),producto_id)
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
            print(f"[{cid}] - {c['nombre']} ({c['email']}) | Deuda: ${c.get('deuda', 0)}")

    def registrar_deuda(self, local_id, cliente_id, monto, plazo_dias=None):
        self.db.registrar_deuda(local_id, cliente_id, monto, plazo_dias)
        if plazo_dias:
            print(f"💰 Deuda de ${monto} añadida al cliente {cliente_id} a pagar en {plazo_dias} días.")
        else:
            print(f"💰 Deuda de ${monto} añadida al cliente {cliente_id}.")

    def obtener_historial_deudas(self, local_id, cliente_id):
        """Devuelve un diccionario con los registros de deudas de un cliente en un local.

        Estructura retornada: { timestamp: {"monto": float, "timestamp": int, "plazo_dias": int?}, ... }
        """
        # Intentar obtener el nodo de deudas directamente
        detalles = self.db.ref.child(f"locales/{local_id}/clientes/{cliente_id}/deudas").get() or {}
        return detalles
  
    # --- Locales ---
    def crear_local(self, nombre, propietario_id, local_id):
        local = Local(nombre, propietario_id)
        self.db.add_local(local_id, local_data=local.local_create())
        print(f"✅ Local '{local_id}' creado.")
    
    def obtener_local(self, local_id):
        local = self.db.get_local(local_id)
        while not local:
            print("❌ Local no encontrado.")
            local_id = input("Ingrese un ID de local válido: ")
            local = self.db.get_local(local_id)
        print(f"Local ID: {local_id} | Datos: {local}")
        return local
    
    def actualizar_local(self, local_id, data):
        self.db.update_local(local_id, data)
        print(f"✅ Local '{local_id}' actualizado.")

    def eliminar_local(self, local_id):
        while not self.db.get_local(local_id):
            print("❌ Local no encontrado.")
            local_id = input("Ingrese un ID de local válido: ")
            self.eliminar_local(local_id)
        self.db.delete_local(local_id)
        print(f"🗑️ Local '{local_id}' eliminado.")
    
    def _listar_locales(self):
        locales = self.db.ref.child("locales").get() or {}
        if not locales:
            print("No hay locales registrados.")
            return
        for lid, l in locales.items():
            print(f"[{lid}] - {l['nombre']} | Propietario: {l['propietario_id']}")
        return locales
    
