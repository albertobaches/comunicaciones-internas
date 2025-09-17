// Funcionalidad para el editor de formularios - Parte 2: Modales y edición

// Función para mostrar el modal de edición de formularios
function showFormEditorModal(formId = null) {
    // Crear modal si no existe
    let modal = document.getElementById('form-editor-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'form-editor-modal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2 id="form-editor-title">Nuevo Formulario</h2>
                    <span class="close-modal">&times;</span>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label for="form-name">Nombre del Formulario</label>
                        <input type="text" id="form-name" class="form-control" placeholder="Nombre del formulario">
                    </div>
                    <div class="form-group">
                        <label>Campos del Formulario</label>
                        <div class="form-fields" id="form-fields"></div>
                        <button id="add-field-btn" class="btn-secondary">
                            <i class="fas fa-plus"></i> Añadir Campo
                        </button>
                    </div>
                </div>
                <div class="modal-footer">
                    <button id="save-form-btn" class="btn-primary">Guardar Formulario</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        // Configurar eventos del modal
        modal.querySelector('.close-modal').addEventListener('click', function() {
            modal.style.display = 'none';
        });
        
        // Botón para añadir campo
        document.getElementById('add-field-btn').addEventListener('click', function() {
            addFieldToEditor();
        });
        
        // Botón para guardar formulario
        document.getElementById('save-form-btn').addEventListener('click', function() {
            saveForm();
        });
    }
    
    // Mostrar modal
    modal.style.display = 'flex';
    
    // Limpiar campos
    document.getElementById('form-name').value = '';
    document.getElementById('form-fields').innerHTML = '';
    
    // Si se está editando un formulario existente, cargar sus datos
    if (formId) {
        const forms = JSON.parse(localStorage.getItem('forms')) || [];
        const form = forms.find(f => f.id === formId);
        
        if (form) {
            document.getElementById('form-editor-title').textContent = 'Editar Formulario';
            document.getElementById('form-name').value = form.name;
            
            // Cargar campos
            form.fields.forEach(field => {
                addFieldToEditor(field);
            });
            
            // Guardar ID del formulario en el botón de guardar
            document.getElementById('save-form-btn').setAttribute('data-id', formId);
        }
    } else {
        document.getElementById('form-editor-title').textContent = 'Nuevo Formulario';
        document.getElementById('save-form-btn').removeAttribute('data-id');
        
        // Añadir un campo por defecto
        addFieldToEditor();
    }
}

// Función para añadir un campo al editor
function addFieldToEditor(fieldData = null) {
    const formFields = document.getElementById('form-fields');
    const fieldId = 'field-' + Date.now();
    
    const fieldItem = document.createElement('div');
    fieldItem.className = 'field-item';
    fieldItem.id = fieldId;
    
    fieldItem.innerHTML = `
        <div class="field-header">
            <span>Campo de Formulario</span>
            <button class="remove-field" title="Eliminar Campo">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="field-content">
            <div class="field-row">
                <div class="field-group">
                    <label for="${fieldId}-label">Etiqueta</label>
                    <input type="text" id="${fieldId}-label" class="form-control field-label" placeholder="Etiqueta del campo" value="${fieldData ? fieldData.label : ''}">
                </div>
                <div class="field-group">
                    <label for="${fieldId}-type">Tipo</label>
                    <select id="${fieldId}-type" class="form-control field-type">
                        <option value="text" ${fieldData && fieldData.type === 'text' ? 'selected' : ''}>Texto</option>
                        <option value="textarea" ${fieldData && fieldData.type === 'textarea' ? 'selected' : ''}>Área de Texto</option>
                        <option value="number" ${fieldData && fieldData.type === 'number' ? 'selected' : ''}>Número</option>
                        <option value="date" ${fieldData && fieldData.type === 'date' ? 'selected' : ''}>Fecha</option>
                        <option value="select" ${fieldData && fieldData.type === 'select' ? 'selected' : ''}>Selección</option>
                    </select>
                </div>
            </div>
            <div class="field-row select-options" style="display: ${fieldData && fieldData.type === 'select' ? 'flex' : 'none'}">
                <div class="field-group">
                    <label for="${fieldId}-options">Opciones (separadas por comas)</label>
                    <input type="text" id="${fieldId}-options" class="form-control field-options" placeholder="Opción 1, Opción 2, Opción 3" value="${fieldData && fieldData.options ? fieldData.options.join(', ') : ''}">
                </div>
            </div>
            <div class="field-row">
                <div class="field-fixed-group">
                    <input type="checkbox" id="${fieldId}-fixed" class="field-fixed" ${fieldData && fieldData.fixed ? 'checked' : ''}>
                    <label for="${fieldId}-fixed">Campo Fijo</label>
                    <div class="tooltip">Los campos fijos no pueden ser modificados por el destinatario al rellenar el formulario.</div>
                </div>
            </div>
        </div>
    `;
    
    formFields.appendChild(fieldItem);
    
    // Configurar evento para eliminar campo
    fieldItem.querySelector('.remove-field').addEventListener('click', function() {
        formFields.removeChild(fieldItem);
    });
    
    // Configurar evento para mostrar/ocultar opciones de selección
    const typeSelect = fieldItem.querySelector('.field-type');
    typeSelect.addEventListener('change', function() {
        const selectOptions = fieldItem.querySelector('.select-options');
        selectOptions.style.display = this.value === 'select' ? 'flex' : 'none';
    });
}

// Función para guardar el formulario
function saveForm() {
    const formName = document.getElementById('form-name').value.trim();
    if (!formName) {
        alert('Por favor, ingrese un nombre para el formulario.');
        return;
    }
    
    const formFields = document.getElementById('form-fields');
    const fieldItems = formFields.querySelectorAll('.field-item');
    
    if (fieldItems.length === 0) {
        alert('Por favor, añada al menos un campo al formulario.');
        return;
    }
    
    const fields = [];
    
    // Recopilar datos de los campos
    fieldItems.forEach(item => {
        const fieldId = item.id;
        const label = document.getElementById(`${fieldId}-label`).value.trim();
        const type = document.getElementById(`${fieldId}-type`).value;
        const fixed = document.getElementById(`${fieldId}-fixed`).checked;
        
        if (!label) {
            alert('Por favor, complete la etiqueta para todos los campos.');
            return;
        }
        
        const field = {
            id: fieldId,
            label,
            type,
            fixed
        };
        
        // Si es tipo select, recopilar opciones
        if (type === 'select') {
            const optionsInput = document.getElementById(`${fieldId}-options`).value.trim();
            if (!optionsInput) {
                alert('Por favor, ingrese opciones para los campos de selección.');
                return;
            }
            
            field.options = optionsInput.split(',').map(opt => opt.trim()).filter(opt => opt);
            
            if (field.options.length === 0) {
                alert('Por favor, ingrese opciones válidas para los campos de selección.');
                return;
            }
        }
        
        fields.push(field);
    });
    
    // Obtener formularios existentes
    const forms = JSON.parse(localStorage.getItem('forms')) || [];
    
    // Verificar si es edición o creación
    const saveBtn = document.getElementById('save-form-btn');
    const formId = saveBtn.getAttribute('data-id');
    
    if (formId) {
        // Editar formulario existente
        const formIndex = forms.findIndex(f => f.id === formId);
        if (formIndex !== -1) {
            forms[formIndex] = {
                id: formId,
                name: formName,
                fields
            };
        }
    } else {
        // Crear nuevo formulario
        forms.push({
            id: 'form-' + Date.now(),
            name: formName,
            fields
        });
    }
    
    // Guardar formularios
    localStorage.setItem('forms', JSON.stringify(forms));
    
    // Cerrar modal
    document.getElementById('form-editor-modal').style.display = 'none';
    
    // Actualizar la interfaz
    alert('Formulario guardado correctamente.');
    location.reload();
}