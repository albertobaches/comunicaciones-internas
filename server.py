#!/usr/bin/env python3
"""
Servidor HTTP profesional para la aplicación de comunicaciones internas
Implementa autenticación JWT y RBAC usando solo librerías estándar
"""

import http.server
import socketserver
import json
import urllib.parse
import os
import base64
import hmac
import hashlib
import time
import threading
import queue
from database_postgres import UserDatabase

# Inicializar base de datos
db = UserDatabase()

# Clave secreta para JWT (en producción usar variable de entorno)
JWT_SECRET = "mi_clave_secreta_super_segura_2024"

# Variables globales para Server-Sent Events
sse_clients = []  # Lista de clientes conectados
sse_lock = threading.Lock()  # Lock para acceso thread-safe

# Funciones JWT usando solo librerías estándar
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
    payload['iat'] = int(time.time())
    
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
        payload = json.loads(base64url_decode(payload_encoded).decode('utf-8'))
        
        # Verificar expiración
        if payload.get('exp', 0) < time.time():
            return None
        
        return payload
    except Exception:
        return None

def require_auth(func):
    """Decorador para requerir autenticación"""
    def wrapper(self, *args, **kwargs):
        auth_header = self.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            self.send_error_response(401, 'Token de autenticación requerido')
            return
        
        token = auth_header[7:]  # Remover "Bearer "
        payload = verify_jwt(token)
        
        if not payload:
            self.send_error_response(401, 'Token inválido o expirado')
            return
        
        self.current_user = payload
        return func(self, *args, **kwargs)
    return wrapper

def require_admin(func):
    """Decorador que requiere rol de administrador"""
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'current_user') or self.current_user.get('role') != 'admin':
            self.send_error_response(403, 'Acceso denegado: se requieren permisos de administrador')
            return None
        return func(self, *args, **kwargs)
    return wrapper

# Funciones para Server-Sent Events
def add_sse_client(client_info):
    """Agregar cliente SSE a la lista"""
    with sse_lock:
        sse_clients.append(client_info)
        print(f"Cliente SSE conectado. Total: {len(sse_clients)}")

def remove_sse_client(client_info):
    """Remover cliente SSE de la lista"""
    with sse_lock:
        if client_info in sse_clients:
            sse_clients.remove(client_info)
            print(f"Cliente SSE desconectado. Total: {len(sse_clients)}")

def broadcast_sse_event(event_type, data):
    """Enviar evento a todos los clientes SSE conectados"""
    with sse_lock:
        disconnected_clients = []
        
        for client_info in sse_clients[:]:  # Copia de la lista
            try:
                event_data = {
                    'type': event_type,
                    'data': data,
                    'timestamp': int(time.time())
                }
                
                message = f"data: {json.dumps(event_data)}\n\n"
                client_info['wfile'].write(message.encode('utf-8'))
                client_info['wfile'].flush()
                
            except Exception as e:
                print(f"Error enviando SSE a cliente: {e}")
                disconnected_clients.append(client_info)
        
        # Remover clientes desconectados
        for client in disconnected_clients:
            if client in sse_clients:
                sse_clients.remove(client)

class CommunicationHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='.', **kwargs)
    
    def send_error_response(self, status_code, message):
        """Enviar respuesta de error"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        
        error_response = {'success': False, 'message': message}
        self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def send_success_response(self, data):
        """Enviar respuesta exitosa"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def do_GET(self):
        """Manejar peticiones GET"""
        if self.path == '/' or self.path == '/simple.html':
            self.path = '/simple.html'
            return super().do_GET()
        elif self.path == '/get-users':
            # Verificar autenticación para obtener usuarios
            auth_header = self.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                self.send_error_response(401, 'Token de autenticación requerido')
                return
            
            token = auth_header[7:]  # Remover "Bearer "
            payload = verify_jwt(token)
            
            if not payload:
                self.send_error_response(401, 'Token inválido o expirado')
                return
            
            self.current_user = payload
            response = self.get_users()
            self.send_success_response(response)
            return
        elif self.path == '/verify-token':
            # Endpoint para verificar si el token es válido
            auth_header = self.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                self.send_error_response(401, 'Token de autenticación requerido')
                return
            
            token = auth_header[7:]
            payload = verify_jwt(token)
            
            if not payload:
                self.send_error_response(401, 'Token inválido o expirado')
                return
            
            self.send_success_response({
                'success': True,
                'user': {
                    'id': payload['user_id'],
                    'username': payload['username'],
                    'role': payload['role']
                }
            })
            return
        elif self.path == '/api/events':
            # Endpoint para Server-Sent Events
            auth_header = self.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                self.send_error_response(401, 'Token de autenticación requerido')
                return
            
            token = auth_header[7:]
            payload = verify_jwt(token)
            
            if not payload:
                self.send_error_response(401, 'Token inválido o expirado')
                return
            
            # Configurar headers para SSE
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Headers', 'Authorization')
            self.end_headers()
            
            # Agregar cliente a la lista
            client_info = {
                'wfile': self.wfile,
                'user_id': payload['user_id'],
                'username': payload['username']
            }
            add_sse_client(client_info)
            
            try:
                # Enviar mensaje inicial
                initial_message = f"data: {json.dumps({'type': 'connected', 'message': 'Conectado a actualizaciones en tiempo real'})}\n\n"
                self.wfile.write(initial_message.encode('utf-8'))
                self.wfile.flush()
                
                # Mantener conexión abierta
                while True:
                    time.sleep(30)  # Enviar keep-alive cada 30 segundos
                    try:
                        keepalive = f"data: {json.dumps({'type': 'keepalive', 'timestamp': int(time.time())})}\n\n"
                        self.wfile.write(keepalive.encode('utf-8'))
                        self.wfile.flush()
                    except:
                        break
                        
            except Exception as e:
                print(f"Error en conexión SSE: {e}")
            finally:
                remove_sse_client(client_info)
            return
        elif self.path == '/api/dev/check-updates':
            # Endpoint para hot reload - verificar cambios en archivos
            try:
                files_to_watch = [
                    'simple.html',
                    'sw.js',
                    'manifest.json',
                    'server.py',
                    'database.py'
                ]
                
                file_timestamps = {}
                for filename in files_to_watch:
                    try:
                        stat = os.stat(filename)
                        file_timestamps[filename] = stat.st_mtime
                    except FileNotFoundError:
                        continue
                
                self.send_success_response({
                    'files': file_timestamps,
                    'timestamp': time.time()
                })
            except Exception as e:
                self.send_error_response(500, f'Error checking updates: {str(e)}')
            return
        
        # Servir archivos estáticos
        return super().do_GET()
    
    def do_POST(self):
        """Manejar peticiones POST"""
        try:
            # Leer datos del cuerpo de la petición
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Enrutar según la URL
            if self.path == '/authenticate-user':
                response = self.authenticate_user(data)
                self.send_success_response(response)
            elif self.path == '/logout':
                response = self.logout()
                self.send_success_response(response)
            elif self.path == '/add-user':
                # Verificar autenticación y rol de admin
                auth_header = self.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    self.send_error_response(401, 'Token de autenticación requerido')
                    return
                
                token = auth_header[7:]
                payload = verify_jwt(token)
                
                if not payload:
                    self.send_error_response(401, 'Token inválido o expirado')
                    return
                
                if payload.get('role') != 'admin':
                    self.send_error_response(403, 'Acceso denegado: se requiere rol de administrador')
                    return
                
                self.current_user = payload
                response = self.add_user(data)
                self.send_success_response(response)
            elif self.path == '/update-user':
                # Verificar autenticación y rol de admin
                auth_header = self.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    self.send_error_response(401, 'Token de autenticación requerido')
                    return
                
                token = auth_header[7:]
                payload = verify_jwt(token)
                
                if not payload:
                    self.send_error_response(401, 'Token inválido o expirado')
                    return
                
                if payload.get('role') != 'admin':
                    self.send_error_response(403, 'Acceso denegado: se requiere rol de administrador')
                    return
                
                self.current_user = payload
                response = self.update_user(data)
                self.send_success_response(response)
            elif self.path == '/delete-user':
                # Verificar autenticación y rol de admin
                auth_header = self.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    self.send_error_response(401, 'Token de autenticación requerido')
                    return
                
                token = auth_header[7:]
                payload = verify_jwt(token)
                
                if not payload:
                    self.send_error_response(401, 'Token inválido o expirado')
                    return
                
                if payload.get('role') != 'admin':
                    self.send_error_response(403, 'Acceso denegado: se requiere rol de administrador')
                    return
                
                self.current_user = payload
                response = self.delete_user(data)
                self.send_success_response(response)
            elif self.path == '/send-communication':
                # Verificar autenticación
                auth_header = self.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    self.send_error_response(401, 'Token de autenticación requerido')
                    return
                
                token = auth_header[7:]
                payload = verify_jwt(token)
                
                if not payload:
                    self.send_error_response(401, 'Token inválido o expirado')
                    return
                
                self.current_user = payload
                response = self.send_communication(data)
                self.send_success_response(response)
            elif self.path == '/get-communications':
                # Verificar autenticación
                auth_header = self.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    self.send_error_response(401, 'Token de autenticación requerido')
                    return
                
                token = auth_header[7:]
                payload = verify_jwt(token)
                
                if not payload:
                    self.send_error_response(401, 'Token inválido o expirado')
                    return
                
                self.current_user = payload
                response = self.get_communications()
                self.send_success_response(response)
            elif self.path == '/delete-communication':
                # Verificar autenticación
                auth_header = self.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    self.send_error_response(401, 'Token de autenticación requerido')
                    return
                
                token = auth_header[7:]
                payload = verify_jwt(token)
                
                if not payload:
                    self.send_error_response(401, 'Token inválido o expirado')
                    return
                
                self.current_user = payload
                response = self.delete_communication(data)
                self.send_success_response(response)
            elif self.path == '/get-inbox':
                # Verificar autenticación
                auth_header = self.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    self.send_error_response(401, 'Token de autenticación requerido')
                    return
                
                token = auth_header[7:]
                payload = verify_jwt(token)
                
                if not payload:
                    self.send_error_response(401, 'Token inválido o expirado')
                    return
                
                self.current_user = payload
                response = self.get_inbox()
                self.send_success_response(response)
            else:
                self.send_error_response(404, 'Endpoint no encontrado')
            
        except Exception as e:
            print(f"Error en POST: {e}")
            self.send_error_response(500, 'Error interno del servidor')
    
    def do_OPTIONS(self):
        """Manejar peticiones OPTIONS para CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def authenticate_user(self, data):
        """Autenticar usuario y generar token JWT"""
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return {'success': False, 'message': 'Usuario y contraseña son requeridos'}
        
        result = db.authenticate_user(username, password)
        
        if result['success']:
            # Crear token JWT
            payload = {
                'user_id': result['user']['id'],
                'username': result['user']['username'],
                'role': result['user']['role']
            }
            
            token = create_jwt(payload)
            
            return {
                'success': True,
                'user': {
                    'id': result['user']['id'],
                    'username': result['user']['username'],
                    'role': result['user']['role']
                },
                'token': token,
                'message': 'Autenticación exitosa'
            }
        else:
            return result
    
    def get_users(self):
        """Obtener todos los usuarios"""
        try:
            users = db.get_all_users()
            # Incluir contraseñas para permitir edición
            safe_users = []
            for user in users:
                safe_users.append({
                    'id': user['id'],
                    'username': user['username'],
                    'password': user['password'],
                    'role': user['role'],
                    'created_at': user['created_at'],
                    'updated_at': user['updated_at']
                })
            return {'success': True, 'users': safe_users}
        except Exception as e:
            print(f"Error al obtener usuarios: {e}")
            return {'success': False, 'message': 'Error al obtener usuarios'}
    
    def add_user(self, data):
        """Añadir nuevo usuario"""
        try:
            username = data.get('username')
            password = data.get('password')
            role = data.get('role', 'user')
            
            if not username or not password:
                return {'success': False, 'message': 'Usuario y contraseña son requeridos'}
            
            # Por simplicidad, permitir crear usuarios sin validación de sesión
            # En producción, validar sesión de admin aquí
            result = db.add_user(username, password, role)
            
            # Enviar notificación en tiempo real si el usuario se creó exitosamente
            if result.get('success'):
                broadcast_sse_event('user_added', {
                    'username': username,
                    'role': role,
                    'message': f'Nuevo usuario {username} agregado'
                })
            
            return result
            
        except Exception as e:
            print(f"Error al añadir usuario: {e}")
            return {'success': False, 'message': 'Error al añadir usuario'}
    
    def update_user(self, data):
        """Actualizar usuario"""
        try:
            user_id = data.get('user_id')
            username = data.get('username')
            password = data.get('password')
            role = data.get('role')
            
            if not user_id:
                return {'success': False, 'message': 'ID de usuario requerido'}
            
            result = db.update_user(user_id, username, password, role)
            
            # Enviar notificación en tiempo real si el usuario se actualizó exitosamente
            if result.get('success'):
                broadcast_sse_event('user_updated', {
                    'user_id': user_id,
                    'username': username,
                    'role': role,
                    'message': f'Usuario {username} actualizado'
                })
            
            return result
            
        except Exception as e:
            print(f"Error al actualizar usuario: {e}")
            return {'success': False, 'message': 'Error al actualizar usuario'}
    
    def delete_user(self, data):
        """Eliminar usuario"""
        try:
            user_id = data.get('user_id')
            
            if not user_id:
                return {'success': False, 'message': 'ID de usuario requerido'}
            
            result = db.delete_user(user_id)
            
            # Enviar notificación en tiempo real si el usuario se eliminó exitosamente
            if result.get('success'):
                broadcast_sse_event('user_deleted', {
                    'user_id': user_id,
                    'message': f'Usuario eliminado'
                })
            
            return result
            
        except Exception as e:
            print(f"Error al eliminar usuario: {e}")
            return {'success': False, 'message': 'Error al eliminar usuario'}
    
    def logout(self):
        """Cerrar sesión"""
        return {'success': True, 'message': 'Sesión cerrada'}
    
    def send_communication(self, data):
        """Enviar un nuevo comunicado"""
        try:
            # Validar datos requeridos
            required_fields = ['destinatario', 'mensaje', 'prioridad']
            for field in required_fields:
                if field not in data or not data[field]:
                    return {'success': False, 'message': f'Campo {field} es requerido'}
            
            # Generar título automáticamente si no se proporciona
            titulo = data.get('titulo', f"Comunicado de {self.current_user['username']}")
            
            # Obtener hora actual
            from datetime import datetime
            now = datetime.now()
            hora = now.strftime("%H:%M")
            
            # Guardar en la base de datos
            result = db.add_communication(
                titulo=titulo,
                mensaje=data['mensaje'],
                destinatario=data['destinatario'],
                prioridad=data['prioridad'],
                remitente=self.current_user['username'],
                hora=hora
            )
            
            # Enviar notificación en tiempo real si el comunicado se guardó exitosamente
            if result.get('success'):
                broadcast_sse_event('new_communication', {
                    'titulo': titulo,
                    'mensaje': data['mensaje'],
                    'destinatario': data['destinatario'],
                    'prioridad': data['prioridad'],
                    'remitente': self.current_user['username'],
                    'hora': hora
                })
            
            return result
            
        except Exception as e:
            print(f"Error al enviar comunicado: {e}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    def get_communications(self):
        """Obtener comunicados del usuario actual"""
        try:
            # Los administradores pueden ver todos los comunicados
            if self.current_user['role'] == 'admin':
                communications = db.get_all_communications()
            else:
                # Los usuarios regulares solo ven sus propios comunicados enviados
                communications = db.get_communications_by_sender(self.current_user['username'])
            
            return {
                'success': True,
                'communications': communications
            }
            
        except Exception as e:
            print(f"Error al obtener comunicados: {e}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    def get_inbox(self):
        """Obtener bandeja de entrada del usuario actual (mensajes recibidos)"""
        try:
            # Obtener mensajes recibidos por el usuario actual
            communications = db.get_communications_by_recipient(self.current_user['username'])
            
            return {
                'success': True,
                'communications': communications
            }
            
        except Exception as e:
            print(f"Error al obtener bandeja de entrada: {e}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    def delete_communication(self, data):
        """Eliminar un comunicado específico"""
        try:
            comm_id = data.get('id')
            if not comm_id:
                return {'success': False, 'message': 'ID del comunicado es requerido'}
            
            # Solo el remitente puede eliminar sus propios comunicados
            # Los administradores también pueden eliminar cualquier comunicado
            if self.current_user['role'] == 'admin':
                # Los administradores pueden eliminar cualquier comunicado
                result = db.delete_communication(comm_id, None)  # Pasamos None para admin
            else:
                # Los usuarios regulares solo pueden eliminar sus propios comunicados
                result = db.delete_communication(comm_id, self.current_user['username'])
            
            return result
            
        except Exception as e:
            print(f"Error al eliminar comunicado: {e}")
            return {'success': False, 'message': 'Error interno del servidor'}

if __name__ == '__main__':
    # Usar puerto asignado por el hosting o 8000 por defecto
    PORT = int(os.environ.get('PORT', 8000))

    print("🚀 Iniciando servidor de comunicaciones internas...")
    print(f"📱 Aplicación disponible en puerto {PORT}")
    print("👤 Usuario admin: admin / admin123")
    print("👤 Usuario regular: usuario1 / pass123")

    with socketserver.TCPServer(("", PORT), CommunicationHandler) as httpd:
        print(f"✅ Servidor ejecutándose en puerto {PORT}")
        httpd.serve_forever()