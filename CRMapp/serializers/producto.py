from rest_framework import serializers
from ..models import Producto
from .base import ProductoSerializer

class ProductoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'imagen', 'stock']
        
    def validate_precio(self, value):
        # Validación adicional para el precio al crear
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor que cero.")
        return value
        
    def validate_stock(self, value):
        # Validación adicional para el stock al crear
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo.")
        return value

class ProductoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'imagen', 'stock']
        
    def validate_precio(self, value):
        # Validación adicional para el precio al actualizar
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor que cero.")
        return value
        
    def validate_stock(self, value):
        # Validación adicional para el stock al actualizar
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo.")
        return value 