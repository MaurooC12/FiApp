from database.auth_service import AuthService
from database.local_service import LocalService

def main():
    auth = AuthService()
    local = LocalService()

    # Crear usuarios
    auth.crear_usuario("uid_admin_1", "Admin", "admin@fiapp.com", "admin")
    auth.crear_usuario("uid_tendero_1", "Juan", "juan@fiapp.com", "tendero")
    auth.crear_usuario("uid_cliente_1", "Pedro", "pedro@fiapp.com", "cliente")

    # Crear un local
    local.crear_local("local_1", "uid_tendero_1", "Tienda La Esquina")

    # CRUD de productos
    local.agregar_producto("local_1", "prod_1", "Arroz", 3000, 20)
    local.agregar_producto("local_1", "prod_2", "Aceite", 5000, 10)
    local.actualizar_producto("local_1", "prod_1", precio=3200)

    # Manejo de clientes y deudas
    local.agregar_cliente("local_1", "uid_cliente_1")
    local.actualizar_deuda("local_1", "uid_cliente_1", 25000)
    local.registrar_pago("local_1", "uid_cliente_1", "pago_1", 10000, "2025-10-28")

if __name__ == "__main__":
    main()
