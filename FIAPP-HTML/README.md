# FIAPP - Migrado a Flask

Instrucciones rápidas para ejecutar la interfaz web (Flask) localmente (Windows PowerShell):

- Abre PowerShell en la carpeta del proyecto (donde está `requirements.txt`).
- Instala dependencias:

```powershell
python -m pip install -r requirements.txt
```

- Establece las variables de entorno para Firebase (usa la ruta real de tu JSON). Ejemplo:

```powershell
$Env:FIREBASE_CREDENTIALS_PATH = 'C:\Users\Jhose\OneDrive\Documentos\UNAL\SEMESTRES\PRIMER SEMESTRE\POO\fiappp\FIAPP\fiappp-17341-firebase-adminsdk-fbsvc-a811628f3e.json'
$Env:FIREBASE_DB_URL = 'https://<tu-project>.firebaseio.com'

- (Opcional) Control de autenticación local vs Realtime Database:

```powershell
# Para usar la Realtime Database (recomendado en integración):
$Env:USE_LOCAL_AUTH = 'false'

# Para desarrollo rápido y evitar llamadas a la red, usa la base local (archivo JSON):
$Env:USE_LOCAL_AUTH = 'true'
```
```

- Ejecuta la aplicación web:

```powershell
python -m app.main
```

- Abre en tu navegador `http://127.0.0.1:5000/`.

Uso de la UI web:
- `GET /` — página principal.
- `GET,POST /login` — iniciar sesión con tu `UID` de Firebase (sin contraseña en esta versión).
- Tras iniciar sesión, accederás al `dashboard` que muestra opciones según el rol (`admin` o `tendero`).

- `Admin`:
  - `GET /admin/users` — listar usuarios.
  - `GET,POST /admin/create_user` — formulario para crear usuarios.

- `Tendero`:
  - `GET /locales` — listar locales.
  - `GET /locales/<local_id>/productos` — ver productos de un local.
  - `GET,POST /locales/<local_id>/productos/create` — crear producto mediante formulario.

Notas:
- La app web usa `presentation.ViewModel` y los `UseCases` adaptados para devolver datos en lugar de imprimir.
- La sesión se mantiene en cookies de Flask (variable `session`) y se usa una `secret_key` de desarrollo; cambia en producción.
- Todavía hay APIs JSON en el proyecto original, pero la UI principal ahora es HTML.
