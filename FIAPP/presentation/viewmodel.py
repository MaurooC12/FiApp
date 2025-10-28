from domain.use_cases import UseCases
from domain.user_manager import UserManager


class ViewModel:
    def __init__(self, auth_service):
        self.auth_service = auth_service
        self.use_cases = UseCases()
        self.user_manager = UserManager()
        self.current_user = None

    # --- Sesión ---
    def login(self, uid):
        rol = self.auth_service.get_user_role(uid)
        if not rol:
            print("❌ UID no encontrado en la base de datos.")
            return
        self.current_user = {"uid": uid, "rol": rol}
        print(f"Sesión iniciada como {rol} ({uid})")

    # --- Admin ---
    def admin_crear_usuario(self, email, password, rol):
        if self.current_user["rol"] != "admin":
            print("❌ Solo los administradores pueden crear usuarios.")
            return
        self.user_manager.crear_usuario(email, password, rol)

    def admin_listar_usuarios(self):
        if self.current_user["rol"] != "admin":
            print("❌ Solo los administradores pueden listar usuarios.")
            return
        self.user_manager.listar_usuarios()

    def admin_eliminar_usuario(self, uid):
        if self.current_user["rol"] != "admin":
            print("❌ Solo los administradores pueden eliminar usuarios.")
            return
        self.user_manager.eliminar_usuario(uid)

    # --- Tendero ---
    def crear_producto(self, local_id, nombre, precio, stock):
        self.use_cases.crear_producto(local_id, nombre, precio, stock)

    def listar_productos(self, local_id):
        self.use_cases.listar_productos(local_id)

    def actualizar_producto(self, local_id, producto_id, nombre=None, precio=None, stock=None):
        self.use_cases.actualizar_producto(local_id, producto_id, nombre, precio, stock)

    def eliminar_producto(self, local_id, producto_id):
        self.use_cases.eliminar_producto(local_id, producto_id)

    def registrar_cliente(self, local_id, cliente_id, cliente_data):
        self.use_cases.registrar_cliente(local_id, cliente_id, cliente_data)

    def listar_clientes(self, local_id):
        self.use_cases.listar_clientes(local_id)

    def registrar_deuda(self, local_id, cliente_id, monto):
        self.use_cases.registrar_deuda(local_id, cliente_id, monto)
