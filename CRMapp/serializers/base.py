from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Cliente, Producto, Pedido, DetallePedido

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    direccion = serializers.CharField(write_only=True, required=False, default='')
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name', 'direccion')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }
    
    def create(self, validated_data):
        try:
            direccion = validated_data.pop('direccion', '')
            
            # Crear usuario
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data.get('email', ''),
                password=validated_data['password'],
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', '')
            )
            
            # Verificar si ya existe un cliente con este email
            from ..models import Cliente
            cliente_existente = Cliente.objects.filter(email=user.email).first()
            
            # Si existe un cliente con ese email y no tiene usuario asociado, vincularlo
            if cliente_existente and not cliente_existente.usuario:
                cliente_existente.usuario = user
                cliente_existente.save()
                return user
            
            # Si no existe un cliente con ese email, crear uno nuevo
            if not cliente_existente:
                nombre_completo = f"{user.first_name} {user.last_name}".strip()
                if not nombre_completo:
                    nombre_completo = user.username
                    
                Cliente.objects.create(
                    usuario=user,
                    nombre=nombre_completo,
                    email=user.email,
                    direccion=direccion
                )
            
            return user
        except Exception as e:
            # Si ocurre algún error, eliminar el usuario si fue creado
            if 'user' in locals():
                user.delete()
            raise serializers.ValidationError(f"Error al registrar usuario: {str(e)}")

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
        fields = ['id', 'cliente', 'cliente_nombre', 'fecha', 'estado', 'fecha_actualizacion', 'detalles', 'total'] 