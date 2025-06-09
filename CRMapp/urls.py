from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views

# Configuración del router para la API
router = DefaultRouter()
router.register(r'clientes', api_views.ClienteViewSet)
router.register(r'productos', api_views.ProductoViewSet)
router.register(r'pedidos', api_views.PedidoViewSet)

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    
    # Endpoint para datos del dashboard
    path('api/dashboard/', views.dashboard_data, name='dashboard_data'),
    
    # Admin API URLs
    path('admin/api/producto/<int:producto_id>/precio/', views.get_producto_precio, name='get_producto_precio'),
    
    # Registro de usuarios
    path('api/register/', api_views.register_user, name='register_user'),
    
    # Redirige la página principal al admin
    path('', views.home, name='home'),
]