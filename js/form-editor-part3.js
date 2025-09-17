// Funcionalidad para el editor de formularios - Parte 3: Visualización y rellenado

// Función para mostrar el modal de visualización de formulario
function showFormViewModal(formId) {
    // Obtener formulario
    const forms = JSON.parse(localStorage.getItem('forms')) || [];
    const form = forms.find(f => f.id === formId);
    
    if (!form) return;
    
    // Crear modal si no existe
    let modal = document.getElementById('form-view-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'form-view-modal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2 id="form-view-title"></h2>
                    <span class="close-modal">&times;</span>
                </div>
                <div class="modal-body">
                    <div class="view-form-fields" id="view-form-fields"></div>
                </div>
                <div class="modal-footer">
                    <button id="close-view-btn" class="btn-primary">Cerrar</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        // Configurar eventos del modal
        modal.querySelector('.close-modal').addEventListener('click', function() {
            modal.style.display = 'none';
        });
        
        document.getElementById('close-view-btn').addEventListener('click', function() {
            modal.style.display = 'none';
        });
    }
    
    // Mostrar modal
    modal.style.display = 'flex';
    
    // Actualizar título
    document.getElementById('form-view-title').textContent = form.name;
    
    // Mostrar campos
    const viewFormFields = document.getElementById('view-form-fields');
    viewFormFields.innerHTML = '';
    
    form.fields.forEach(field => {
        const fieldItem = document.createElement('div');
        fieldItem.className = 'view-field-item';
        
        let fieldContent = `
            <div class="view-field-label">
                ${field.label}
                ${field.fixed ? '<span class="fixed-badge">Fijo</span>' : ''}
            </div>
            <div class="view-field-type">Tipo: ${getFieldTypeName(field.type)}</div>
        `;
        
        if (field.type === 'select' && field.options) {
            fieldContent += `
                <div class="view-field-options">
                    Opciones: ${field.options.join(', ')}
                </div>
            `;
        }
        
        fieldItem.innerHTML = fieldContent;
        viewFormFields.appendChild(fieldItem);
    });
}

// Función para mostrar el modal de rellenar formulario
function showFormFillModal(formId) {
    // Obtener formulario
    const forms = JSON.parse(localStorage.getItem('forms')) || [];
    const form = forms.find(f => f.id === formId);
    
    if (!form) return;
    
    // Crear modal si no existe
    let modal = document.getElementById('form-fill-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'form-fill-modal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2 id="form-fill-title"></h2>
                    <span class="close-modal">&times;</span>
                </div>
                <div class="modal-body">
                    <div class="fill-form-fields" id="fill-form-fields"></div>
                </div>
                <div class="modal-footer">
                    <button id="insert-filled-form-btn" class="btn-primary">Insertar en Mensaje</button>
                    <button id="cancel-fill-btn" class="btn-secondary">Cancelar</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        // Configurar eventos del modal
        modal.querySelector('.close-modal').addEventListener('click', function() {
            modal.style.display = 'none';
        });
        
        document.getElementById('cancel-fill-btn').addEventListener('click', function() {
            modal.style.display = 'none';
        });
        
        document.getElementById('insert-filled-form-btn').addEventListener('click', function() {
            insertFilledForm();
        });
    }
    
    // Mostrar modal
    modal.style.display = 'flex';
    
    // Actualizar título
    document.getElementById('form-fill-title').textContent = 'Rellenar: ' + form.name;
    
    // Mostrar campos para rellenar
    const fillFormFields = document.getElementById('fill-form-fields');
    fillFormFields.innerHTML = '';
    fillFormFields.setAttribute('data-form-id', formId);
    
    form.fields.forEach(field => {
        const fieldItem = document.createElement('div');
        fieldItem.className = 'field-item';
        fieldItem.setAttribute('data-field-id', field.id);
        
        let fieldInput = '';
        
        switch (field.type) {
            case 'text':
                fieldInput = `<input type="text" class="form-control field-value" ${field.fixed ? 'disabled' : ''}>`;
                break;
            case 'textarea':
                fieldInput = `<textarea class="form-control field-value" rows="3" ${field.fixed ? 'disabled' : ''}></textarea>`;
                break;
            case 'number':
                fieldInput = `<input type="number" class="form-control field-value" ${field.fixed ? 'disabled' : ''}>`;
                break;
            case 'date':
                fieldInput = `<input type="date" class="form-control field-value" ${field.fixed ? 'disabled' : ''}>`;
                break;
            case 'select':
                fieldInput = `<select class="form-control field-value" ${field.fixed ? 'disabled' : ''}>`;
                fieldInput += '<option value="">Seleccionar...</option>';
                if (field.options) {
                    field.options.forEach(option => {
                        fieldInput += `<option value="${option}">${option}</option>`;
                    });
                }
                fieldInput += '</select>';
                break;
        }
        
        fieldItem.innerHTML = `
            <div class="field-label">
                ${field.label}
                ${field.fixed ? '<span class="fixed-badge">Fijo</span>' : ''}
            </div>
            <div class="field-input">
                ${fieldInput}
            </div>
        `;
        
        fillFormFields.appendChild(fieldItem);
    });
    
    // Guardar ID del formulario en el botón de insertar
    document.getElementById('insert-filled-form-btn').setAttribute('data-form-id', formId);
}

// Función para insertar el formulario rellenado en el mensaje
function insertFilledForm() {
    const messageBody = document.getElementById('message-body');
    if (!messageBody) return;
    
    const formId = document.getElementById('insert-filled-form-btn').getAttribute('data-form-id');
    const forms = JSON.parse(localStorage.getItem('forms')) || [];
    const form = forms.find(f => f.id === formId);
    
    if (!form) return;
    
    // Recopilar valores de los campos
    const fillFormFields = document.getElementById('fill-form-fields');
    const fieldItems = fillFormFields.querySelectorAll('.field-item');
    
    let formHTML = `<div class="inserted-form" data-form-id="${formId}">`;
    formHTML += `<h3>${form.name}</h3>`;
    formHTML += '<table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">';
    
    fieldItems.forEach(item => {
        const fieldId = item.getAttribute('data-field-id');
        const field = form.fields.find(f => f.id === fieldId);
        
        if (!field) return;
        
        const fieldValue = item.querySelector('.field-value').value;
        
        formHTML += '<tr>';
        formHTML += `<td><strong>${field.label}:</strong></td>`;
        formHTML += `<td>${fieldValue || '(No completado)'}</td>`;
        formHTML += '</tr>';
    });
    
    formHTML += '</table></div>';
    
    // Insertar en el contenido del mensaje
    messageBody.value += formHTML;
    
    // Cerrar modal
    document.getElementById('form-fill-modal').style.display = 'none';
}

// Función auxiliar para obtener el nombre del tipo de campo
function getFieldTypeName(type) {
    const types = {
        'text': 'Texto',
        'textarea': 'Área de Texto',
        'number': 'Número',
        'date': 'Fecha',
        'select': 'Selección'
    };
    
    return types[type] || type;
}