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
            print("4. Cambiar de usuario")
            print("0. Salir")

            op = input("> ")

            if op == "1":
                email = input("Email: ")
                password = input("Contraseña: ")
                rol = input("Rol (admin/tendero/cliente): ")
                user_uid = input("UID del usuario: ")
                self.vm.admin_crear_usuario(email, password, rol, user_uid)
            elif op == "2":
                self.vm.admin_listar_usuarios()
            elif op == "3":
                uid = input("UID del usuario a eliminar: ")
                self.vm.admin_eliminar_usuario(uid)
            elif op == "4":
                print("Cambiando de usuario...\n\n")
                self.run()
                break
            elif op == "0":
                print("Saliendo...")
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
            print("8. Cambiar de usuario")
            print("9. Locales")
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
                producto_id = input("ID del producto: ")
                self.vm.crear_producto(local, nombre, precio, stock, producto_id)

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
                print("Saliendo...")
                self.vm.current_user = None
                break
            elif op == "8":
                print("Cambiando de usuario...")
                break
                self.run()
            elif op == "9":
                self.menu_locales()
            else:
                print("Opción inválida.")

    
    def menu_locales(self):
        while True:
            print("\n=== Gestión de Locales ===")
            print("1. Crear local")
            print("2. Obtener local")
            print("3. Actualizar local")
            print("4. Eliminar local")
            print("5. Mis locales")
            print("0. Volver al menú anterior")
            op = input("> ")

            if op == "1":
                nombre = input("Nombre del local: ")
                propietario_id = input("UID del propietario: ")
                local_id = input("ID del local: ")
                self.vm.crear_local(nombre, propietario_id, local_id)
            
            elif op == "2":
                local_id = input("ID del local: ")
                self.vm.obtener_local(local_id)
            
            elif op == "3":
                local_id = input("ID del local: ")
                data = {}
                nombre = input("Nuevo nombre (Enter para omitir): ")
                if nombre:
                    data["nombre"] = nombre
                propietario_id = input("Nuevo UID del propietario (Enter para omitir): ")
                if propietario_id:
                    data["propietario_id"] = propietario_id
                self.vm.actualizar_local(local_id, data)

            elif op == "4":
                local_id = input("ID del local: ")
                self.vm.eliminar_local(local_id)
            
            elif op =="5":
                propietario_id = self.vm.current_user["uid"]
                print(f"Locales del propietario {propietario_id}:")
                locales = self.vm._listar_locales()
                encontrados = False
                for lid, ldata in locales.items():
                    if ldata.get("propietario_id") == propietario_id:
                        print(f"- ID: {lid}, Nombre: {ldata.get('nombre')}")
                        encontrados = True
                if not encontrados:
                    print("No tienes locales registrados.")
                
            elif op == "0":
                break
                self.run()
            else:
                print("Opción inválida.")
        
            


