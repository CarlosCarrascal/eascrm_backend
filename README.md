# EasyCRM - Sistema de Gestión de Relaciones con Clientes

EasyCRM es un sistema de gestión de relaciones con clientes desarrollado con Django que permite administrar clientes, productos y pedidos de manera eficiente.

## Características

- Panel de administración personalizado con diseño moderno y responsivo
- Gestión completa de clientes con datos de contacto e historial de pedidos
- Catálogo de productos con imágenes, descripciones y control de inventario
- Sistema de pedidos con múltiples productos por pedido
- Dashboard con estadísticas y gráficos
- API RESTful para integración con otras aplicaciones

## Estructura del Proyecto

```
easycrm_project/
├── CRMapp/                    # Aplicación principal
│   ├── migrations/            # Migraciones de la base de datos
│   ├── admin.py               # Configuración del panel de administración
│   ├── api_views.py           # Vistas para la API REST
│   ├── apps.py                # Configuración de la aplicación
│   ├── models.py              # Modelos de datos
│   ├── serializers.py         # Serializadores para la API
│   ├── tests.py               # Pruebas unitarias
│   ├── urls.py                # Configuración de URLs
│   └── views.py               # Vistas de la aplicación
├── easycrm_project/           # Configuración del proyecto
│   ├── settings.py            # Configuración general
│   ├── urls.py                # URLs principales
│   ├── wsgi.py                # Configuración WSGI
│   └── asgi.py                # Configuración ASGI
├── media/                     # Archivos subidos por los usuarios
│   ├── clientes/              # Fotos de clientes
│   └── productos/             # Imágenes de productos
├── static/                    # Archivos estáticos
│   ├── admin/                 # Archivos específicos para el admin
│   │   ├── css/               # Estilos CSS para el admin
│   │   │   ├── base.css       # Estilos generales del admin
│   │   │   ├── detail.css     # Estilos para vistas de detalle
│   │   │   ├── dashboard.css  # Estilos para el dashboard
│   │   │   └── jazzmin.css    # Estilos para Jazzmin
│   │   ├── js/                # JavaScript para el admin
│   │   │   ├── dashboard.js   # Scripts para el dashboard
│   │   │   ├── tooltips.js    # Scripts para tooltips
│   │   │   ├── jazzmin.js     # Scripts para Jazzmin
│   │   │   └── pedidos.js     # Scripts específicos para pedidos
│   │   └── img/               # Imágenes para el admin
│   └── common/                # Archivos compartidos
│       ├── css/               # Estilos CSS comunes
│       ├── js/                # JavaScript común
│       └── img/               # Imágenes comunes
├── templates/                 # Plantillas HTML
│   └── admin/                 # Plantillas para el admin
│       ├── base_site.html     # Plantilla base del admin
│       ├── index.html         # Plantilla del dashboard
│       └── CRMapp/            # Plantillas específicas de la app
│           ├── cliente/       # Plantillas para clientes
│           ├── producto/      # Plantillas para productos
│           └── pedido/        # Plantillas para pedidos
├── manage.py                  # Script de gestión de Django
└── requirements.txt           # Dependencias del proyecto
```

## Modelos de Datos

### Cliente
- nombre: Nombre completo del cliente
- email: Correo electrónico (único)
- direccion: Dirección postal
- foto: Imagen de perfil (opcional)
- fecha_registro: Fecha de registro automática

### Producto
- nombre: Nombre del producto
- descripcion: Descripción detallada
- precio: Precio unitario
- imagen: Imagen del producto (opcional)
- stock: Cantidad disponible en inventario

### Pedido
- cliente: Relación con Cliente
- fecha: Fecha de creación
- estado: Estado del pedido (pendiente, en_proceso, completado, cancelado)
- fecha_actualizacion: Última actualización

### DetallePedido
- pedido: Relación con Pedido
- producto: Relación con Producto
- cantidad: Cantidad de unidades
- precio_unitario: Precio al momento de la compra

## Instalación

1. Clonar el repositorio
2. Crear un entorno virtual: `python -m venv venv`
3. Activar el entorno virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Instalar dependencias: `pip install -r requirements.txt`
5. Configurar la base de datos en `settings.py`
6. Aplicar migraciones: `python manage.py migrate`
7. Crear superusuario: `python manage.py createsuperuser`
8. Iniciar el servidor: `python manage.py runserver`

## API REST

La API REST proporciona endpoints para:

- `/api/clientes/`: CRUD de clientes
- `/api/productos/`: CRUD de productos
- `/api/pedidos/`: CRUD de pedidos
- `/api/token/`: Obtener token JWT
- `/api/token/refresh/`: Refrescar token JWT

## Licencia

Este proyecto está bajo la Licencia MIT. 