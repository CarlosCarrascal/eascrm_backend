from django.contrib import admin
from django.db.models import Sum, F, Count
from django.db.models.functions import TruncMonth
from datetime import datetime
from ..models import Cliente, Producto, Pedido, DetallePedido

class AdminSite(admin.AdminSite):
    # No usar template personalizado, usar el dashboard de Jazzmin
    
    def index(self, request, extra_context=None):
        # Obtener estadísticas para el dashboard
        clientes_count = Cliente.objects.count()
        productos_count = Producto.objects.count()
        pedidos_count = Pedido.objects.count()
        
        # Calcular ingresos totales
        ingresos = DetallePedido.objects.filter(pedido__estado='completado').aggregate(
            total=Sum(F('cantidad') * F('precio_unitario'))
        )
        ingresos_totales = ingresos['total'] or 0
        
        # Crear contexto
        context = {
            'clientes_count': clientes_count,
            'productos_count': productos_count,
            'pedidos_count': pedidos_count,
            'ingresos_totales': ingresos_totales,
        }
        
        # Combinar con contexto adicional si existe
        if extra_context:
            context.update(extra_context)
            
        return super().index(request, context) 