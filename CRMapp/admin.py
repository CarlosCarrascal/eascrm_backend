from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .admin.cliente import ClienteAdmin
from .admin.producto import ProductoAdmin
from .admin.pedido import PedidoAdmin, DetallePedidoInline
from .admin.site import AdminSite
from .models import Cliente, Producto, Pedido

# Crear instancia personalizada del sitio admin
admin_site = AdminSite(name='admin')
admin_site.register(User, UserAdmin)
admin_site.register(Cliente, ClienteAdmin)
admin_site.register(Producto, ProductoAdmin)
admin_site.register(Pedido, PedidoAdmin)

# Personalizar el panel de administración
admin_site.site_header = 'EasyCRM - Panel de Administración'
admin_site.site_title = 'EasyCRM Admin'
admin_site.site_index_title = 'Panel de Control'

# Para mantener compatibilidad con el admin original
admin.site.site_header = 'EasyCRM - Panel de Administración'
admin.site.site_title = 'EasyCRM Admin'
admin.site.index_title = 'Panel de Control'

# Registrar modelos en el admin estándar
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Pedido, PedidoAdmin)
