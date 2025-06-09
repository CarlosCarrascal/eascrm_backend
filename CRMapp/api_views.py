from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
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
    DetallePedidoSerializer
)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

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
    queryset = Pedido.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'cliente']
    search_fields = ['cliente__nombre', 'detalles__producto__nombre']
    ordering_fields = ['fecha', 'estado']
    ordering = ['-fecha']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PedidoCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PedidoUpdateSerializer
        return PedidoSerializer
    
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