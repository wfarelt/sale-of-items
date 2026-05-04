# 🏬 Sistema de Venta de Artículos - Django

Proyecto Django configurado con control de acceso por roles utilizando SQLite3 y Bootstrap 5.

## 📦 Características

- ✅ **Proyecto Django 4.2** completamente configurado
- ✅ **Base de datos SQLite3** (predeterminada)
- ✅ **Bootstrap 5** integrado en plantillas
- ✅ **Sistema de Roles**: Admin, Vendedor, Almacén
- ✅ **Módulo de Usuarios** con modelo User extendido
- ✅ **Panel de Administración** personalizado
- ✅ **Crispy Forms** para formularios Bootstrap

## 🔐 Módulo de Usuarios

### Modelos

####  `Role`
Define los roles del sistema con permisos específicos:
- **Admin**: Acceso total al sistema
- **Vendedor**: Gestiona ventas y clientes
- **Almacén**: Gestiona inventario y almacén

Campos:
- `name`: Nombre del rol (único)
- `description`: Descripción del rol
- `created_at`: Fecha de creación

#### `User` (Extendido de AbstractUser)
Modelo de usuario personalizado que extiende el User de Django.

Campos clave:
- `username`: Nombre de usuario (único)
- `password`: Contraseña encriptada
- `email`: Correo electrónico
- `role`: ForeignKey a Role (requerido)
- `is_active`: Estado del usuario (activo/inactivo)
- `first_name`: Nombre
- `last_name`: Apellido
- `phone`: Teléfono (opcional)
- `address`: Dirección (opcional)
- `avatar`: Imagen de perfil (opcional)
- `created_at`: Fecha de creación
- `updated_at`: Fecha de última actualización

## 🚀 Instalación y Configuración

### Requisitos previos
- Python 3.12+
- pip

### 1. Activar entorno virtual

#### En Windows:
```bash
.venv\Scripts\activate
```

#### En Linux/Mac:
```bash
source venv/bin/activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Aplicar migraciones
```bash
python manage.py migrate
```

### 4. Crear datos iniciales (Roles y Usuarios de prueba)
```bash
python bootstrap_project.py
```

### 5. Iniciar servidor de desarrollo
```bash
python manage.py runserver
```

Accede a: http://localhost:8000/

## 🔑 Credenciales de Prueba

Despues de ejecutar `bootstrap_project.py`:

| Usuario | Contraseña | Rol | Acceso |
|---------|-----------|-----|--------|
| `admin` | `admin123` | Administrador | [Panel admin](/admin/) |
| `vendedor` | `vendedor123` | Vendedor | [Panel admin](/admin/) |
| `almacen` | `almacen123` | Almacén | [Panel admin](/admin/) |

## 📁 Estructura del Proyecto

```
sale-of-items/
├── config/                 # Configuración del proyecto
│   ├── settings.py        # Configuraciones (BASE_DIR, APPS, TEMPLATES, etc.)
│   ├── urls.py            # URLs principales
│   ├── wsgi.py            # WSGI configuration
│   └── asgi.py            # ASGI configuration
├── usuarios/              # App de usuarios
│   ├── migrations/        # Migraciones de BD
│   ├── admin.py           # Admin personalizado
│   ├── apps.py            # Configuración de app
│   ├── models.py          # Modelos (User, Role)
│   ├── views.py           # Vistas
│   ├── urls.py            # URLs de la app
│   └── forms.py           # Formularios
├── templates/             # Plantillas HTML
│   └── base.html          # Plantilla base con Bootstrap
├── static/                # Archivos estáticos (CSS, JS, IMG)
├── media/                 # Archivos subidos (avatares, etc.)
├── bootstrap_project.py   # Script para crear datos iniciales
├── manage.py              # Gestor de Django
├── requirements.txt       # Dependencias del proyecto
└── db.sqlite3            # Base de datos SQLite3
```

## 🛠️ Dependencias Instaladas

```
Django==4.2
django-crispy-forms
crispy-bootstrap5
Pillow  (para manejo de imágenes)
```

## 📝 Configuración en settings.py

### Apps instaladas
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'usuarios',
]
```

### Modelo de Usuario personalizado
```python
AUTH_USER_MODEL = 'usuarios.User'
```

### Configuración de Crispy Forms
```python
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
```

### Base de datos SQLite3
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Idioma y zona horaria
```python
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Bogota'
```

## 🔓 Panel de Administración

El panel de administración está completamente personalizado:

### Vista de Roles
- Lista de roles disponibles
- Filtrado por fecha de creación
- Búsqueda por nombre y descripción

### Vista de Usuarios
- Lista de todos los usuarios
- Filtrado por rol, estado activo y fecha
- Búsqueda avanzada por username, email, nombre y apellido
- Visualización de información adicional (teléfono, dirección, avatar)

Acceso: http://localhost:8000/admin/

## 📚 Próximos pasos

Para continuar con el desarrollo:

1. **Crear más apps** según sea necesario (productos, ventas, etc.)
2. **Desarrollar vistas** y lógica de negocio
3. **Crear formularios** con Crispy Forms para cada modelo
4. **Implementar permisos** basados en roles
5. **Crear API REST** (opcional, con Django REST Framework)

## 🐛 Solución de problemas

### Error: "Cannot use ImageField because Pillow is not installed"
```bash
pip install Pillow
```

### Error: "No such file or directory: 'db.sqlite3'"
```bash
python manage.py migrate
```

### Permisos denegados en Linux/Mac
```bash
chmod +x manage.py
```

## 📞 Soporte

Para más información sobre Django:
- [Documentación oficial Django](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Bootstrap 5](https://getbootstrap.com/)

---

**Versión**: 1.0  
**Última actualización**: Abril 2026
