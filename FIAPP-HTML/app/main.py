from flask import Flask, request, render_template, redirect, url_for, session
import os
import time
from database.firebase_config import init_firebase
from database.auth_service import AuthService
from presentation.presentation import ViewModel


app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = "dev-secret-fiapp-2025"

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
    return render_template("tendero_inventario.html", local_id=local_id, productos=productos)


@app.route("/tendero/locales/<local_id>/clientes")
def tendero_clientes(local_id):
    """Tendero: ve clientes de una tienda y gestiona sus deudas."""
    if session.get("tipo_usuario") != "tendero":
        return redirect(url_for("login"))
    clientes = view_model.listar_clientes(local_id)
    return render_template("tendero_clientes.html", local_id=local_id, clientes=clientes)


@app.route("/cliente/deudas")
def cliente_deudas():
    """Cliente: ve todas sus deudas."""
    if session.get("tipo_usuario") != "cliente":
        return redirect(url_for("login"))
    cliente_id = session.get("user")
    deudas = view_model.get_deudas_cliente(cliente_id)
    return render_template("cliente_deudas.html", deudas=deudas)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
