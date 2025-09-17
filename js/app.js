document.addEventListener('DOMContentLoaded', function() {
    // Navegación entre pestañas
    const navLinks = document.querySelectorAll('nav a');
    const sections = document.querySelectorAll('main section');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remover clase active de todos los enlaces
            navLinks.forEach(link => link.classList.remove('active'));
            
            // Añadir clase active al enlace clickeado
            this.classList.add('active');
            
            // Obtener la sección a mostrar
            const targetSection = this.getAttribute('data-section');
            
            // Ocultar todas las secciones
            sections.forEach(section => section.classList.remove('active'));
            
            // Mostrar la sección seleccionada
            document.getElementById(targetSection).classList.add('active');
        });
    });
    
    // Manejo de mensajes en la bandeja de entrada
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        message.addEventListener('click', function() {
            // Aquí se implementaría la lógica para abrir el mensaje
            const messageId = this.getAttribute('data-id');
            console.log('Abriendo mensaje con ID:', messageId);
            
            // Marcar como leído si estaba sin leer
            if (this.classList.contains('unread')) {
                this.classList.remove('unread');
            }
            
            // Aquí se podría implementar la apertura del mensaje en una ventana modal
            // o redireccionar a una página de detalle
            window.location.href = `abrir.html?id=${messageId}`;
        });
    });
    
    // Manejo del formulario de nuevo mensaje
    const composeForm = document.getElementById('compose-form');
    if (composeForm) {
        composeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Aquí se implementaría la lógica para enviar el mensaje
            console.log('Enviando mensaje...');
            
            // Simulación de envío exitoso
            alert('Mensaje enviado correctamente');
            
            // Limpiar formulario
            this.reset();
        });
    }
    
    // Manejo del botón de cerrar sesión
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            // Aquí se implementaría la lógica para cerrar sesión
            console.log('Cerrando sesión...');
            
            // Simulación de cierre de sesión
            alert('Sesión cerrada correctamente');
            
            // Redireccionar a la página de login (si existe)
            // window.location.href = 'login.html';
        });
    }
    
    // Gestión de usuarios
    
    // Almacenamiento local de usuarios (simulación de base de datos)
    let users = [
        { id: 1, name: 'Juan Pérez', department: 'Ventas', email: 'juan.perez@empresa.com', password: 'password123', role: 'user' },
        { id: 2, name: 'María González', department: 'Recursos Humanos', email: 'maria.gonzalez@empresa.com', password: 'password123', role: 'user' },
        { id: 3, name: 'Carlos Rodríguez', department: 'IT', email: 'carlos.rodriguez@empresa.com', password: 'password123', role: 'admin' }
    ];
    
    // Función para guardar usuarios en localStorage
    function saveUsers() {
        localStorage.setItem('users', JSON.stringify(users));
    }
    
    // Función para cargar usuarios desde localStorage
    function loadUsers() {
        const storedUsers = localStorage.getItem('users');
        if (storedUsers) {
            users = JSON.parse(storedUsers);
        } else {
            saveUsers(); // Guardar los usuarios iniciales
        }
    }
    
    // Cargar usuarios al iniciar
    loadUsers();
    
    // Modal de usuario
    const userModal = document.getElementById('user-modal');
    const userForm = document.getElementById('user-form');
    const userModalTitle = document.getElementById('user-modal-title');
    let editingUserId = null;
    
    // Función para abrir el modal de usuario
    function openUserModal(user = null) {
        if (user) {
            userModalTitle.textContent = 'Editar Usuario';
            document.getElementById('user-name').value = user.name;
            document.getElementById('user-department').value = user.department;
            document.getElementById('user-email').value = user.email;
            document.getElementById('user-password').value = user.password;
            document.getElementById('user-role').value = user.role;
            editingUserId = user.id;
        } else {
            userModalTitle.textContent = 'Añadir Usuario';
            userForm.reset();
            editingUserId = null;
        }
        userModal.style.display = 'block';
    }
    
    // Función para cerrar el modal de usuario
    function closeUserModal() {
        userModal.style.display = 'none';
    }
    
    // Botón para añadir usuario
    const addUserBtn = document.getElementById('add-user');
    if (addUserBtn) {
        addUserBtn.addEventListener('click', function() {
            openUserModal();
        });
    }
    
    // Cerrar modal al hacer clic en la X o en Cancelar
    document.querySelectorAll('#user-modal .close-modal').forEach(element => {
        element.addEventListener('click', closeUserModal);
    });
    
    // Manejar envío del formulario de usuario
    if (userForm) {
        userForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const name = document.getElementById('user-name').value;
            const department = document.getElementById('user-department').value;
            const email = document.getElementById('user-email').value;
            const password = document.getElementById('user-password').value;
            const role = document.getElementById('user-role').value;
            
            if (editingUserId) {
                // Editar usuario existente
                const userIndex = users.findIndex(u => u.id == editingUserId);
                if (userIndex !== -1) {
                    users[userIndex] = {
                        ...users[userIndex],
                        name,
                        department,
                        email,
                        password,
                        role
                    };
                }
            } else {
                // Añadir nuevo usuario
                const newId = users.length > 0 ? Math.max(...users.map(u => u.id)) + 1 : 1;
                users.push({
                    id: newId,
                    name,
                    department,
                    email,
                    password,
                    role
                });
            }
            
            saveUsers();
            alert(editingUserId ? 'Usuario actualizado correctamente' : 'Usuario añadido correctamente');
            closeUserModal();
            location.reload(); // Recargar la página para mostrar los cambios
        });
    }
});