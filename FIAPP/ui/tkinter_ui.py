import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os


class App(tk.Tk): # Aplicación principal basado en stacked
    
    def __init__(self, view_model):
        super().__init__()
        self.vm = view_model
        
        
        self.title("FiApp")
        self.geometry("900x650+350+50")
        self.iconbitmap("LogoFiApp.ico")
        self.resizable(False, False)
        self.configure(bg="#b8d0cc", bd=5)
        self.attributes("-alpha",0.95)
        
        # Configurar estilo
        style = ttk.Style()
        style.theme_use("clam")
        
        # Contenedor principal que guardará las vistas apiladas
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Diccionario para almacenar las vistas por nombre
        self.frames = {}
        
        # Stack de navegación para rastrear qué frame fue anterior (para botón "Atrás")
        self.navigation_stack = []
        
        # Lista de clases de vistas principales
        main_views = (LoginView, AdminView, TenderoView, UsuarioView)
        # Lista de clases de vistas de diálogos
        dialog_views = (
            TenderoRegistrarDeudaView,
            TenderoListarProductosView,
            TenderoCrearProductoView,
            TenderoActualizarProductoView,
            TenderoEliminarProductoView,
            TenderoListarClientesView,
            TenderoAñadirClienteView,
            UsuarioConsultarDeudasView,
            UsuarioDetallesDeudasView,
            UsuarioVerTransaccionesView,
            UsuarioHistorialDeudasView
        )
        
        # Crear y apilar todas las vistas
        for ViewClass in main_views + dialog_views:
            view_instance = ViewClass(container, self, view_model)
            name = ViewClass.__name__
            self.frames[name] = view_instance
            # Coloca cada vista en la misma celda (0,0) para poder alternarlas con tkraise()
            view_instance.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("LoginView")
    
    def show_frame(self, name: str, add_to_stack=True):
        """Cambia de vista según su nombre"""
        # Guardar el frame anterior en el stack si es necesario
        if add_to_stack:
            # Siempre agregar el frame actual (incluso si es repetido)
            # Esto asegura que go_back() siempre tenga un elemento anterior
            self.navigation_stack.append(name)
            print(f"[NAV] Stack tras agregar {name}: {self.navigation_stack}")
        
        frame = self.frames[name]
        frame.tkraise()  # Eleva esa vista al frente (la hace visible sobre las demás)
        # Llamar hook cuando la vista se muestra (útil para refrescar datos)
        try:
            if hasattr(frame, "on_show") and callable(frame.on_show):
                frame.on_show()
        except Exception:
            pass
    
    def go_back(self):
        """Retrocede al frame anterior del stack de navegación."""
        print(f"[NAV] go_back() - Stack actual: {self.navigation_stack}, tamaño: {len(self.navigation_stack)}")
        if len(self.navigation_stack) > 1:
            self.navigation_stack.pop()  # Remover el actual
            prev_frame = self.navigation_stack[-1]
            print(f"[NAV] Volviendo a: {prev_frame}")
            self.show_frame(prev_frame, add_to_stack=False)
        else:
            print(f"[NAV] Stack insuficiente para go_back()")


class BaseView(ttk.Frame):
    """Clase base para todas las vistas"""
    
    def __init__(self, parent, controller, view_model):
        super().__init__(parent)
        self.controller = controller
        self.vm = view_model
        
        # Configurar grid para que se expanda
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def on_show(self):
        """Hook llamado cuando la vista es mostrada. Override en vistas que necesiten refrescar datos."""
        return


# ========== VISTA DE LOGIN ==========

class LoginView(BaseView):
    """Vista para ingresar ID del usuario"""
    
    def __init__(self, parent, controller, view_model):
        super().__init__(parent, controller, view_model)
        
        # Frame principal centrado
        main_frame = ttk.Frame(self)
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Título
        title = ttk.Label(main_frame, text="FiApp", font=("Montserrat", 60, "bold"), foreground="#082341")
        title.pack()
        subtitle = ttk.Label(main_frame, text="De la libreta al clic: tus finanzas en la palma de tu mano", font=("Montserrat", 10, "italic"), foreground="#344460")
        subtitle.pack()
        # Label y Entry para el UID
        ttk.Label(main_frame, text="Ingrese su UID de Firebase:", font=("Montserrat", 11)).pack(pady=(50,5))
        self.uid_entry = ttk.Entry(main_frame, width=30, font=("Montserrat", 15), foreground="#344460")
        self.uid_entry.pack(pady=5)
        self.uid_entry.focus()
        
        # Botón para iniciar sesión
        ttk.Button(main_frame, text="Iniciar Sesión", command=self._login).pack(pady=15)
        
        # Permitir presionar Enter para login
        self.uid_entry.bind("<Return>", lambda e: self._login())
    
    def _login(self):
        """Procesa el login del usuario"""
        uid = self.uid_entry.get().strip()
        
        if not uid:
            messagebox.showerror("Error", "Por favor ingrese un UID")
            return
        
        # Llamar al ViewModel para autenticar (capturar errores de red/servicio)
        try:
            self.vm.login(uid)
        except Exception as e:
            # Mensaje amigable para errores de red / DNS / autenticación remota
            message = (
                "Error al conectar con Firebase:\n"
                f"{e}\n\n"
                "Compruebe su conexión a Internet, proxy/VPN, o la configuración DNS."
            )
            messagebox.showerror("Error de conexión", message)
            return

        if not self.vm.current_user:
            messagebox.showerror("Error", "UID no válido")
            self.uid_entry.delete(0, tk.END)
            return
        
        # Redirigir según el rol
        rol = self.vm.current_user.get("rol")
        if rol == "admin":
            self.controller.show_frame("AdminView")
        elif rol == "tendero":
            self.controller.show_frame("TenderoView")
        elif rol == "usuario" or rol == "cliente":
            self.controller.show_frame("UsuarioView")
        else:
            messagebox.showwarning("Aviso", "Rol no reconocido")


# ========== VISTA DE ADMIN ==========

class AdminView(BaseView):
    """Vista del Administrador"""
    
    def __init__(self, parent, controller, view_model):
        super().__init__(parent, controller, view_model)
        
        # Frame principal
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Título con nombre del usuario
        user_name = view_model.current_user.get("uid", "Admin") if view_model.current_user else "Admin"
        title = ttk.Label(main_frame, text=f"Panel de Administrador - {user_name}", font=("Segoe UI", 16, "bold"))
        title.pack(pady=20)
        
        # Contenedor de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        # Botones del menú
        ttk.Button(button_frame, text="Crear Usuario", command=lambda:self.create_user(), width=30).pack(pady=8)
        ttk.Button(button_frame, text="Listar Usuarios", command=lambda: self.list_user(), width=30).pack(pady=8)
        ttk.Button(button_frame, text="Eliminar Usuario", command=lambda: self.eliminar_user(), width=30).pack(pady=8)
        ttk.Button(button_frame, text="Cambiar de Usuario", command=lambda: controller.show_frame("LoginView"), width=30).pack(pady=8)
        ttk.Button(button_frame, text="Salir", command=controller.quit, width=30).pack(pady=8)

    def create_user(self):
        """Abrir diálogo para crear un nuevo usuario"""
        dialog = tk.Toplevel(self)
        dialog.title("Crear Usuario")
        dialog.geometry("400x350")
       
        dialog.transient(self)
        dialog.grab_set()

        frm = ttk.Frame(dialog, padding=12)
        frm.pack(fill="both", expand=True)

        #--Entrada Email--#

        ttk.Label(frm, text="Email:").grid(row=0, column=0, sticky="w", pady=6)
        entrada_email = ttk.Entry(frm, width=30)
        entrada_email.grid(row=0, column=1, pady=6)

        #--Entrada Password--#

        ttk.Label(frm, text="Contraseña:").grid(row=1, column=0, sticky="w", pady=6)
        entrada_password = ttk.Entry(frm, width=30, show="*")
        entrada_password.grid(row=1, column=1, pady=6)
        
        #--Entrada Rol--#
        ttk.Label(frm, text="Rol (admin/tendero/usuario):").grid(row=2, column=0, sticky="w", pady=6)
        roles = ["admin", "tendero", "usuario"]
        
        entry_rol = ttk.Combobox(frm, values=roles, state="readonly", width=28)
        entry_rol.grid(row=2, column=1, pady=6)
        entry_rol.set("usuario")
    
        #--Entrada User ID--#
        ttk.Label(frm, text="User ID:").grid(row=3, column=0, sticky="w", pady=6)
        entrada_user_id = ttk.Entry(frm, width=30)
        entrada_user_id.grid(row=3, column=1, pady=6)

        # Botones
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=12)
        
        def _submit():
            email = entrada_email.get().strip()
            password = entrada_password.get().strip()
            rol = entry_rol.get().strip()
            user_id = entrada_user_id.get().strip()

            if not email or not password or not rol or not user_id:
                messagebox.showerror("Error", "Por favor complete todos los campos")
                return
            if not rol in roles:
                messagebox.showerror("Error", "Rol inválido. Use admin, tendero o usuario.")
                return
            
            #--llamada al viewmodel--#

            try:
                self.vm.admin_crear_usuario(email, password, rol, user_id)
                messagebox.showinfo("Éxito", "Usuario creado correctamente")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo crear el usuario:\n{e}")

            #--botones--#
        ttk.Button(btn_frame, text="Crear", command=_submit).pack(side="left",padx=8)
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side="left", padx=8)

        entrada_email.focus()

    def  list_user(self):
        """Abrir diálogo para listar usuarios"""
        dialog = tk.Toplevel(self)
        dialog.title("Listar Usuarios")
        dialog.geometry("600x400")
        
        dialog.transient(self)
        dialog.grab_set()

        frm = ttk.Frame(dialog, padding=12)
        frm.pack(fill="both", expand=True)

        # Treeview para mostrar usuarios
        columns = ("user_id", "email", "rol")
        tree = ttk.Treeview(frm, columns=columns, show="headings", height=15)
        tree.heading("user_id", text="User ID")
        tree.heading("email", text="Email")
        tree.heading("rol", text="Rol")
        tree.pack(fill="both", expand=True)
        # Scrollbars
        vsb = ttk.Scrollbar(frm, orient="vertical", command=tree.yview)
        vsb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=vsb.set)
        
        
        #--llamada al viewmodel--#
        view_model = self.vm
        try:
            usuarios = view_model.admin_listar_usuarios()
            for usuario in usuarios:
                tree.insert("", "end", values=(usuario["user_id"], usuario["email"], usuario["rol"]))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo listar los usuarios:\n{e}")
            #--botones--#
        ttk.Button(frm, text="Cerrar", command=dialog.destroy).pack(pady=8)

    def eliminar_user(self):
        """Abrir diálogo para eliminar un usuario"""
        dialog = tk.Toplevel(self)
        dialog.title("Eliminar Usuario")
        dialog.geometry("400x200")
        
        dialog.transient(self)
        dialog.grab_set()

        frm = ttk.Frame(dialog, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Ingrese el User ID del usuario a eliminar:").pack(pady=6)
        entrada_user_id = ttk.Entry(frm, width=30)
        entrada_user_id.pack(pady=6)
        entrada_user_id.focus()

        def _submit():
            user_id = entrada_user_id.get().strip()

            if not user_id:
                messagebox.showerror("Error", "Por favor ingrese un User ID")
                return
            
            #--llamada al viewmodel--#
            try:
                elim = self.vm.admin_eliminar_usuario(user_id)
                if elim == True:
                    messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
                else:
                    messagebox.showwarning("Aviso", "No se pudo eliminar el usuario")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el usuario:\n{e}")

        #--botones--#
        btn_frame = ttk.Frame(frm,)
        btn_frame.pack(pady=8)

        ttk.Button(btn_frame, text="Eliminar", command=_submit).pack(side="left", padx=8)
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side="left", padx=8)




# ========== VISTA DE TENDERO ==========

class TenderoView(BaseView):
    """Vista del Tendero"""
    
    def __init__(self, parent, controller, view_model):
        super().__init__(parent, controller, view_model)
        
        # Frame principal
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Título con nombre del usuario
        user_name = view_model.current_user.get("uid", "Tendero") if view_model.current_user else "Tendero"
        title = ttk.Label(main_frame, text=f"Panel del Tendero - {user_name}", font=("Segoe UI", 16, "bold"))
        title.pack(pady=20)
        
        # Contenedor de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        # Botones del menú (exactamente como en consola)
        ttk.Button(button_frame, text="Listar productos", width=40, command=lambda: self.controller.show_frame("TenderoListarProductosView")).pack(pady=5, fill="x")
        ttk.Button(button_frame, text="Crear producto", width=40, command=lambda: self.controller.show_frame("TenderoCrearProductoView")).pack(pady=5, fill="x")
        ttk.Button(button_frame, text="Actualizar producto", width=40, command=lambda: self.controller.show_frame("TenderoActualizarProductoView")).pack(pady=5, fill="x")
        ttk.Button(button_frame, text="Eliminar producto", width=40, command=lambda: self.controller.show_frame("TenderoEliminarProductoView")).pack(pady=5, fill="x")
        ttk.Button(button_frame, text="Listar clientes", width=40, command=lambda: self.controller.show_frame("TenderoListarClientesView")).pack(pady=5, fill="x")
        ttk.Button(button_frame, text="Añadir cliente", width=40, command=lambda: self.controller.show_frame("TenderoAñadirClienteView")).pack(pady=5, fill="x")
        ttk.Button(button_frame, text="Registrar deuda", width=40, command=lambda: self.controller.show_frame("TenderoRegistrarDeudaView")).pack(pady=5, fill="x")
        ttk.Button(button_frame, text="Cambiar de usuario", command=lambda: self.controller.show_frame("LoginView"), width=40).pack(pady=5, fill="x")
        ttk.Button(button_frame, text="Locales", width=40).pack(pady=5, fill="x")
        ttk.Button(button_frame, text="Salir", command=self.controller.quit, width=40).pack(pady=5, fill="x")


# ========== VISTA DE USUARIO ==========

class UsuarioView(BaseView):
    """Vista del Usuario (Cliente)"""
    
    def __init__(self, parent, controller, view_model):
        super().__init__(parent, controller, view_model)
        
        # Frame principal
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Título con nombre del usuario
        user_name = view_model.current_user.get("uid", "Usuario") if view_model.current_user else "Usuario"
        title = ttk.Label(main_frame, text=f"Panel de Usuario - {user_name}", font=("Segoe UI", 16, "bold"))
        title.pack(pady=20)
        
        # Deuda total (agregada de todas las tiendas)
        debt_frame = ttk.Frame(main_frame)
        debt_frame.pack(pady=(0,12))
        ttk.Label(debt_frame, text="Deuda total:", font=("Segoe UI", 12, "bold")).pack(side="left")
        self.debt_label = ttk.Label(debt_frame, text="$0.00", font=("Segoe UI", 12))
        self.debt_label.pack(side="left", padx=(8,12))
        ttk.Button(debt_frame, text="Detalles", command=lambda: controller.show_frame("UsuarioDetallesDeudasView")).pack(side="left")

        # Contenedor de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)

        # Botones del menú
        ttk.Button(button_frame, text="Consultar Deuda", width=30, command=lambda: controller.show_frame("UsuarioConsultarDeudasView")).pack(pady=8)
        ttk.Button(button_frame, text="Refrescar", width=30, command=self._refresh_deuda_total).pack(pady=8)
        ttk.Button(button_frame, text="Ver Transacciones", width=30, command=lambda: controller.show_frame("UsuarioVerTransaccionesView")).pack(pady=8)
        ttk.Button(button_frame, text="Historial de Deudas", width=30, command=lambda: controller.show_frame("UsuarioHistorialDeudasView")).pack(pady=8)
        ttk.Button(button_frame, text="Cambiar de Usuario", command=lambda: controller.show_frame("LoginView"), width=30).pack(pady=8)
        ttk.Button(button_frame, text="Salir", command=controller.quit, width=30).pack(pady=8)

        # Cargar deuda total al abrir la vista
        self.after(200, self._refresh_deuda_total)

    def _refresh_deuda_total(self):
        """Consulta al ViewModel la deuda total del cliente y actualiza la etiqueta con verificación defensiva."""
        cliente_id = self.vm.current_user.get("uid") if self.vm.current_user else None
        if not cliente_id:
            self.debt_label.config(text="$0.00")
            print("[DEBUG] No hay cliente_id. current_user:", self.vm.current_user)
            return
        try:
            total = self.vm.obtener_deuda_total_por_cliente(cliente_id)
            # Conversión defensiva a float
            if total is None:
                total = 0.0
            else:
                total = float(total)
            self.debt_label.config(text=f"${total:.2f}")
            print(f"[DEBUG] Deuda total para {cliente_id}: ${total:.2f}")
        except Exception as e:
            # Mostrar 0 y no bloquear la UI
            self.debt_label.config(text="$0.00")
            print(f"[ERROR] No se pudo obtener deuda total: {e}")

    def on_show(self):
        """Cuando la vista se muestra, refresca la deuda total."""
        self._refresh_deuda_total()


# ========== VISTA DE DIÁLOGOS - TENDERO ==========

class TenderoRegistrarDeudaView(BaseView):
    """Frame para registrar deuda (reemplaza tk.Toplevel)"""
    
    def __init__(self, parent, controller, view_model):
        super().__init__(parent, controller, view_model)
        
        # Frame principal
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Título
        title = ttk.Label(main_frame, text="Registrar Deuda", font=("Segoe UI", 16, "bold"))
        title.pack(pady=20)
        
        # Frame de formulario
        frm = ttk.Frame(main_frame)
        frm.pack(fill="both", expand=True, padx=20, pady=20)
        
        ttk.Label(frm, text="ID del local:").grid(row=0, column=0, sticky="w", pady=12)
        self.entry_local = ttk.Entry(frm, width=40)
        self.entry_local.grid(row=0, column=1, pady=12)
        
        ttk.Label(frm, text="ID del cliente:").grid(row=1, column=0, sticky="w", pady=12)
        self.entry_cliente = ttk.Entry(frm, width=40)
        self.entry_cliente.grid(row=1, column=1, pady=12)
        
        ttk.Label(frm, text="Monto:").grid(row=2, column=0, sticky="w", pady=12)
        self.entry_monto = ttk.Entry(frm, width=40)
        self.entry_monto.grid(row=2, column=1, pady=12)
        
        ttk.Label(frm, text="Plazo (días) - opcional:").grid(row=3, column=0, sticky="w", pady=12)
        self.entry_plazo = ttk.Entry(frm, width=40)
        self.entry_plazo.grid(row=3, column=1, pady=12)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Registrar", command=self._submit).pack(side="left", padx=8)
        ttk.Button(btn_frame, text="Atrás", command=lambda: self.controller.go_back()).pack(side="left", padx=8)
        
        self.entry_local.focus()
    
    def _submit(self):
        """Registra la deuda y regresa a la vista anterior"""
        local = self.entry_local.get().strip()
        cliente = self.entry_cliente.get().strip()
        monto_s = self.entry_monto.get().strip()
        plazo_s = self.entry_plazo.get().strip()
        
        if not local or not cliente or not monto_s:
            messagebox.showerror("Error", "Por favor complete local, cliente y monto")
            return
        
        try:
            monto = float(monto_s)
        except ValueError:
            messagebox.showerror("Error", "Monto inválido. Ingrese un número.")
            return
        
        plazo = None
        if plazo_s:
            try:
                plazo = int(plazo_s)
            except ValueError:
                messagebox.showerror("Error", "Plazo inválido. Ingrese un número entero de días.")
                return
        
        try:
            self.vm.registrar_deuda(local, cliente, monto, plazo)
            messagebox.showinfo("Éxito", "Deuda registrada correctamente")
            # Limpiar campos
            self.entry_local.delete(0, tk.END)
            self.entry_cliente.delete(0, tk.END)
            self.entry_monto.delete(0, tk.END)
            self.entry_plazo.delete(0, tk.END)
            # Regresar
            self.controller.go_back()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar la deuda:\n{e}")


# ========== VISTA DE DIÁLOGOS - USUARIO ==========

class UsuarioConsultarDeudasView(BaseView):
    """Frame para consultar deudas vigentes (reemplaza tk.Toplevel)"""
    
    def __init__(self, parent, controller, view_model):
        super().__init__(parent, controller, view_model)
        
        # Frame principal
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Título
        title = ttk.Label(main_frame, text="Consultar Deudas Vigentes", font=("Segoe UI", 16, "bold"))
        title.pack(pady=20)
        
        # Frame del tree
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Treeview
        columns = ("local", "monto", "plazo", "vencimiento", "estado")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        self.tree.heading("local", text="Tienda")
        self.tree.heading("monto", text="Monto")
        self.tree.heading("plazo", text="Plazo")
        self.tree.heading("vencimiento", text="Vencimiento")
        self.tree.heading("estado", text="Detalles")
        self.tree.column("local", width=120)
        self.tree.column("monto", width=100, anchor="e")
        self.tree.column("plazo", width=80, anchor="center")
        self.tree.column("vencimiento", width=120, anchor="center")
        self.tree.column("estado", width=200, anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)
        
        # Botón Atrás
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Atrás", command=lambda: self.controller.go_back()).pack()
    
    def on_show(self):
        """Refrescar datos cuando se muestra la vista"""
        self._cargar_deudas()
    
    def _cargar_deudas(self):
        """Carga las deudas vigentes en el treeview"""
        # Limpiar tree anterior
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        cliente_id = self.vm.current_user.get("uid") if self.vm.current_user else None
        if not cliente_id:
            messagebox.showerror("Error", "Usuario no autenticado")
            return
        
        try:
            deudas = self.vm.obtener_deudas_vigentes_cliente(cliente_id)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo recuperar deudas:\n{e}")
            return
        
        if not deudas:
            messagebox.showinfo("Sin deudas", "No tienes deudas vigentes con plazo definido.")
            return
        
        # Mapping de colores
        color_map = {
            "verde": "#90EE90",
            "amarillo": "#FFFF99",
            "naranja": "#FFB366",
            "rojo": "#FF6B6B"
        }
        
        # Insertar datos
        for deuda in deudas:
            local_id = deuda["local_id"]
            monto = f"${deuda['monto']:.2f}"
            plazo = f"{deuda['plazo_dias']} días"
            fecha_venc = deuda["fecha_vencimiento"].strftime("%Y-%m-%d")
            estado_texto = deuda["texto_estado"]
            
            iid = self.tree.insert("", "end", values=(local_id, monto, plazo, fecha_venc, estado_texto))
            
            # Aplicar color
            color_tag = "color_" + deuda["color"]
            self.tree.item(iid, tags=(color_tag,))
        
        # Configurar etiquetas de color
        for color_name, color_hex in color_map.items():
            self.tree.tag_configure("color_" + color_name, background=color_hex)


class UsuarioDetallesDeudasView(BaseView):
    """Frame para detalles de deudas por tienda (reemplaza tk.Toplevel)"""
    
    def __init__(self, parent, controller, view_model):
        super().__init__(parent, controller, view_model)
        
        # Frame principal
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Título
        title = ttk.Label(main_frame, text="Detalles de Deudas por Tienda", font=("Segoe UI", 16, "bold"))
        title.pack(pady=20)
        
        # Frame del tree
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Treeview
        columns = ("local", "deuda")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        self.tree.heading("local", text="Local")
        self.tree.heading("deuda", text="Deuda")
        self.tree.column("local", width=300)
        self.tree.column("deuda", width=150, anchor="e")
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Atrás", command=lambda: self.controller.go_back()).pack()
    
    def on_show(self):
        """Refrescar datos cuando se muestra la vista"""
        self._cargar_detalles()
    
    def _cargar_detalles(self):
        """Carga los detalles por tienda"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        cliente_id = self.vm.current_user.get("uid") if self.vm.current_user else None
        if not cliente_id:
            return
        
        try:
            detalles = self.vm.obtener_detalles_deudas_por_local(cliente_id)
            for lid, deuda in detalles.items():
                self.tree.insert("", "end", iid=lid, values=(lid, f"${deuda:.2f}"))
        except Exception:
            pass


class UsuarioVerTransaccionesView(BaseView):
    """Frame para ver todas las transacciones (reemplaza tk.Toplevel)"""
    
    def __init__(self, parent, controller, view_model):
        super().__init__(parent, controller, view_model)
        
        # Frame principal
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Título
        title = ttk.Label(main_frame, text="Transacciones del Cliente", font=("Segoe UI", 16, "bold"))
        title.pack(pady=20)
        
        # Frame del tree
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Treeview
        columns = ("fecha", "local", "monto", "plazo")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("local", text="Local")
        self.tree.heading("monto", text="Monto")
        self.tree.heading("plazo", text="Plazo (días)")
        self.tree.column("fecha", width=200, anchor="center")
        self.tree.column("local", width=150)
        self.tree.column("monto", width=100, anchor="e")
        self.tree.column("plazo", width=100, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)
        
        # Botón Atrás
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Atrás", command=lambda: self.controller.go_back()).pack()
    
    def on_show(self):
        """Refrescar datos"""
        self._cargar_transacciones()
    
    def _cargar_transacciones(self):
        """Carga las transacciones"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        cliente_id = self.vm.current_user.get("uid") if self.vm.current_user else None
        if not cliente_id:
            return
        
        try:
            trans = self.vm.obtener_transacciones_cliente(cliente_id)
            for t in trans:
                ts = t.get("timestamp")
                fecha = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else "-"
                self.tree.insert("", "end", values=(fecha, t.get("local_id"), f"${t.get('monto',0):.2f}", t.get("plazo_dias", "-")))
        except Exception:
            pass


class UsuarioHistorialDeudasView(BaseView):
    """Frame para historial de deudas por local (reemplaza tk.Toplevel)"""
    
    def __init__(self, parent, controller, view_model):
        super().__init__(parent, controller, view_model)
        
        # Frame principal
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Título
        title = ttk.Label(main_frame, text="Historial de Deudas", font=("Segoe UI", 16, "bold"))
        title.pack(pady=20)
        
        # Frame de entrada
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(input_frame, text="ID del local:").pack(side="left")
        self.entry_local = ttk.Entry(input_frame, width=30)
        self.entry_local.pack(side="left", padx=10)
        ttk.Button(input_frame, text="Buscar", command=self._buscar).pack(side="left")
        
        # Frame del tree
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Treeview
        columns = ("fecha", "monto", "plazo")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("monto", text="Monto")
        self.tree.heading("plazo", text="Plazo (días)")
        self.tree.column("fecha", width=250)
        self.tree.column("monto", width=120, anchor="e")
        self.tree.column("plazo", width=120, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)
        
        # Botón Atrás
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Atrás", command=lambda: self.controller.go_back()).pack()
        
        self.entry_local.focus()
    
    def _buscar(self):
        """Busca el historial del local especificado"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        local_id = self.entry_local.get().strip()
        if not local_id:
            messagebox.showerror("Error", "Por favor ingrese un ID de local")
            return
        
        cliente_id = self.vm.current_user.get("uid") if self.vm.current_user else None
        if not cliente_id:
            messagebox.showerror("Error", "Usuario no autenticado")
            return
        
        try:
            datos = self.vm.obtener_historial_deudas(local_id, cliente_id)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo recuperar historial:\n{e}")
            return
        
        if not datos:
            messagebox.showinfo("Sin registros", "No se encontraron deudas para este cliente en el local proporcionado.")
            return
        
        # Ordenar por timestamp
        try:
            items = sorted(datos.items(), key=lambda kv: int(kv[0]))
        except Exception:
            items = list(datos.items())
        
        for ts_key, detalle in items:
            try:
                ts = int(detalle.get("timestamp", ts_key))
            except Exception:
                try:
                    ts = int(ts_key)
                except Exception:
                    ts = None
            fecha = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else "-"
            monto = detalle.get("monto", "-")
            plazo = detalle.get("plazo_dias", "-")
            self.tree.insert("", "end", values=(fecha, monto, plazo))


# ========== VISTA TENDERO: LISTAR PRODUCTOS ==========

class TenderoListarProductosView(BaseView):
    """Vista para listar productos de una local"""
    
    def __init__(self, parent, controller, view_model):
        super().__init__(parent, controller, view_model)
        
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        title = ttk.Label(main_frame, text="Listar Productos", font=("Segoe UI", 14, "bold"))
        title.pack(pady=10)
        
        # Frame para entrada de local_id
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(pady=10)
        
        ttk.Label(input_frame, text="ID del Local:").pack(side="left", padx=5)
        self.entrada_local_id = ttk.Entry(input_frame, width=20)
        self.entrada_local_id.pack(side="left", padx=5)
        self.entrada_local_id.focus()
        
        ttk.Button(input_frame, text="Buscar", command=self._cargar_productos).pack(side="left", padx=5)
        
        # Treeview para mostrar productos
        columns = ("Producto ID", "Nombre", "Precio", "Stock")
        self.tree = ttk.Treeview(main_frame, columns=columns, height=15)
        self.tree.column("#0", width=0, stretch="no")
        self.tree.column("Producto ID", anchor="center", width=100)
        self.tree.column("Nombre", anchor="w", width=150)
        self.tree.column("Precio", anchor="center", width=100)
        self.tree.column("Stock", anchor="center", width=80)
        
        self.tree.heading("Producto ID", text="Producto ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Precio", text="Precio")
        self.tree.heading("Stock", text="Stock")
        self.tree.pack(fill="both", expand=True, pady=10)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Atrás", command=lambda: self.controller.go_back()).pack(side="left", padx=5)
    
    def _cargar_productos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        local_id = self.entrada_local_id.get().strip()
        if not local_id:
            messagebox.showerror("Error", "Ingrese un ID de local")
            return
        
        try:
            productos = self.vm.listar_productos(local_id)
            if productos:
                for prod_id, prod_data in productos.items():
                    nombre = prod_data.get("nombre", "-")
                    precio = prod_data.get("precio", "-")
                    stock = prod_data.get("stock", "-")
                    self.tree.insert("", "end", values=(prod_id, nombre, precio, stock))
            else:
                messagebox.showinfo("Resultado", "No hay productos registrados")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los productos:\n{e}")


# ========== VISTA TENDERO: CREAR PRODUCTO ==========

class TenderoCrearProductoView(BaseView):
    """Vista para crear un nuevo producto"""
    
    def __init__(self, parent, controller, view_model):
        super().__init__(parent, controller, view_model)
        
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        title = ttk.Label(main_frame, text="Crear Producto", font=("Segoe UI", 14, "bold"))
        title.pack(pady=10)
        
        # Formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(pady=10)
        
        ttk.Label(form_frame, text="ID del Local:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.entrada_local_id = ttk.Entry(form_frame, width=30)
        self.entrada_local_id.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(form_frame, text="ID del Producto:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.entrada_prod_id = ttk.Entry(form_frame, width=30)
        self.entrada_prod_id.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(form_frame, text="Nombre:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.entrada_nombre = ttk.Entry(form_frame, width=30)
        self.entrada_nombre.grid(row=2, column=1, padx=10, pady=5)
        self.entrada_nombre.focus()
        
        ttk.Label(form_frame, text="Precio:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.entrada_precio = ttk.Entry(form_frame, width=30)
        self.entrada_precio.grid(row=3, column=1, padx=10, pady=5)
        
        ttk.Label(form_frame, text="Stock:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.entrada_stock = ttk.Entry(form_frame, width=30)
        self.entrada_stock.grid(row=4, column=1, padx=10, pady=5)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Crear", command=self._submit).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Atrás", command=lambda: self.controller.go_back()).pack(side="left", padx=5)
    
    def _submit(self):
        local_id = self.entrada_local_id.get().strip()
        prod_id = self.entrada_prod_id.get().strip()
        nombre = self.entrada_nombre.get().strip()
        precio_str = self.entrada_precio.get().strip()
        stock_str = self.entrada_stock.get().strip()
        
        if not all([local_id, prod_id, nombre, precio_str, stock_str]):
            messagebox.showerror("Error", "Complete todos los campos")
            return
        
        try:
            precio = float(precio_str)
            stock = int(stock_str)
            self.vm.crear_producto(local_id, nombre, precio, stock, prod_id)
            messagebox.showinfo("Éxito", "Producto creado correctamente")
            self.entrada_local_id.delete(0, "end")
            self.entrada_prod_id.delete(0, "end")
            self.entrada_nombre.delete(0, "end")
            self.entrada_precio.delete(0, "end")
            self.entrada_stock.delete(0, "end")
            self.entrada_nombre.focus()
        except ValueError:
            messagebox.showerror("Error", "Precio debe ser número y Stock debe ser entero")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el producto:\n{e}")


# ========== VISTA TENDERO: ACTUALIZAR PRODUCTO ==========

class TenderoActualizarProductoView(BaseView):
    """Vista para actualizar un producto"""
    
    def __init__(self, parent, controller, view_model):
        super().__init__(parent, controller, view_model)
        
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        title = ttk.Label(main_frame, text="Actualizar Producto", font=("Segoe UI", 14, "bold"))
        title.pack(pady=10)
        
        # Formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(pady=10)
        
        ttk.Label(form_frame, text="ID del Local:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.entrada_local_id = ttk.Entry(form_frame, width=30)
        self.entrada_local_id.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(form_frame, text="ID del Producto:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.entrada_prod_id = ttk.Entry(form_frame, width=30)
        self.entrada_prod_id.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(form_frame, text="Nuevo Nombre:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.entrada_nombre = ttk.Entry(form_frame, width=30)
        self.entrada_nombre.grid(row=2, column=1, padx=10, pady=5)
        self.entrada_nombre.focus()
        
        ttk.Label(form_frame, text="Nuevo Precio:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.entrada_precio = ttk.Entry(form_frame, width=30)
        self.entrada_precio.grid(row=3, column=1, padx=10, pady=5)
        
        ttk.Label(form_frame, text="Nuevo Stock:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.entrada_stock = ttk.Entry(form_frame, width=30)
        self.entrada_stock.grid(row=4, column=1, padx=10, pady=5)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Actualizar", command=self._submit).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Atrás", command=lambda: self.controller.go_back()).pack(side="left", padx=5)
    
    def _submit(self):
        local_id = self.entrada_local_id.get().strip()
        prod_id = self.entrada_prod_id.get().strip()
        nombre = self.entrada_nombre.get().strip()
        precio_str = self.entrada_precio.get().strip()
        stock_str = self.entrada_stock.get().strip()
        
        if not all([local_id, prod_id, nombre, precio_str, stock_str]):
            messagebox.showerror("Error", "Complete todos los campos")
            return
        
        try:
            precio = float(precio_str)
            stock = int(stock_str)
            self.vm.actualizar_producto(local_id, prod_id, nombre, precio, stock)
            messagebox.showinfo("Éxito", "Producto actualizado correctamente")
            self.entrada_local_id.delete(0, "end")
            self.entrada_prod_id.delete(0, "end")
            self.entrada_nombre.delete(0, "end")
            self.entrada_precio.delete(0, "end")
            self.entrada_stock.delete(0, "end")
            self.entrada_nombre.focus()
        except ValueError:
            messagebox.showerror("Error", "Precio debe ser número y Stock debe ser entero")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el producto:\n{e}")


# ========== VISTA TENDERO: ELIMINAR PRODUCTO ==========

class TenderoEliminarProductoView(BaseView):
    """Vista para eliminar un producto"""
    
    def __init__(self, parent, controller, view_model):
        super().__init__(parent, controller, view_model)
        
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        title = ttk.Label(main_frame, text="Eliminar Producto", font=("Segoe UI", 14, "bold"))
        title.pack(pady=10)
        
        # Formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(pady=10)
        
        ttk.Label(form_frame, text="ID del Local:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.entrada_local_id = ttk.Entry(form_frame, width=30)
        self.entrada_local_id.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(form_frame, text="ID del Producto:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.entrada_prod_id = ttk.Entry(form_frame, width=30)
        self.entrada_prod_id.grid(row=1, column=1, padx=10, pady=5)
        self.entrada_prod_id.focus()
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Eliminar", command=self._submit).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Atrás", command=lambda: self.controller.go_back()).pack(side="left", padx=5)
    
    def _submit(self):
        local_id = self.entrada_local_id.get().strip()
        prod_id = self.entrada_prod_id.get().strip()
        
        if not local_id or not prod_id:
            messagebox.showerror("Error", "Complete todos los campos")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este producto?"):
            try:
                self.vm.eliminar_producto(local_id, prod_id)
                messagebox.showinfo("Éxito", "Producto eliminado correctamente")
                self.entrada_local_id.delete(0, "end")
                self.entrada_prod_id.delete(0, "end")
                self.entrada_prod_id.focus()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el producto:\n{e}")


# ========== VISTA TENDERO: LISTAR CLIENTES ==========

class TenderoListarClientesView(BaseView):
    """Vista para listar clientes de una local"""
    
    def __init__(self, parent, controller, view_model):
        super().__init__(parent, controller, view_model)
        
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        title = ttk.Label(main_frame, text="Listar Clientes", font=("Segoe UI", 14, "bold"))
        title.pack(pady=10)
        
        # Frame para entrada de local_id
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(pady=10)
        
        ttk.Label(input_frame, text="ID del Local:").pack(side="left", padx=5)
        self.entrada_local_id = ttk.Entry(input_frame, width=20)
        self.entrada_local_id.pack(side="left", padx=5)
        self.entrada_local_id.focus()
        
        ttk.Button(input_frame, text="Buscar", command=self._cargar_clientes).pack(side="left", padx=5)
        
        # Treeview para mostrar clientes
        columns = ("Cliente ID", "Nombre", "Email", "Deuda")
        self.tree = ttk.Treeview(main_frame, columns=columns, height=15)
        self.tree.column("#0", width=0, stretch="no")
        self.tree.column("Cliente ID", anchor="center", width=100)
        self.tree.column("Nombre", anchor="w", width=150)
        self.tree.column("Email", anchor="w", width=150)
        self.tree.column("Deuda", anchor="center", width=100)
        
        self.tree.heading("Cliente ID", text="Cliente ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Deuda", text="Deuda")
        self.tree.pack(fill="both", expand=True, pady=10)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Atrás", command=lambda: self.controller.go_back()).pack(side="left", padx=5)
    
    def _cargar_clientes(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        local_id = self.entrada_local_id.get().strip()
        if not local_id:
            messagebox.showerror("Error", "Ingrese un ID de local")
            return
        
        try:
            clientes = self.vm.listar_clientes(local_id)
            if clientes:
                for cliente_id, cliente_data in clientes.items():
                    nombre = cliente_data.get("nombre", "-")
                    email = cliente_data.get("email", "-")
                    deuda = cliente_data.get("deuda", 0)
                    self.tree.insert("", "end", values=(cliente_id, nombre, email, f"${deuda:.2f}"))
            else:
                messagebox.showinfo("Resultado", "No hay clientes registrados")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los clientes:\n{e}")


# ========== VISTA TENDERO: AÑADIR CLIENTE ==========

class TenderoAñadirClienteView(BaseView):
    """Vista para añadir un nuevo cliente"""
    
    def __init__(self, parent, controller, view_model):
        super().__init__(parent, controller, view_model)
        
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        title = ttk.Label(main_frame, text="Añadir Cliente", font=("Segoe UI", 14, "bold"))
        title.pack(pady=10)
        
        # Formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(pady=10)
        
        ttk.Label(form_frame, text="ID del Local:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.entrada_local_id = ttk.Entry(form_frame, width=30)
        self.entrada_local_id.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(form_frame, text="ID del Cliente:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.entrada_cliente_id = ttk.Entry(form_frame, width=30)
        self.entrada_cliente_id.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(form_frame, text="Nombre:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.entrada_nombre = ttk.Entry(form_frame, width=30)
        self.entrada_nombre.grid(row=2, column=1, padx=10, pady=5)
        self.entrada_nombre.focus()
        
        ttk.Label(form_frame, text="Email:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.entrada_email = ttk.Entry(form_frame, width=30)
        self.entrada_email.grid(row=3, column=1, padx=10, pady=5)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Añadir", command=self._submit).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Atrás", command=lambda: self.controller.go_back()).pack(side="left", padx=5)
    
    def _submit(self):
        local_id = self.entrada_local_id.get().strip()
        cliente_id = self.entrada_cliente_id.get().strip()
        nombre = self.entrada_nombre.get().strip()
        email = self.entrada_email.get().strip()
        
        if not all([local_id, cliente_id, nombre, email]):
            messagebox.showerror("Error", "Complete todos los campos")
            return
        
        # Verificar si el usuario existe en la base de datos global
        if not self.vm.usuario_existe_globalmente(cliente_id):
            messagebox.showerror("Error", f"El usuario '{cliente_id}' no existe en la base de datos")
            return
        
        # Verificar si el cliente ya existe en esta local
        if self.vm.cliente_existe(local_id, cliente_id):
            messagebox.showerror("Error", f"El cliente '{cliente_id}' ya existe en esta local")
            return
        
        try:
            cliente_data = {
                "nombre": nombre,
                "email": email,
                "deuda": 0
            }
            self.vm.registrar_cliente(local_id, cliente_id, cliente_data)
            messagebox.showinfo("Éxito", "Cliente añadido correctamente")
            self.entrada_local_id.delete(0, "end")
            self.entrada_cliente_id.delete(0, "end")
            self.entrada_nombre.delete(0, "end")
            self.entrada_email.delete(0, "end")
            self.entrada_nombre.focus()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo añadir el cliente:\n{e}")

    


    
