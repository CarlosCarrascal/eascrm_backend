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

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Cliente, Producto, Pedido, DetallePedido

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

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user