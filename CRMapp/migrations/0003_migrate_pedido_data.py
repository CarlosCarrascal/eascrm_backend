from django.db import migrations

def migrar_pedidos(apps, schema_editor):
    # Obtener los modelos
    Pedido = apps.get_model('CRMapp', 'Pedido')
    DetallePedido = apps.get_model('CRMapp', 'DetallePedido')
    
    # Iterar sobre los pedidos existentes
    for pedido in Pedido.objects.all():
        # Si el pedido tiene los campos antiguos producto y cantidad
        if hasattr(pedido, 'producto') and hasattr(pedido, 'cantidad'):
            try:
                producto = pedido.producto
                cantidad = pedido.cantidad
                
                # Crear un nuevo detalle de pedido
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio
                )
            except Exception as e:
                print(f"Error migrando pedido {pedido.id}: {e}")

class Migration(migrations.Migration):

    dependencies = [
        ('CRMapp', '0003_remove_pedido_cantidad_remove_pedido_producto_and_more'),
    ]

    operations = [
        migrations.RunPython(migrar_pedidos, migrations.RunPython.noop),
    ] 