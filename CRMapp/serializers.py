# Este archivo ahora solo importa los serializers desde el paquete serializers
from .serializers import (
    ClienteSerializer, 
    ClienteCreateSerializer,
    ClienteUpdateSerializer,
    ProductoSerializer, 
    ProductoCreateSerializer,
    ProductoUpdateSerializer,
    PedidoSerializer,
    PedidoCreateSerializer,
    PedidoUpdateSerializer,
    DetallePedidoSerializer,
    DetallePedidoCreateSerializer
)

__all__ = [
    'ClienteSerializer', 
    'ClienteCreateSerializer',
    'ClienteUpdateSerializer',
    'ProductoSerializer', 
    'ProductoCreateSerializer',
    'ProductoUpdateSerializer',
    'PedidoSerializer',
    'PedidoCreateSerializer',
    'PedidoUpdateSerializer',
    'DetallePedidoSerializer',
    'DetallePedidoCreateSerializer'
]