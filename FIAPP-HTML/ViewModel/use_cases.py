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
        return {"success": True, "producto_id": key}

    def listar_productos(self, local_id):
        productos = self.db.get_productos(local_id)
        return productos or {}

    def actualizar_producto(self, local_id, producto_id, nombre=None, precio=None, stock=None):
        data = {}
        if nombre:
            data["nombre"] = nombre
        if precio:
            data["precio"] = precio
        if stock:
            data["stock"] = stock
        self.db.update_producto(local_id, producto_id, data)
        return {"success": True}

    def eliminar_producto(self, local_id, producto_id):
        self.db.delete_producto(local_id, producto_id)
        return {"success": True}

    # --- Clientes / Deudas ---
    def registrar_cliente(self, local_id, cliente_id, cliente_data):
        self.db.add_cliente_a_local(local_id, cliente_id, cliente_data)
        return {"success": True}

    def listar_clientes(self, local_id):
        clientes = self.db.get_clientes(local_id)
        return clientes or {}

    def registrar_deuda(self, local_id, cliente_id, monto, plazo_dias=None):
        self.db.registrar_deuda(local_id, cliente_id, monto, plazo_dias)
        return {"success": True}

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
        return {"success": True, "local_id": local_id}
    
    def obtener_local(self, local_id):
        local = self.db.get_local(local_id)
        return local
    
    def actualizar_local(self, local_id, data):
        self.db.update_local(local_id, data)
        return {"success": True}

    def eliminar_local(self, local_id):
        if not self.db.get_local(local_id):
            return {"error": "Local no encontrado"}
        self.db.delete_local(local_id)
        return {"success": True}
    
    def _listar_locales(self):
        locales = self.db.ref.child("locales").get() or {}
        return locales
    
    def listar_locales_por_propietario(self, propietario_id):
        """Lista locales propiedad de un tendero."""
        todos_locales = self.db.ref.child("locales").get() or {}
        resultado = {}
        for local_id, local_data in todos_locales.items():
            if local_data.get("propietario_id") == propietario_id:
                resultado[local_id] = local_data
        return resultado
    
    def get_deudas_cliente(self, cliente_id):
        """Obtiene todas las deudas de un cliente en todos los locales."""
        todos_locales = self.db.ref.child("locales").get() or {}
        deudas = {}
        for local_id, local_data in todos_locales.items():
            clientes = local_data.get("clientes", {})
            if cliente_id in clientes:
                deuda_total = clientes[cliente_id].get("deuda", 0)
                deudas[local_id] = {
                    "nombre_local": local_data.get("nombre"),
                    "deuda_total": deuda_total
                }
        return deudas
