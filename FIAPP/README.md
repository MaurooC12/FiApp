# FiApp

Este directorio contiene el código fuente completo de la aplicación FiApp.

## 📸 Verificación de Estructura
Para que el sistema funcione correctamente y evitar errores de importación (como `ModuleNotFoundError`), tu estructura de carpetas debe verse **exactamente** así antes de ejecutar el servidor:

<img width="242" height="613" alt="image" src="https://github.com/user-attachments/assets/272493fb-31f2-4988-a7b0-bd0bf2afb70b" />


> **Nota:** Es vital ejecutar el proyecto desde la carpeta superior a esta, o usando `python -m app.main` estando en la raíz de `FIAPP`.

## Estructura del Código

El proyecto sigue una arquitectura modular organizada de la siguiente manera:

* **`app/`**: Configuración principal del servidor Flask y rutas base.
* **`database/`**: Conexión con Firebase (`firebase_config.py`), servicios de autenticación y operaciones CRUD.
* **`domain/`**: Definiciones de entidades y lógica de negocio pura.
* **`presentation/`**: Manejo de rutas y controladores web.
* **`ViewModel/`**: Intermediarios que procesan datos entre la base de datos y la vista.
* **`static/`**: Archivos públicos (CSS, JavaScript del Chatbot `script.js`, imágenes de productos).
* **`templates/`**: Vistas HTML (Jinja2) para el frontend.
* **`requirements.txt`**: Lista de dependencias necesarias para instalar con `pip`.
