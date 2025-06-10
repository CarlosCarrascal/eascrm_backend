from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from .models import Cliente, Producto, Pedido, DetallePedido
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
    UserSerializer
)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar usuarios del sistema
    """
    permission_classes = [permissions.IsAdminUser]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'date_joined']
    ordering = ['username']
    serializer_class = UserSerializer
    
    def get_queryset(self):
        """
        Filtrar usuarios según el tipo de usuario:
        - Si es staff o admin: todos los usuarios
        - Si es usuario normal: solo su propio usuario
        """
        user = self.request.user
        
        # Si es admin o staff, mostrar todos los usuarios
        if user.is_staff or user.is_superuser:
            return User.objects.all()
        
        # Si es usuario normal, mostrar solo su propio usuario
        return User.objects.filter(id=user.id)
    
    def get_permissions(self):
        """
        Permitir que los usuarios vean y actualicen su propio perfil
        """
        if self.action in ['retrieve', 'update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def perform_update(self, serializer):
        """
        Asegurar que un usuario normal solo pueda actualizar su propio perfil
        """
        user = self.request.user
        if not (user.is_staff or user.is_superuser) and self.get_object().id != user.id:
            raise permissions.exceptions.PermissionDenied("No tienes permiso para actualizar este usuario")
        serializer.save()
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def cliente(self, request, pk=None):
        """
        Obtener el cliente asociado a un usuario específico
        """
        user = self.get_object()
        
        # Verificar permisos
        if not (request.user.is_staff or request.user.is_superuser) and request.user.id != user.id:
            return Response({"error": "No tienes permiso para ver este cliente"}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            cliente = Cliente.objects.get(usuario=user)
            from .serializers import ClienteSerializer
            serializer = ClienteSerializer(cliente, context={'request': request})
            return Response(serializer.data)
        except Cliente.DoesNotExist:
            return Response({"error": "No hay cliente asociado a este usuario"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def pedidos(self, request, pk=None):
        """
        Obtener los pedidos asociados a un usuario específico
        """
        user = self.get_object()
        
        # Verificar permisos
        if not (request.user.is_staff or request.user.is_superuser) and request.user.id != user.id:
            return Response({"error": "No tienes permiso para ver estos pedidos"}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            cliente = Cliente.objects.get(usuario=user)
            pedidos = Pedido.objects.filter(cliente=cliente)
            page = self.paginate_queryset(pedidos)
            
            if page is not None:
                serializer = PedidoSerializer(page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)
                
            serializer = PedidoSerializer(pedidos, many=True, context={'request': request})
            return Response(serializer.data)
        except Cliente.DoesNotExist:
            return Response({"error": "No hay cliente asociado a este usuario"}, status=status.HTTP_404_NOT_FOUND)

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['nombre']
    search_fields = ['nombre', 'email']
    ordering_fields = ['nombre', 'fecha_registro']
    ordering = ['-fecha_registro']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ClienteCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ClienteUpdateSerializer
        return ClienteSerializer
    
    def perform_update(self, serializer):
        """
        Log para verificar los datos recibidos en la actualización
        """
        print(f"Actualizando cliente: {serializer.instance.id}")
        if 'foto' in self.request.data:
            print("Imagen recibida en la actualización")
            
        # Guardar con los datos actualizados
        serializer.save()
        print(f"Cliente actualizado: {serializer.instance.id}")
    
    @action(detail=True, methods=['get'])
    def pedidos(self, request, pk=None):
        """
        Obtener todos los pedidos de un cliente específico
        """
        cliente = self.get_object()
        pedidos = cliente.pedidos.all()
        page = self.paginate_queryset(pedidos)
        
        if page is not None:
            serializer = PedidoSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
            
        serializer = PedidoSerializer(pedidos, many=True, context={'request': request})
        return Response(serializer.data)

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['nombre']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'precio']
    ordering = ['nombre']
    
    def get_permissions(self):
        """
        Permitir acceso público a la lista y detalle de productos,
        pero requerir autenticación para crear, actualizar o eliminar
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProductoCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProductoUpdateSerializer
        return ProductoSerializer
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def pedidos(self, request, pk=None):
        """
        Obtener todos los pedidos que incluyen este producto
        """
        producto = self.get_object()
        detalles = producto.detallepedido_set.all()
        pedidos = Pedido.objects.filter(detalles__in=detalles).distinct()
        page = self.paginate_queryset(pedidos)
        
        if page is not None:
            serializer = PedidoSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
            
        serializer = PedidoSerializer(pedidos, many=True, context={'request': request})
        return Response(serializer.data)

class PedidoViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'cliente']
    search_fields = ['cliente__nombre', 'detalles__producto__nombre']
    ordering_fields = ['fecha', 'estado']
    ordering = ['-fecha']
    
    def get_queryset(self):
        """
        Filtrar pedidos según el tipo de usuario:
        - Si es staff o admin: todos los pedidos
        - Si es cliente: solo sus propios pedidos
        """
        user = self.request.user
        
        # Si es admin o staff, mostrar todos los pedidos
        if user.is_staff or user.is_superuser:
            return Pedido.objects.all()
        
        # Si es cliente, mostrar solo sus pedidos
        try:
            cliente = Cliente.objects.get(usuario=user)
            return Pedido.objects.filter(cliente=cliente)
        except Cliente.DoesNotExist:
            # Si el usuario no está asociado a un cliente, no mostrar pedidos
            return Pedido.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PedidoCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PedidoUpdateSerializer
        return PedidoSerializer
    
    def perform_create(self, serializer):
        """
        Al crear un pedido, asignar automáticamente el cliente asociado al usuario
        """
        user = self.request.user
        
        # Si el usuario es cliente, asignar automáticamente su cliente
        if not user.is_staff and not user.is_superuser:
            try:
                cliente = Cliente.objects.get(usuario=user)
                serializer.save(cliente=cliente)
                return
            except Cliente.DoesNotExist:
                # Si el usuario no tiene cliente asociado, devolver un error claro
                from rest_framework.exceptions import ValidationError
                raise ValidationError({
                    "error": "No tienes un perfil de cliente asociado a tu cuenta. Por favor, contacta con el administrador.",
                    "detail": "Para crear pedidos, tu cuenta de usuario debe estar vinculada a un cliente."
                })
        
        # Si el cliente fue proporcionado en los datos o es un admin
        serializer.save()
    
    @action(detail=True, methods=['get'])
    def detalles(self, request, pk=None):
        """
        Obtener todos los detalles de un pedido específico
        """
        pedido = self.get_object()
        detalles = pedido.detalles.all()
        serializer = DetallePedidoSerializer(detalles, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def agregar_producto(self, request, pk=None):
        """
        Agregar un producto a un pedido existente
        """
        pedido = self.get_object()
        
        # Validar datos
        producto_id = request.data.get('producto')
        cantidad = request.data.get('cantidad', 1)
        
        if not producto_id:
            return Response(
                {'error': 'Se requiere el ID del producto'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            producto = Producto.objects.get(pk=producto_id)
        except Producto.DoesNotExist:
            return Response(
                {'error': 'Producto no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar stock
        if producto.stock < cantidad:
            return Response(
                {'error': f'Stock insuficiente. Solo hay {producto.stock} unidades disponibles.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar stock
        producto.stock -= cantidad
        producto.save()
        
        # Crear detalle de pedido
        detalle = DetallePedido(
            pedido=pedido,
            producto=producto,
            cantidad=cantidad
        )
        detalle.save()
        
        serializer = DetallePedidoSerializer(detalle)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """
    Registrar un nuevo usuario
    """
    try:
        # Verificar primero si ya existe un cliente con ese email
        email = request.data.get('email')
        if email:
            from .models import Cliente
            if Cliente.objects.filter(email=email).exists():
                return Response({
                    "error": "Este correo electrónico ya está registrado como cliente. Por favor, usa otro correo o utiliza la opción de vincular cuenta."
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si ya existe un usuario con ese email
        from django.contrib.auth.models import User
        if User.objects.filter(email=email).exists():
            return Response({
                "error": "Un usuario con este correo electrónico ya existe."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si ya existe un usuario con ese username
        username = request.data.get('username')
        if username and User.objects.filter(username=username).exists():
            return Response({
                "error": "Este nombre de usuario ya está en uso."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Si pasa todas las validaciones, proceder con la creación
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "user": UserSerializer(user).data,
                "message": "Usuario creado exitosamente",
            }, status=status.HTTP_201_CREATED)
        else:
            # Devolver errores de validación detallados
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        # Capturar cualquier excepción y devolver un mensaje claro
        import traceback
        error_message = str(e)
        error_traceback = traceback.format_exc()
        print(f"Error en register_user: {error_message}")
        print(f"Traceback: {error_traceback}")
        return Response({
            "error": error_message,
            "detail": "Error interno del servidor al registrar usuario."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def link_user_to_client(request):
    """
    Vincular un usuario recién creado a un cliente existente por email
    """
    try:
        email = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not email or not username or not password:
            return Response({
                "error": "Se requiere email, username y password"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si ya existe un usuario con ese username
        from django.contrib.auth.models import User
        if User.objects.filter(username=username).exists():
            return Response({
                "error": "Este nombre de usuario ya está en uso"
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Verificar si ya existe un usuario con ese email
        if User.objects.filter(email=email).exists():
            return Response({
                "error": "Este correo electrónico ya está asociado a un usuario"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si existe el cliente
        from .models import Cliente
        try:
            cliente = Cliente.objects.get(email=email)
        except Cliente.DoesNotExist:
            return Response({
                "error": "No existe un cliente con este email"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verificar si el cliente ya tiene usuario
        if cliente.usuario:
            return Response({
                "error": "Este cliente ya está vinculado a un usuario"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear el usuario y vincularlo al cliente
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=request.data.get('first_name', ''),
            last_name=request.data.get('last_name', '')
        )
        
        cliente.usuario = user
        cliente.save()
        
        return Response({
            "message": "Usuario creado y vinculado al cliente exitosamente",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            },
            "cliente": {
                "id": cliente.id,
                "nombre": cliente.nombre
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        import traceback
        error_message = str(e)
        error_traceback = traceback.format_exc()
        print(f"Error en link_user_to_client: {error_message}")
        print(f"Traceback: {error_traceback}")
        return Response({
            "error": error_message,
            "detail": "Error interno del servidor al vincular usuario con cliente."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user(request):
    """
    Obtener datos del usuario actual y su cliente asociado (si existe)
    """
    user = request.user
    
    # Datos del usuario
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser
    }
    
    # Intentar obtener el cliente asociado
    cliente_data = None
    try:
        cliente = Cliente.objects.get(usuario=user)
        # Incluir todos los campos relevantes, incluida la foto
        cliente_data = {
            'id': cliente.id,
            'nombre': cliente.nombre,
            'email': cliente.email,
            'direccion': cliente.direccion,
            'foto': request.build_absolute_uri(cliente.foto.url) if cliente.foto else None
        }
        print(f"Datos del cliente para {user.username}:", cliente_data)
    except Cliente.DoesNotExist:
        pass
    except Exception as e:
        # Capturar cualquier excepción al procesar la foto
        print(f"Error al obtener datos del cliente: {str(e)}")
        cliente_data = {
            'id': cliente.id,
            'nombre': cliente.nombre,
            'email': cliente.email,
            'direccion': cliente.direccion,
            'foto': None
        }
    
    return Response({
        'user': user_data,
        'cliente': cliente_data
    }) 