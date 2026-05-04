# ⚡ Guía Rápida de Inicio

## 🚀 Iniciar el servidor de desarrollo

### Paso 1: Activar entorno virtual

**Windows:**
```powershell
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Paso 2: Preparar base de datos y datos base
```bash
python manage.py migrate
python bootstrap_project.py
```

### Paso 3: Iniciar servidor Django
```bash
python manage.py runserver
```

O especificar puerto:
```bash
python manage.py runserver 0.0.0.0:8000
```

### Paso 4: Acceder a la aplicación

**Panel Admin:**
- URL: [http://localhost:8000/admin/](http://localhost:8000/admin/)
- Usuario: `admin`
- Contraseña: `admin123`

**Aplicación:**
- URL: [http://localhost:8000](http://localhost:8000)

## 👥 Usuarios disponibles

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| admin | admin123 | Administrador |
| vendedor | vendedor123 | Vendedor |
| almacen | almacen123 | Almacén |

## 📝 Comandos útiles

### Crear migraciones
```bash
python manage.py makemigrations
```

### Aplicar migraciones
```bash
python manage.py migrate
```

### Crear nuevo superusuario
```bash
python manage.py createsuperuser
```

### Shell interactivo de Django
```bash
python manage.py shell
```

### Recolectar archivos estáticos
```bash
python manage.py collectstatic
```

### Ver URL patterns
```bash
python manage.py show_urls
```

## 📦 Instalar más dependencias

```bash
pip install nombre-del-paquete
pip freeze > requirements.txt  # Actualizar requirements.txt
```

## 🛑 Detener el servidor

Presiona `Ctrl + C` en la terminal

## 📂 Estructura de archivos importante

- `config/settings.py` - Configuración del proyecto
- `config/urls.py` - URLs principales
- `usuarios/models.py` - Modelos de usuarios y roles
- `usuarios/admin.py` - Configuración del admin
- `templates/base.html` - Plantilla base con Bootstrap
- `db.sqlite3` - Base de datos

## 🔗 Documentación

- [Django Documentation](https://docs.djangoproject.com/)
- [Bootstrap 5](https://getbootstrap.com/docs/5.0/)
- [Crispy Forms](https://django-crispy-forms.readthedocs.io/)

---

¡Listo para desarrollar! 🎉
