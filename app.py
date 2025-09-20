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
    </style>
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
            <div class="feature">
                <div class="feature-icon">👥</div>
                <h3>Gestión de Usuarios</h3>
                <p>Control de acceso y roles</p>
            </div>
            <div class="feature">
                <div class="feature-icon">📨</div>
                <h3>Comunicaciones</h3>
                <p>Envío y recepción de mensajes</p>
            </div>
            <div class="feature">
                <div class="feature-icon">🔒</div>
                <h3>Seguridad</h3>
                <p>Autenticación JWT</p>
            </div>
            <div class="feature">
                <div class="feature-icon">📊</div>
                <h3>Monitoreo</h3>
                <p>Logs y métricas en tiempo real</p>
            </div>
        </div>
        
        <div>
            <a href="/api/status" class="btn">Ver Estado API</a>
            <a href="/health" class="btn">Health Check</a>
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