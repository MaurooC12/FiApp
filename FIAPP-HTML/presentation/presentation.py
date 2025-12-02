from ViewModel.use_cases import UseCases
from ViewModel.user_manager import Administrador
from database.db_service import DBService


class ViewModel:
    def __init__(self, auth_service):
        self.auth_service = auth_service
        self.use_cases = UseCases()
        self.user_manager = Administrador()
        self.current_user = None
        self.db = DBService()

    # --- Sesión ---
    def login(self, uid):
        rol = self.auth_service.get_user_role(uid)
        if not rol:
            return {"error": "UID no encontrado"}
        self.current_user = {"uid": uid, "rol": rol}
        return {"success": True, "uid": uid, "rol": rol}

    # --- Gestión de usuarios ---
    def crear_usuario(self, email, password, user_id):
        """Crea usuario sin tipo (se asigna después)."""
        return self.user_manager.crear_usuario(email, password, user_id)

    def asignar_tipo_usuario(self, email, tipo_usuario):
        """Asigna tipo de usuario después del registro."""
        return self.user_manager.asignar_tipo_usuario(email, tipo_usuario)

    def listar_usuarios(self):
        return self.user_manager.listar_usuarios()

    def eliminar_usuario(self, uid):
        return self.user_manager.eliminar_usuario(uid)

    # --- Tendero ---
    # --Productos ---
    def crear_producto(self, local_id, nombre, precio, stock, producto_id):
        return self.use_cases.crear_producto(local_id, nombre, precio, stock, producto_id)

    def listar_productos(self, local_id):
        return self.use_cases.listar_productos(local_id)

    def actualizar_producto(self, local_id, producto_id, nombre=None, precio=None, stock=None):
        return self.use_cases.actualizar_producto(local_id, producto_id, nombre, precio, stock)

    def eliminar_producto(self, local_id, producto_id):
        return self.use_cases.eliminar_producto(local_id, producto_id)

    def registrar_cliente(self, local_id, cliente_id, cliente_data):
        return self.use_cases.registrar_cliente(local_id, cliente_id, cliente_data)

    def listar_clientes(self, local_id):
        return self.use_cases.listar_clientes(local_id)

    def registrar_deuda(self, local_id, cliente_id, monto, plazo_dias=None):
        return self.use_cases.registrar_deuda(local_id, cliente_id, monto, plazo_dias)

    # --- Locales ---
    def crear_local(self, nombre, propietario_id, local_id):
        return self.use_cases.crear_local(nombre, propietario_id, local_id)

    def obtener_local(self, local_id):
        return self.use_cases.obtener_local(local_id)

    def actualizar_local(self, local_id, data):
        return self.use_cases.actualizar_local(local_id, data)

    def eliminar_local(self, local_id):
        return self.use_cases.eliminar_local(local_id)

    def _listar_locales(self):
        return self.use_cases._listar_locales()

    def listar_locales_por_propietario(self, propietario_id):
        """Tendero: lista sus locales."""
        return self.use_cases.listar_locales_por_propietario(propietario_id)
    
    def get_deudas_cliente(self, cliente_id):
        """Cliente: obtiene sus deudas en todos los locales."""
        return self.use_cases.get_deudas_cliente(cliente_id)

    # --- Usuario: historial de deudas ---
    def obtener_historial_deudas(self, local_id, cliente_id):
        """Retorna el historial de deudas (diccionario) para un cliente en un local.

        Devuelve {} si no hay registros.
        """
        return self.use_cases.obtener_historial_deudas(local_id, cliente_id)
        
