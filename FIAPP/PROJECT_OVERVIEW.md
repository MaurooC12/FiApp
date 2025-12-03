# Project Overview — FIAPP

Este archivo explica el propósito de las carpetas y archivos principales del proyecto, para que cualquier desarrollador pueda ubicarse rápidamente.

## Estructura general

- `app/`
  - `main.py` — Aplicación Flask: define las rutas web, sesiones, configuración de uploads, inicializa Firebase y contiene algunos helpers (ej. `save_upload_file`). Aquí se añadieron recientemente el endpoint `/api/ai_chat` y la lógica que inyecta proveedores en formularios.

- `database/`
  - `firebase_config.py` — Inicializa `firebase_admin` usando las variables de entorno (`FIREBASE_CREDENTIALS_PATH`, `FIREBASE_DB_URL`).
  - `auth_service.py` — Lógica de autenticación y gestión de usuarios. Contiene: registro, login, verificación de `user_id`, asignación de `tipo_usuario`.
  - `db_service.py` — Abstracción sobre la Realtime Database: CRUD para `locales`, `productos`, `clientes`, `proveedores`, y operaciones de deuda.

- `domain/`
  - Modelos de dominio: `cliente.py`, `local.py`, `producto.py`, `proveedor.py`, `tendero.py`, `usuario.py`. Cada archivo define la clase de dominio y `to_dict()/from_dict()` para serializar a Firebase.

- `presentation/`
  - `presentation.py` — Adaptadores entre los `ViewModel` y la capa de presentación (plantillas). Se usa para organizar la preparación de datos antes de renderizar.

- `ViewModel/`
  - `use_cases.py` — Implementación de casos de uso: crear producto, listar proveedores, crear local, etc. Aquí vive la lógica de negocio que coordina `DBService` y los modelos.
  - `user_manager.py` — Utilidades para administrar usuarios en pruebas o entorno local.

- `templates/`
  - Plantillas Jinja2 para las vistas HTML. Archivos importantes: `register.html`, `login.html`, `select_type.html`, `tendero_*` (dashboards, locales, inventario), `base.html`.
  - `base.html` contiene el `header`/`footer` global, ahora incluye el markup del chat (botón flotante y modal), y referencia a `static/script.js`.

- `static/`
  - `script.js` — Lógica cliente: validaciones (opcional), animaciones, y la lógica del chat IA (abrir modal, enviar a `/api/ai_chat`, renderizar respuestas).
  - `style.css` — Estilos globales, incluyendo estilos del chat modal y botón.
  - `productos/` — Carpeta donde se almacenan las imágenes subidas por los tenderos.
  - `lofofiapp.ico` — Icono (placeholder) usado para el botón del chat y favicon.

- `BACKEND_MANUAL.md` — Manual de uso y despliegue del backend (este archivo).
- `PROJECT_OVERVIEW.md` — Este archivo: visión general y propósito de cada pieza.
- `requirements.txt` — Dependencias del proyecto.

## Flujos importantes y dónde modificarlos

- Registro / Login
  - Lógica: `database/auth_service.py` y `app/main.py` (rutas `/register`, `/login`, `/select-type`).
  - Validaciones de frontend: `static/script.js` (activable con `window.FIAPP_ENABLE_CUSTOM_VALIDATION`).

- Crear producto
  - Formulario: `templates/tendero_create_producto.html`.
  - Backend: `app/main.py` (ruta que gestiona `POST` y llama a `view_model.crear_producto`) y `database/db_service.py` (persistencia).
  - Imágenes: `save_upload_file()` en `app/main.py` guarda en `static/productos/` y devuelve `imagen_url`.

- Proveedores
  - Model: `domain/proveedor.py`.
  - Persistencia: `database/db_service.py` (métodos CRUD para proveedores).
  - API y vistas: rutas en `app/main.py` (`/tendero/proveedores`, `/api/proveedores`) y plantillas `tendero_proveedores.html`, `tendero_create_proveedor.html`.
  - Scope: cada proveedor contiene `propietario_id` para filtrar por tendero.

- Chat IA (ayuda de cuentas)
  - Frontend: `static/script.js` (abre modal, captura mensajes, hace POST a `/api/ai_chat`).
  - Estilos: `static/style.css`.
  - Backend: `app/main.py` — endpoint `/api/ai_chat` que procesa mensajes con un motor local heurístico y un evaluador aritmético seguro. Restringido a `tipo_usuario == 'tendero'`.

## Notas para desarrolladores

- Seguridad: nunca comprometer el JSON de Service Account. En producción separar la configuración y usar variables de entorno.
- Extensibilidad:
  - Para mejorar el asistente IA: integrar con un servicio externo (OpenAI). Añadir variables de entorno `OPENAI_API_KEY` y modularizar `app/main.py` para delegar al cliente OpenAI.
  - Para exponer APIs REST completas: crear rutas `api/*` que serialicen las entidades y permitan token-based auth.

## Cómo empezar a contribuir

1. Clona el repositorio y crea una rama nueva:

```bash
git checkout -b feat/mi-cambio
```

2. Instala dependencias y configura tus variables de entorno locales.
3. Ejecuta la app y prueba los flujos desde el navegador.
4. Añade tests en un directorio `tests/` si vas a tocar lógica crítica.

---

Si quieres, puedo generar una versión en `README.md` con un resumen y enlaces rápidos a estas secciones, o añadir más archivos de ayuda (ej. `DEV_SETUP.md` con pasos para VSCode, linters y testing).
