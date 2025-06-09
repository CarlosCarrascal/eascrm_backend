from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum, F
from django.urls import reverse, path
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from ..models import Producto # Asegurarse que Producto está importado para la vista AJAX
from ..models import Pedido, DetallePedido # Ensure DetallePedido is imported
from ..forms import DetallePedidoForm # Import the custom form
# from django.http import HttpResponseRedirect # No longer needed for this specific view

class DetallePedidoInline(admin.TabularInline):
    form = DetallePedidoForm # Use the custom form
    model = DetallePedido
    extra = 1
    fields = ('producto', 'cantidad', 'precio_unitario')
    readonly_fields = ('precio_unitario',)
    min_num = 1
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        
        # Personalizar widgets
        form.base_fields['producto'].widget.attrs.update({'class': 'select2'})
        form.base_fields['cantidad'].widget.attrs.update({'min': '1', 'class': 'cantidad-input'})
        
        return formset

class PedidoAdmin(admin.ModelAdmin):

    list_display = ('id', 'cliente_info', 'fecha_formateada', 'estado', 'estado_badge', 'total_formateado', 'acciones_pedido')
    list_filter = ('estado', 'fecha')
    search_fields = ('cliente__nombre', 'detalles__producto__nombre')
    date_hierarchy = 'fecha'
    readonly_fields = ('fecha', 'total_calculado')
    list_editable = ('estado',)
    save_on_top = True
    list_per_page = 15
    inlines = [DetallePedidoInline]
    # Asegurarse que la clase Media esté definida antes de cualquier método que la use implícitamente
    # o al final de las definiciones de atributos de clase.
    
    fieldsets = (
        ('Cliente', {
            'fields': ('cliente',),
            'description': 'Cliente que realizó el pedido'
        }),
        ('Estado y Seguimiento', {
            'fields': ('estado', 'fecha'),
            'description': 'Estado actual del pedido y fecha de creación'
        }),
        ('Detalles Financieros', {
            'fields': ('total_calculado',),
            'classes': ('collapse',),
            'description': 'Información de costos y facturación'
        }),
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'ajax/get-product-price/', 
                self.admin_site.admin_view(self.get_product_price_ajax),
                name='CRMapp_get_product_price'
            ),
            path(
                '<int:pedido_id>/detalle/',
                self.admin_site.admin_view(self.pedido_detail_view),
                name='CRMapp_pedido_detail', # Consistent naming
            ),
        ]
        return custom_urls + urls
    
    def get_product_price_ajax(self, request):
        product_id = request.GET.get('product_id')
        data = {'price': None}
        if product_id:
            try:
                producto = Producto.objects.get(pk=product_id)
                data['price'] = str(producto.precio) # Convertir Decimal a string para JSON
            except Producto.DoesNotExist:
                pass # El producto no existe, el precio seguirá siendo None
        return JsonResponse(data)

    def pedido_detail_view(self, request, pedido_id):
        pedido = get_object_or_404(Pedido, pk=pedido_id)
        detalles_pedido = pedido.detalles.all() # Get related DetallePedido items
        
        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'pedido': pedido,
            'detalles_pedido': detalles_pedido,
            'title': f"Detalle del Pedido #{pedido.id}",
            'has_view_permission': self.has_view_permission(request, pedido),
            'has_change_permission': self.has_change_permission(request, pedido),
            'has_delete_permission': self.has_delete_permission(request, pedido),
        }
        return render(request, 'admin/CRMapp/pedido/pedido_detail.html', context)
    
    def cliente_info(self, obj):
        url = reverse('admin:CRMapp_cliente_change', args=[obj.cliente.id])
        if obj.cliente.foto:
            return format_html(
                '<div class="cliente-cell">'
                '<img src="{0}" class="mini-foto" /> '
                '<a href="{1}">{2}</a>'
                '</div>', 
                obj.cliente.foto.url, url, obj.cliente.nombre
            )
        return format_html(
            '<div class="cliente-cell">'
            '<span class="mini-avatar"><i class="fas fa-user"></i></span> '
            '<a href="{0}">{1}</a>'
            '</div>', 
            url, obj.cliente.nombre
        )
    cliente_info.short_description = 'Cliente'
    cliente_info.admin_order_field = 'cliente__nombre'
    
    def total_formateado(self, obj):
        total_formateado = "${:.2f}".format(obj.total)
        return format_html('<span class="precio-total">{0}</span>', total_formateado)
    total_formateado.short_description = 'Total'
    
    def fecha_formateada(self, obj):
        return format_html('<span class="fecha-pedido">{0}</span>', obj.fecha.strftime("%d/%m/%Y %H:%M"))
    fecha_formateada.short_description = 'Fecha'
    fecha_formateada.admin_order_field = 'fecha'
    
    def estado_badge(self, obj):
        estado_clases = {
            'pendiente': 'warning',
            'en_proceso': 'info',
            'completado': 'success',
            'cancelado': 'danger'
        }
        
        estado_iconos = {
            'pendiente': 'clock',
            'en_proceso': 'spinner fa-spin',
            'completado': 'check-circle',
            'cancelado': 'times-circle'
        }
        
        estado_texto = dict(Pedido.ESTADO_CHOICES).get(obj.estado)
        estado_clase = estado_clases.get(obj.estado, 'secondary')
        estado_icono = estado_iconos.get(obj.estado, 'question-circle')
        
        return format_html(
            '<span class="badge badge-{0}"><i class="fas fa-{1}"></i> {2}</span>', 
            estado_clase, estado_icono, estado_texto
        )
    estado_badge.short_description = 'Estado'
    estado_badge.admin_order_field = 'estado'
    
    def total_calculado(self, obj):
        if not obj.pk:
            return "N/A"
        
        html = '<div class="total-detalle">'
        
        for detalle in obj.detalles.all():
            precio_formateado = "${:.2f}".format(detalle.precio_unitario)
            subtotal_formateado = "${:.2f}".format(detalle.subtotal)
            
            html += '<div class="detalle-producto">'
            html += '<p><strong>{0}</strong></p>'.format(detalle.producto.nombre)
            html += '<p>Precio unitario: {0} × {1} = {2}</p>'.format(
                precio_formateado, detalle.cantidad, subtotal_formateado)
            html += '</div>'
        
        total_formateado = "${:.2f}".format(obj.total)
        html += '<p><strong>Total:</strong> <span class="precio-total">{0}</span></p>'.format(total_formateado)
        html += '</div>'
        
        return format_html(html)
    total_calculado.short_description = 'Desglose del Total'
    
    def acciones_pedido(self, obj):
        view_url = reverse('admin:CRMapp_pedido_detail', args=[obj.pk]) # Use consistent naming
        edit_url = reverse('admin:CRMapp_pedido_change', args=[obj.pk])
        delete_url = reverse('admin:CRMapp_pedido_delete', args=[obj.pk])

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
    acciones_pedido.short_description = 'Acciones'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Personalizar campos
        if form.base_fields.get('cliente'):
            form.base_fields['cliente'].widget.attrs['class'] = 'select2'
            form.base_fields['cliente'].help_text = 'Selecciona el cliente que realiza el pedido'
        
        if form.base_fields.get('estado'):
            form.base_fields['estado'].widget.attrs['class'] = 'select2 estado-select'
            form.base_fields['estado'].help_text = 'Estado actual del proceso del pedido'
        
        return form
    
    def save_model(self, request, obj, form, change):
        # Verificar si es una creación o una edición
        if not change:  # Es una creación
            from django.contrib import messages
            messages.success(request, '¡Pedido creado exitosamente! Ahora puede añadir productos al pedido.')
        super().save_model(request, obj, form, change)
    
    class Media:
        css = {
            'all': ('admin/css/base.css', 'admin/css/detail.css')
        }
        js = [] 