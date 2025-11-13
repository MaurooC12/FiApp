from domain.producto import Producto
from database.db_service import DBService
from domain.local import Local
from datetime import datetime, timedelta
import time


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
            return {}
        for pid, p in productos.items():
            print(f"[{pid}] {p['nombre']} - ${p['precio']} (Stock: {p['stock']})")
        return productos

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

    def cliente_existe(self, local_id, cliente_id):
        """Verifica si un cliente existe en una local específica"""
        cliente = self.db.get_cliente(local_id, cliente_id)
        return cliente is not None
    
    def usuario_existe_globalmente(self, user_id):
        """Verifica si un usuario existe en la base de datos global de usuarios"""
        return self.db.usuario_existe(user_id)

    def listar_clientes(self, local_id):
        clientes = self.db.get_clientes(local_id)
        if not clientes:
            print("No hay clientes en este local.")
            return {}
        for cid, c in clientes.items():
            print(f"[{cid}] - {c['nombre']} ({c['email']}) | Deuda: ${c.get('deuda', 0)}")
        return clientes

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

    def obtener_deuda_total_por_cliente(self, cliente_id):
        """Agrega la deuda numérica (`deuda`) del cliente across todos los locales.

        Retorna un float con la suma total. Si no hay registros, devuelve 0.0
        """
        total = 0.0
        locales = self.db.ref.child("locales").get() or {}
        for lid, datos_local in locales.items():
            clientes = datos_local.get("clientes") or {}
            cliente = clientes.get(cliente_id)
            if cliente:
                try:
                    deuda_val = float(cliente.get("deuda", 0) or 0)
                except Exception:
                    deuda_val = 0.0
                total += deuda_val
        return total

    def obtener_detalles_deudas_por_local(self, cliente_id):
        """Devuelve un dict { local_id: deuda_total } para todos los locales donde exista el cliente."""
        resultados = {}
        locales = self.db.ref.child("locales").get() or {}
        for lid, datos_local in locales.items():
            clientes = datos_local.get("clientes") or {}
            cliente = clientes.get(cliente_id)
            if cliente:
                try:
                    deuda_val = float(cliente.get("deuda", 0) or 0)
                except Exception:
                    deuda_val = 0.0
                resultados[lid] = deuda_val
        return resultados

    def obtener_transacciones_cliente(self, cliente_id):
        """Recolecta todas las entradas de `deudas` para el cliente en todos los locales.

        Retorna una lista de diccionarios: [{"local_id": lid, "timestamp": int, "monto": float, "plazo_dias": int?}, ...]
        """
        transacciones = []
        locales = self.db.ref.child("locales").get() or {}
        for lid, datos_local in locales.items():
            clientes = datos_local.get("clientes") or {}
            cliente = clientes.get(cliente_id)
            if not cliente:
                continue
            deudas = cliente.get("deudas") or {}
            for ts_key, detalle in (deudas.items() if isinstance(deudas, dict) else []):
                try:
                    monto = float(detalle.get("monto", 0))
                except Exception:
                    monto = 0.0
                try:
                    timestamp = int(detalle.get("timestamp", ts_key))
                except Exception:
                    try:
                        timestamp = int(ts_key)
                    except Exception:
                        timestamp = None
                trans = {"local_id": lid, "timestamp": timestamp, "monto": monto}
                if "plazo_dias" in detalle:
                    try:
                        trans["plazo_dias"] = int(detalle.get("plazo_dias"))
                    except Exception:
                        trans["plazo_dias"] = detalle.get("plazo_dias")
                transacciones.append(trans)
        # ordenar por timestamp descendente (más reciente primero)
        transacciones.sort(key=lambda x: x.get("timestamp") or 0, reverse=True)
        return transacciones
  
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
    
    def obtener_deudas_vigentes_cliente(self, cliente_id):
        """
        Retorna todas las deudas vigentes del cliente con estado y color.
        
        Estructura: [
            {
                "local_id": str,
                "timestamp": int,
                "monto": float,
                "plazo_dias": int,
                "fecha_creacion": datetime,
                "fecha_vencimiento": datetime,
                "dias_restantes": int,
                "estado": "vigente" | "por_vencer" | "vencido",
                "color": "verde" | "amarillo" | "naranja" | "rojo",
                "texto_estado": str (ej: "Vence en 15 días" o "Vencido hace 5 días")
            },
            ...
        ]
        """
        deudas = []
        locales = self.db.ref.child("locales").get() or {}
        ahora = datetime.now()
        
        for lid, datos_local in locales.items():
            clientes = datos_local.get("clientes") or {}
            cliente = clientes.get(cliente_id)
            if not cliente:
                continue
            
            deudas_dict = cliente.get("deudas") or {}
            for ts_key, detalle in (deudas_dict.items() if isinstance(deudas_dict, dict) else []):
                try:
                    monto = float(detalle.get("monto", 0))
                except Exception:
                    monto = 0.0
                
                try:
                    timestamp = int(detalle.get("timestamp", ts_key))
                except Exception:
                    try:
                        timestamp = int(ts_key)
                    except Exception:
                        continue
                
                plazo_dias = None
                if "plazo_dias" in detalle:
                    try:
                        plazo_dias = int(detalle.get("plazo_dias"))
                    except Exception:
                        pass
                
                # Si no tiene plazo_dias, saltarlo (no se puede calcular estado)
                if plazo_dias is None:
                    continue
                
                # Calcular fechas
                fecha_creacion = datetime.fromtimestamp(timestamp)
                fecha_vencimiento = fecha_creacion + timedelta(days=plazo_dias)
                dias_restantes = (fecha_vencimiento - ahora).days
                
                # Calcular color según proporción de tiempo restante
                proporcion = dias_restantes / plazo_dias if plazo_dias > 0 else 0
                
                if dias_restantes < 0:
                    # Vencido
                    color = "rojo"
                    estado = "vencido"
                    texto_estado = f"Vencido hace {abs(dias_restantes)} días"
                elif proporcion >= 0.75:
                    # Verde: ≥ 3/4 del plazo
                    color = "verde"
                    estado = "vigente"
                    texto_estado = f"Vence en {dias_restantes} días"
                elif proporcion >= 0.5:
                    # Amarillo: entre 3/4 y 1/2
                    color = "amarillo"
                    estado = "vigente"
                    texto_estado = f"Vence en {dias_restantes} días"
                elif proporcion >= 0.125:
                    # Naranja: entre 1/2 y 1/8
                    color = "naranja"
                    estado = "por_vencer"
                    texto_estado = f"Vence en {dias_restantes} días"
                else:
                    # Rojo: < 1/8 del plazo
                    color = "rojo"
                    estado = "por_vencer"
                    texto_estado = f"Vence en {dias_restantes} días"
                
                deuda_info = {
                    "local_id": lid,
                    "timestamp": timestamp,
                    "monto": monto,
                    "plazo_dias": plazo_dias,
                    "fecha_creacion": fecha_creacion,
                    "fecha_vencimiento": fecha_vencimiento,
                    "dias_restantes": dias_restantes,
                    "estado": estado,
                    "color": color,
                    "texto_estado": texto_estado
                }
                deudas.append(deuda_info)
        
        # Ordenar por fecha de vencimiento (más próximos primero)
        deudas.sort(key=lambda x: x["fecha_vencimiento"])
        return deudas
