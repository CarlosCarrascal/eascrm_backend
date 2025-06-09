// JavaScript para mejorar la interacción en la administración de pedidos
document.addEventListener('DOMContentLoaded', function() {
    // Función para actualizar el cálculo de total
    function actualizarTotal() {
        const cantidadInput = document.querySelector('#id_cantidad');
        const productoSelect = document.querySelector('#id_producto');
        
        if (!cantidadInput || !productoSelect) return;
        
        const previewContainer = document.querySelector('#total-preview-container');
        
        // Si no existe el contenedor de previsualización, crearlo
        if (!previewContainer) {
            const newPreview = document.createElement('div');
            newPreview.id = 'total-preview-container';
            newPreview.className = 'total-preview';
            newPreview.innerHTML = '<h4>Previsualización del Total</h4><div id="total-preview-content"></div>';
            
            // Insertar después del campo de cantidad
            cantidadInput.parentNode.parentNode.appendChild(newPreview);
        }
        
        // Obtener los valores
        const cantidad = parseInt(cantidadInput.value) || 0;
        const productoId = productoSelect.value;
        
        if (cantidad > 0 && productoId) {
            // Hacer una petición para obtener el precio del producto
            fetch(`/admin/api/producto/${productoId}/precio/`)
                .then(response => response.json())
                .then(data => {
                    const precio = parseFloat(data.precio) || 0;
                    const total = precio * cantidad;
                    
                    const previewContent = document.querySelector('#total-preview-content');
                    if (previewContent) {
                        previewContent.innerHTML = `
                            <p><strong>Precio unitario:</strong> $${precio.toFixed(2)}</p>
                            <p><strong>Cantidad:</strong> ${cantidad}</p>
                            <p class="total-preview-value"><strong>Total estimado:</strong> $${total.toFixed(2)}</p>
                        `;
                    }
                })
                .catch(error => {
                    console.error('Error al obtener el precio:', error);
                });
        }
    }
    
    // Mejorar la selección de estado con indicadores visuales
    function mejorarSelectorEstado() {
        const estadoSelect = document.querySelector('#id_estado');
        
        if (!estadoSelect) return;
        
        // Agregar clases a las opciones según el estado
        Array.from(estadoSelect.options).forEach(option => {
            const value = option.value;
            
            if (value === 'pendiente') {
                option.classList.add('estado-pendiente');
            } else if (value === 'en_proceso') {
                option.classList.add('estado-proceso');
            } else if (value === 'completado') {
                option.classList.add('estado-completado');
            } else if (value === 'cancelado') {
                option.classList.add('estado-cancelado');
            }
        });
        
        // Cambiar el color de fondo del select según el valor seleccionado
        function actualizarEstiloEstado() {
            const selectedValue = estadoSelect.value;
            
            estadoSelect.classList.remove('estado-pendiente', 'estado-proceso', 'estado-completado', 'estado-cancelado');
            
            if (selectedValue === 'pendiente') {
                estadoSelect.classList.add('estado-pendiente');
            } else if (selectedValue === 'en_proceso') {
                estadoSelect.classList.add('estado-proceso');
            } else if (selectedValue === 'completado') {
                estadoSelect.classList.add('estado-completado');
            } else if (selectedValue === 'cancelado') {
                estadoSelect.classList.add('estado-cancelado');
            }
        }
        
        // Inicializar
        actualizarEstiloEstado();
        
        // Agregar evento para cambios
        estadoSelect.addEventListener('change', actualizarEstiloEstado);
    }
    
    // Inicializar funciones
    const cantidadInput = document.querySelector('#id_cantidad');
    const productoSelect = document.querySelector('#id_producto');
    
    if (cantidadInput) {
        cantidadInput.addEventListener('input', actualizarTotal);
    }
    
    if (productoSelect) {
        productoSelect.addEventListener('change', actualizarTotal);
    }
    
    mejorarSelectorEstado();
    
    // Inicializar una vez cargada la página
    setTimeout(actualizarTotal, 500);
}); 