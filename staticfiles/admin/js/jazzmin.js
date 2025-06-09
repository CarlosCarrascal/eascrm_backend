/**
 * Jazzmin Minimalist Theme
 * JavaScript para mejorar la experiencia de usuario
 */

document.addEventListener('DOMContentLoaded', function() {
  // Polyfill para Popper.js
  if (typeof window.Popper === 'undefined') {
    window.Popper = {
      createPopper: function(referenceElement, popperElement, options) {
        // Implementación básica para posicionar tooltips
        function positionTooltip() {
          const refRect = referenceElement.getBoundingClientRect();
          popperElement.style.position = 'absolute';
          popperElement.style.top = (refRect.top - popperElement.offsetHeight - 10) + 'px';
          popperElement.style.left = (refRect.left + (refRect.width / 2) - (popperElement.offsetWidth / 2)) + 'px';
        }
        
        // Posicionar inicialmente
        positionTooltip();
        
        // Devolver objeto API
        return {
          update: positionTooltip,
          forceUpdate: positionTooltip,
          destroy: function() {}
        };
      }
    };
  }
  
  // Inicializar tooltips si jQuery y Bootstrap están disponibles
  if (typeof $ !== 'undefined' && typeof $.fn.tooltip !== 'undefined') {
    $('[data-toggle="tooltip"]').tooltip();
  }
  
  // Mejoras de usabilidad para el panel de administración
  function initAdminEnhancements() {
    // Añadir clases a las tablas para mejorar apariencia
    const adminTables = document.querySelectorAll('.results');
    adminTables.forEach(table => {
      table.classList.add('table', 'table-striped', 'table-hover');
    });
    
    // Añadir animaciones suaves a notificaciones
    const messages = document.querySelectorAll('.messagelist li');
    messages.forEach((message, index) => {
      message.style.animationDelay = (index * 0.1) + 's';
      message.classList.add('animated', 'fadeInDown');
    });
    
    // Mejorar experiencia en formularios
    const formRows = document.querySelectorAll('.form-row');
    formRows.forEach(row => {
      const inputs = row.querySelectorAll('input, select, textarea');
      inputs.forEach(input => {
        // Añadir clases para inputs
        if (input.type !== 'checkbox' && input.type !== 'radio') {
          input.classList.add('form-control');
        }
        
        // Animar focus
        input.addEventListener('focus', function() {
          this.closest('.form-row').classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
          this.closest('.form-row').classList.remove('focused');
        });
      });
    });
  }
  
  // Inicializar mejoras
  initAdminEnhancements();
  
  // Ejecutar mejoras cuando cambia el DOM (para cuando se cargan partes vía AJAX)
  const observer = new MutationObserver(function(mutations) {
    initAdminEnhancements();
  });
  
  // Configurar observador
  observer.observe(document.body, { 
    childList: true,
    subtree: true
  });
});

/**
 * Mejora las tablas con interactividad y estilos
 */
function enhanceTables() {
  const tables = document.querySelectorAll('.table');
  
  tables.forEach(table => {
    // Marcar la fila al hacer clic
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
      // Excluir filas que son cabeceras o tienen formularios
      if (row.querySelector('th') || row.querySelector('form')) return;
      
      // Hacer las filas clickeables si tienen enlaces
      const firstLink = row.querySelector('a');
      if (firstLink && !firstLink.getAttribute('onclick')) {
        row.style.cursor = 'pointer';
        row.addEventListener('click', function(e) {
          // No disparar si se hace click en botones o enlaces
          if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON' || 
              e.target.tagName === 'INPUT' || e.target.closest('a') || 
              e.target.closest('button')) {
            return;
          }
          firstLink.click();
        });
      }
    });
  });
}

/**
 * Mejora las notificaciones para hacerlas más elegantes
 */
function enhanceNotifications() {
  const alerts = document.querySelectorAll('.alert:not(.persistent)');
  
  alerts.forEach(alert => {
    // Añadir icono apropiado
    let icon = 'info-circle';
    if (alert.classList.contains('alert-success')) icon = 'check-circle';
    if (alert.classList.contains('alert-danger')) icon = 'exclamation-circle';
    if (alert.classList.contains('alert-warning')) icon = 'exclamation-triangle';
    
    // Solo añadir icono si no tiene uno ya
    if (!alert.querySelector('.fas')) {
      alert.innerHTML = `<i class="fas fa-${icon} mr-2"></i> ${alert.innerHTML}`;
    }
    
    // Hacer que las alertas sean descartables
    if (!alert.querySelector('.close')) {
      const closeBtn = document.createElement('button');
      closeBtn.className = 'close';
      closeBtn.setAttribute('type', 'button');
      closeBtn.setAttribute('data-dismiss', 'alert');
      closeBtn.setAttribute('aria-label', 'Close');
      closeBtn.innerHTML = '<span aria-hidden="true">&times;</span>';
      
      alert.appendChild(closeBtn);
      alert.classList.add('alert-dismissible');
      
      // Auto-ocultar después de 5 segundos
      setTimeout(() => {
        if (alert.parentNode) {
          alert.style.opacity = '0';
          alert.style.transition = 'opacity 0.5s ease';
          setTimeout(() => {
            if (alert.parentNode) alert.parentNode.removeChild(alert);
          }, 500);
        }
      }, 5000);
    }
  });
}

/**
 * Mejora la usabilidad de los formularios
 */
function enhanceForms() {
  // Resaltar el campo activo
  const formControls = document.querySelectorAll('.form-control');
  
  formControls.forEach(control => {
    control.addEventListener('focus', function() {
      const formGroup = this.closest('.form-group');
      if (formGroup) formGroup.classList.add('focused');
    });
    
    control.addEventListener('blur', function() {
      const formGroup = this.closest('.form-group');
      if (formGroup) formGroup.classList.remove('focused');
    });
  });
  
  // Mejorar presentación de errores de formulario
  const errorList = document.querySelectorAll('.errorlist');
  
  errorList.forEach(list => {
    list.classList.add('text-danger', 'pl-0', 'mt-1');
    list.style.listStyleType = 'none';
    list.style.fontSize = '0.875rem';
    
    const items = list.querySelectorAll('li');
    items.forEach(item => {
      item.innerHTML = `<i class="fas fa-exclamation-circle mr-1"></i> ${item.innerHTML}`;
    });
  });
} 