from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.db.models import Count, Sum, F
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from .models import Cliente, Producto, Pedido, DetallePedido
from django.views.decorators.http import require_GET
from django.contrib.admin.views.decorators import staff_member_required

# Vista para la página de inicio
def home(request):
    # Redirige al panel de administración
    return redirect('admin:index')

# Vista para proporcionar datos para el dashboard
def dashboard_data(request):
    # Verificar si el usuario está autenticado y es staff
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=401)
    
    # Obtener fecha actual y fecha hace un año
    now = timezone.now()
    year_ago = now - timedelta(days=365)
    
    # Estadísticas generales
    total_clientes = Cliente.objects.count()
    total_productos = Producto.objects.count()
    total_pedidos = Pedido.objects.count()
    
    # Calcular ingresos totales usando el nuevo modelo DetallePedido
    ingresos_totales = DetallePedido.objects.filter(
        pedido__estado='completado'
    ).aggregate(
        total=Sum(F('cantidad') * F('precio_unitario'))
    )['total'] or 0
    
    # Ventas mensuales del último año
    ventas_mensuales = DetallePedido.objects.filter(
        pedido__fecha__gte=year_ago
    ).annotate(
        mes=TruncMonth('pedido__fecha')
    ).values('mes').annotate(
        total=Sum(F('cantidad') * F('precio_unitario'))
    ).order_by('mes')
    
    # Formatear datos de ventas mensuales
    meses_labels = []
    ventas_data = []
    
    # Crear diccionario con todos los meses
    meses_dict = {}
    current_month = year_ago.replace(day=1)
    while current_month <= now:
        meses_dict[current_month.strftime('%Y-%m')] = 0
        current_month = (current_month.replace(day=28) + timedelta(days=4)).replace(day=1)
    
    # Llenar con datos reales
    for venta in ventas_mensuales:
        mes_key = venta['mes'].strftime('%Y-%m')
        meses_dict[mes_key] = float(venta['total'])
    
    # Convertir a listas para el gráfico
    for mes_key, total in meses_dict.items():
        year, month = mes_key.split('-')
        month_names = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        meses_labels.append(f"{month_names[int(month)-1]} {year}")
        ventas_data.append(total)
    
    # Estado de pedidos
    estado_pedidos = Pedido.objects.values('estado').annotate(total=Count('id'))
    estados_labels = []
    estados_data = []
    estados_colors = {
        'pendiente': '#f59e0b',
        'en_proceso': '#3b82f6',
        'completado': '#10b981',
        'cancelado': '#ef4444'
    }
    estados_colors_list = []
    
    estados_dict = {estado[0]: 0 for estado in Pedido.ESTADO_CHOICES}
    for estado in estado_pedidos:
        estados_dict[estado['estado']] = estado['total']
    
    for estado_key, nombre_estado in Pedido.ESTADO_CHOICES:
        estados_labels.append(nombre_estado)
        estados_data.append(estados_dict[estado_key])
        estados_colors_list.append(estados_colors[estado_key])
    
    # Productos más vendidos
    productos_top = DetallePedido.objects.values(
        'producto__nombre'
    ).annotate(
        total=Sum('cantidad')
    ).order_by('-total')[:5]
    
    productos_labels = [p['producto__nombre'] for p in productos_top]
    productos_data = [p['total'] for p in productos_top]
    
    # Clientes principales (por número de pedidos)
    clientes_top = Pedido.objects.values(
        'cliente__nombre'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    clientes_labels = [c['cliente__nombre'] for c in clientes_top]
    clientes_data = [c['total'] for c in clientes_top]
    
    # Construir respuesta
    data = {
        'stats': {
            'totalClientes': total_clientes,
            'totalProductos': total_productos,
            'totalPedidos': total_pedidos,
            'ingresosTotales': float(ingresos_totales)
        },
        'ventas': {
            'labels': meses_labels,
            'data': ventas_data
        },
        'estadoPedidos': {
            'labels': estados_labels,
            'data': estados_data,
            'colors': estados_colors_list
        },
        'productosTop': {
            'labels': productos_labels,
            'data': productos_data
        },
        'clientesTop': {
            'labels': clientes_labels,
            'data': clientes_data
        }
    }
    
    return JsonResponse(data)

@staff_member_required
@require_GET
def get_producto_precio(request, producto_id):
    """Endpoint API para obtener el precio de un producto"""
    try:
        producto = Producto.objects.get(pk=producto_id)
        return JsonResponse({
            'success': True,
            'precio': float(producto.precio),
            'nombre': producto.nombre,
            'stock': producto.stock
        })
    except Producto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Producto no encontrado'
        }, status=404)
