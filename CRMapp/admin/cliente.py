from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum, F
from django.urls import reverse, path
from django.shortcuts import render, get_object_or_404
from ..models import Cliente, Pedido # Asegúrate que Pedido está aquí si resumen_pedidos lo usa directamente o a través de obj.pedidos
from django.http import HttpResponseRedirect

class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'mostrar_foto', 'direccion_corta', 'fecha_formateada', 'total_pedidos', 'acciones_cliente')
    search_fields = ('nombre', 'email', 'direccion')
    list_filter = ('fecha_registro',)
    readonly_fields = ('fecha_registro', 'resumen_pedidos')
    list_per_page = 15
    save_on_top = True
    ordering = ('-fecha_registro',)
    date_hierarchy = 'fecha_registro'
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('nombre', 'email'),
            'description': 'Datos básicos del cliente'
        }),
        ('Información de Contacto', {
            'fields': ('direccion',),
            'description': 'Dirección completa para envíos y facturación'
        }),
        ('Multimedia', {
            'fields': ('foto',),
            'description': 'Imagen de perfil del cliente'
        }),
        ('Actividad del Cliente', {
            'fields': ('resumen_pedidos',),
            'description': 'Resumen de la actividad del cliente en el sistema'
        }),
        ('Metadatos', {
            'fields': ('fecha_registro',),
            'classes': ('collapse',),
            'description': 'Información de seguimiento y auditoría'
        }),
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            pedidos_count=Count('pedidos', distinct=True),
            total_compras=Sum(F('pedidos__detalles__cantidad') * F('pedidos__detalles__precio_unitario'))
        )
        return queryset
    
    def mostrar_foto(self, obj):
        if obj.foto:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%; object-fit: cover; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />', obj.foto.url)
        return format_html('<div style="width: 50px; height: 50px; border-radius: 50%; background-color: #f0f0f0; display: flex; align-items: center; justify-content: center; color: #999;"><i class="fas fa-user"></i></div>')
    mostrar_foto.short_description = 'Foto'
    
    def mostrar_foto_detalle(self, obj):
        if obj and obj.foto:
            return format_html('<img src="{0}" width="200" style="border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />', obj.foto.url)
        return format_html('<div style="width: 200px; height: 200px; border-radius: 8px; background-color: #f0f0f0; display: flex; align-items: center; justify-content: center; color: #999;"><i class="fas fa-user" style="font-size: 48px;"></i></div>')
    mostrar_foto_detalle.short_description = 'Vista previa'
    
    def direccion_corta(self, obj):
        if not obj.direccion:
            return format_html('<span class="text-muted"><i class="fas fa-map-marker-alt"></i> Sin dirección</span>')
        
        if len(obj.direccion) > 30:
            # Extraer primera línea para mostrar la calle principal
            primera_linea = obj.direccion.split('\n')[0] if '\n' in obj.direccion else obj.direccion[:30]
            
            return format_html(
                '<span data-toggle="tooltip" title="{0}">'
                '<i class="fas fa-map-marker-alt text-danger"></i> {1}...</span>',
                obj.direccion.replace('\n', ', '),
                primera_linea[:30]
            )
        return format_html(
            '<span><i class="fas fa-map-marker-alt text-danger"></i> {0}</span>',
            obj.direccion
        )
    direccion_corta.short_description = 'Dirección'
    
    def total_pedidos(self, obj):
        count = getattr(obj, 'pedidos_count', 0) or 0
        total = getattr(obj, 'total_compras', 0) or 0
        
        if count > 0:
            url = reverse('admin:CRMapp_pedido_changelist') + '?cliente__id__exact={}'.format(obj.id)
            # Clasificación del cliente según el total de compras
            if total > 1000:
                badge_class = "badge-premium"
            elif total > 500:
                badge_class = "badge-gold"
            else:
                badge_class = "badge-info"
        
            return format_html(
                '<div class="client-status">'
                '<a href="{0}" class="badge {1}" style="text-decoration: none; color: white;">{2} pedido(s)</a> '
                '<span class="badge badge-success" data-toggle="tooltip" title="Total de compras">${3}</span>'
                '</div>', 
                url, badge_class, count, "{:.2f}".format(total)
            )
        return format_html('<span class="badge badge-secondary">Sin actividad</span>')
    total_pedidos.short_description = 'Actividad'
    total_pedidos.admin_order_field = 'pedidos_count'
    
    def resumen_pedidos(self, obj):
        # Verificar si es un objeto nuevo (aún no guardado en la base de datos)
        if not obj or not obj.pk:
            return mark_safe('<div class="alert alert-warning">'
                            '<i class="fas fa-info-circle"></i> '
                            'Guarde el cliente primero para ver el historial de pedidos.'
                            '</div>')
        
        pedidos = obj.pedidos.all().order_by('-fecha')[:5]
        if not pedidos:
            return mark_safe('<div class="alert alert-info">'
                            '<i class="fas fa-shopping-cart"></i> '
                            'Este cliente no tiene pedidos todavía. '
                            '<a href="/admin/CRMapp/pedido/add/?cliente={0}" class="alert-link">'
                            'Crear un nuevo pedido</a>'
                            '</div>'.format(obj.id))
        
        html = '<div class="table-responsive"><table class="table table-sm table-striped"><thead><tr>'
        html += '<th>ID</th><th>Fecha</th><th>Estado</th><th>Total</th><th>Acciones</th></tr></thead><tbody>'
        
        for pedido in pedidos:
            estado_badge = {
                'pendiente': 'warning',
                'en_proceso': 'info',
                'completado': 'success',
                'cancelado': 'danger'
            }.get(pedido.estado, 'secondary')
            
            url = reverse('admin:CRMapp_pedido_change', args=[pedido.id])
            html += '<tr>'
            html += '<td><a href="{0}">#{1}</a></td>'.format(url, pedido.id)
            html += '<td>{0}</td>'.format(pedido.fecha.strftime("%d/%m/%Y %H:%M"))
            html += '<td><span class="badge badge-{0}">{1}</span></td>'.format(
                estado_badge, dict(Pedido.ESTADO_CHOICES).get(pedido.estado))
            html += '<td>${0:.2f}</td>'.format(pedido.total)
            html += '<td><a href="{0}" class="btn btn-sm btn-outline-primary">Ver</a></td>'.format(url)
            html += '</tr>'
        
        html += '</tbody></table></div>'
        
        if obj.pedidos.count() > 5:
            url = reverse('admin:CRMapp_pedido_changelist') + '?cliente__id__exact={0}'.format(obj.id)
            html += '<a href="{0}" class="btn btn-sm btn-outline-primary">Ver todos los pedidos</a>'.format(url)
            
        return mark_safe(html)
    resumen_pedidos.short_description = 'Últimos pedidos'

    def fecha_formateada(self, obj):
        # Calcular tiempo desde registro
        from django.utils import timezone
        from datetime import timedelta
        
        ahora = timezone.now()
        diferencia = ahora - obj.fecha_registro
        
        if diferencia < timedelta(days=1):
            # Cliente nuevo (menos de 1 día)
            return format_html('<span class="badge badge-info">Nuevo</span> <span class="text-muted">{0}</span>', 
                              obj.fecha_registro.strftime("%d/%m/%Y"))
        elif diferencia < timedelta(days=7):
            # Cliente reciente (menos de 1 semana)
            return format_html('<span class="text-primary">{0}</span>', 
                              obj.fecha_registro.strftime("%d/%m/%Y"))
        elif diferencia > timedelta(days=365):
            # Cliente antiguo (más de 1 año)
            años = diferencia.days // 365
            return format_html('<span class="badge badge-success">{0} año(s)</span> <span class="text-muted">{1}</span>', 
                              años, obj.fecha_registro.strftime("%d/%m/%Y"))
        else:
            # Cliente normal
            return format_html('{0}', obj.fecha_registro.strftime("%d/%m/%Y"))
    
    fecha_formateada.short_description = 'Registro'
    fecha_formateada.admin_order_field = 'fecha_registro'
    
    def has_delete_permission(self, request, obj=None):
        # Si el cliente tiene pedidos, no permitir eliminar
        if obj and obj.pedidos.exists():
            return False
        return super().has_delete_permission(request, obj)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Personalizar campos
        if form.base_fields.get('nombre'):
            form.base_fields['nombre'].widget.attrs['placeholder'] = 'Nombre completo del cliente'
            form.base_fields['nombre'].widget.attrs['class'] = 'form-control-lg'
            form.base_fields['nombre'].help_text = 'Nombre y apellidos del cliente para identificación'
        
        if form.base_fields.get('email'):
            form.base_fields['email'].widget.attrs['placeholder'] = 'correo@ejemplo.com'
            form.base_fields['email'].help_text = 'Correo electrónico principal para contacto y notificaciones'
        
        if form.base_fields.get('direccion'):
            form.base_fields['direccion'].widget.attrs['rows'] = 3
            form.base_fields['direccion'].widget.attrs['placeholder'] = 'Calle, número, ciudad, CP'
            form.base_fields['direccion'].help_text = 'Ingresa la dirección completa incluyendo calle, número, ciudad y código postal'
        
        if form.base_fields.get('foto'):
            form.base_fields['foto'].help_text = '''
                <span class="help-block">
                    <i class="fas fa-info-circle text-primary"></i> 
                    Sube una imagen de perfil del cliente (formato recomendado: cuadrado, mínimo 200x200px)
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
            messages.success(request, f'¡Cliente {obj.nombre} creado exitosamente! Ahora puede añadir pedidos para este cliente.')
        super().save_model(request, obj, form, change)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:cliente_id>/detalle/',
                self.admin_site.admin_view(self.cliente_detail_view),
                name='CRMapp_cliente_detail', # Consistent naming
            ),
        ]
        return custom_urls + urls
    
    def cliente_detail_view(self, request, cliente_id):
        from django.shortcuts import render, get_object_or_404
        cliente = get_object_or_404(Cliente, pk=cliente_id)
        
        # Obtener los pedidos del cliente
        pedidos_cliente = Pedido.objects.filter(cliente=cliente).order_by('-fecha')

        context = {
            **self.admin_site.each_context(request), # Pasa el contexto base del admin
            'opts': self.model._meta, # Opciones del modelo para breadcrumbs, etc.
            'cliente': cliente,
            'pedidos_cliente': pedidos_cliente, # Pasamos la lista de objetos Pedido
            'title': f'Detalle de Cliente: {cliente.nombre}', # Título de la página
            'has_view_permission': self.has_view_permission(request, cliente),
            'has_change_permission': self.has_change_permission(request, cliente),
            'has_delete_permission': self.has_delete_permission(request, cliente),
        }
        return render(request, 'admin/CRMapp/cliente/cliente_detail.html', context)
    
    def acciones_cliente(self, obj):
        view_url = reverse('admin:CRMapp_cliente_detail', args=[obj.pk]) # Consistent naming
        edit_url = reverse('admin:CRMapp_cliente_change', args=[obj.pk])
        delete_url = reverse('admin:CRMapp_cliente_delete', args=[obj.pk])

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
    acciones_cliente.short_description = 'Acciones'
    
    class Media:
        css = {
            'all': ('admin/css/base.css', 'admin/css/detail.css')
        }