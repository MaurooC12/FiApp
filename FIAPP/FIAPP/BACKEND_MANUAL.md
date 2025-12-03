# Manual de Usuario — Backend FIAPP

Este manual describe cómo instalar, configurar, operar y depurar el backend de FIAPP (Flask + Firebase Realtime Database).

**Resumen rápido**
- El backend es una aplicación Flask que usa Firebase Realtime Database a través de `firebase_admin`.
- Archivos clave: `app/main.py`, `database/firebase_config.py`, `database/auth_service.py`, `database/db_service.py`, `ViewModel/use_cases.py`.

**Requisitos**
- Python 3.8+
- Paquetes (ver `requirements.txt`): `Flask`, `firebase-admin`, `python-dotenv`, `requests`.

**Instalación**
- Clona o abre el repositorio y sitúate en la carpeta `FIAPP`.
- Instala dependencias:

```powershell
python -m pip install -r requirements.txt
```

**Variables de entorno necesarias**
- `FIREBASE_CREDENTIALS_PATH`: ruta absoluta al JSON de la Service Account (no subirlo a VCS).
- `FIREBASE_DB_URL`: URL de tu Realtime Database (ej: `https://fiapp-17341-default-rtdb.firebaseio.com`).
- `USE_LOCAL_AUTH`: `true` para evitar llamadas a Firebase (uso local/debug), `false` para usar Realtime DB.
- (Opcional) `FLASK_ENV=production` en despliegue.

```markdown
# Manual de Usuario — Backend FIAPP (versión actualizada)

Este manual describe cómo instalar, configurar, operar y depurar el backend de FIAPP (Flask + Firebase Realtime Database). Incluye las actualizaciones recientes: manejo de imágenes, proveedores con propietario y un asistente de chat IA orientado a cálculos.

**Resumen rápido**
- El backend es una aplicación Flask que usa Firebase Realtime Database a través de `firebase_admin`.
- Archivos clave: `app/main.py`, `database/firebase_config.py`, `database/auth_service.py`, `database/db_service.py`, `ViewModel/use_cases.py`, `static/script.js`, `static/style.css`.

**Requisitos**
- Python 3.8+
- Paquetes (ver `requirements.txt`): `Flask`, `firebase-admin`, `python-dotenv`, `requests`.

**Instalación**
- Clona o abre el repositorio y sitúate en la carpeta `FIAPP`.
- Instala dependencias:

```powershell
python -m pip install -r requirements.txt
```

**Variables de entorno necesarias**
- `FIREBASE_CREDENTIALS_PATH`: ruta absoluta al JSON de la Service Account (no subirlo a VCS).
- `FIREBASE_DB_URL`: URL de tu Realtime Database (ej: `https://fiapp-17341-default-rtdb.firebaseio.com`).
- `USE_LOCAL_AUTH`: `true` para evitar llamadas a Firebase (uso local/debug), `false` para usar Realtime DB.
- (Opcional) `FLASK_ENV=production` en despliegue.

Ejemplo (PowerShell):

```powershell
$Env:FIREBASE_CREDENTIALS_PATH = 'C:\ruta\a\fiapp-17341-firebase-adminsdk.json'
$Env:FIREBASE_DB_URL = 'https://fiapp-17341-default-rtdb.firebaseio.com'
$Env:USE_LOCAL_AUTH = 'false'
```

**Inicialización de Firebase**
- Archivo: `database/firebase_config.py`.
- Función `init_firebase()` lee `FIREBASE_CREDENTIALS_PATH` y `FIREBASE_DB_URL` (usa `python-dotenv` si existe `.env`).
- Llamada inicial: `init_firebase()` (ya invocado en `app/main.py`).

**Estructura del proyecto (resumen)**
- `app/main.py`: servidor Flask, rutas principales y control de sesiones.
- `database/firebase_config.py`: inicialización de Firebase.
- `database/auth_service.py`: lógica de registro/login, hashing de contraseñas y asignación de `tipo_usuario`.
- `database/db_service.py`: operaciones CRUD en Realtime Database (locales, productos, clientes, deudas).
- `ViewModel/use_cases.py`: casos de uso que combinan la lógica de negocio y `DBService`.
- `ViewModel/user_manager.py`: adaptador para administración de usuarios.
- `templates/`: vistas HTML (registro, login, select_type, dashboards, etc.).
- `static/`: archivos estáticos, incluido `script.js` y `style.css` (ahora contienen la lógica y estilos del chat y del UI moderno).

**Modelos y datos importantes**
- Usuario almacenado en Realtime DB bajo `usuarios/{email_key}` donde `email_key = MD5(email.lower())`.
  - Campos: `email`, `password_hash`, `user_id`, `tipo_usuario` (null hasta asignación).
- Locales: `locales/{local_id}`
  - Estructura típica:
    ```json
    locales: {
      "local_{userId}_{timestamp}": {
        "nombre": "Mi Tienda",
        "propietario_id": "jhose9282",
        "productos": { ... },
        "clientes": { ... }
      }
    }
    ```
- Productos: `locales/{local_id}/productos/{producto_id}` con campos `nombre`, `precio`, `stock`, opcional `proveedor`, y `imagen_url` (ruta relativa dentro de `static/productos/`).
- Clientes en local: `locales/{local_id}/clientes/{cliente_id}` con `deuda` (acumulado) y `deudas/{timestamp}` listado detallado.
- Proveedores: `proveedores/{proveedor_id}` con campos `nombre`, `contacto`, `email`, y `propietario_id` para scoping por tendero.

**Servicios clave**
- `AuthService` (`database/auth_service.py`):
  - `register_user(email, password, user_id)` → crea usuario (sin `tipo_usuario`).
  - `login_user(email, password)` → retorna `(user_id, tipo_usuario)`.
  - `set_user_type(email, tipo_usuario)` → asigna `tendero` o `cliente`.
  - `get_user_by_email(email)`, `list_users()`, `delete_user(email)`.

- `DBService` (`database/db_service.py`):
  - `add_local(local_id, local_data)`, `get_local(local_id)`, `update_local(local_id, data)`, `delete_local(local_id)`.
  - `add_producto(local_id, producto_data, producto_id)`, `get_productos(local_id)`, `update_producto`, `delete_producto`.
  - `add_cliente_a_local(local_id, cliente_id, cliente_data)`, `get_clientes(local_id)`, `get_cliente(local_id, cliente_id)`.
  - `registrar_deuda(local_id, cliente_id, monto, plazo_dias=None)` → actualiza total y añade registro timestamp.
  - `proveedores`: CRUD y soporte para `propietario_id` (ver `database/db_service.py` y `ViewModel/use_cases.py`).

**Rutas HTTP principales (resumen)**
- `GET /` — Página principal.
- `GET, POST /register` — Registro de usuario (form: `email`, `password`, `password_confirm`, `user_id`).
  - Flujo: crea usuario y redirige a `/select-type`.
- `GET, POST /login` — Login (form: `email`, `password`).
  - Si `tipo_usuario` no asignado → redirige a `/select-type`.
- `GET, POST /select-type` — Selección post-registro (`tipo_usuario` = `tendero`|`cliente`).
- `GET /dashboard` — Redirige a panel según `tipo_usuario`.

Rutas Tendero (prefijo `/tendero`):
- `GET /tendero/locales` — Lista locales del tendero.
- `GET, POST /tendero/locales/create` — Crear tienda (form: `nombre`).
- `GET /tendero/locales/<local_id>/inventario` — Ver productos.
- `GET /tendero/locales/<local_id>/clientes` — Ver clientes y sus deudas.
- `GET /tendero/locales/<local_id>/productos/create` — Formulario de crear producto (recibe `proveedores` del tendero para seleccionar opcionalmente).

Rutas adicionales:
- `GET /tendero/proveedores` — Lista proveedores del tendero actual.
- `GET, POST /tendero/proveedores/create` — Crear proveedor (propietario asignado automáticamente desde sesión).
- `POST /tendero/proveedores/<proveedor_id>/delete` — Eliminar proveedor.
- `GET /api/proveedores` — API JSON que devuelve proveedores filtrados por propietario (usa la cookie de sesión).
- `POST /api/ai_chat` — API simple del asistente IA orientado a cálculos financieros. Está restringida a usuarios con `tipo_usuario == 'tendero'` en sesión y acepta JSON: `{ "message": "tu pregunta" }`. Responde `{ "reply": "texto" }`.

**Ejemplos de uso (comandos)**
- Ejecutar el servidor (modo desarrollo):

```powershell
python -m app.main
```

- Registrar (desde formulario web): visita `http://127.0.0.1:5000/register`.

- Asignar tipo mediante POST (ejemplo curl):

```bash
curl -X POST -d "tipo_usuario=tendero" -c cookies.txt -b cookies.txt http://127.0.0.1:5000/select-type
```
(Usa `-c` y `-b` para guardar/cargar cookies de sesión si haces llamadas desde CLI.)

- Crear tienda (desde formulario web en `/tendero/locales/create`). Ejemplo JSON teórico usando la API interna (no expuesta como JSON API por defecto):

```python
# Usando ViewModel desde Python (ejemplo local)
from ViewModel.use_cases import UseCases
uc = UseCases()
uc.crear_local('Mi tienda', 'jhose9282', 'local_jhose9282_1610000000')
```

**Probar el asistente IA (chat)**

1. Arranca el servidor (modo desarrollo):

```powershell
python -m app.main
```

2. En el navegador: inicia sesión con un usuario `tendero` (o registra y asigna el tipo en `/select-type`).

3. En cualquier página verás (para tenderos) un botón circular en la esquina inferior derecha con el icono `lofofiapp.ico`. Haz clic para abrir el chat.

4. Envía peticiones de ejemplo:
- `3 unidades a 12.50` → multiplicación y total.
- `12.5*3+2` → evaluación aritmética segura.
- `10% de 250` → cálculo de porcentaje.

5. Internamente la ruta es `POST /api/ai_chat` y espera JSON `{ "message": "..." }`.

Nota: la implementación actual usa un motor local heurístico y un evaluador aritmético seguro (sin llamadas externas). Si quieres respuestas más conversacionales, se puede integrar OpenAI u otro servicio (requiere clave y dependencias adicionales).

**Estructura esperada en Realtime DB (ejemplo)**
```json
{
  "usuarios": {
    "<md5_email>": {
      "email": "jhose@example.com",
      "password_hash": "...",
      "user_id": "jhose9282",
      "tipo_usuario": "tendero"
    }
  },
  "locales": {
    "local_jhose9282_1610000000": {
      "nombre": "La Esquina",
      "propietario_id": "jhose9282",
      "productos": {
        "p1": {"nombre":"Arroz","precio":8200,"stock":10, "imagen_url":"/static/productos/archivo.jpg"}
      },
      "clientes": {
        "cliente123": {"nombre":"Ana","deuda":15000, "deudas":{...}}
      }
    }
  },
  "proveedores": {
    "prov_...": {"nombre":"Proveedor A","contacto":"123","email":"a@prov.com","propietario_id":"tendero123"}
  }
}
```

**Pruebas y diagnósticos**
- Archivos de prueba incluidos:
  - `tmp_reptest.py`: intenta crear un usuario con `firebase_admin.auth.create_user` (útil para verificar permisos).
  - `tmp_diagnose_jwt.py`: verifica que el `private_key` existe y ejecuta `creds.refresh()` para reproducir errores `invalid_grant`.

- Errores comunes y soluciones:
  - `ValueError: Invalid certificate argument: "None"` → `FIREBASE_CREDENTIALS_PATH` no definido o apunta a ruta inexistente.
  - `invalid_grant: Invalid JWT Signature.` → frecuentemente reloj del sistema desincronizado. Solución:
    - Ejecutar `w32tm /resync` en PowerShell (ventana elevada) o Sync desde Settings → Time & language → Sync now.
    - Generar una nueva clave privada desde Firebase Console si el problema persiste.
  - `Invalid path: "//locales/..." Path contains illegal characters.` → no usar el `email` (contiene `@` y `.`) como clave. Use `user_id` limpio o un hash/slug para `local_id` (la app ahora genera `local_{user_id}_{timestamp}`).
  - `Chat no aparece` → el botón del chat se muestra sólo cuando el usuario tiene `tipo_usuario = tendero`. Si inicias sesión y no ves el botón:
    1. Confirma que tu sesión tiene `tipo_usuario` configurado (revisa `/select-type`).
    2. Abre la consola del navegador (F12) y busca el log: `FIAPP chat init, role=` y `chatButtonExists=`. Si no aparece, recarga con Ctrl+F5.
    3. Asegúrate de que `static/script.js` está cargado (ver en Network).

**Buenas prácticas y seguridad**
- Nunca subir el JSON de Service Account al repositorio.
- Configurar reglas de Realtime Database en Firebase Console para restringir lectura/escritura.
- Usar HTTPS y servidor WSGI (uWSGI/Gunicorn + reverse proxy) en producción.
- Rotar la `service account` si sospechas un compromiso.
- Cambiar `app.secret_key` por una variable de entorno segura en producción.

**Despliegue (recomendado)**
- Coloca las variables de entorno en el entorno del servidor (no en `.env` commit).
- Ejecuta la app detrás de un WSGI server y proxy (Nginx + Gunicorn). Ejemplo (Linux):

```bash
# instalar dependencias en virtualenv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# luego usar gunicorn
gunicorn -w 3 -b 127.0.0.1:8000 app.main:app
```

**Checklist antes de poner en producción**
- [ ] `FIREBASE_CREDENTIALS_PATH` apuntando al JSON correcto en servidor.
- [ ] `FIREBASE_DB_URL` correcto.
- [ ] `app.secret_key` seguro (variable de entorno).
- [ ] Reglas de seguridad en Realtime Database ajustadas.
- [ ] HTTPS configurado.

---

Si quieres, puedo:
- Añadir este manual también dentro del `README.md` o vincularlo.
- Generar ejemplos `curl` y tests unitarios para endpoints específicos.
- Implementar formularios faltantes (crear producto, registrar abono) y APIs JSON REST.

Fin del Manual — FIAPP Backend
```
