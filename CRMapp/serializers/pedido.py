from rest_framework import serializers
from ..models import Pedido, DetallePedido, Producto
from .base import PedidoSerializer

class DetallePedidoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePedido
        fields = ['producto', 'cantidad', 'precio_unitario']
        extra_kwargs = {'precio_unitario': {'required': False}}
    
    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor que cero.")
        return value
    
    def validate(self, data):
        # Si no se proporciona precio_unitario, usar el precio del producto
        if 'precio_unitario' not in data or data['precio_unitario'] is None:
            data['precio_unitario'] = data['producto'].precio
            
        # Verificar stock disponible
        producto = data['producto']
        cantidad = data['cantidad']
        if producto.stock < cantidad:
            raise serializers.ValidationError({
                "cantidad": f"Stock insuficiente. Solo hay {producto.stock} unidades disponibles."
            })
            
        return data

class PedidoCreateSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoCreateSerializer(many=True)
    
    class Meta:
        model = Pedido
        fields = ['cliente', 'estado', 'detalles']
        extra_kwargs = {
            'cliente': {'required': False},  # No requerido, se asigna automáticamente
            'estado': {'default': 'pendiente'}
        }
    
    def validate_detalles(self, value):
        if not value:
            raise serializers.ValidationError("El pedido debe tener al menos un detalle.")
        return value
    
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        
        # Si el cliente no se proporciona, se asigna en el perform_create del viewset
        pedido = Pedido.objects.create(**validated_data)
        
        for detalle_data in detalles_data:
            # Actualizar stock del producto
            producto = detalle_data['producto']
            cantidad = detalle_data['cantidad']
            producto.stock -= cantidad
            producto.save()
            
            # Crear detalle
            DetallePedido.objects.create(pedido=pedido, **detalle_data)
        
        return pedido

class PedidoUpdateSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoCreateSerializer(many=True, required=False)
    
    class Meta:
        model = Pedido
        fields = ['cliente', 'estado', 'detalles']
    
    def update(self, instance, validated_data):
        detalles_data = validated_data.pop('detalles', None)
        
        # Actualizar campos del pedido
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar detalles si se proporcionaron
        if detalles_data is not None:
            # Devolver stock de productos de detalles anteriores
            for detalle in instance.detalles.all():
                producto = detalle.producto
                producto.stock += detalle.cantidad
                producto.save()
            
            # Eliminar detalles existentes
            instance.detalles.all().delete()
            
            # Crear nuevos detalles y actualizar stock
            for detalle_data in detalles_data:
                # Actualizar stock del producto
                producto = detalle_data['producto']
                cantidad = detalle_data['cantidad']
                producto.stock -= cantidad
                producto.save()
                
                # Crear detalle
                DetallePedido.objects.create(pedido=instance, **detalle_data)
        
        return instance 