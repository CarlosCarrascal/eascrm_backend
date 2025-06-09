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
    
    def validate_email(self, value):
        # Verificar si ya existe un usuario con este email
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Un usuario con este correo electrónico ya existe.")
        
        # Verificar si ya existe un cliente con este email
        from ..models import Cliente
        if Cliente.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo electrónico ya está registrado como cliente. Por favor, usa otro correo.")
        
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está en uso.")
        return value
    
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
            
            # Crear cliente asociado al usuario
            try:
                nombre_completo = f"{user.first_name} {user.last_name}".strip()
                if not nombre_completo:
                    nombre_completo = user.username
                    
                Cliente.objects.create(
                    usuario=user,
                    nombre=nombre_completo,
                    email=user.email,
                    direccion=direccion
                )
            except Exception as e:
                # Si falla la creación del cliente, eliminar el usuario para evitar inconsistencias
                user.delete()
                raise serializers.ValidationError(f"Error al crear el cliente: {str(e)}")
            
            return user
        except Exception as e:
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