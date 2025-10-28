from database.firebase_config import db

class LocalService:
    def __init__(self):
        self.ref_locales = db.reference("locales")

    def crear_local(self, local_id, tendero_id, nombre_local):
        """Crea un nuevo local asociado a un tendero."""
        self.ref_locales.child(local_id).set({
            "nombre": nombre_local,
            "tendero_id": tendero_id,
            "productos": {},
            "clientes": {}
        })
        print(f"🏪 Local '{nombre_local}' creado por tendero {tendero_id}")

    # === CRUD de productos ===
    def agregar_producto(self, local_id, prod_id, nombre, precio, stock):
        self.ref_locales.child(local_id).child("productos").child(prod_id).set({
            "nombre": nombre,
            "precio": precio,
            "stock": stock
        })
        print(f"🛒 Producto '{nombre}' agregado al local {local_id}")

    def actualizar_producto(self, local_id, prod_id, **kwargs):
        self.ref_locales.child(local_id).child("productos").child(prod_id).update(kwargs)
        print(f"✏️ Producto {prod_id} actualizado")

    def eliminar_producto(self, local_id, prod_id):
        self.ref_locales.child(local_id).child("productos").child(prod_id).delete()
        print(f"🗑️ Producto {prod_id} eliminado del local {local_id}")

    # === Manejo de clientes y deudas ===
    def agregar_cliente(self, local_id, cliente_uid):
        self.ref_locales.child(local_id).child("clientes").child(cliente_uid).set({
            "deuda": 0,
            "historialPagos": {}
        })
        print(f"👥 Cliente {cliente_uid} agregado al local {local_id}")

    def actualizar_deuda(self, local_id, cliente_uid, nueva_deuda):
        self.ref_locales.child(local_id).child("clientes").child(cliente_uid).update({
            "deuda": nueva_deuda
        })
        print(f"💰 Deuda actualizada para cliente {cliente_uid}: {nueva_deuda}")

    def registrar_pago(self, local_id, cliente_uid, pago_id, monto, fecha):
        pago_ref = self.ref_locales.child(local_id).child("clientes").child(cliente_uid).child("historialPagos")
        pago_ref.child(pago_id).set({
            "monto": monto,
            "fecha": fecha
        })
        print(f"💵 Pago registrado: {monto} el {fecha}")
