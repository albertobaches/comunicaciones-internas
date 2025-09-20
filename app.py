#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask application for Render deployment
Simplified version to avoid WSGI compatibility issues
"""

from flask import Flask, jsonify
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    """Main page with simple HTML"""
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Centro de Comunicaciones Internas</title>
        <style>
            body {
                font-family: 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0;
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
            
            <div>
                <a href="/api/status" class="btn">Ver Estado de la API</a>
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
    return html

@app.route('/health')
def health_check():
    """Health check endpoint"""
    health_data = {
        'status': 'healthy',
        'message': 'Aplicación funcionando correctamente',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'environment': 'production'
    }
    return jsonify(health_data)

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    status_data = {
        'api': 'comunicaciones-internas',
        'status': 'operational',
        'environment': 'production',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'endpoints': [
            {'path': '/', 'method': 'GET', 'description': 'Página principal'},
            {'path': '/health', 'method': 'GET', 'description': 'Health check'},
            {'path': '/api/status', 'method': 'GET', 'description': 'Estado de la API'}
        ]
    }
    return jsonify(status_data)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint no encontrado',
        'status_code': 404,
        'message': 'La ruta solicitada no existe'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Error interno del servidor',
        'status_code': 500,
        'message': 'Ha ocurrido un error interno'
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)