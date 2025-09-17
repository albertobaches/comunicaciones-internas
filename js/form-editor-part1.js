// Funcionalidad para el editor de formularios - Parte 1: Inicialización y carga
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar almacenamiento de formularios si no existe
    if (!localStorage.getItem('forms')) {
        localStorage.setItem('forms', JSON.stringify([
            {
                id: 'form-1',
                name: 'Solicitud de Vacaciones',
                fields: [
                    {id: 'field-1', label: 'Fecha de inicio', type: 'date', fixed: false},
                    {id: 'field-2', label: 'Fecha de fin', type: 'date', fixed: false},
                    {id: 'field-3', label: 'Motivo', type: 'textarea', fixed: false}
                ]
            },
            {
                id: 'form-2',
                name: 'Informe de Proyecto',
                fields: [
                    {id: 'field-4', label: 'Nombre del proyecto', type: 'text', fixed: true},
                    {id: 'field-5', label: 'Estado actual', type: 'select', fixed: false, options: ['En progreso', 'Completado', 'Retrasado', 'Cancelado']},
                    {id: 'field-6', label: 'Descripción de avances', type: 'textarea', fixed: false}
                ]
            }
        ]));
    }

    // Cargar opciones de formularios en el selector
    loadFormOptions();
    
    // Cargar lista de formularios
    loadFormsList();
    
    // Configurar eventos para botones de formularios
    setupFormEvents();
});

// Cargar opciones de formularios en el selector
function loadFormOptions() {
    const templateSelect = document.getElementById('template-select');
    if (!templateSelect) return;
    
    // Limpiar opciones existentes
    templateSelect.innerHTML = '<option value="">Seleccionar formulario...</option>';
    
    // Obtener formularios
    const forms = JSON.parse(localStorage.getItem('forms')) || [];
    
    // Añadir opciones
    forms.forEach(form => {
        const option = document.createElement('option');
        option.value = form.id;
        option.textContent = form.name;
        templateSelect.appendChild(option);
    });
}

// Cargar lista de formularios
function loadFormsList() {
    const templatesList = document.getElementById('templates-list');
    if (!templatesList) return;
    
    // Limpiar lista existente
    templatesList.innerHTML = '';
    
    // Obtener formularios
    const forms = JSON.parse(localStorage.getItem('forms')) || [];
    
    // Añadir formularios a la lista
    forms.forEach(form => {
        const templateItem = document.createElement('div');
        templateItem.className = 'template-item';
        templateItem.innerHTML = `
            <div class="template-name">${form.name}</div>
            <div class="template-actions">
                <button class="btn-icon view-template" data-template="${form.id}" title="Ver Formulario">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn-icon edit-template" data-template="${form.id}" title="Editar Formulario">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn-icon use-template" data-template="${form.id}" title="Usar Formulario">
                    <i class="fas fa-file-import"></i>
                </button>
            </div>
        `;
        templatesList.appendChild(templateItem);
    });
}

// Configurar eventos para botones de formularios
function setupFormEvents() {
    // Botón para crear nuevo formulario
    const addTemplateBtn = document.getElementById('add-template');
    if (addTemplateBtn) {
        addTemplateBtn.addEventListener('click', function() {
            showFormEditorModal();
        });
    }

    // Botones para editar formularios
    document.querySelectorAll('.edit-template').forEach(button => {
        button.addEventListener('click', function() {
            const templateId = this.getAttribute('data-template');
            showFormEditorModal(templateId);
        });
    });

    // Botones para ver formularios
    document.querySelectorAll('.view-template').forEach(button => {
        button.addEventListener('click', function() {
            const templateId = this.getAttribute('data-template');
            showFormViewModal(templateId);
        });
    });

    // Botones para usar formularios
    document.querySelectorAll('.use-template').forEach(button => {
        button.addEventListener('click', function() {
            const templateId = this.getAttribute('data-template');
            showFormFillModal(templateId);
        });
    });

    // Botón para rellenar formulario desde el selector
    const fillTemplateBtn = document.getElementById('fill-template');
    if (fillTemplateBtn) {
        fillTemplateBtn.addEventListener('click', function() {
            const templateSelect = document.getElementById('template-select');
            if (templateSelect.value) {
                showFormFillModal(templateSelect.value);
            } else {
                alert('Por favor, seleccione un formulario primero.');
            }
        });
    }
}