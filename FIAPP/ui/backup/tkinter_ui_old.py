import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext


class TkinterUI(tk.Tk):
    """Aplicación principal con patrón de stacked frames"""
    
    def __init__(self, view_model):
        super().__init__()
        self.vm = view_model
        
        self.title("FiApp - Sistema de Administración para Tenderos")
        self.geometry("900x650+350+50")
        self.iconbitmap("LogoFiApp.ico")
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Contenedor principal
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Diccionario de vistas
        self.frames = {}
        
        # Lista de vistas a crear
        for ViewClass in (LoginView, AdminMenuView, TenderoMenuView, 
                         CrearUsuarioView, ListarUsuariosView, EliminarUsuarioView,
                         ProductosMenuView, ListarProductosView, CrearProductoView,
                         ActualizarProductoView, EliminarProductoView,
                         ClientesMenuView, ListarClientesView, RegistrarClienteView,
                         RegistrarDeudaView,
                         LocalesMenuView, CrearLocalView, ObtenerLocalView,
                         ActualizarLocalView, EliminarLocalView, MisLocalesView):
            view = ViewClass(container, self, view_model)
            self.frames[ViewClass.__name__] = view
            view.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("LoginView")
    
    def show_frame(self, name: str):
        """Muestra una vista específica"""
        frame = self.frames[name]
        frame.tkraise()
    
    def run(self):
        """Inicia la aplicación"""
        self.mainloop()


class BaseView(ttk.Frame):
    """Clase base para todas las vistas"""
    
    def __init__(self, parent, controller, view_model):
        super().__init__(parent)
        self.controller = controller
        self.vm = view_model

    # ========== PANTALLA DE LOGIN ==========
    def show_login_screen(self):
        """Pantalla de login"""
        self.clear_frame()
        
        title = ttk.Label(self.current_frame, text="FIAPP - Login", font=("Arial", 20, "bold"))
        title.pack(pady=20)
        
        # Frame de entrada
        entry_frame = ttk.Frame(self.current_frame)
        entry_frame.pack(pady=20)
        
        ttk.Label(entry_frame, text="UID de Firebase:", font=("Arial", 12)).pack(anchor="w", pady=5)
        uid_entry = ttk.Entry(entry_frame, width=40, font=("Arial", 11))
        uid_entry.pack(pady=5)
        uid_entry.focus()
        
        def login_click():
            uid = uid_entry.get().strip()
            if not uid:
                messagebox.showerror("Error", "Por favor ingrese un UID")
                return
            
            self.vm.login(uid)
            if not self.vm.current_user:
                messagebox.showerror("Error", "UID no válido")
                uid_entry.delete(0, tk.END)
                return
            
            rol = self.vm.current_user.get("rol")
            if rol == "admin":
                self.show_admin_menu()
            elif rol == "tendero":
                self.show_tendero_menu()
            else:
                messagebox.showinfo("Info", "Interfaz cliente (consulta de deuda) aún no implementada.")
        
        ttk.Button(entry_frame, text="Iniciar Sesión", command=login_click).pack(pady=10)
        
        # Permitir Enter para login
        uid_entry.bind("<Return>", lambda e: login_click())

    # ========== MENÚ DE ADMIN ==========
    def show_admin_menu(self):
        """Menú principal del administrador"""
        self.clear_frame()
        
        title = ttk.Label(self.current_frame, text="Panel de Administrador", font=("Arial", 18, "bold"))
        title.pack(pady=20)
        
        # Botones principales
        button_frame = ttk.Frame(self.current_frame)
        button_frame.pack(pady=20)
        
        buttons = [
            ("Crear Usuario", self.show_crear_usuario),
            ("Listar Usuarios", self.show_listar_usuarios),
            ("Eliminar Usuario", self.show_eliminar_usuario),
            ("Cambiar de Usuario", self.show_login_screen),
            ("Salir", self.root.quit),
        ]
        
        for text, command in buttons:
            ttk.Button(button_frame, text=text, command=command, width=25).pack(pady=5)

    def show_crear_usuario(self):
        """Diálogo para crear usuario"""
        self.clear_frame()
        
        title = ttk.Label(self.current_frame, text="Crear Usuario", font=("Arial", 16, "bold"))
        title.pack(pady=15)
        
        form_frame = ttk.Frame(self.current_frame)
        form_frame.pack(pady=15)
        
        # Email
        ttk.Label(form_frame, text="Email:", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=5, padx=5)
        email_entry = ttk.Entry(form_frame, width=30)
        email_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Contraseña
        ttk.Label(form_frame, text="Contraseña:", font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=5, padx=5)
        password_entry = ttk.Entry(form_frame, width=30, show="*")
        password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Rol
        ttk.Label(form_frame, text="Rol:", font=("Arial", 11)).grid(row=2, column=0, sticky="w", pady=5, padx=5)
        rol_var = tk.StringVar(value="tendero")
        rol_combo = ttk.Combobox(form_frame, textvariable=rol_var, values=["admin", "tendero", "cliente"], state="readonly", width=27)
        rol_combo.grid(row=2, column=1, padx=5, pady=5)
        
        def crear():
            email = email_entry.get().strip()
            password = password_entry.get()
            rol = rol_var.get()
            
            if not all([email, password, rol]):
                messagebox.showerror("Error", "Complete todos los campos")
                return
            
            self.vm.admin_crear_usuario(email, password, rol)
            messagebox.showinfo("Éxito", "Usuario creado exitosamente")
            self.show_admin_menu()
        
        button_frame = ttk.Frame(self.current_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Crear", command=crear).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Volver", command=self.show_admin_menu).pack(side=tk.LEFT, padx=5)

    def show_listar_usuarios(self):
        """Muestra la lista de usuarios"""
        self.clear_frame()
        
        title = ttk.Label(self.current_frame, text="Listar Usuarios", font=("Arial", 16, "bold"))
        title.pack(pady=15)
        
        # Mostrar usuarios
        usuarios_text = scrolledtext.ScrolledText(self.current_frame, height=15, width=70, font=("Arial", 10))
        usuarios_text.pack(pady=10, padx=10)
        usuarios_text.config(state=tk.DISABLED)
        
        # Capturar output
        import io
        import sys
        
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        
        self.vm.admin_listar_usuarios()
        
        output = buffer.getvalue()
        sys.stdout = old_stdout
        
        usuarios_text.config(state=tk.NORMAL)
        usuarios_text.insert(tk.END, output if output else "No hay usuarios")
        usuarios_text.config(state=tk.DISABLED)
        
        button_frame = ttk.Frame(self.current_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Volver", command=self.show_admin_menu).pack()

    def show_eliminar_usuario(self):
        """Diálogo para eliminar usuario"""
        self.clear_frame()
        
        title = ttk.Label(self.current_frame, text="Eliminar Usuario", font=("Arial", 16, "bold"))
        title.pack(pady=15)
        
        form_frame = ttk.Frame(self.current_frame)
        form_frame.pack(pady=15)
        
        ttk.Label(form_frame, text="UID del usuario:", font=("Arial", 11)).pack(pady=5)
        uid_entry = ttk.Entry(form_frame, width=40)
        uid_entry.pack(pady=5)
        
        def eliminar():
            uid = uid_entry.get().strip()
            if not uid:
                messagebox.showerror("Error", "Ingrese un UID")
                return
            
            if messagebox.askyesno("Confirmar", f"¿Eliminar usuario {uid}?"):
                self.vm.admin_eliminar_usuario(uid)
                messagebox.showinfo("Éxito", "Usuario eliminado")
                self.show_admin_menu()
        
        button_frame = ttk.Frame(self.current_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Eliminar", command=eliminar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Volver", command=self.show_admin_menu).pack(side=tk.LEFT, padx=5)

    # ========== MENÚ DE TENDERO ==========
    def show_tendero_menu(self):
        """Menú principal del tendero"""
        self.clear_frame()
        
        user_name = self.vm.current_user.get("uid", "Usuario")
        title = ttk.Label(self.current_frame, text=f"Panel del Tendero - {user_name}", font=("Arial", 16, "bold"))
        title.pack(pady=15)
        
        button_frame = ttk.Frame(self.current_frame)
        button_frame.pack(pady=15)
        
        buttons = [
            ("Gestionar Productos", self.show_productos_menu),
            ("Gestionar Clientes", self.show_clientes_menu),
            ("Registrar Deuda", self.show_registrar_deuda),
            ("Gestionar Locales", self.show_locales_menu),
            ("Cambiar de Usuario", self.show_login_screen),
            ("Salir", self.root.quit),
        ]
        
        for text, command in buttons:
            ttk.Button(button_frame, text=text, command=command, width=25).pack(pady=5)

    def show_productos_menu(self):
        """Menú de gestión de productos"""
        self.clear_frame()
        
        title = ttk.Label(self.current_frame, text="Gestionar Productos", font=("Arial", 16, "bold"))
        title.pack(pady=15)
        
        button_frame = ttk.Frame(self.current_frame)
        button_frame.pack(pady=15)
        
        buttons = [
            ("Listar Productos", self.show_listar_productos),
            ("Crear Producto", self.show_crear_producto),
            ("Actualizar Producto", self.show_actualizar_producto),
            ("Eliminar Producto", self.show_eliminar_producto),
            ("Volver", self.show_tendero_menu),
        ]
        
        for text, command in buttons:
            ttk.Button(button_frame, text=text, command=command, width=25).pack(pady=5)

    def show_listar_productos(self):
        """Muestra lista de productos"""
        self.clear_frame()
        
        title = ttk.Label(self.current_frame, text="Listar Productos", font=("Arial", 16, "bold"))
        title.pack(pady=15)
        
        input_frame = ttk.Frame(self.current_frame)
        input_frame.pack(pady=10)
        
        ttk.Label(input_frame, text="ID del Local:", font=("Arial", 11)).pack(anchor="w", pady=5)
        local_entry = ttk.Entry(input_frame, width=30)
        local_entry.pack(pady=5)
        
        def listar():
            local = local_entry.get().strip()
            if not local:
                messagebox.showerror("Error", "Ingrese un ID de local")
                return
            
            import io
            import sys
            
            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()
            
            self.vm.listar_productos(local)
            
            output = buffer.getvalue()
            sys.stdout = old_stdout
            
            # Mostrar resultado
            result_window = tk.Toplevel(self.root)
            result_window.title("Productos")
            result_window.geometry("600x400")
            
            text_widget = scrolledtext.ScrolledText(result_window, font=("Arial", 10))
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert(tk.END, output if output else "No hay productos")
            text_widget.config(state=tk.DISABLED)
        
        button_frame = ttk.Frame(self.current_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Listar", command=listar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Volver", command=self.show_productos_menu).pack(side=tk.LEFT, padx=5)

    def show_crear_producto(self):
        """Diálogo para crear producto"""
        self.clear_frame()
        
        title = ttk.Label(self.current_frame, text="Crear Producto", font=("Arial", 16, "bold"))
        title.pack(pady=15)
        
        form_frame = ttk.Frame(self.current_frame)
        form_frame.pack(pady=15)
        
        fields = [
            ("ID del Local:", "local"),
            ("ID del Producto:", "producto_id"),
            ("Nombre:", "nombre"),
            ("Precio:", "precio"),
            ("Stock:", "stock"),
        ]
        
        entries = {}
        for label, key in fields:
            ttk.Label(form_frame, text=label, font=("Arial", 11)).pack(anchor="w", pady=3, padx=5)
            entry = ttk.Entry(form_frame, width=30)
            entry.pack(pady=3, padx=5)
            entries[key] = entry
        
        def crear():
            try:
                local = entries["local"].get().strip()
                producto_id = entries["producto_id"].get().strip()
                nombre = entries["nombre"].get().strip()
                precio = float(entries["precio"].get().strip())
                stock = int(entries["stock"].get().strip())
                
                if not all([local, producto_id, nombre]):
                    raise ValueError("Complete todos los campos")
                
                self.vm.crear_producto(local, nombre, precio, stock, producto_id)
                messagebox.showinfo("Éxito", "Producto creado exitosamente")
                self.show_productos_menu()
            except ValueError as e:
                messagebox.showerror("Error", f"Entrada inválida: {e}")
        
        button_frame = ttk.Frame(self.current_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Crear", command=crear).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Volver", command=self.show_productos_menu).pack(side=tk.LEFT, padx=5)

    def show_actualizar_producto(self):
        """Diálogo para actualizar producto"""
        self.clear_frame()
        
        title = ttk.Label(self.current_frame, text="Actualizar Producto", font=("Arial", 16, "bold"))
        title.pack(pady=15)
        
        form_frame = ttk.Frame(self.current_frame)
        form_frame.pack(pady=15)
        
        ttk.Label(form_frame, text="ID del Local:", font=("Arial", 11)).pack(anchor="w", pady=3, padx=5)
        local_entry = ttk.Entry(form_frame, width=30)
        local_entry.pack(pady=3, padx=5)
        
        ttk.Label(form_frame, text="ID del Producto:", font=("Arial", 11)).pack(anchor="w", pady=3, padx=5)
        producto_entry = ttk.Entry(form_frame, width=30)
        producto_entry.pack(pady=3, padx=5)
        
        ttk.Label(form_frame, text="Nuevo Nombre (opcional):", font=("Arial", 11)).pack(anchor="w", pady=3, padx=5)
        nombre_entry = ttk.Entry(form_frame, width=30)
        nombre_entry.pack(pady=3, padx=5)
        
        ttk.Label(form_frame, text="Nuevo Precio (opcional):", font=("Arial", 11)).pack(anchor="w", pady=3, padx=5)
        precio_entry = ttk.Entry(form_frame, width=30)
        precio_entry.pack(pady=3, padx=5)
        
        ttk.Label(form_frame, text="Nuevo Stock (opcional):", font=("Arial", 11)).pack(anchor="w", pady=3, padx=5)
        stock_entry = ttk.Entry(form_frame, width=30)
        stock_entry.pack(pady=3, padx=5)
        
        def actualizar():
            try:
                local = local_entry.get().strip()
                producto_id = producto_entry.get().strip()
                nombre = nombre_entry.get().strip() or None
                precio = precio_entry.get().strip()
                precio = float(precio) if precio else None
                stock = stock_entry.get().strip()
                stock = int(stock) if stock else None
                
                if not all([local, producto_id]):
                    raise ValueError("Ingrese local e ID de producto")
                
                self.vm.actualizar_producto(local, producto_id, nombre, precio, stock)
                messagebox.showinfo("Éxito", "Producto actualizado")
                self.show_productos_menu()
            except ValueError as e:
                messagebox.showerror("Error", f"Entrada inválida: {e}")
        
        button_frame = ttk.Frame(self.current_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Actualizar", command=actualizar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Volver", command=self.show_productos_menu).pack(side=tk.LEFT, padx=5)

    def show_eliminar_producto(self):
        """Diálogo para eliminar producto"""
        self.clear_frame()
        
        title = ttk.Label(self.current_frame, text="Eliminar Producto", font=("Arial", 16, "bold"))
        title.pack(pady=15)
        
        form_frame = ttk.Frame(self.current_frame)
        form_frame.pack(pady=15)
        
        ttk.Label(form_frame, text="ID del Local:", font=("Arial", 11)).pack(anchor="w", pady=5, padx=5)
        local_entry = ttk.Entry(form_frame, width=30)
        local_entry.pack(pady=5, padx=5)
        
        ttk.Label(form_frame, text="ID del Producto:", font=("Arial", 11)).pack(anchor="w", pady=5, padx=5)
        producto_entry = ttk.Entry(form_frame, width=30)
        producto_entry.pack(pady=5, padx=5)
        
        def eliminar():
            local = local_entry.get().strip()
            producto_id = producto_entry.get().strip()
            
            if not all([local, producto_id]):
                messagebox.showerror("Error", "Complete todos los campos")
                return
            
            if messagebox.askyesno("Confirmar", f"¿Eliminar producto {producto_id}?"):
                self.vm.eliminar_producto(local, producto_id)
                messagebox.showinfo("Éxito", "Producto eliminado")
                self.show_productos_menu()
        
        button_frame = ttk.Frame(self.current_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Eliminar", command=eliminar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Volver", command=self.show_productos_menu).pack(side=tk.LEFT, padx=5)

    # ========== MENÚ DE CLIENTES ==========
    def show_clientes_menu(self):
        """Menú de gestión de clientes"""
        self.clear_frame()
        
        title = ttk.Label(self.current_frame, text="Gestionar Clientes", font=("Arial", 16, "bold"))
        title.pack(pady=15)
        
        button_frame = ttk.Frame(self.current_frame)
        button_frame.pack(pady=15)
        
        buttons = [
            ("Listar Clientes", self.show_listar_clientes),
            ("Añadir Cliente", self.show_registrar_cliente),
            ("Volver", self.show_tendero_menu),
        ]
        
        for text, command in buttons:
            ttk.Button(button_frame, text=text, command=command, width=25).pack(pady=5)

    def show_listar_clientes(self):
        """Muestra lista de clientes"""
        self.clear_frame()
        
        title = ttk.Label(self.current_frame, text="Listar Clientes", font=("Arial", 16, "bold"))
        title.pack(pady=15)
        
        input_frame = ttk.Frame(self.current_frame)
        input_frame.pack(pady=10)
        
        ttk.Label(input_frame, text="ID del Local:", font=("Arial", 11)).pack(anchor="w", pady=5)
        local_entry = ttk.Entry(input_frame, width=30)
        local_entry.pack(pady=5)
        
        def listar():
            local = local_entry.get().strip()
            if not local:
                messagebox.showerror("Error", "Ingrese un ID de local")
                return
            
            import io
            import sys
            
            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()
            
            self.vm.listar_clientes(local)
            
            output = buffer.getvalue()
            sys.stdout = old_stdout
            
            result_window = tk.Toplevel(self.root)
            result_window.title("Clientes")
            result_window.geometry("600x400")
            
            text_widget = scrolledtext.ScrolledText(result_window, font=("Arial", 10))
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert(tk.END, output if output else "No hay clientes")
            text_widget.config(state=tk.DISABLED)
        
        button_frame = ttk.Frame(self.current_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Listar", command=listar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Volver", command=self.show_clientes_menu).pack(side=tk.LEFT, padx=5)

    def show_registrar_cliente(self):
        """Diálogo para registrar cliente"""
        self.clear_frame()
        
        title = ttk.Label(self.current_frame, text="Añadir Cliente", font=("Arial", 16, "bold"))
        title.pack(pady=15)
        
        form_frame = ttk.Frame(self.current_frame)
        form_frame.pack(pady=15)
        
        fields = [
            ("ID del Local:", "local"),
            ("ID del Cliente:", "cliente_id"),
            ("Nombre:", "nombre"),
            ("Email:", "email"),
        ]
        
        entries = {}
        for label, key in fields:
            ttk.Label(form_frame, text=label, font=("Arial", 11)).pack(anchor="w", pady=3, padx=5)
            entry = ttk.Entry(form_frame, width=30)
            entry.pack(pady=3, padx=5)
            entries[key] = entry
        
        def registrar():
            try:
                local = entries["local"].get().strip()
                cliente_id = entries["cliente_id"].get().strip()
                nombre = entries["nombre"].get().strip()
                email = entries["email"].get().strip()
                
                if not all([local, cliente_id, nombre, email]):
                    raise ValueError("Complete todos los campos")
                
                self.vm.registrar_cliente(local, cliente_id, {
                    "nombre": nombre,
                    "email": email,
                    "deuda": 0
                })
                messagebox.showinfo("Éxito", "Cliente registrado exitosamente")
                self.show_clientes_menu()
            except ValueError as e:
                messagebox.showerror("Error", f"Entrada inválida: {e}")
        
        button_frame = ttk.Frame(self.current_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Registrar", command=registrar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Volver", command=self.show_clientes_menu).pack(side=tk.LEFT, padx=5)

    def show_registrar_deuda(self):
        """Diálogo para registrar deuda"""
        self.clear_frame()
        
        title = ttk.Label(self.current_frame, text="Registrar Deuda", font=("Arial", 16, "bold"))
        title.pack(pady=15)
        
        form_frame = ttk.Frame(self.current_frame)
        form_frame.pack(pady=15)
        
        ttk.Label(form_frame, text="ID del Local:", font=("Arial", 11)).pack(anchor="w", pady=5, padx=5)
        local_entry = ttk.Entry(form_frame, width=30)
        local_entry.pack(pady=5, padx=5)
        
        ttk.Label(form_frame, text="ID del Cliente:", font=("Arial", 11)).pack(anchor="w", pady=5, padx=5)
        cliente_entry = ttk.Entry(form_frame, width=30)
        cliente_entry.pack(pady=5, padx=5)
        
        ttk.Label(form_frame, text="Monto de Deuda:", font=("Arial", 11)).pack(anchor="w", pady=5, padx=5)
        monto_entry = ttk.Entry(form_frame, width=30)
        monto_entry.pack(pady=5, padx=5)
        
        def registrar():
            try:
                local = local_entry.get().strip()
                cliente = cliente_entry.get().strip()
                monto = float(monto_entry.get().strip())
                
                if not all([local, cliente]):
                    raise ValueError("Complete todos los campos")
                
                self.vm.registrar_deuda(local, cliente, monto)
                messagebox.showinfo("Éxito", "Deuda registrada exitosamente")
                self.show_tendero_menu()
            except ValueError as e:
                messagebox.showerror("Error", f"Entrada inválida: {e}")
        
        button_frame = ttk.Frame(self.current_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Registrar", command=registrar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Volver", command=self.show_tendero_menu).pack(side=tk.LEFT, padx=5)

    # ========== MENÚ DE LOCALES ==========
    def show_locales_menu(self):
        """Menú de gestión de locales"""
        self.clear_frame()
        
        title = ttk.Label(self.current_frame, text="Gestión de Locales", font=("Arial", 16, "bold"))
        title.pack(pady=15)
        
        button_frame = ttk.Frame(self.current_frame)
        button_frame.pack(pady=15)
        
        buttons = [
            ("Crear Local", self.show_crear_local),
            ("Obtener Local", self.show_obtener_local),
            ("Actualizar Local", self.show_actualizar_local),
            ("Eliminar Local", self.show_eliminar_local),
            ("Mis Locales", self.show_mis_locales),
            ("Volver", self.show_tendero_menu),
        ]
        
        for text, command in buttons:
            ttk.Button(button_frame, text=text, command=command, width=25).pack(pady=5)

    def show_crear_local(self):
        """Diálogo para crear local"""
        self.clear_frame()
        
        title = ttk.Label(self.current_frame, text="Crear Local", font=("Arial", 16, "bold"))
        title.pack(pady=15)
        
        form_frame = ttk.Frame(self.current_frame)
        form_frame.pack(pady=15)
        
        ttk.Label(form_frame, text="Nombre del Local:", font=("Arial", 11)).pack(anchor="w", pady=5, padx=5)
        nombre_entry = ttk.Entry(form_frame, width=30)
        nombre_entry.pack(pady=5, padx=5)
        
        ttk.Label(form_frame, text="UID del Propietario:", font=("Arial", 11)).pack(anchor="w", pady=5, padx=5)
        propietario_entry = ttk.Entry(form_frame, width=30)
        propietario_entry.pack(pady=5, padx=5)
        propietario_entry.insert(0, self.vm.current_user.get("uid", ""))
        
        ttk.Label(form_frame, text="ID del Local:", font=("Arial", 11)).pack(anchor="w", pady=5, padx=5)
        local_id_entry = ttk.Entry(form_frame, width=30)
        local_id_entry.pack(pady=5, padx=5)
        
        def crear():
            nombre = nombre_entry.get().strip()
            propietario = propietario_entry.get().strip()
            local_id = local_id_entry.get().strip()
            
            if not all([nombre, propietario, local_id]):
                messagebox.showerror("Error", "Complete todos los campos")
                return
            
            self.vm.crear_local(nombre, propietario, local_id)
            messagebox.showinfo("Éxito", "Local creado exitosamente")
            self.show_locales_menu()
        
        button_frame = ttk.Frame(self.current_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Crear", command=crear).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Volver", command=self.show_locales_menu).pack(side=tk.LEFT, padx=5)

    def show_obtener_local(self):
        """Diálogo para obtener local"""
        self.clear_frame()
        
        title = ttk.Label(self.current_frame, text="Obtener Local", font=("Arial", 16, "bold"))
        title.pack(pady=15)
        
        input_frame = ttk.Frame(self.current_frame)
        input_frame.pack(pady=10)
        
        ttk.Label(input_frame, text="ID del Local:", font=("Arial", 11)).pack(anchor="w", pady=5)
        local_entry = ttk.Entry(input_frame, width=30)
        local_entry.pack(pady=5)
        
        def obtener():
            local_id = local_entry.get().strip()
            if not local_id:
                messagebox.showerror("Error", "Ingrese un ID de local")
                return
            
            import io
            import sys
            
            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()
            
            self.vm.obtener_local(local_id)
            
            output = buffer.getvalue()
            sys.stdout = old_stdout
            
            result_window = tk.Toplevel(self.root)
            result_window.title("Local")
            result_window.geometry("600x300")
            
            text_widget = scrolledtext.ScrolledText(result_window, font=("Arial", 10))
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert(tk.END, output if output else "Local no encontrado")
            text_widget.config(state=tk.DISABLED)
        
        button_frame = ttk.Frame(self.current_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Obtener", command=obtener).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Volver", command=self.show_locales_menu).pack(side=tk.LEFT, padx=5)

    def show_actualizar_local(self):
        """Diálogo para actualizar local"""
        self.clear_frame()
        
        title = ttk.Label(self.current_frame, text="Actualizar Local", font=("Arial", 16, "bold"))
        title.pack(pady=15)
        
        form_frame = ttk.Frame(self.current_frame)
        form_frame.pack(pady=15)
        
        ttk.Label(form_frame, text="ID del Local:", font=("Arial", 11)).pack(anchor="w", pady=5, padx=5)
        local_id_entry = ttk.Entry(form_frame, width=30)
        local_id_entry.pack(pady=5, padx=5)
        
        ttk.Label(form_frame, text="Nuevo Nombre (opcional):", font=("Arial", 11)).pack(anchor="w", pady=5, padx=5)
        nombre_entry = ttk.Entry(form_frame, width=30)
        nombre_entry.pack(pady=5, padx=5)
        
        ttk.Label(form_frame, text="Nuevo UID del Propietario (opcional):", font=("Arial", 11)).pack(anchor="w", pady=5, padx=5)
        propietario_entry = ttk.Entry(form_frame, width=30)
        propietario_entry.pack(pady=5, padx=5)
        
        def actualizar():
            local_id = local_id_entry.get().strip()
            if not local_id:
                messagebox.showerror("Error", "Ingrese un ID de local")
                return
            
            data = {}
            nombre = nombre_entry.get().strip()
            if nombre:
                data["nombre"] = nombre
            propietario = propietario_entry.get().strip()
            if propietario:
                data["propietario_id"] = propietario
            
            if not data:
                messagebox.showwarning("Aviso", "No hay datos para actualizar")
                return
            
            self.vm.actualizar_local(local_id, data)
            messagebox.showinfo("Éxito", "Local actualizado")
            self.show_locales_menu()
        
        button_frame = ttk.Frame(self.current_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Actualizar", command=actualizar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Volver", command=self.show_locales_menu).pack(side=tk.LEFT, padx=5)

    def show_eliminar_local(self):
        """Diálogo para eliminar local"""
        self.clear_frame()
        
        title = ttk.Label(self.current_frame, text="Eliminar Local", font=("Arial", 16, "bold"))
        title.pack(pady=15)
        
        input_frame = ttk.Frame(self.current_frame)
        input_frame.pack(pady=10)
        
        ttk.Label(input_frame, text="ID del Local:", font=("Arial", 11)).pack(anchor="w", pady=5)
        local_entry = ttk.Entry(input_frame, width=30)
        local_entry.pack(pady=5)
        
        def eliminar():
            local_id = local_entry.get().strip()
            if not local_id:
                messagebox.showerror("Error", "Ingrese un ID de local")
                return
            
            if messagebox.askyesno("Confirmar", f"¿Eliminar local {local_id}?"):
                self.vm.eliminar_local(local_id)
                messagebox.showinfo("Éxito", "Local eliminado")
                self.show_locales_menu()
        
        button_frame = ttk.Frame(self.current_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Eliminar", command=eliminar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Volver", command=self.show_locales_menu).pack(side=tk.LEFT, padx=5)

    def show_mis_locales(self):
        """Muestra los locales del propietario actual"""
        self.clear_frame()
        
        title = ttk.Label(self.current_frame, text="Mis Locales", font=("Arial", 16, "bold"))
        title.pack(pady=15)
        
        propietario_id = self.vm.current_user.get("uid")
        
        info_frame = ttk.Frame(self.current_frame)
        info_frame.pack(pady=10)
        
        ttk.Label(info_frame, text=f"Locales del propietario: {propietario_id}", font=("Arial", 12)).pack()
        
        result_text = scrolledtext.ScrolledText(self.current_frame, height=12, width=70, font=("Arial", 10))
        result_text.pack(pady=10, padx=10)
        result_text.config(state=tk.DISABLED)
        
        import io
        import sys
        
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        
        locales = self.vm._listar_locales()
        encontrados = False
        output = ""
        for lid, ldata in locales.items():
            if ldata.get("propietario_id") == propietario_id:
                output += f"- ID: {lid}, Nombre: {ldata.get('nombre')}\n"
                encontrados = True
        
        if not encontrados:
            output = "No tienes locales registrados."
        
        sys.stdout = old_stdout
        
        result_text.config(state=tk.NORMAL)
        result_text.insert(tk.END, output)
        result_text.config(state=tk.DISABLED)
        
        button_frame = ttk.Frame(self.current_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Volver", command=self.show_locales_menu).pack()
