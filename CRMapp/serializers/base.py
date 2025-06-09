from rest_framework import serializers
from ..models import Cliente, Producto, Pedido, DetallePedido

class ClienteSerializer(serializers.ModelSerializer):
    foto_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'email', 'direccion', 'foto', 'foto_url', 'fecha_registro']
        read_only_fields = ['fecha_registro']
    
    def get_foto_url(self, obj):
        if obj.foto and hasattr(obj.foto, 'url'):
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.foto.url)
            return obj.foto.url
        return None

class ProductoSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'precio', 'imagen', 'imagen_url', 'stock']
    
    def get_imagen_url(self, obj):
        if obj.imagen and hasattr(obj.imagen, 'url'):
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.imagen.url)
            return obj.imagen.url
        return None

class DetallePedidoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.ReadOnlyField(source='producto.nombre')
    subtotal = serializers.ReadOnlyField()
    
    class Meta:
        model = DetallePedido
        fields = ['id', 'producto', 'producto_nombre', 'cantidad', 'precio_unitario', 'subtotal']

class PedidoSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.ReadOnlyField(source='cliente.nombre')
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    total = serializers.ReadOnlyField()
    
    class Meta:
        model = Pedido
        fields = ['id', 'cliente', 'cliente_nombre', 'fecha', 'estado', 'detalles', 'total', 'fecha_actualizacion']
        read_only_fields = ['fecha', 'fecha_actualizacion'] 