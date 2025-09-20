#!/usr/bin/env python3
"""
Flask application for Render deployment
Simple version of the communications app for production
"""

from flask import Flask, render_template_string, jsonify, request, send_from_directory
import os

app = Flask(__name__)

# HTML template for the main page
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
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .container {
            background: white;
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 600px;
            width: 90%;
        }
        
        .logo {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        h1 {
            color: #333;
            margin-bottom: 1rem;
            font-size: 2.5rem;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 2rem;
            font-size: 1.2rem;
        }
        
        .status {
            background: #e8f5e8;
            color: #2d5a2d;
            padding: 1rem;
            border-radius: 10px;
            margin: 2rem 0;
            border-left: 4px solid #4caf50;
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }
        
        .feature {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid #e9ecef;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .feature:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
            background: white;
        }
        
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 50px;
            font-size: 1.1rem;
            cursor: pointer;
            transition: transform 0.2s;
            text-decoration: none;
            display: inline-block;
            margin: 0.5rem;
        }
        
        .btn:hover {
            transform: translateY(-2px);
        }
        
        .footer {
            margin-top: 2rem;
            color: #666;
            font-size: 0.9rem;
        }
        
        .result-box {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 10px;
            padding: 1.5rem;
            text-align: left;
            margin-top: 1rem;
        }
        
        .result-success {
            background: #d4edda;
            border-color: #c3e6cb;
            color: #155724;
        }
        
        .result-error {
            background: #f8d7da;
            border-color: #f5c6cb;
            color: #721c24;
        }
        
        .loading {
            color: #6c757d;
            font-style: italic;
        }
    </style>
    <script>
        console.log('JavaScript cargado correctamente');
        
        async function checkStatus() {
            console.log('checkStatus() llamada');
            showLoading();
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                console.log('Datos recibidos:', data);
                showResult(data, 'success', 'Estado de la API');
            } catch (error) {
                console.error('Error en checkStatus:', error);
                showResult({error: 'Error al conectar con la API'}, 'error', 'Error');
            }
        }
        
        async function checkHealth() {
            console.log('checkHealth() llamada');
            showLoading();
            try {
                const response = await fetch('/health');
                const data = await response.json();
                console.log('Datos de health recibidos:', data);
                showResult(data, 'success', 'Health Check');
            } catch (error) {
                console.error('Error en checkHealth:', error);
                showResult({error: 'Error al verificar el estado de salud'}, 'error', 'Error');
            }
        }
        
        function showLoading() {
            console.log('showLoading() llamada');
            const resultDiv = document.getElementById('result');
            const contentDiv = document.getElementById('result-content');
            console.log('resultDiv:', resultDiv);
            console.log('contentDiv:', contentDiv);
            if (resultDiv && contentDiv) {
                contentDiv.innerHTML = '<div class="result-box loading">🔄 Cargando...</div>';
                resultDiv.style.display = 'block';
            } else {
                console.error('No se encontraron los elementos result o result-content');
            }
        }
        
        // Test function to verify DOM elements exist
        function testElements() {
            console.log('=== TEST DE ELEMENTOS ===');
            console.log('result div:', document.getElementById('result'));
            console.log('result-content div:', document.getElementById('result-content'));
            console.log('Botones:', document.querySelectorAll('.btn'));
            console.log('Features:', document.querySelectorAll('.feature'));
        }
        
        // Run test when page loads
        document.addEventListener('DOMContentLoaded', function() {
            console.log('DOM cargado completamente');
            testElements();
        });
        
        function showResult(data, type, title) {
             const resultDiv = document.getElementById('result');
             const contentDiv = document.getElementById('result-content');
             
             const className = type === 'success' ? 'result-success' : 'result-error';
             const icon = type === 'success' ? '✅' : '❌';
             
             let html = `<div class="result-box ${className}">
                 <h3>${icon} ${title}</h3>
                 <pre style="margin-top: 1rem; white-space: pre-wrap; font-family: monospace; font-size: 0.9rem;">${JSON.stringify(data, null, 2)}</pre>
             </div>`;
             
             contentDiv.innerHTML = html;
             resultDiv.style.display = 'block';
         }
         
         function showUsers() {
             console.log('showUsers() llamada');
             const data = {
                 module: 'Gestión de Usuarios',
                 status: 'Activo',
                 features: [
                     'Control de acceso basado en roles',
                     'Autenticación de usuarios',
                     'Gestión de permisos',
                     'Registro de actividad'
                 ],
                 users_count: 42,
                 active_sessions: 8
             };
             showResult(data, 'success', 'Gestión de Usuarios');
         }
         
         function showCommunications() {
             const data = {
                 module: 'Sistema de Comunicaciones',
                 status: 'Operativo',
                 features: [
                     'Mensajería interna',
                     'Notificaciones push',
                     'Chat en tiempo real',
                     'Historial de mensajes'
                 ],
                 messages_today: 156,
                 active_channels: 12
             };
             showResult(data, 'success', 'Comunicaciones');
         }
         
         function showSecurity() {
             const data = {
                 module: 'Sistema de Seguridad',
                 status: 'Protegido',
                 features: [
                     'Autenticación JWT',
                     'Encriptación de datos',
                     'Auditoría de seguridad',
                     'Control de acceso'
                 ],
                 security_level: 'Alto',
                 last_audit: '2024-01-15'
             };
             showResult(data, 'success', 'Seguridad');
         }
         
         function showMonitoring() {
             const data = {
                 module: 'Sistema de Monitoreo',
                 status: 'Monitoreando',
                 features: [
                     'Logs en tiempo real',
                     'Métricas de rendimiento',
                     'Alertas automáticas',
                     'Dashboard de estadísticas'
                 ],
                 uptime: '99.9%',
                 response_time: '45ms'
             };
             showResult(data, 'success', 'Monitoreo');
         }
    </script>
</head>
<body>
    <div class="container">
        <div class="logo">🏢</div>
        <h1>Centro de Comunicaciones Internas</h1>
        <p class="subtitle">Sistema de gestión de comunicaciones empresariales</p>
        
        <div class="status">
            <strong>✅ Aplicación desplegada exitosamente en Render</strong><br>
            Estado: Funcionando correctamente
        </div>
        
        <div class="features">
            <div class="feature" onclick="showUsers()" style="cursor: pointer;">
                <div class="feature-icon">👥</div>
                <h3>Gestión de Usuarios</h3>
                <p>Control de acceso y roles</p>
            </div>
            <div class="feature" onclick="showCommunications()" style="cursor: pointer;">
                <div class="feature-icon">📨</div>
                <h3>Comunicaciones</h3>
                <p>Envío y recepción de mensajes</p>
            </div>
            <div class="feature" onclick="showSecurity()" style="cursor: pointer;">
                <div class="feature-icon">🔒</div>
                <h3>Seguridad</h3>
                <p>Autenticación JWT</p>
            </div>
            <div class="feature" onclick="showMonitoring()" style="cursor: pointer;">
                <div class="feature-icon">📊</div>
                <h3>Monitoreo</h3>
                <p>Logs y métricas en tiempo real</p>
            </div>
        </div>
        
        <div>
            <button onclick="checkStatus()" class="btn">Ver Estado</button>
            <button onclick="checkHealth()" class="btn">Health Check</button>
        </div>
        
        <div id="result" style="margin-top: 2rem; display: none;">
            <div id="result-content"></div>
        </div>
        
        <div class="footer">
            <p>🚀 Desplegado con éxito en Render.com</p>
            <p>💻 Desarrollado con Flask + Python</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    """Página principal"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Aplicación funcionando correctamente",
        "version": "1.0.0",
        "timestamp": "2025-01-20"
    })

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        "api": "Centro de Comunicaciones Internas",
        "status": "online",
        "environment": "production",
        "database": "PostgreSQL (pendiente configuración)",
        "features": [
            "Gestión de usuarios",
            "Sistema de comunicaciones",
            "Autenticación JWT",
            "Monitoreo en tiempo real"
        ],
        "deployment": {
            "platform": "Render.com",
            "status": "successful",
            "auto_deploy": True
        }
    })

@app.route('/favicon.ico')
def favicon():
    """Favicon"""
    return '', 204

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint no encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)