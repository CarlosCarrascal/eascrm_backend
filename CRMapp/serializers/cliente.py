from rest_framework import serializers
from ..models import Cliente
from .base import ClienteSerializer

class ClienteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['nombre', 'email', 'direccion', 'foto']
        
    def validate_email(self, value):
        # Validación adicional para el email al crear
        if Cliente.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un cliente con este email.")
        return value

class ClienteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['nombre', 'email', 'direccion', 'foto']
        
    def validate_email(self, value):
        # Validación adicional para el email al actualizar
        # Permitir que el cliente conserve su email actual
        instance = getattr(self, 'instance', None)
        if instance and instance.email != value and Cliente.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un cliente con este email.")
        return value 