from firebase_admin import db


class DBService:
    """
    CRUD general para locales, productos, clientes y deudas.
    """

    def __init__(self):
        self.ref = db.reference("/")
    @property
    def key(self):
        return self.ref.key
    @key.setter
    def key(self, value):
        self.ref.key = value
    # --- Productos ---
    def add_producto(self, local_id, producto_data, producto_id):
        # Crear referencia directamente con el ID proporcionado
        new_ref = self.ref.child(f"locales/{local_id}/productos/{producto_id}")
        new_ref.set(producto_data)
        return producto_id

    def get_productos(self, local_id):
        return self.ref.child(f"locales/{local_id}/productos").get() or {}

    def update_producto(self, local_id, producto_id, data):
        self.ref.child(f"locales/{local_id}/productos/{producto_id}").update(data)

    def delete_producto(self, local_id, producto_id):
        self.ref.child(f"locales/{local_id}/productos/{producto_id}").delete()

    # --- Clientes ---
    def add_cliente_a_local(self, local_id, cliente_id, cliente_data):
        self.ref.child(f"locales/{local_id}/clientes/{cliente_id}").set(cliente_data)

    def get_clientes(self, local_id):
        return self.ref.child(f"locales/{local_id}/clientes").get() or {}

    def get_cliente(self, local_id, cliente_id):
        return self.ref.child(f"locales/{local_id}/clientes/{cliente_id}").get()

    # --- Deudas ---
    def registrar_deuda(self, local_id, cliente_id, monto, plazo_dias=None):
        """Registra una deuda para un cliente.

        - Actualiza el acumulado numérico en 'deuda'.
        - Añade un registro individual bajo 'deudas/<timestamp>' con monto y plazo (si se proporciona).
        """
        # Actualizar suma total de deuda
        deuda_ref = self.ref.child(f"locales/{local_id}/clientes/{cliente_id}/deuda")
        deuda_actual = deuda_ref.get() or 0
        try:
            nueva_total = float(deuda_actual) + float(monto)
        except Exception:
            # Fallback si hay datos corruptos
            nueva_total = float(monto)
        deuda_ref.set(nueva_total)

        # Agregar registro detallado de la deuda
        import time
        timestamp = str(int(time.time()))
        detalle = {"monto": float(monto), "timestamp": int(timestamp)}
        if plazo_dias is not None:
            try:
                detalle["plazo_dias"] = int(plazo_dias)
            except Exception:
                detalle["plazo_dias"] = plazo_dias

        detalles_ref = self.ref.child(f"locales/{local_id}/clientes/{cliente_id}/deudas")
        detalles_ref.child(timestamp).set(detalle)
   
    # --- Locales ---
    def add_local(self, local_id, local_data):
        self.ref.child(f"locales/{local_id}").set(local_data)
    
    def get_local(self, local_id):
        return self.ref.child(f"locales/{local_id}").get()
    
    def update_local(self, local_id, data):
        self.ref.child(f"locales/{local_id}").update(data)

    def delete_local(self, local_id):
        self.ref.child(f"locales/{local_id}").delete()