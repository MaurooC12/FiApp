class ConsoleUI:
    def __init__(self, view_model):
        self.vm = view_model

    def run(self):
        print("Bienvenido a FIAPP Console\n")

        uid = input("Ingrese su UID de Firebase: ")
        self.vm.login(uid)

        if not self.vm.current_user:
            return

        rol = self.vm.current_user["rol"]
        if rol == "admin":
            self.menu_admin()
        elif rol == "tendero":
            self.menu_tendero()
        else:
            print("Interfaz cliente (consulta de deuda) aún no implementada.")

    # --- Menú de Admin ---
    def menu_admin(self):
        while True:
            print("\n=== Panel de Administrador ===")
            print("1. Crear usuario")
            print("2. Listar usuarios")
            print("3. Eliminar usuario")
            print("0. Salir")

            op = input("> ")

            if op == "1":
                email = input("Email: ")
                password = input("Contraseña: ")
                rol = input("Rol (admin/tendero/cliente): ")
                self.vm.admin_crear_usuario(email, password, rol)
            elif op == "2":
                self.vm.admin_listar_usuarios()
            elif op == "3":
                uid = input("UID del usuario a eliminar: ")
                self.vm.admin_eliminar_usuario(uid)
            elif op == "0":
                break
            else:
                print("Opción inválida.")

    # --- Menú de Tendero ---
    def menu_tendero(self):
        while True:
            print("\n=== Panel del Tendero ===")
            print("1. Listar productos")
            print("2. Crear producto")
            print("3. Actualizar producto")
            print("4. Eliminar producto")
            print("5. Listar clientes")
            print("6. Añadir cliente")
            print("7. Registrar deuda")
            print("0. Salir")

            op = input("> ")

            if op == "1":
                local = input("ID del local: ")
                self.vm.listar_productos(local)

            elif op == "2":
                local = input("ID del local: ")
                nombre = input("Nombre del producto: ")
                precio = float(input("Precio: "))
                stock = int(input("Stock: "))
                self.vm.crear_producto(local, nombre, precio, stock)

            elif op == "3":
                local = input("ID del local: ")
                producto_id = input("ID del producto: ")
                nombre = input("Nuevo nombre (Enter para omitir): ") or None
                precio = input("Nuevo precio (Enter para omitir): ")
                precio = float(precio) if precio else None
                stock = input("Nuevo stock (Enter para omitir): ")
                stock = int(stock) if stock else None
                self.vm.actualizar_producto(local, producto_id, nombre, precio, stock)

            elif op == "4":
                local = input("ID del local: ")
                producto_id = input("ID del producto: ")
                self.vm.eliminar_producto(local, producto_id)

            elif op == "5":
                local = input("ID del local: ")
                self.vm.listar_clientes(local)

            elif op == "6":
                local = input("ID del local: ")
                cliente_id = input("ID del cliente: ")
                nombre = input("Nombre del cliente: ")
                email = input("Email del cliente: ")
                self.vm.registrar_cliente(local, cliente_id, {"nombre": nombre, "email": email, "deuda": 0})

            elif op == "7":
                local = input("ID del local: ")
                cliente = input("ID del cliente: ")
                monto = float(input("Monto de deuda: "))
                self.vm.registrar_deuda(local, cliente, monto)

            elif op == "0":
                break
            else:
                print("Opción inválida.")
