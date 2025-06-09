from django.contrib import admin
from .cliente import ClienteAdmin
from .producto import ProductoAdmin
from .pedido import PedidoAdmin, DetallePedidoInline
from ..models import Cliente, Producto, Pedido

# Registrar modelos en el admin estándar
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Pedido, PedidoAdmin)

# Personalizar el panel de administración
admin.site.site_header = 'EasyCRM - Panel de Administración'
admin.site.site_title = 'EasyCRM Admin'
admin.site.index_title = 'Panel de Control' 