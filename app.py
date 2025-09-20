#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask application for Render deployment
Complete communications system with JWT authentication and RBAC
"""

from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
import os
import json
import base64
import hmac
import hashlib
import time
import functools
from database_postgres import UserDatabase

app = Flask(__name__)
CORS(app)

# Inicializar base de datos
db = UserDatabase()

# Clave secreta para JWT
JWT_SECRET = "mi_clave_secreta_super_segura_2024"

# Funciones JWT
def base64url_encode(data):
    """Codifica en base64url"""
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def base64url_decode(data):
    """Decodifica de base64url"""
    padding = 4 - len(data) % 4
    if padding != 4:
        data += '=' * padding
    return base64.urlsafe_b64decode(data)

def create_jwt(payload):
    """Crear token JWT"""
    header = {
        "alg": "HS256",
        "typ": "JWT"
    }
    
    # Agregar timestamp de expiración (24 horas)
    payload['exp'] = int(time.time()) + 86400
    
    # Codificar header y payload
    header_encoded = base64url_encode(json.dumps(header).encode('utf-8'))
    payload_encoded = base64url_encode(json.dumps(payload).encode('utf-8'))
    
    # Crear firma
    message = f"{header_encoded}.{payload_encoded}"
    signature = hmac.new(
        JWT_SECRET.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    signature_encoded = base64url_encode(signature)
    
    return f"{message}.{signature_encoded}"

def verify_jwt(token):
    """Verificar token JWT"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        header_encoded, payload_encoded, signature_encoded = parts
        
        # Verificar firma
        message = f"{header_encoded}.{payload_encoded}"
        expected_signature = hmac.new(
            JWT_SECRET.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        received_signature = base64url_decode(signature_encoded)
        
        if not hmac.compare_digest(expected_signature, received_signature):
            return None
        
        # Decodificar payload
        payload = json.loads(base64url_decode(payload_encoded))
        
        # Verificar expiración
        if payload.get('exp', 0) < time.time():
            return None
        
        return payload
    except:
        return None

def require_auth(f):
    """Decorador para requerir autenticación"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Token de autenticación requerido'}), 401
        
        token = auth_header[7:]  # Remover "Bearer "
        payload = verify_jwt(token)
        
        if not payload:
            return jsonify({'success': False, 'message': 'Token inválido o expirado'}), 401
        
        request.current_user = payload
        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    """Decorador para requerir rol de administrador"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if request.current_user.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Acceso denegado. Se requiere rol de administrador'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Plantilla HTML principal
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Centro de Comunicaciones Internas</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .logo {
            font-size: 3rem;
            margin-bottom: 10px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5rem;
        }
        
        .subtitle {
            color: #666;
            font-size: 1.2rem;
        }
        
        .auth-section {
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }
        
        input[type="text"], input[type="password"], textarea, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input[type="text"]:focus, input[type="password"]:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: transform 0.2s;
            margin: 5px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
        }
        
        .btn-secondary {
            background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
        }
        
        .hidden {
            display: none;
        }
        
        .user-info {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .communications-section {
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .communication-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
        }
        
        .communication-meta {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 5px;
        }
        
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .alert-success {
            background-color: #d4edda;
            border-color: #c3e6cb;
            color: #155724;
        }
        
        .alert-error {
            background-color: #f8d7da;
            border-color: #f5c6cb;
            color: #721c24;
        }
        
        .tabs {
            display: flex;
            margin-bottom: 20px;
        }
        
        .tab {
            background: #f8f9fa;
            padding: 12px 24px;
            border: none;
            cursor: pointer;
            border-radius: 8px 8px 0 0;
            margin-right: 5px;
            font-weight: bold;
        }
        
        .tab.active {
            background: #667eea;
            color: white;
        }
        
        .tab-content {
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 0 15px 15px 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🏢</div>
            <h1>Centro de Comunicaciones Internas</h1>
            <p class="subtitle">Sistema de gestión de comunicaciones empresariales</p>
        </div>
        
        <!-- Sección de autenticación -->
        <div id="auth-section" class="auth-section">
            <h2>Iniciar Sesión</h2>
            <div id="auth-message"></div>
            <form id="login-form">
                <div class="form-group">
                    <label for="username">Usuario:</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Contraseña:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="btn">Iniciar Sesión</button>
            </form>
            <p style="margin-top: 20px; color: #666;">
                <strong>Usuarios de prueba:</strong><br>
                Admin: admin / admin123<br>
                Usuario: usuario1 / pass123
            </p>
        </div>
        
        <!-- Sección principal (oculta inicialmente) -->
        <div id="main-section" class="hidden">
            <div class="user-info">
                <h3>Bienvenido, <span id="user-name"></span></h3>
                <p>Rol: <span id="user-role"></span></p>
                <button onclick="logout()" class="btn btn-secondary">Cerrar Sesión</button>
            </div>
            
            <div class="tabs">
                <button class="tab active" onclick="showTab('communications')">Comunicaciones</button>
                <button class="tab" onclick="showTab('send')">Enviar</button>
                <button class="tab" id="users-tab" onclick="showTab('users')" style="display: none;">Usuarios</button>
            </div>
            
            <!-- Tab de Comunicaciones -->
            <div id="communications-tab" class="tab-content">
                <h3>Mis Comunicaciones</h3>
                <div id="communications-list"></div>
            </div>
            
            <!-- Tab de Enviar -->
            <div id="send-tab" class="tab-content hidden">
                <h3>Enviar Comunicación</h3>
                <div id="send-message"></div>
                <form id="send-form">
                    <div class="form-group">
                        <label for="recipient">Destinatario:</label>
                        <select id="recipient" name="recipient" required>
                            <option value="">Seleccionar destinatario...</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="subject">Asunto:</label>
                        <input type="text" id="subject" name="subject" required>
                    </div>
                    <div class="form-group">
                        <label for="message">Mensaje:</label>
                        <textarea id="message" name="message" rows="5" required></textarea>
                    </div>
                    <button type="submit" class="btn">Enviar Comunicación</button>
                </form>
            </div>
            
            <!-- Tab de Usuarios (solo admin) -->
            <div id="users-tab-content" class="tab-content hidden">
                <h3>Gestión de Usuarios</h3>
                <div id="users-message"></div>
                <button onclick="showAddUserForm()" class="btn">Agregar Usuario</button>
                <div id="users-list"></div>
                
                <!-- Formulario para agregar usuario -->
                <div id="add-user-form" class="hidden" style="margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                    <h4>Agregar Nuevo Usuario</h4>
                    <form id="new-user-form">
                        <div class="form-group">
                            <label for="new-username">Usuario:</label>
                            <input type="text" id="new-username" name="username" required>
                        </div>
                        <div class="form-group">
                            <label for="new-password">Contraseña:</label>
                            <input type="password" id="new-password" name="password" required>
                        </div>
                        <div class="form-group">
                            <label for="new-role">Rol:</label>
                            <select id="new-role" name="role" required>
                                <option value="user">Usuario</option>
                                <option value="admin">Administrador</option>
                            </select>
                        </div>
                        <button type="submit" class="btn">Crear Usuario</button>
                        <button type="button" onclick="hideAddUserForm()" class="btn btn-secondary">Cancelar</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let currentUser = null;
        let authToken = null;
        
        // Verificar si hay token guardado
        document.addEventListener('DOMContentLoaded', function() {
            const savedToken = localStorage.getItem('authToken');
            if (savedToken) {
                verifyToken(savedToken);
            }
        });
        
        // Función para verificar token
        async function verifyToken(token) {
            try {
                const response = await fetch('/verify-token', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        authToken = token;
                        currentUser = data.user;
                        showMainSection();
                        return;
                    }
                }
            } catch (error) {
                console.error('Error verificando token:', error);
            }
            
            // Si llegamos aquí, el token no es válido
            localStorage.removeItem('authToken');
            showAuthSection();
        }
        
        // Manejar login
        document.getElementById('login-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    authToken = data.token;
                    currentUser = data.user;
                    localStorage.setItem('authToken', authToken);
                    showMainSection();
                } else {
                    showMessage('auth-message', data.message, 'error');
                }
            } catch (error) {
                showMessage('auth-message', 'Error de conexión', 'error');
            }
        });
        
        // Mostrar sección principal
        function showMainSection() {
            document.getElementById('auth-section').classList.add('hidden');
            document.getElementById('main-section').classList.remove('hidden');
            document.getElementById('user-name').textContent = currentUser.username;
            document.getElementById('user-role').textContent = currentUser.role;
            
            // Mostrar tab de usuarios si es admin
            if (currentUser.role === 'admin') {
                document.getElementById('users-tab').style.display = 'block';
            }
            
            loadCommunications();
            loadUsers();
        }
        
        // Mostrar sección de autenticación
        function showAuthSection() {
            document.getElementById('auth-section').classList.remove('hidden');
            document.getElementById('main-section').classList.add('hidden');
        }
        
        // Cerrar sesión
        function logout() {
            localStorage.removeItem('authToken');
            authToken = null;
            currentUser = null;
            showAuthSection();
        }
        
        // Mostrar tabs
        function showTab(tabName) {
            // Ocultar todos los tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.add('hidden');
            });
            
            // Remover clase active de todos los tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Mostrar tab seleccionado
            if (tabName === 'communications') {
                document.getElementById('communications-tab').classList.remove('hidden');
                document.querySelector('[onclick="showTab(\'communications\')"]').classList.add('active');
            } else if (tabName === 'send') {
                document.getElementById('send-tab').classList.remove('hidden');
                document.querySelector('[onclick="showTab(\'send\')"]').classList.add('active');
            } else if (tabName === 'users') {
                document.getElementById('users-tab-content').classList.remove('hidden');
                document.querySelector('[onclick="showTab(\'users\')"]').classList.add('active');
            }
        }
        
        // Cargar comunicaciones
        async function loadCommunications() {
            try {
                const response = await fetch('/get-communications', {
                    headers: {
                        'Authorization': `Bearer ${authToken}`
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const list = document.getElementById('communications-list');
                    list.innerHTML = '';
                    
                    if (data.communications.length === 0) {
                        list.innerHTML = '<p>No hay comunicaciones.</p>';
                    } else {
                        data.communications.forEach(comm => {
                            const item = document.createElement('div');
                            item.className = 'communication-item';
                            item.innerHTML = `
                                <div class="communication-meta">
                                    De: ${comm.sender} | Para: ${comm.recipient} | ${new Date(comm.timestamp).toLocaleString()}
                                </div>
                                <strong>${comm.subject}</strong>
                                <p>${comm.message}</p>
                            `;
                            list.appendChild(item);
                        });
                    }
                }
            } catch (error) {
                console.error('Error cargando comunicaciones:', error);
            }
        }
        
        // Cargar usuarios para el select
        async function loadUsers() {
            try {
                const response = await fetch('/get-users', {
                    headers: {
                        'Authorization': `Bearer ${authToken}`
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const select = document.getElementById('recipient');
                    select.innerHTML = '<option value="">Seleccionar destinatario...</option>';
                    
                    data.users.forEach(user => {
                        if (user.username !== currentUser.username) {
                            const option = document.createElement('option');
                            option.value = user.username;
                            option.textContent = `${user.username} (${user.role})`;
                            select.appendChild(option);
                        }
                    });
                    
                    // Si es admin, cargar también la lista de usuarios
                    if (currentUser.role === 'admin') {
                        loadUsersList(data.users);
                    }
                }
            } catch (error) {
                console.error('Error cargando usuarios:', error);
            }
        }
        
        // Cargar lista de usuarios (para admin)
        function loadUsersList(users) {
            const list = document.getElementById('users-list');
            list.innerHTML = '<h4>Usuarios del Sistema</h4>';
            
            users.forEach(user => {
                const item = document.createElement('div');
                item.className = 'communication-item';
                item.innerHTML = `
                    <strong>${user.username}</strong> - ${user.role}
                    <button onclick="deleteUser('${user.username}')" class="btn btn-danger" style="float: right;">Eliminar</button>
                `;
                list.appendChild(item);
            });
        }
        
        // Enviar comunicación
        document.getElementById('send-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const recipient = document.getElementById('recipient').value;
            const subject = document.getElementById('subject').value;
            const message = document.getElementById('message').value;
            
            try {
                const response = await fetch('/send-communication', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authToken}`
                    },
                    body: JSON.stringify({ recipient, subject, message })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showMessage('send-message', 'Comunicación enviada exitosamente', 'success');
                    document.getElementById('send-form').reset();
                    loadCommunications();
                } else {
                    showMessage('send-message', data.message, 'error');
                }
            } catch (error) {
                showMessage('send-message', 'Error de conexión', 'error');
            }
        });
        
        // Mostrar formulario de agregar usuario
        function showAddUserForm() {
            document.getElementById('add-user-form').classList.remove('hidden');
        }
        
        // Ocultar formulario de agregar usuario
        function hideAddUserForm() {
            document.getElementById('add-user-form').classList.add('hidden');
            document.getElementById('new-user-form').reset();
        }
        
        // Agregar nuevo usuario
        document.getElementById('new-user-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('new-username').value;
            const password = document.getElementById('new-password').value;
            const role = document.getElementById('new-role').value;
            
            try {
                const response = await fetch('/add-user', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authToken}`
                    },
                    body: JSON.stringify({ username, password, role })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showMessage('users-message', 'Usuario creado exitosamente', 'success');
                    hideAddUserForm();
                    loadUsers();
                } else {
                    showMessage('users-message', data.message, 'error');
                }
            } catch (error) {
                showMessage('users-message', 'Error de conexión', 'error');
            }
        });
        
        // Eliminar usuario
        async function deleteUser(username) {
            if (!confirm(`¿Estás seguro de que quieres eliminar al usuario ${username}?`)) {
                return;
            }
            
            try {
                const response = await fetch('/delete-user', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authToken}`
                    },
                    body: JSON.stringify({ username })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showMessage('users-message', 'Usuario eliminado exitosamente', 'success');
                    loadUsers();
                } else {
                    showMessage('users-message', data.message, 'error');
                }
            } catch (error) {
                showMessage('users-message', 'Error de conexión', 'error');
            }
        }
        
        // Función para mostrar mensajes
        function showMessage(elementId, message, type) {
            const element = document.getElementById(elementId);
            element.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
            setTimeout(() => {
                element.innerHTML = '';
            }, 5000);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """Página principal con aplicación completa"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    """Autenticar usuario"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Usuario y contraseña requeridos'})
        
        # Verificar credenciales
        user = db.authenticate_user(username, password)
        if not user:
            return jsonify({'success': False, 'message': 'Credenciales inválidas'})
        
        # Crear token JWT
        payload = {
            'user_id': user['id'],
            'username': user['username'],
            'role': user['role']
        }
        token = create_jwt(payload)
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'role': user['role']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'})

@app.route('/verify-token')
@require_auth
def verify_token():
    """Verificar token JWT"""
    return jsonify({
        'success': True,
        'user': {
            'id': request.current_user['user_id'],
            'username': request.current_user['username'],
            'role': request.current_user['role']
        }
    })

@app.route('/get-users')
@require_auth
def get_users():
    """Obtener lista de usuarios"""
    try:
        users = db.get_all_users()
        return jsonify({
            'success': True,
            'users': users
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error obteniendo usuarios: {str(e)}'})

@app.route('/add-user', methods=['POST'])
@require_auth
@require_admin
def add_user():
    """Agregar nuevo usuario (solo admin)"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'user')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Usuario y contraseña requeridos'})
        
        # Verificar si el usuario ya existe
        if db.get_user_by_username(username):
            return jsonify({'success': False, 'message': 'El usuario ya existe'})
        
        # Crear usuario
        user_id = db.create_user(username, password, role)
        if user_id:
            return jsonify({'success': True, 'message': 'Usuario creado exitosamente'})
        else:
            return jsonify({'success': False, 'message': 'Error creando usuario'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'})

@app.route('/delete-user', methods=['POST'])
@require_auth
@require_admin
def delete_user():
    """Eliminar usuario (solo admin)"""
    try:
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({'success': False, 'message': 'Usuario requerido'})
        
        if username == request.current_user['username']:
            return jsonify({'success': False, 'message': 'No puedes eliminarte a ti mismo'})
        
        # Eliminar usuario
        if db.delete_user(username):
            return jsonify({'success': True, 'message': 'Usuario eliminado exitosamente'})
        else:
            return jsonify({'success': False, 'message': 'Error eliminando usuario'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'})

@app.route('/send-communication', methods=['POST'])
@require_auth
def send_communication():
    """Enviar comunicación"""
    try:
        data = request.get_json()
        recipient = data.get('recipient')
        subject = data.get('subject')
        message = data.get('message')
        
        if not recipient or not subject or not message:
            return jsonify({'success': False, 'message': 'Todos los campos son requeridos'})
        
        # Verificar que el destinatario existe
        recipient_user = db.get_user_by_username(recipient)
        if not recipient_user:
            return jsonify({'success': False, 'message': 'Destinatario no encontrado'})
        
        # Enviar comunicación
        comm_id = db.send_communication(
            request.current_user['username'],
            recipient,
            subject,
            message
        )
        
        if comm_id:
            return jsonify({'success': True, 'message': 'Comunicación enviada exitosamente'})
        else:
            return jsonify({'success': False, 'message': 'Error enviando comunicación'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'})

@app.route('/get-communications')
@require_auth
def get_communications():
    """Obtener comunicaciones del usuario"""
    try:
        communications = db.get_user_communications(request.current_user['username'])
        return jsonify({
            'success': True,
            'communications': communications
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error obteniendo comunicaciones: {str(e)}'})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': int(time.time()),
        'service': 'comunicaciones-internas'
    })

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'status': 'running',
        'version': '1.0.0',
        'database': 'connected' if db else 'disconnected',
        'features': [
            'JWT Authentication',
            'User Management',
            'Communications System',
            'Role-based Access Control'
        ]
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)