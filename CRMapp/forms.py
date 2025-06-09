from django import forms
from .models import DetallePedido, Producto

class DetallePedidoForm(forms.ModelForm):
    class Meta:
        model = DetallePedido
        fields = ['producto', 'cantidad', 'precio_unitario']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacemos que precio_unitario sea readonly en el form, 
        # ya que se debe popular desde el producto o por el save del modelo.
        # Esto complementa el readonly_fields en el admin.
        if 'precio_unitario' in self.fields:
            self.fields['precio_unitario'].widget.attrs['readonly'] = True

        # Si estamos editando una instancia existente y hay un producto seleccionado,
        # podríamos mostrar el stock actual. Por ahora, nos enfocaremos en la validación.

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        producto = self.cleaned_data.get('producto')

        if producto and cantidad is not None:
            if cantidad <= 0:
                raise forms.ValidationError("La cantidad debe ser mayor que cero.")
            if cantidad > producto.stock:
                raise forms.ValidationError(
                    f"La cantidad solicitada ({cantidad}) excede el stock disponible ({producto.stock}) para {producto.nombre}."
                )
        elif not producto and cantidad is not None:
            # Esto no debería pasar si el producto es requerido, pero por si acaso.
            raise forms.ValidationError("Por favor, seleccione un producto.")
        
        return cantidad

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        
        # Asegurar que el precio unitario se establezca desde el producto
        # si se está creando un nuevo detalle o si el producto cambia.
        # Esto es un refuerzo a lo que hace el modelo, pero es bueno tenerlo en el form.
        if producto:
            # Si es una instancia nueva (no tiene ID) o el producto ha cambiado
            # (comparamos con la instancia inicial si existe)
            is_new = not self.instance.pk
            product_changed = not is_new and self.instance.producto != producto

            if is_new or product_changed:
                cleaned_data['precio_unitario'] = producto.precio
            elif 'precio_unitario' not in cleaned_data or not cleaned_data['precio_unitario']:
                # Si por alguna razón no está, lo ponemos.
                 cleaned_data['precio_unitario'] = producto.precio

        return cleaned_data
