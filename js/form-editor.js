// Funcionalidad para el editor de formularios
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar almacenamiento de formularios si no existe
    if (!localStorage.getItem('forms')) {
        localStorage.setItem('forms', JSON.stringify([
            {
                id: 'form-1',
                name: 'Solicitud de Cambio de Horario, Día Libre o Vacaciones',
                fields: [
                    {id: 'field-1', label: 'PARA: SECCION DE HORARIOS DEL PERSONAL', type: 'text', fixed: true, value: 'SECCION DE HORARIOS DEL PERSONAL'},
                    {id: 'field-2', label: 'FECHA', type: 'date', fixed: false},
                    {id: 'field-3', label: 'VIA: DIRECTOR EJECUTIVO', type: 'text', fixed: true, value: 'DIRECTOR EJECUTIVO (FIRMA DEL DIRECTOR EJECUTIVO APROBANDOLO)'},
                    {id: 'field-4', label: 'DE: (NOMBRE Y PUESTO DEL EMPLEADO QUE HACE LA PETICION)', type: 'text', fixed: false},
                    {id: 'field-5', label: 'SOLICITUD DE CAMBIO DE HORARIO, DIA LIBRE O VACACIONES COMO APLIQUE', type: 'text', fixed: true, value: 'SOLICITUD DE CAMBIO DE HORARIO, DIA LIBRE O VACACIONES COMO APLIQUE'},
                    {id: 'field-6', label: 'INDICA CLARAMENTE POR CUAL DE LAS RAZONES ES LA PETICION Y PORQUE:', type: 'textarea', fixed: false},
                    {id: 'field-7', label: 'INDICA CLARAMENTE LAS FECHAS Y HORAS QUE DEBERÍAS DE VENIR O ESTAN PREVISTAS EN TU HORARIO PERO ESTAS SOLICITANDO NO VENIR O CAMBIAR Y POR CUALES LAS CAMBIARÍAS SI ES EL CASO:', type: 'textarea', fixed: false},
                    {id: 'field-8', label: 'OPCIONAL: Si ya has hablado con un compañero para que te cambie el turno sin el permiso del superior, puede que no sea válido ya que el superior puede tener otros planes, en cualquier caso puedes sugerir tu recomendación, especifica quien y qué días y/o horas.', type: 'textarea', fixed: false},
                    {id: 'field-9', label: 'FIRMA CON TU NOMBRE Y', type: 'text', fixed: false}
                ]
            },
            {
                id: 'form-2',
                name: 'Solicitud de Vacaciones Simple',
                fields: [
                    {id: 'field-10', label: 'Fecha de inicio', type: 'date', fixed: false},
                    {id: 'field-11', label: 'Fecha de fin', type: 'date', fixed: false},
                    {id: 'field-12', label: 'Motivo', type: 'textarea', fixed: false}
                ]
            },
            {
                id: 'form-3',
                name: 'Informe de Proyecto',
                fields: [
                    {id: 'field-13', label: 'Nombre del proyecto', type: 'text', fixed: false},
                    {id: 'field-14', label: 'Estado actual', type: 'select', fixed: false, options: ['En progreso', 'Completado', 'Retrasado', 'Cancelado']},
                    {id: 'field-15', label: 'Descripción de avances', type: 'textarea', fixed: false}
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

    // Botones para editar formularios (usar delegación de eventos)
    document.addEventListener('click', function(e) {
        if (e.target.closest('.edit-template')) {
            const templateId = e.target.closest('.edit-template').getAttribute('data-template');
            showFormEditorModal(templateId);
        }
        
        if (e.target.closest('.view-template')) {
            const templateId = e.target.closest('.view-template').getAttribute('data-template');
            showFormViewModal(templateId);
        }
        
        if (e.target.closest('.use-template')) {
            const templateId = e.target.closest('.use-template').getAttribute('data-template');
            showFormFillModal(templateId);
        }
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
                    <div class="help-section">
                        <div class="simple-help">
                            <p><strong>💡 Ayuda rápida:</strong></p>
                            <p>• <strong>Campo normal:</strong> La persona escribe (ej: su nombre)</p>
                            <p>• <strong>Campo fijo:</strong> Ya está escrito (ej: "Departamento: RRHH")</p>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="form-name">Nombre del Formulario</label>
                        <input type="text" id="form-name" class="form-control" placeholder="Ej: Solicitud de Vacaciones, Informe de Proyecto...">
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
                    <button id="cancel-form-btn" class="btn-secondary">Cancelar</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        // Configurar eventos del modal
        modal.querySelector('.close-modal').addEventListener('click', function() {
            modal.style.display = 'none';
        });
        
        document.getElementById('cancel-form-btn').addEventListener('click', function() {
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
        
        // Botón para mostrar/ocultar ayuda
        document.getElementById('toggle-help').addEventListener('click', function() {
            const helpContent = document.getElementById('help-content');
            const isVisible = helpContent.style.display !== 'none';
            helpContent.style.display = isVisible ? 'none' : 'block';
            this.innerHTML = isVisible ? 
                '<i class="fas fa-question-circle"></i> ¿Cómo crear un formulario?' : 
                '<i class="fas fa-times"></i> Ocultar ayuda';
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
            <span>Campo ${formFields.children.length + 1}</span>
            <button class="remove-field" title="Eliminar">×</button>
        </div>
        <div class="field-content">
            <div class="field-row">
                <label>Nombre del campo:</label>
                <input type="text" id="${fieldId}-label" class="form-control field-label" placeholder="Ej: Nombre, Fecha, Departamento..." value="${fieldData ? fieldData.label : ''}">
            </div>
            
            <div class="field-row">
                <label>¿Qué tipo de campo es?</label>
                <select id="${fieldId}-type" class="form-control field-type">
                    <option value="text" ${fieldData && fieldData.type === 'text' ? 'selected' : ''}>Texto</option>
                    <option value="textarea" ${fieldData && fieldData.type === 'textarea' ? 'selected' : ''}>Texto largo</option>
                    <option value="date" ${fieldData && fieldData.type === 'date' ? 'selected' : ''}>Fecha</option>
                    <option value="select" ${fieldData && fieldData.type === 'select' ? 'selected' : ''}>Lista de opciones</option>
                </select>
            </div>
            
            <div class="field-row select-options" style="display: ${fieldData && fieldData.type === 'select' ? 'block' : 'none'}">
                <label>Opciones (separadas por coma):</label>
                <input type="text" id="${fieldId}-options" class="form-control field-options" placeholder="Urgente, Normal, Baja" value="${fieldData && fieldData.options ? fieldData.options.join(', ') : ''}">
            </div>
            
            <div class="field-row">
                <label>¿Quién llena este campo?</label>
                <div class="simple-options">
                    <label class="simple-option ${!fieldData || !fieldData.fixed ? 'selected' : ''}">
                        <input type="radio" id="${fieldId}-editable" name="${fieldId}-fieldtype" value="editable" ${!fieldData || !fieldData.fixed ? 'checked' : ''}>
                        <span class="option-text">
                            <strong>La persona que llena el formulario</strong>
                            <small>Ejemplo: Su nombre, comentarios</small>
                        </span>
                    </label>
                    <label class="simple-option ${fieldData && fieldData.fixed ? 'selected' : ''}">
                        <input type="radio" id="${fieldId}-fixed" name="${fieldId}-fieldtype" value="fixed" ${fieldData && fieldData.fixed ? 'checked' : ''}>
                        <span class="option-text">
                            <strong>Ya está definido (no cambia)</strong>
                            <small>Ejemplo: Departamento, Tipo de solicitud</small>
                        </span>
                    </label>
                </div>
            </div>
            
            <div class="field-row fixed-value-section" style="display: ${fieldData && fieldData.fixed ? 'block' : 'none'}">
                <label>¿Qué valor tiene?</label>
                <input type="text" id="${fieldId}-value" class="form-control field-value" placeholder="Ej: Recursos Humanos" value="${fieldData && fieldData.value ? fieldData.value : ''}">
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
    
    // Configurar eventos para los radio buttons de tipo de campo
    const editableRadio = fieldItem.querySelector(`#${fieldId}-editable`);
    const fixedRadio = fieldItem.querySelector(`#${fieldId}-fixed`);
    const fixedValueSection = fieldItem.querySelector('.fixed-value-section');
    
    editableRadio.addEventListener('change', function() {
        if (this.checked) {
            fixedValueSection.style.display = 'none';
        }
    });
    
    fixedRadio.addEventListener('change', function() {
        if (this.checked) {
            fixedValueSection.style.display = 'flex';
        }
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
    let hasError = false;
    
    // Recopilar datos de los campos
    fieldItems.forEach(item => {
        const fieldId = item.id;
        const label = document.getElementById(`${fieldId}-label`).value.trim();
        const type = document.getElementById(`${fieldId}-type`).value;
        const fixedRadio = document.getElementById(`${fieldId}-fixed`);
        const fixed = fixedRadio.checked;
        
        if (!label) {
            alert('Por favor, complete la etiqueta para todos los campos.');
            hasError = true;
            return;
        }
        
        const field = {
            id: fieldId,
            label,
            type,
            fixed
        };
        
        // Si es campo fijo, recopilar el valor fijo
        if (fixed) {
            const valueInput = document.getElementById(`${fieldId}-value`);
            if (valueInput) {
                const value = valueInput.value.trim();
                if (!value) {
                    alert('Por favor, ingrese un valor para todos los campos fijos.');
                    hasError = true;
                    return;
                }
                field.value = value;
            }
        }
        
        // Si es tipo select, recopilar opciones
        if (type === 'select') {
            const optionsInput = document.getElementById(`${fieldId}-options`).value.trim();
            if (!optionsInput) {
                alert('Por favor, ingrese opciones para los campos de selección.');
                hasError = true;
                return;
            }
            
            field.options = optionsInput.split(',').map(opt => opt.trim()).filter(opt => opt);
            
            if (field.options.length === 0) {
                alert('Por favor, ingrese opciones válidas para los campos de selección.');
                hasError = true;
                return;
            }
        }
        
        fields.push(field);
    });
    
    if (hasError) return;
    
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
    loadFormOptions();
    loadFormsList();
    alert('Formulario guardado correctamente.');
}

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
        fieldItem.setAttribute('data-field-fixed', field.fixed);
        
        let fieldInput = '';
        
        switch (field.type) {
            case 'text':
                const textValue = field.fixed && field.value ? field.value : '';
                fieldInput = `<input type="text" class="form-control field-value" value="${textValue}" ${field.fixed ? 'disabled' : ''}>`;
                break;
            case 'textarea':
                const textareaValue = field.fixed && field.value ? field.value : '';
                fieldInput = `<textarea class="form-control field-value" rows="3" ${field.fixed ? 'disabled' : ''}>${textareaValue}</textarea>`;
                break;
            case 'number':
                const numberValue = field.fixed && field.value ? field.value : '';
                fieldInput = `<input type="number" class="form-control field-value" value="${numberValue}" ${field.fixed ? 'disabled' : ''}>`;
                break;
            case 'date':
                const dateValue = field.fixed && field.value ? field.value : '';
                fieldInput = `<input type="date" class="form-control field-value" value="${dateValue}" ${field.fixed ? 'disabled' : ''}>`;
                break;
            case 'select':
                fieldInput = `<select class="form-control field-value" ${field.fixed ? 'disabled' : ''}>`;
                fieldInput += '<option value="">Seleccionar...</option>';
                if (field.options) {
                    field.options.forEach(option => {
                        const selected = field.fixed && field.value === option ? 'selected' : '';
                        fieldInput += `<option value="${option}" ${selected}>${option}</option>`;
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
    
    let formHTML = `\n\n--- ${form.name} ---\n`;
    
    fieldItems.forEach(item => {
        const fieldId = item.getAttribute('data-field-id');
        const field = form.fields.find(f => f.id === fieldId);
        
        if (!field) return;
        
        const fieldValue = item.querySelector('.field-value').value;
        
        formHTML += `${field.label}: ${fieldValue || '(No completado)'}\n`;
    });
    
    formHTML += `--- Fin ${form.name} ---\n\n`;
    
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