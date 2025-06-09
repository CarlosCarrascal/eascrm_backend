from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum, F, Max
from django.urls import reverse, path
from django.shortcuts import render, get_object_or_404
from ..models import Producto, DetallePedido
from django.http import HttpResponseRedirect

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_formateado', 'stock_status', 'descripcion_corta', 'mostrar_imagen', 'acciones_producto')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('precio',)
    ordering = ('nombre',)
    list_per_page = 15
    save_on_top = True
    
    fieldsets = (
        ('Información del Producto', {
            'fields': ('nombre', 'descripcion', 'precio', 'stock', 'imagen'),
            'description': 'Datos del producto'
        }),
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Añadir datos de ventas como anotaciones
        queryset = queryset.annotate(
            total_ventas=Count('detallepedido'),
            ultimo_pedido=Max('detallepedido__pedido__fecha')
        )
        return queryset
    
    def fecha_modificacion(self, obj):
        # Este es un campo calculado para mostrar la "última modificación"
        from django.utils import timezone
        
        if hasattr(obj, 'ultimo_pedido') and obj.ultimo_pedido:
            delta = timezone.now() - obj.ultimo_pedido
            if delta.days < 30:
                return format_html('<span class="text-success"><i class="fas fa-clock"></i> Hace {0} días</span>', delta.days)
            else:
                return format_html('<span class="text-muted"><i class="fas fa-history"></i> {0}</span>', obj.ultimo_pedido.strftime("%d/%m/%Y"))
        return format_html('<span class="text-muted"><i class="fas fa-minus-circle"></i> Sin actividad reciente</span>')
    fecha_modificacion.short_description = 'Última Actividad'
    
    def mostrar_imagen(self, obj):
        if obj.imagen:
            return format_html('<img src="{0}" style="max-width: 60px; max-height: 60px; border-radius: 4px; object-fit: cover;" class="producto-thumbnail" />', obj.imagen.url)
        return format_html('<div class="producto-sin-imagen" style="width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; background-color: #f0f0f0; border-radius: 4px;"><i class="fas fa-image" style="font-size: 24px; color: #aaa;"></i></div>')
    mostrar_imagen.short_description = 'Imagen'
    
    def mostrar_imagen_detalle(self, obj):
        if obj.imagen:
            return format_html('<div class="imagen-detalle-container">'
                             '<img src="{0}" class="producto-imagen-detalle" />'
                             '</div>', obj.imagen.url)
        return format_html('<div class="producto-sin-imagen-grande">'
                         '<i class="fas fa-image"></i>'
                         '<p>Sin imagen disponible</p>'
                         '</div>')
    mostrar_imagen_detalle.short_description = 'Vista previa'
    
    def precio_formateado(self, obj):
        precio_str = "${:.2f}".format(obj.precio)
        return format_html('<span class="precio-producto">{0}</span>', precio_str)
    precio_formateado.short_description = 'Precio'
    precio_formateado.admin_order_field = 'precio'
    
    def descripcion_corta(self, obj):
        if not obj.descripcion:
            return format_html('<span class="sin-descripcion">Sin descripción</span>')
        
        # Mostrar solo los primeros 50 caracteres de la descripción
        desc_corta = obj.descripcion[:50] + ('...' if len(obj.descripcion) > 50 else '')
        return format_html('<span class="descripcion-truncada" title="{0}">{1}</span>', 
                          obj.descripcion, desc_corta)
    descripcion_corta.short_description = 'Descripción'
    
    def stock_status(self, obj):
        if obj.stock <= 0:
            return format_html('<span class="stock agotado"><i class="fas fa-exclamation-circle"></i> Agotado</span>')
        elif obj.stock < 5:
            return format_html('<span class="stock bajo"><i class="fas fa-exclamation-circle"></i> Bajo</span>')
        elif obj.stock < 10:
            return format_html('<span class="stock medio"><i class="fas fa-check-circle"></i> Medio</span>')
        else:
            return format_html('<span class="stock disponible"><i class="fas fa-check-circle"></i> Disponible</span>')
    stock_status.short_description = 'Stock'
    
    def ventas_totales(self, obj):
        if hasattr(obj, 'total_ventas'):
            if obj.total_ventas > 0:
                return format_html('<span class="ventas-contador">{0}</span>', obj.total_ventas)
            return format_html('<span class="sin-ventas">Sin ventas</span>')
        return format_html('<span class="sin-ventas">Sin ventas</span>')
    ventas_totales.short_description = 'Ventas'
    ventas_totales.admin_order_field = 'total_ventas'
    
    def ventas_info(self, obj):
        if not hasattr(obj, 'total_ventas'):
            return format_html('<div class="alert alert-info">'
                              '<i class="fas fa-info-circle"></i> '
                              'No hay información de ventas disponible.'
                              '</div>')
        
        # Generar gráfico básico de ventas
        html = '<div class="ventas-resumen">'
        
        # Información general
        html += '<div class="ventas-seccion general">'
        html += '<h3><i class="fas fa-chart-line"></i> Resumen de Ventas</h3>'
        
        if obj.total_ventas > 0:
            # Calculamos los ingresos totales
            detalles = DetallePedido.objects.filter(producto=obj)
            ingresos = sum(detalle.cantidad * detalle.precio_unitario for detalle in detalles)
            
            html += '<div class="ventas-stats">'
            html += '<div class="stat-card">'
            html += '<span class="stat-value">{0}</span>'.format(obj.total_ventas)
            html += '<span class="stat-label">Unidades vendidas</span>'
            html += '</div>'
            
            html += '<div class="stat-card">'
            html += '<span class="stat-value">${0:.2f}</span>'.format(ingresos)
            html += '<span class="stat-label">Ingresos generados</span>'
            html += '</div>'
            
            # Último pedido
            if hasattr(obj, 'ultimo_pedido') and obj.ultimo_pedido:
                html += '<div class="stat-card">'
                html += '<span class="stat-value">{0}</span>'.format(obj.ultimo_pedido.strftime("%d/%m/%Y"))
                html += '<span class="stat-label">Última venta</span>'
                html += '</div>'
                
            html += '</div>'  # Cierra ventas-stats
            
            # Simulamos una gráfica de tendencia
            html += '<div class="ventas-trend">'
            html += '<h4>Tendencia de Ventas</h4>'
            html += '<div class="trend-graph">'
            
            # Gráfico básico de barras simulado
            max_ventas = max(5, obj.total_ventas)
            for i in range(6):
                # Simulamos alturas aleatorias pero consistentes para el producto
                altura = (obj.id * (i+1) % max_ventas) + 1
                porcentaje = (altura / max_ventas) * 100
                
                html += '<div class="trend-bar">'
                html += '<div class="bar" style="height: {0}%;"></div>'.format(porcentaje)
                html += '<span class="month">M{0}</span>'.format(i+1)
                html += '</div>'
            
            html += '</div>'  # Cierra trend-graph
            html += '</div>'  # Cierra ventas-trend
            
        else:
            html += '<div class="alert alert-warning">'
            html += '<i class="fas fa-exclamation-triangle"></i> Este producto aún no registra ventas.'
            html += '</div>'
            html += '<p>Recomendaciones:</p>'
            html += '<ul>'
            html += '<li>Considere actualizar la descripción del producto</li>'
            html += '<li>Revise el precio para asegurar competitividad</li>'
            html += '<li>Verifique la calidad de la imagen del producto</li>'
            html += '</ul>'
        
        html += '</div>'  # Cierra ventas-seccion
        html += '</div>'  # Cierra ventas-resumen
        
        return format_html(html)
    ventas_info.short_description = 'Análisis de Ventas'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Personalizar campos
        if form.base_fields.get('nombre'):
            form.base_fields['nombre'].widget.attrs['placeholder'] = 'Nombre del producto'
            form.base_fields['nombre'].help_text = 'Nombre comercial completo del producto'
        
        if form.base_fields.get('descripcion'):
            form.base_fields['descripcion'].widget.attrs['placeholder'] = 'Descripción detallada del producto...'
            form.base_fields['descripcion'].widget.attrs['rows'] = 4
            form.base_fields['descripcion'].help_text = 'Incluya características principales, materiales, usos recomendados, etc.'
        
        if form.base_fields.get('precio'):
            form.base_fields['precio'].widget.attrs['placeholder'] = '0.00'
            form.base_fields['precio'].widget.attrs['class'] = 'precio-input'
            form.base_fields['precio'].help_text = ''
            form.base_fields['precio'].min_value = 0.01
            form.base_fields['precio'].label = 'Precio ($)'
        
        if form.base_fields.get('imagen'):
            form.base_fields['imagen'].help_text = '''
                <span class="help-block">
                    <i class="fas fa-info-circle text-primary"></i> 
                    Sube una imagen del producto (formato recomendado: cuadrado, mínimo 500x500px)
                </span>
                <div id="image-preview-container" class="mt-2 preview-box">
                    <p class="help-block">Vista previa:</p>
                    <img id="image-preview" style="max-width: 200px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />
                </div>
                <script>
                    document.addEventListener('DOMContentLoaded', function() {
                        const fileInput = document.querySelector('input[type="file"]');
                        const previewContainer = document.getElementById('image-preview-container');
                        const preview = document.getElementById('image-preview');
                        
                        // Ocultar inicialmente el contenedor solo si no hay una imagen ya seleccionada
                        if (!fileInput.value) {
                            previewContainer.style.display = 'none';
                        } else {
                            previewContainer.style.display = 'block';
                        }
                        
                        if (fileInput) {
                            fileInput.addEventListener('change', function() {
                                if (this.files && this.files[0]) {
                                    const reader = new FileReader();
                                    reader.onload = function(e) {
                                        preview.src = e.target.result;
                                        previewContainer.style.display = 'block';
                                    }
                                    reader.readAsDataURL(this.files[0]);
                                } else {
                                    previewContainer.style.display = 'none';
                                }
                            });
                        }
                    });
                </script>
            '''
        
        return form
    
    def save_model(self, request, obj, form, change):
        # Verificar si es una creación o una edición
        if not change:  # Es una creación
            from django.contrib import messages
            precio_formateado = "${:.2f}".format(obj.precio)
            messages.success(request, '¡Producto "{0}" creado exitosamente con precio {1}!'.format(obj.nombre, precio_formateado))
        super().save_model(request, obj, form, change)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:producto_id>/detalle/',
                self.admin_site.admin_view(self.producto_detail_view),
                name='CRMapp_producto_detail', # Consistent naming
            ),
        ]
        return custom_urls + urls
    
    def producto_detail_view(self, request, producto_id):
        producto = get_object_or_404(Producto, pk=producto_id)
        # Fetch related order details for this product
        # Order by most recent pedido first, then by the detail ID as a fallback tie-breaker
        detalles_pedido = DetallePedido.objects.filter(producto=producto).order_by('-pedido__fecha', '-id')
        
        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'producto': producto,
            'detalles_pedido': detalles_pedido,
            'title': f"Detalle de {producto.nombre}",
            'has_view_permission': self.has_view_permission(request, producto),
            'has_change_permission': self.has_change_permission(request, producto),
            'has_delete_permission': self.has_delete_permission(request, producto),
        }
        return render(request, 'admin/CRMapp/producto/producto_detail.html', context)
    
    def acciones_producto(self, obj):
        view_url = reverse('admin:CRMapp_producto_detail', args=[obj.pk]) # Use consistent naming
        edit_url = reverse('admin:CRMapp_producto_change', args=[obj.pk])
        delete_url = reverse('admin:CRMapp_producto_delete', args=[obj.pk])

        return format_html(
            '<div class="acciones-botones">'
            '<a href="{}" class="button viewlink" title="Ver detalle">'
            '<i class="fas fa-eye"></i></a>'
            '<a href="{}" class="button editlink" title="Editar">'
            '<i class="fas fa-edit"></i></a>'
            '<a href="{}" class="button deletelink" title="Eliminar">'
            '<i class="fas fa-trash-alt"></i></a>'
            '</div>',
            view_url,
            edit_url,
            delete_url
        )
    acciones_producto.short_description = 'Acciones'
    
    class Media:
        css = {
            'all': ('admin/css/base.css', 'admin/css/detail.css')
        }
        js = [] 