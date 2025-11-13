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
            print("❌ UID no encontrado en la base de datos.")
            return
        self.current_user = {"uid": uid, "rol": rol}
        print(f"Sesión iniciada como {rol} ({uid})")

    # --- Admin ---
    def admin_crear_usuario(self, email, password, rol,user_id):
        while self.current_user["rol"] != "admin":
            print("❌ Solo los administradores pueden crear usuarios.")
            chage_user = input("Ingrese su UID de administrador: ")
            self.login(chage_user)
        self.user_manager.crear_usuario(email, password, rol,user_id)

    def admin_listar_usuarios(self):
        while self.current_user["rol"] != "admin":
            print("❌ Solo los administradores pueden crear usuarios.")
            chage_user = input("Ingrese su UID de administrador: ")
            self.login(chage_user)
        users = self.user_manager.listar_usuarios()
        #print("DEBUG: users =", users, type(users))
        # Asegurar que siempre devolvemos un iterable (lista) al llamador.
        if users is None:
            return []

        # Si la función de bajo nivel devuelve un diccionario {uid: data},
        # convertimos a una lista de dicts con keys: user_id, email, rol.
        if isinstance(users, dict):
            result = []
            for uid, data in users.items():
                result.append({
                    "user_id": uid,
                    "email": data.get("email"),
                    "rol": data.get("rol"),
                })
            return result

        # Si ya es una lista/iterable de usuarios, devolver como lista.
        try:
            return list(users)
        except Exception:
            return []

    def admin_eliminar_usuario(self, uid):
        while self.current_user["rol"] != "admin":
            print("❌ Solo los administradores pueden crear usuarios.")
            chage_user = input("Ingrese su UID de administrador: ")
            self.login(chage_user)
        proof = self.user_manager.eliminar_usuario(uid)
        return proof

    # --- Tendero ---
   #--Productos ---
    def crear_producto(self, local_id, nombre, precio, stock,producto_id):
        self.use_cases.crear_producto(local_id, nombre, precio, stock,producto_id)

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

    def registrar_deuda(self, local_id, cliente_id, monto, plazo_dias=None):
        self.use_cases.registrar_deuda(local_id, cliente_id, monto, plazo_dias)
    #---Locales ---
    def crear_local(self, nombre, propietario_id, local_id):
        self.use_cases.crear_local(nombre, propietario_id, local_id)

    def obtener_local(self, local_id):
        return self.use_cases.obtener_local(local_id)
    
    def actualizar_local(self, local_id, data):
        self.use_cases.actualizar_local(local_id, data)

    def eliminar_local(self, local_id):
        self.use_cases.eliminar_local(local_id)
    
    def _listar_locales(self):
        return self.use_cases._listar_locales()

    # --- Usuario: historial de deudas ---
    def obtener_historial_deudas(self, local_id, cliente_id):
        """Retorna el historial de deudas (diccionario) para un cliente en un local.

        Devuelve {} si no hay registros.
        """
        return self.use_cases.obtener_historial_deudas(local_id, cliente_id)
        
