# Sistema de Venta de Articulos

Sistema de gestion de ventas e inventario desarrollado con Django 6.0.4, con control de acceso por roles y soporte multiempresa.

## Descripcion

Aplicacion web para administrar productos, clientes, ventas, compras, movimientos de inventario y caja. Incluye flujo de ventas optimizado con busqueda de clientes y creacion rapida desde el mismo formulario.

## Modulos

- usuarios: gestion de usuarios y roles (admin, vendedor, almacen)
- empresas: configuracion de empresa y datos operativos
- clientes: administracion de clientes
- productos: catalogo, marcas, categorias y stock
- ventas: registro de proformas y ventas confirmadas
- compras: gestion de compras a proveedores
- movimientos: kardex y trazabilidad de inventario
- caja: control de caja diaria y movimientos monetarios

## Requisitos

- Python 3.12+
- Django 6.0.4
- pip
- SQLite3 (incluida por defecto)

## Inicio rapido

1. Activar entorno virtual

Windows:

```powershell
.venv\Scripts\activate
```

Linux/Mac:

```bash
source .venv/bin/activate
```

2. Instalar dependencias

```bash
pip install -r requirements.txt
```

3. Inicializar datos base

```bash
python bootstrap_project.py
```

4. Ejecutar servidor

```bash
python manage.py runserver
```

Acceso:

- App: http://localhost:8000
- Admin: http://localhost:8000/admin

## Comandos utiles

- Crear migraciones: `python manage.py makemigrations`
- Aplicar migraciones: `python manage.py migrate`
- Crear superusuario: `python manage.py createsuperuser`
- Shell Django: `python manage.py shell`
- Recolectar estaticos: `python manage.py collectstatic`

## Configuracion de entorno

Este proyecto requiere archivos de entorno para iniciar:

- `.env.development`
- `.env.production`

Puedes copiar la base desde `.env.example` y ajustar valores segun tu entorno.

## Usuarios demo

- superadmin / superadmin123
- admin / admin123
- vendedor / vendedor123
- almacen / almacen123

## Licencia

Este proyecto se distribuye bajo Unlicense. Revisa LICENSE para mas detalles.
