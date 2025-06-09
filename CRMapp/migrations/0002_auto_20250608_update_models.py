from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('CRMapp', '0002_remove_pedido_recibo_producto_imagen'),
    ]

    operations = [
        # Las operaciones de añadir campos ya están en la migración automática 0003
        # Dejamos esta migración vacía para mantener la secuencia
    ] 