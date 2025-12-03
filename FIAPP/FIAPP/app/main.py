from flask import Flask, request, render_template, redirect, url_for, session
import os
import requests
import time
from werkzeug.utils import secure_filename
from database.firebase_config import init_firebase
from database.auth_service import AuthService
from presentation.presentation import ViewModel
import ast
import re


app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = "dev-secret-fiapp-2025"

# Configuración de uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../static/productos')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Crear carpeta de uploads si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    """Verifica que el archivo tenga extensión permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_upload_file(file):
    """Guarda archivo subido y retorna nombre único + relativo."""
    if not file or file.filename == '':
        return None
    if not allowed_file(file.filename):
        return None
    try:
        # Generar nombre único
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_name = f"producto_{int(time.time())}_{os.urandom(4).hex()}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(filepath)
        # Retornar ruta relativa para guardar en BD
        return f"/static/productos/{unique_name}"
    except Exception as e:
        print(f"[ERROR] al guardar archivo: {e}")
        return None

# Inicializar Firebase (usa variables de entorno FIREBASE_CREDENTIALS_PATH y FIREBASE_DB_URL)
init_firebase()

# Control de uso de autenticación local vs Realtime DB
# Para usar Realtime Database, asegúrate de tener las variables de entorno y
# establece `USE_LOCAL_AUTH=false` (o no definirla). Para desarrollo rápido,
# puedes poner `USE_LOCAL_AUTH=true`.
use_local_auth = os.getenv("USE_LOCAL_AUTH", "false").lower() in ("1", "true", "yes")
print(f"[CONFIG] USE_LOCAL_AUTH={use_local_auth}")

auth_service = AuthService(use_local=use_local_auth)
view_model = ViewModel(auth_service)


@app.before_request
def log_request_info():
    try:
        print(f"[REQ] {request.method} {request.path}", flush=True)
        if request.method in ("POST", "PUT", "PATCH"):
            try:
                form = request.form.to_dict()
                print(f"[REQ] form: {form}", flush=True)
            except Exception:
                data = request.get_data(as_text=True)
                print(f"[REQ] raw: {data}", flush=True)
    except Exception:
        pass


@app.after_request
def set_csp(response):
    # Strict CSP: no unsafe-eval, only allow scripts/styles from our origin
    csp = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self' https://identitytoolkit.googleapis.com https://*.firebaseio.com https://firebaserules.googleapis.com; "
        "frame-src 'none'; object-src 'none';"
    )
    response.headers['Content-Security-Policy'] = csp
    return response


@app.route("/")
def index():
    user = session.get("user")
    role = session.get("role")
    return render_template("index.html", user=user, role=role)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        password_confirm = request.form.get("password_confirm", "").strip()
        user_id = request.form.get("user_id", "").strip()
        
        # Validaciones rápidas
        if not email:
            return render_template("register.html", error="Email es requerido")
        if not password:
            return render_template("register.html", error="Contraseña es requerida")
        if not password_confirm:
            return render_template("register.html", error="Confirma tu contraseña")
        if not user_id:
            return render_template("register.html", error="Usuario es requerido")
        if password != password_confirm:
            return render_template("register.html", error="Las contraseñas no coinciden")
        if len(password) < 6:
            return render_template("register.html", error="Contraseña mínimo 6 caracteres")
        
        try:
            res = view_model.crear_usuario(email, password, user_id)
            if res.get("success"):
                session["user"] = user_id
                session["email"] = email
                session["tipo_usuario"] = None  # Se asigna en siguiente paso
                return redirect(url_for("select_type"))
            else:
                return render_template("register.html", error=res.get("error", "Error al registrar"))
        except Exception as e:
            error_msg = str(e)
            if "already exists" in error_msg or "ALREADY_EXISTS" in error_msg or "registrado" in error_msg:
                error_msg = "El email ya está registrado"
            elif "WEAK_PASSWORD" in error_msg:
                error_msg = "Contraseña muy débil"
            return render_template("register.html", error=error_msg)
    
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        
        if not email:
            return render_template("login.html", error="Email es requerido")
        if not password:
            return render_template("login.html", error="Contraseña es requerida")
        
        try:
            uid, tipo_usuario = auth_service.login_user(email, password)
            if uid and tipo_usuario:  # Usuario debe tener tipo asignado
                session["user"] = uid
                session["email"] = email
                session["tipo_usuario"] = tipo_usuario
                return redirect(url_for("dashboard"))
            elif uid and not tipo_usuario:  # Usuario existe pero sin tipo asignado
                session["user"] = uid
                session["email"] = email
                return redirect(url_for("select_type"))
            else:
                return render_template("login.html", error="Email o contraseña incorrectos")
        except Exception as e:
            return render_template("login.html", error=f"Error: {str(e)}")
    
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/select-type", methods=["GET", "POST"])
def select_type():
    """Permite al usuario seleccionar su tipo (tendero/cliente) después de registrarse."""
    email = session.get("email")
    if not email:
        return redirect(url_for("login"))
    
    if request.method == "POST":
        tipo_usuario = request.form.get("tipo_usuario", "").strip()
        if tipo_usuario not in ("tendero", "cliente"):
            return render_template("select_type.html", error="Selecciona un tipo válido")
        
        try:
            res = view_model.asignar_tipo_usuario(email, tipo_usuario)
            if res.get("success"):
                session["tipo_usuario"] = tipo_usuario
                return redirect(url_for("dashboard"))
            else:
                return render_template("select_type.html", error=res.get("error", "Error al asignar tipo"))
        except Exception as e:
            return render_template("select_type.html", error=f"Error: {str(e)}")
    
    return render_template("select_type.html")


@app.route("/dashboard")
def dashboard():
    tipo_usuario = session.get("tipo_usuario")
    if not tipo_usuario:
        return redirect(url_for("login"))
    
    if tipo_usuario == "tendero":
        return render_template("tendero_dashboard.html")
    elif tipo_usuario == "cliente":
        return render_template("cliente_dashboard.html")
    else:
        return redirect(url_for("login"))


@app.route("/tendero/locales")
def tendero_locales():
    """Tendero: lista sus locales."""
    if session.get("tipo_usuario") != "tendero":
        return redirect(url_for("login"))
    user_id = session.get("user")
    locales = view_model.listar_locales_por_propietario(user_id)
    return render_template("tendero_locales.html", locales=locales)


@app.route("/tendero/locales/create", methods=["GET", "POST"])
def tendero_create_local():
    """Tendero: crea una tienda."""
    if session.get("tipo_usuario") != "tendero":
        return redirect(url_for("login"))
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        if not nombre:
            return render_template("tendero_create_local.html", error="Nombre requerido")
        user_id = session.get("user")
        # Generar ID de local seguro: user_id_timestamp (sin caracteres especiales)
        local_id = f"local_{user_id}_{int(time.time())}"
        try:
            res = view_model.crear_local(nombre, user_id, local_id)
            if res.get("success"):
                return redirect(url_for("tendero_locales"))
            else:
                return render_template("tendero_create_local.html", error=res.get("error"))
        except Exception as e:
            return render_template("tendero_create_local.html", error=str(e))
    return render_template("tendero_create_local.html")


@app.route("/tendero/locales/<local_id>/inventario")
def tendero_inventario(local_id):
    """Tendero: ve inventario de una tienda."""
    if session.get("tipo_usuario") != "tendero":
        return redirect(url_for("login"))
    productos = view_model.listar_productos(local_id)
    local_data = view_model.db.ref.child(f"locales/{local_id}").get() or {}
    local_name = local_data.get("nombre", local_id)
    
    # Obtener mapa de proveedores para resolver nombres
    owner = session.get('user')
    proveedores = view_model.listar_proveedores(owner) or {}
    
    return render_template("tendero_inventario.html", local_id=local_id, local_name=local_name, productos=productos, proveedores=proveedores)


@app.route("/tendero/locales/<local_id>/productos/create", methods=["GET", "POST"])
def tendero_create_producto(local_id):
    """Tendero: crea un producto en una tienda."""
    if session.get("tipo_usuario") != "tendero":
        return redirect(url_for("login"))
    
    # Obtener nombre del local
    local_data = view_model.db.ref.child(f"locales/{local_id}").get() or {}
    local_name = local_data.get("nombre", local_id)
    
    # obtener proveedores para el formulario (solo del tendero actual)
    proveedores = {}
    try:
        owner = session.get('user')
        proveedores = view_model.listar_proveedores(owner) or {}
    except Exception:
        proveedores = {}

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        precio = request.form.get("precio", "").strip()
        stock = request.form.get("stock", "").strip()
        proveedor = request.form.get("proveedor", "").strip()
        file = request.files.get("imagen")
        
        # Validaciones
        if not nombre:
            return render_template("tendero_create_producto.html", local_id=local_id, local_name=local_name, error="Nombre requerido", proveedores=proveedores)
        if not precio:
            return render_template("tendero_create_producto.html", local_id=local_id, local_name=local_name, error="Precio requerido", proveedores=proveedores)
        if not stock:
            return render_template("tendero_create_producto.html", local_id=local_id, local_name=local_name, error="Stock requerido", proveedores=proveedores)
        
        try:
            precio = float(precio)
            stock = int(stock)
        except ValueError:
            return render_template("tendero_create_producto.html", local_id=local_id, local_name=local_name, error="Precio y stock deben ser números", proveedores=proveedores)
        
        # Guardar imagen si se envió
        imagen_url = None
        if file:
            imagen_url = save_upload_file(file)
            if not imagen_url:
                return render_template("tendero_create_producto.html", local_id=local_id, local_name=local_name, error="Imagen no válida (PNG, JPG, GIF, WebP; máx 5MB)", proveedores=proveedores)
        
        # Generar ID único para producto
        producto_id = f"prod_{int(time.time())}_{os.urandom(3).hex()}"
        
        try:
            res = view_model.crear_producto(local_id, nombre, precio, stock, producto_id, imagen_url, proveedor)
            if res.get("success"):
                return redirect(url_for("tendero_inventario", local_id=local_id))
            else:
                return render_template("tendero_create_producto.html", local_id=local_id, local_name=local_name, error=res.get("error"), proveedores=proveedores)
        except Exception as e:
            return render_template("tendero_create_producto.html", local_id=local_id, local_name=local_name, error=str(e), proveedores=proveedores)
    
    return render_template("tendero_create_producto.html", local_id=local_id, local_name=local_name, proveedores=proveedores)


@app.route("/tendero/locales/<local_id>/clientes")
def tendero_clientes(local_id):
    """Tendero: ve clientes de una tienda y gestiona sus deudas."""
    if session.get("tipo_usuario") != "tendero":
        return redirect(url_for("login"))
    clientes = view_model.listar_clientes(local_id)
    local_data = view_model.db.ref.child(f"locales/{local_id}").get() or {}
    local_name = local_data.get("nombre", local_id)
    return render_template("tendero_clientes.html", local_id=local_id, local_name=local_name, clientes=clientes)


@app.route("/tendero/locales/<local_id>/clientes/agregar", methods=["GET", "POST"])
def tendero_agregar_cliente(local_id):
    """Tendero: formulario para agregar un cliente existente con deuda inicial."""
    if session.get("tipo_usuario") != "tendero":
        return redirect(url_for("login"))
    
    # Obtener nombre del local
    local_data = view_model.db.ref.child(f"locales/{local_id}").get() or {}
    local_name = local_data.get("nombre", local_id)
    
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        deuda_inicial = request.form.get("deuda_inicial", "").strip()
        
        if not email or not deuda_inicial:
            return render_template("tendero_agregar_cliente.html", local_id=local_id, local_name=local_name,
                                 error="Email y deuda son requeridos")
        
        # Verificar que el cliente exista en el sistema
        try:
            import hashlib
            email_key = hashlib.md5(email.lower().encode()).hexdigest()
            user_data = view_model.db.ref.child(f"usuarios/{email_key}").get()
            
            if not user_data:
                return render_template("tendero_agregar_cliente.html", local_id=local_id, local_name=local_name,
                                     error=f"El cliente con email '{email}' no existe en el sistema")
            
            # Verificar que sea cliente (no tendero)
            if user_data.get("tipo_usuario") != "cliente":
                return render_template("tendero_agregar_cliente.html", local_id=local_id, local_name=local_name,
                                     error="Este usuario no es un cliente")
            
            # Validar deuda
            try:
                deuda_inicial = float(deuda_inicial)
                if deuda_inicial < 0:
                    return render_template("tendero_agregar_cliente.html", local_id=local_id, local_name=local_name,
                                         error="La deuda no puede ser negativa")
            except ValueError:
                return render_template("tendero_agregar_cliente.html", local_id=local_id, local_name=local_name,
                                     error="La deuda debe ser un número válido")
            
            # Obtener cliente_id (user_id del usuario)
            cliente_id = user_data.get("user_id")
            nombre = user_data.get("email", email)
            
            # Verificar que no esté ya registrado en esta tienda
            cliente_existente = view_model.db.ref.child(f"locales/{local_id}/clientes/{cliente_id}").get()
            if cliente_existente:
                return render_template("tendero_agregar_cliente.html", local_id=local_id, local_name=local_name,
                                     error="Este cliente ya está registrado en esta tienda")
            
            # Agregar cliente
            cliente_data = {
                "email": email,
                "nombre": nombre,
                "deuda": deuda_inicial
            }
            view_model.registrar_cliente(local_id, cliente_id, cliente_data)
            return redirect(url_for("tendero_clientes", local_id=local_id))
            
        except Exception as e:
            print(f"[ERROR] al agregar cliente: {e}")
            return render_template("tendero_agregar_cliente.html", local_id=local_id, local_name=local_name,
                                 error=f"Error: {str(e)}")
    
    return render_template("tendero_agregar_cliente.html", local_id=local_id, local_name=local_name)


@app.route("/tendero/locales/<local_id>/cliente/<cliente_id>/abono", methods=["POST"])
def tendero_registrar_abono(local_id, cliente_id):
    """Tendero: registra un abono/pago parcial a la deuda de un cliente."""
    if session.get("tipo_usuario") != "tendero":
        return redirect(url_for("login"))
    
    print(f"[ABONO] local_id={local_id}, cliente_id={cliente_id}")
    monto_pago = request.form.get("monto_pago", "").strip()
    print(f"[ABONO] monto_pago recibido: {monto_pago}")
    
    if not monto_pago:
        print(f"[ABONO] monto_pago vacío, retornando")
        return redirect(url_for("tendero_clientes", local_id=local_id))
    
    try:
        monto_pago = float(monto_pago)
        print(f"[ABONO] monto_pago convertido: {monto_pago}")
        if monto_pago <= 0:
            print(f"[ABONO] monto_pago es <= 0, retornando")
            return redirect(url_for("tendero_clientes", local_id=local_id))
    except ValueError as e:
        print(f"[ABONO] Error al convertir monto_pago: {e}")
        return redirect(url_for("tendero_clientes", local_id=local_id))
    
    try:
        # Obtener deuda actual
        cliente = view_model.db.ref.child(f"locales/{local_id}/clientes/{cliente_id}").get()
        print(f"[ABONO] cliente data: {cliente}")
        if not cliente:
            print(f"[ABONO] cliente no encontrado")
            return redirect(url_for("tendero_clientes", local_id=local_id))
        
        deuda_actual = cliente.get("deuda", 0)
        print(f"[ABONO] deuda_actual: {deuda_actual}")
        nueva_deuda = max(0, deuda_actual - monto_pago)
        print(f"[ABONO] nueva_deuda calculada: {nueva_deuda}")
        
        # Actualizar deuda
        result = view_model.actualizar_deuda(local_id, cliente_id, nueva_deuda)
        print(f"[ABONO] resultado de actualización: {result}")
        if not result.get("success"):
            print(f"[ERROR] al actualizar deuda: {result.get('error')}")
        
        print(f"[ABONO] ✓ Abono registrado correctamente")
        return redirect(url_for("tendero_clientes", local_id=local_id))
    except Exception as e:
        print(f"[ERROR] al registrar abono: {e}")
        import traceback
        traceback.print_exc()
        return redirect(url_for("tendero_clientes", local_id=local_id))


@app.route("/tendero/locales/<local_id>/cliente/<cliente_id>/cancelar", methods=["POST"])
def tendero_cancelar_deuda(local_id, cliente_id):
    """Tendero: cancela completamente la deuda de un cliente."""
    if session.get("tipo_usuario") != "tendero":
        return redirect(url_for("login"))
    
    print(f"[CANCELAR] local_id={local_id}, cliente_id={cliente_id}")
    try:
        result = view_model.cancelar_deuda(local_id, cliente_id)
        print(f"[CANCELAR] resultado: {result}")
        if not result.get("success"):
            print(f"[ERROR] al cancelar deuda: {result.get('error')}")
        print(f"[CANCELAR] ✓ Deuda cancelada correctamente")
        return redirect(url_for("tendero_clientes", local_id=local_id))
    except Exception as e:
        print(f"[ERROR] al cancelar deuda: {e}")
        import traceback
        traceback.print_exc()
        return redirect(url_for("tendero_clientes", local_id=local_id))


@app.route("/tendero/locales/<local_id>/cliente/<cliente_id>/sumar", methods=["POST"])
def tendero_sumar_deuda(local_id, cliente_id):
    """Tendero: suma/aumenta la deuda de un cliente."""
    if session.get("tipo_usuario") != "tendero":
        return redirect(url_for("login"))
    
    print(f"[SUMAR] local_id={local_id}, cliente_id={cliente_id}")
    monto_sumar = request.form.get("monto_sumar", "").strip()
    print(f"[SUMAR] monto_sumar recibido: {monto_sumar}")
    
    if not monto_sumar:
        print(f"[SUMAR] monto_sumar vacío, retornando")
        return redirect(url_for("tendero_clientes", local_id=local_id))
    
    try:
        monto_sumar = float(monto_sumar)
        print(f"[SUMAR] monto_sumar convertido: {monto_sumar}")
        if monto_sumar <= 0:
            print(f"[SUMAR] monto_sumar es <= 0, retornando")
            return redirect(url_for("tendero_clientes", local_id=local_id))
    except ValueError as e:
        print(f"[SUMAR] Error al convertir monto_sumar: {e}")
        return redirect(url_for("tendero_clientes", local_id=local_id))
    
    try:
        # Obtener deuda actual
        cliente = view_model.db.ref.child(f"locales/{local_id}/clientes/{cliente_id}").get()
        print(f"[SUMAR] cliente data: {cliente}")
        if not cliente:
            print(f"[SUMAR] cliente no encontrado")
            return redirect(url_for("tendero_clientes", local_id=local_id))
        
        deuda_actual = cliente.get("deuda", 0)
        print(f"[SUMAR] deuda_actual: {deuda_actual}")
        nueva_deuda = deuda_actual + monto_sumar
        print(f"[SUMAR] nueva_deuda calculada: {nueva_deuda}")
        
        # Actualizar deuda
        result = view_model.actualizar_deuda(local_id, cliente_id, nueva_deuda)
        print(f"[SUMAR] resultado de actualización: {result}")
        if not result.get("success"):
            print(f"[ERROR] al actualizar deuda: {result.get('error')}")
        
        print(f"[SUMAR] ✓ Deuda aumentada correctamente")
        return redirect(url_for("tendero_clientes", local_id=local_id))
    except Exception as e:
        print(f"[ERROR] al sumar deuda: {e}")
        import traceback
        traceback.print_exc()
        return redirect(url_for("tendero_clientes", local_id=local_id))


@app.route("/tendero/locales/<local_id>/cliente/<cliente_id>/eliminar", methods=["POST"])
def tendero_eliminar_cliente(local_id, cliente_id):
    """Tendero: elimina completamente un cliente del local."""
    if session.get("tipo_usuario") != "tendero":
        return redirect(url_for("login"))
    
    print(f"[ELIMINAR] local_id={local_id}, cliente_id={cliente_id}")
    try:
        view_model.db.ref.child(f"locales/{local_id}/clientes/{cliente_id}").delete()
        print(f"[ELIMINAR] ✓ Cliente eliminado correctamente")
        return redirect(url_for("tendero_clientes", local_id=local_id))
    except Exception as e:
        print(f"[ERROR] al eliminar cliente: {e}")
        import traceback
        traceback.print_exc()
        return redirect(url_for("tendero_clientes", local_id=local_id))


@app.route("/tendero/locales/<local_id>/productos/<producto_id>/editar", methods=["GET", "POST"])
def tendero_editar_producto(local_id, producto_id):
    """Tendero: edita un producto."""
    if session.get("tipo_usuario") != "tendero":
        return redirect(url_for("login"))
    
    # Obtener nombre del local
    local_data = view_model.db.ref.child(f"locales/{local_id}").get() or {}
    local_name = local_data.get("nombre", local_id)
    
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        precio = request.form.get("precio", "").strip()
        stock = request.form.get("stock", "").strip()
        proveedor = request.form.get("proveedor", "").strip()
        file = request.files.get("imagen")
        
        if not nombre or not precio or not stock:
            return render_template("tendero_editar_producto.html", local_id=local_id, local_name=local_name, producto_id=producto_id, error="Todos los campos son requeridos")
        
        try:
            precio = float(precio)
            stock = int(stock)
        except ValueError:
            return render_template("tendero_editar_producto.html", local_id=local_id, local_name=local_name, producto_id=producto_id, error="Precio y stock deben ser números")
        
        # Preparar datos a actualizar
        update_data = {
            "nombre": nombre,
            "precio": precio,
            "stock": stock,
            "proveedor": proveedor if proveedor else None
        }
        
        # Si se subió una nueva imagen
        if file and file.filename != '':
            imagen_url = save_upload_file(file)
            if not imagen_url:
                return render_template("tendero_editar_producto.html", local_id=local_id, local_name=local_name, producto_id=producto_id, error="Imagen no válida (PNG, JPG, GIF, WebP; máx 5MB)")
            update_data["imagen_url"] = imagen_url
        
        try:
            view_model.db.update_producto(local_id, producto_id, update_data)
            return redirect(url_for("tendero_inventario", local_id=local_id))
        except Exception as e:
            return render_template("tendero_editar_producto.html", local_id=local_id, local_name=local_name, producto_id=producto_id, error=str(e))
    
    # GET: mostrar formulario con datos actuales
    producto = view_model.db.ref.child(f"locales/{local_id}/productos/{producto_id}").get()
    if not producto:
        return redirect(url_for("tendero_inventario", local_id=local_id))
    
    owner = session.get('user')
    proveedores = view_model.listar_proveedores(owner)
    return render_template("tendero_editar_producto.html", local_id=local_id, local_name=local_name, producto_id=producto_id, producto=producto, proveedores=proveedores)


@app.route("/tendero/locales/<local_id>/productos/<producto_id>/eliminar", methods=["POST"])
def tendero_eliminar_producto(local_id, producto_id):
    """Tendero: elimina un producto."""
    if session.get("tipo_usuario") != "tendero":
        return redirect(url_for("login"))
    
    try:
        view_model.eliminar_producto(local_id, producto_id)
        return redirect(url_for("tendero_inventario", local_id=local_id))
    except Exception as e:
        print(f"[ERROR] al eliminar producto: {e}")
        return redirect(url_for("tendero_inventario", local_id=local_id))


@app.route("/tendero/proveedores")
def tendero_proveedores():
    """Tendero: lista sus proveedores."""
    if session.get("tipo_usuario") != "tendero":
        return redirect(url_for("login"))
    user_id = session.get('user')
    proveedores = view_model.listar_proveedores(user_id)
    return render_template("tendero_proveedores.html", proveedores=proveedores)


@app.route("/tendero/proveedores/create", methods=["GET", "POST"])
def tendero_crear_proveedor():
    """Tendero: formulario para crear nuevo proveedor."""
    if session.get("tipo_usuario") != "tendero":
        return redirect(url_for("login"))
    
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        contacto = request.form.get("contacto", "").strip()
        email = request.form.get("email", "").strip()
        
        if not nombre:
            return render_template("tendero_create_proveedor.html", error="El nombre es requerido")
        
        # Generar ID único para el proveedor
        proveedor_id = f"prov_{int(time.time())}_{os.urandom(4).hex()}"
        
        try:
            owner = session.get('user')
            view_model.crear_proveedor(proveedor_id, nombre, contacto or None, email or None, propietario_id=owner)
            return redirect(url_for("tendero_proveedores"))
        except Exception as e:
            print(f"[ERROR] al crear proveedor: {e}")
            return render_template("tendero_create_proveedor.html", error=str(e))
    
    return render_template("tendero_create_proveedor.html")


@app.route("/tendero/proveedores/<proveedor_id>/delete", methods=["POST"])
def tendero_eliminar_proveedor(proveedor_id):
    """Tendero: elimina un proveedor."""
    if session.get("tipo_usuario") != "tendero":
        return redirect(url_for("login"))
    
    try:
        view_model.eliminar_proveedor(proveedor_id)
        return redirect(url_for("tendero_proveedores"))
    except Exception as e:
        print(f"[ERROR] al eliminar proveedor: {e}")
        return redirect(url_for("tendero_proveedores"))


@app.route("/api/proveedores")
def api_get_proveedores():
    """API para obtener lista de proveedores (JSON)."""
    if session.get("tipo_usuario") != "tendero":
        return {"error": "No autorizado"}, 401
    
    try:
        owner = session.get('user')
        proveedores = view_model.listar_proveedores(owner)
        return {"proveedores": proveedores}, 200
    except Exception as e:
        print(f"[ERROR] en API proveedores: {e}")
        return {"error": str(e)}, 500


@app.route("/cliente/deudas")
def cliente_deudas():
    """Cliente: ve todas sus deudas."""
    if session.get("tipo_usuario") != "cliente":
        return redirect(url_for("login"))
    cliente_id = session.get("user")
    deudas = view_model.get_deudas_cliente(cliente_id)
    return render_template("cliente_deudas.html", deudas=deudas)


def _safe_eval(expr: str):
    """Evalúa expresiones aritméticas simples de forma segura usando ast."""
    # Sólo permitir dígitos, operadores y paréntesis
    if not re.match(r'^[0-9\.\s\+\-\*\/\%\(\)]+$', expr):
        raise ValueError('Expresión no permitida')
    node = ast.parse(expr, mode='eval')
    allowed = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Constant,
               ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow,
               ast.USub, ast.UAdd, ast.Load)
    for n in ast.walk(node):
        if not isinstance(n, allowed):
            raise ValueError('Operación no permitida')
    return eval(compile(node, '<string>', 'eval'))


def _handle_finance_message(message: str) -> str:
    m = (message or '').lower().strip()
    if not m:
        return 'Mensaje vacío.'

    # Reemplazar comas por puntos
    expr = re.sub(r',', '.', m)
    # Si parece una expresión aritmética, intentamos evaluarla
    if re.match(r'^[0-9\.\s\+\-\*\/\%\(\)]+$', expr):
        try:
            val = _safe_eval(expr)
            return f'El resultado es {val}'
        except Exception:
            pass

    # Patrón: '3 unidades a 12.50' o '3 u a 12.50'
    p = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*(?:unidades|u|uds)?\s*(?:a|x|por)\s*\$?\s*([0-9]+(?:\.[0-9]+)?)', m)
    if p:
        qty = float(p.group(1))
        price = float(p.group(2))
        total = qty * price
        qty_display = int(qty) if qty.is_integer() else qty
        return f'{qty_display} × {price} = {total:.2f} (total)'

    # Patrón: porcentaje '10% de 250'
    p2 = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*%\s*(?:de)?\s*\$?\s*([0-9]+(?:\.[0-9]+)?)', m)
    if p2:
        pct = float(p2.group(1))
        base = float(p2.group(2))
        value = base * pct / 100.0
        return f'{pct}% de {base} = {value:.2f}'

    # Fallback con ejemplos
    return ('Puedo ayudar con cálculos: ejemplos:\n- "3 unidades a 12.50"\n- "12.5*3+2"\n- "10% de 250"')


def _build_ai_context(tendero_id: str) -> str:
    """Construye contexto de negocio del tendero para la IA (locales, productos, clientes, deudas)."""
    try:
        locales = view_model.listar_locales(tendero_id) or {}
        context_lines = ["📊 CONTEXTO DE TU NEGOCIO:\n"]
        
        if not locales:
            context_lines.append("No tienes locales registrados aún.")
            return '\n'.join(context_lines)
        
        for local_id, local_data in locales.items():
            local_name = local_data.get('nombre', local_id)
            context_lines.append(f"\n🏪 Tienda: {local_name}")
            
            # Productos
            try:
                productos = view_model.listar_productos(local_id) or {}
                if productos:
                    context_lines.append(f"  📦 Productos ({len(productos)}):")
                    for pid, pdata in list(productos.items())[:5]:  # Top 5
                        nombre = pdata.get('nombre', 'Sin nombre')
                        precio = pdata.get('precio', 0)
                        stock = pdata.get('stock', 0)
                        context_lines.append(f"    - {nombre}: ${precio} (stock: {stock})")
                    if len(productos) > 5:
                        context_lines.append(f"    ... y {len(productos) - 5} más")
            except Exception as e:
                print(f"[AI CONTEXT] error productos: {e}")
            
            # Clientes y deudas
            try:
                clientes = view_model.listar_clientes(local_id) or {}
                if clientes:
                    total_deuda = 0
                    clientes_deudores = 0
                    for cid, cdata in clientes.items():
                        deuda = float(cdata.get('deuda', 0))
                        if deuda > 0:
                            clientes_deudores += 1
                            total_deuda += deuda
                    context_lines.append(f"  👥 Clientes: {len(clientes)} (deudores: {clientes_deudores}, deuda total: ${total_deuda:.2f})")
            except Exception as e:
                print(f"[AI CONTEXT] error clientes: {e}")
        
        return '\n'.join(context_lines)
    except Exception as e:
        print(f"[AI CONTEXT] error building context: {e}")
        return "Contexto no disponible."


def _execute_firebase_query(tendero_id: str, query_type: str) -> str:
    """Ejecuta consultas específicas en Firebase y devuelve datos formateados para la IA."""
    try:
        locales = view_model.listar_locales(tendero_id) or {}
        if not locales:
            return "No tienes locales registrados."
        
        results = []
        
        # Iterar sobre locales del tendero
        for local_id, local_data in locales.items():
            local_name = local_data.get('nombre', local_id)
            
            if query_type == 'deudas':
                # Consultar clientes y sus deudas
                clientes = view_model.listar_clientes(local_id) or {}
                deudas_list = []
                for cid, cdata in clientes.items():
                    nombre = cdata.get('nombre', cdata.get('email', cid))
                    deuda = float(cdata.get('deuda', 0))
                    if deuda > 0:
                        deudas_list.append({'nombre': nombre, 'deuda': deuda, 'cliente_id': cid})
                
                # Ordenar por deuda descendente
                deudas_list.sort(key=lambda x: x['deuda'], reverse=True)
                
                if deudas_list:
                    results.append(f"🏪 {local_name}:")
                    for d in deudas_list:
                        results.append(f"  - {d['nombre']}: ${d['deuda']:.2f}")
                    total = sum(d['deuda'] for d in deudas_list)
                    results.append(f"  TOTAL DEUDA: ${total:.2f}")
            
            elif query_type == 'productos':
                # Consultar todos los productos
                productos = view_model.listar_productos(local_id) or {}
                if productos:
                    results.append(f"🏪 {local_name} - Productos:")
                    prods_list = []
                    for pid, pdata in productos.items():
                        prods_list.append({
                            'nombre': pdata.get('nombre', 'Sin nombre'),
                            'precio': float(pdata.get('precio', 0)),
                            'stock': int(pdata.get('stock', 0))
                        })
                    
                    # Ordenar por precio descendente
                    prods_list.sort(key=lambda x: x['precio'], reverse=True)
                    
                    for p in prods_list[:10]:  # Top 10
                        results.append(f"  - {p['nombre']}: ${p['precio']:.2f} (stock: {p['stock']})")
                    
                    if len(prods_list) > 10:
                        results.append(f"  ... y {len(prods_list) - 10} más")
            
            elif query_type == 'clientes':
                # Consultar clientes
                clientes = view_model.listar_clientes(local_id) or {}
                if clientes:
                    results.append(f"🏪 {local_name} - Clientes ({len(clientes)}):")
                    for cid, cdata in list(clientes.items())[:10]:
                        nombre = cdata.get('nombre', cdata.get('email', cid))
                        deuda = float(cdata.get('deuda', 0))
                        estado = f"Debe: ${deuda:.2f}" if deuda > 0 else "Al día"
                        results.append(f"  - {nombre}: {estado}")
                    
                    if len(clientes) > 10:
                        results.append(f"  ... y {len(clientes) - 10} más")
            
            elif query_type == 'stock':
                # Consultar productos con bajo stock
                productos = view_model.listar_productos(local_id) or {}
                bajo_stock = []
                for pid, pdata in productos.items():
                    stock = int(pdata.get('stock', 0))
                    if stock < 10:
                        bajo_stock.append({
                            'nombre': pdata.get('nombre', 'Sin nombre'),
                            'stock': stock,
                            'precio': float(pdata.get('precio', 0))
                        })
                
                bajo_stock.sort(key=lambda x: x['stock'])
                
                if bajo_stock:
                    results.append(f"🏪 {local_name} - Bajo Stock (<10 unidades):")
                    for p in bajo_stock:
                        results.append(f"  - {p['nombre']}: {p['stock']} unidades (${p['precio']:.2f})")
                else:
                    results.append(f"🏪 {local_name}: Todo el stock está bien.")
        
        return '\n'.join(results) if results else "No hay datos disponibles para esa consulta."
    
    except Exception as e:
        print(f"[FIREBASE QUERY] error: {e}")
        return f"Error al consultar Firebase: {str(e)}"


@app.route('/api/ai_chat', methods=['POST'])
def api_ai_chat():
    # Solo tendero puede usar el asistente
    if session.get('tipo_usuario') != 'tendero':
        return {'error': 'No autorizado'}, 401
    data = request.get_json(silent=True) or {}
    msg = (data.get('message') or '').strip()
    if not msg:
        return {'error': 'Mensaje vacío'}, 400
    
    # Construir contexto del negocio del tendero para la IA
    tendero_id = session.get('user')
    
    # Determinar tipo de consulta basado en palabras clave
    msg_lower = msg.lower()
    query_type = None
    
    if any(word in msg_lower for word in ['deuda', 'debo', 'debe', 'pago', 'abono', 'acreedor']):
        query_type = 'deudas'
    elif any(word in msg_lower for word in ['producto', 'precio', 'caro', 'barato', 'inventario', 'mercancía']):
        query_type = 'productos'
    elif any(word in msg_lower for word in ['cliente', 'comprador', 'usuario']):
        query_type = 'clientes'
    elif any(word in msg_lower for word in ['stock', 'cantidad', 'falta', 'poco', 'agotado']):
        query_type = 'stock'
    
    # Ejecutar consulta Firebase si se detectó tipo
    firebase_data = ""
    if query_type:
        firebase_data = _execute_firebase_query(tendero_id, query_type)
        print(f"[AI CHAT] Firebase query: {query_type}")
    
    # Construir mensaje para la IA con datos reales de Firebase
    full_message = f"""Eres un asistente de negocios para tenderos. Responde preguntas sobre sus tiendas, productos, clientes y deudas.

DATOS DE FIREBASE (actualizados en tiempo real):
{firebase_data}

Pregunta del usuario: {msg}

Responde de forma concisa, útil y en español. Si pregunta sobre datos específicos, utiliza los datos de Firebase que se proporcionaron arriba."""
    
    try:
        # Si hay una llave de QROQ configurada, proxear la petición a la API externa.
        # La llave debe estar en la variable de entorno QROQ_API_KEY.
        qroq_key = os.environ.get('QROQ_API_KEY')
        if qroq_key:
            # Preferir usar la librería "groq" si está instalada y soporta streaming
            try:
                from groq import Groq
                # Groq client puede leer la variable de entorno GROQ_API_KEY, así que la dejamos disponible
                os.environ.setdefault('GROQ_API_KEY', qroq_key)
                client = Groq()
                # Construir la conversación mínima
                completion = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role": "user", "content": full_message}],
                    temperature=1,
                    max_completion_tokens=1024,
                    top_p=1,
                    reasoning_effort="medium",
                    stream=True,
                    stop=None
                )
                # Si la API es de streaming, iteramos los chunks y los concatenamos
                reply_parts = []
                try:
                    for chunk in completion:
                        try:
                            delta = chunk.choices[0].delta
                            # delta puede tener 'content' o ser None
                            piece = getattr(delta, 'content', None) if hasattr(delta, '__dict__') else (delta.get('content') if isinstance(delta, dict) else None)
                            if piece:
                                reply_parts.append(piece)
                        except Exception:
                            # Ignorar pedazos malformados
                            continue
                except TypeError:
                    # Si completion no es iterable (no streaming), intentar obtener texto directamente
                    try:
                        text = getattr(completion, 'text', None) or getattr(completion, 'message', None) or str(completion)
                        if text:
                            reply_parts.append(text)
                    except Exception:
                        pass

                reply = ''.join(reply_parts).strip()
                if not reply:
                    reply = 'El proveedor external respondió sin contenido.'
                print('[AI PROXY] used groq client')
                return {'reply': reply}, 200
            except ImportError:
                print('[AI PROXY] groq library not installed, falling back to HTTP proxy')
            except Exception as e:
                print(f"[AI PROXY] groq error: {e}")

            # Fallback HTTP attempt (en caso groq no esté disponible)
            try:
                headers = {
                    'Authorization': f'Bearer {qroq_key}',
                    'Content-Type': 'application/json'
                }
                payload = {'input': msg}
                resp = requests.post('https://api.qroq.ai/v1/chat', json=payload, headers=headers, timeout=15)
                if resp.status_code >= 400:
                    print(f"[AI PROXY] provider error: {resp.status_code} {resp.text}")
                    return {'error': 'Error desde el proveedor de AI'}, 502
                data_resp = resp.json()
                # Extraer respuesta de forma robusta
                reply = None
                if isinstance(data_resp, dict):
                    reply = data_resp.get('reply') or data_resp.get('message')
                    if not reply:
                        choices = data_resp.get('choices') or data_resp.get('outputs')
                        if isinstance(choices, list) and len(choices) > 0:
                            first = choices[0]
                            if isinstance(first, dict):
                                reply = first.get('text') or first.get('message') or first.get('output')
                            else:
                                reply = str(first)
                    if not reply:
                        reply = data_resp.get('result')
                if not reply:
                    reply = str(data_resp)
                print('[AI PROXY] used http fallback')
                return {'reply': reply}, 200
            except requests.RequestException as re:
                print(f"[AI PROXY] request error: {re}")
            except Exception as e:
                print(f"[AI PROXY] unexpected error: {e}")

        # Si no hay llave o las llamadas al proveedor fallaron, usar motor local como fallback
        reply = _handle_finance_message(msg)
        return {'reply': reply}, 200
    except Exception as e:
        print(f'[ERROR] ai_chat: {e}')
        return {'error': str(e)}, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
