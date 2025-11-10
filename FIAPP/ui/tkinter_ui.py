import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


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
        
        # Lista de clases de vistas que queremos crear y apilar
        for ViewClass in (LoginView, AdminView, TenderoView, UsuarioView):
            view_instance = ViewClass(container, self, view_model)
            name = ViewClass.__name__
            self.frames[name] = view_instance
            # Coloca cada vista en la misma celda (0,0) para poder alternarlas con tkraise()
            view_instance.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("LoginView")
    
    def show_frame(self, name: str):
        """Cambia de vista según su nombre"""
        frame = self.frames[name]
        frame.tkraise()  # Eleva esa vista al frente (la hace visible sobre las demás)


class BaseView(ttk.Frame):
    """Clase base para todas las vistas"""
    
    def __init__(self, parent, controller, view_model):
        super().__init__(parent)
        self.controller = controller
        self.vm = view_model
        
        # Configurar grid para que se expanda
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


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
        ttk.Button(button_frame, text="Crear Usuario", width=30).pack(pady=8)
        ttk.Button(button_frame, text="Listar Usuarios", width=30).pack(pady=8)
        ttk.Button(button_frame, text="Eliminar Usuario", width=30).pack(pady=8)
        ttk.Button(button_frame, text="Cambiar de Usuario", command=lambda: controller.show_frame("LoginView"), width=30).pack(pady=8)
        ttk.Button(button_frame, text="Salir", command=controller.quit, width=30).pack(pady=8)


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
        ttk.Button(button_frame, text="Listar productos", width=40).pack(pady=5, fill="x")
        ttk.Button(button_frame, text="Crear producto", width=40).pack(pady=5, fill="x")
        ttk.Button(button_frame, text="Actualizar producto", width=40).pack(pady=5, fill="x")
        ttk.Button(button_frame, text="Eliminar producto", width=40).pack(pady=5, fill="x")
        ttk.Button(button_frame, text="Listar clientes", width=40).pack(pady=5, fill="x")
        ttk.Button(button_frame, text="Añadir cliente", width=40).pack(pady=5, fill="x")
        ttk.Button(button_frame, text="Registrar deuda", width=40, command=self._open_registrar_deuda_dialog).pack(pady=5, fill="x")
        ttk.Button(button_frame, text="Cambiar de usuario", command=lambda: controller.show_frame("LoginView"), width=40).pack(pady=5, fill="x")
        ttk.Button(button_frame, text="Locales", width=40).pack(pady=5, fill="x")
        ttk.Button(button_frame, text="Salir", command=controller.quit, width=40).pack(pady=5, fill="x")

        # --- Método para abrir diálogo de registrar deuda ---
    def _open_registrar_deuda_dialog(self):
        """Abrir un diálogo modal para ingresar datos de la deuda y enviarlos al ViewModel."""
        dialog = tk.Toplevel(self)
        dialog.title("Registrar deuda")
        dialog.geometry("420x300")
        dialog.transient(self)
        dialog.grab_set()

        frm = ttk.Frame(dialog, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="ID del local:").grid(row=0, column=0, sticky="w", pady=6)
        entry_local = ttk.Entry(frm, width=35)
        entry_local.grid(row=0, column=1, pady=6)

        ttk.Label(frm, text="ID del cliente:").grid(row=1, column=0, sticky="w", pady=6)
        entry_cliente = ttk.Entry(frm, width=35)
        entry_cliente.grid(row=1, column=1, pady=6)

        ttk.Label(frm, text="Monto:").grid(row=2, column=0, sticky="w", pady=6)
        entry_monto = ttk.Entry(frm, width=35)
        entry_monto.grid(row=2, column=1, pady=6)

        ttk.Label(frm, text="Plazo (días) - opcional:").grid(row=3, column=0, sticky="w", pady=6)
        entry_plazo = ttk.Entry(frm, width=35)
        entry_plazo.grid(row=3, column=1, pady=6)

        # Botones
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=12)

        def _submit():
            local = entry_local.get().strip()
            cliente = entry_cliente.get().strip()
            monto_s = entry_monto.get().strip()
            plazo_s = entry_plazo.get().strip()

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
                    messagebox.showerror("Error", "Plazo inválido. Ingrese un número entero de días o deje en blanco.")
                    return

            try:
                # Llamada al ViewModel; se asume que la firma acepta plazo_dias opcional
                self.vm.registrar_deuda(local, cliente, monto, plazo)
                messagebox.showinfo("Éxito", "Deuda registrada correctamente")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo registrar la deuda:\n{e}")

        ttk.Button(btn_frame, text="Registrar", command=_submit).pack(side="left", padx=8)
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side="left", padx=8)

        entry_local.focus()


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
        
        # Contenedor de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        # Botones del menú
        ttk.Button(button_frame, text="Consultar Deuda", width=30).pack(pady=8)
        ttk.Button(button_frame, text="Ver Transacciones", width=30).pack(pady=8)
        ttk.Button(button_frame, text="Historial de Deudas", width=30, command=self._open_historial_deudas).pack(pady=8)
        ttk.Button(button_frame, text="Cambiar de Usuario", command=lambda: controller.show_frame("LoginView"), width=30).pack(pady=8)
        ttk.Button(button_frame, text="Salir", command=controller.quit, width=30).pack(pady=8)


    def _open_historial_deudas(self):
        """Abre una ventana con el historial de deudas del cliente para un local especificado."""
        cliente_id = self.vm.current_user.get("uid") if self.vm.current_user else None
        if not cliente_id:
            messagebox.showerror("Error", "Usuario no autenticado")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Historial de Deudas")
        dialog.geometry("700x450")
        dialog.transient(self)
        dialog.grab_set()

        frm = ttk.Frame(dialog, padding=12)
        frm.pack(fill="both", expand=True)

        # Input para local_id
        ttk.Label(frm, text="ID del local:").grid(row=0, column=0, sticky="w")
        entry_local = ttk.Entry(frm, width=30)
        entry_local.grid(row=0, column=1, sticky="w")

        # Botón buscar
        def _buscar():
            local_id = entry_local.get().strip()
            if not local_id:
                messagebox.showerror("Error", "Por favor ingrese un ID de local")
                return
            try:
                datos = self.vm.obtener_historial_deudas(local_id, cliente_id)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo recuperar historial:\n{e}")
                return

            # limpiar tree
            for row in tree.get_children():
                tree.delete(row)

            # datos es un dict timestamp -> detalle
            if not datos:
                messagebox.showinfo("Sin registros", "No se encontraron deudas para este cliente en el local proporcionado.")
                return

            # Ordenar por timestamp ascendente
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
                tree.insert("", "end", values=(fecha, monto, plazo))

        ttk.Button(frm, text="Buscar", command=_buscar).grid(row=0, column=2, padx=8)

        # Treeview para mostrar historial
        columns = ("fecha", "monto", "plazo")
        tree = ttk.Treeview(frm, columns=columns, show="headings", height=15)
        tree.heading("fecha", text="Fecha")
        tree.heading("monto", text="Monto")
        tree.heading("plazo", text="Plazo (días)")
        tree.column("fecha", width=300)
        tree.column("monto", width=120, anchor="e")
        tree.column("plazo", width=120, anchor="center")
        tree.grid(row=1, column=0, columnspan=3, pady=12, sticky="nsew")

        # Scrollbars
        vsb = ttk.Scrollbar(frm, orient="vertical", command=tree.yview)
        vsb.grid(row=1, column=3, sticky="ns")
        tree.configure(yscrollcommand=vsb.set)

        entry_local.focus()


    
