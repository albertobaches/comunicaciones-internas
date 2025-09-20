#!/usr/bin/env python3
"""
WSGI entry point para Render.com
Convierte el servidor HTTP en una aplicación WSGI compatible con Gunicorn
"""

import os
import sys
from wsgiref.simple_server import make_server
from urllib.parse import parse_qs, urlparse
import json

# Importar el handler de la aplicación
from server import CommunicationHandler

class WSGIApp:
    def __init__(self):
        self.handler = CommunicationHandler
    
    def __call__(self, environ, start_response):
        """WSGI application callable"""
        
        # Crear un handler mock para procesar la request
        class MockRequest:
            def __init__(self, environ):
                self.environ = environ
                self.method = environ['REQUEST_METHOD']
                self.path = environ['PATH_INFO']
                self.query_string = environ.get('QUERY_STRING', '')
                
                # Leer el body si existe
                try:
                    content_length = int(environ.get('CONTENT_LENGTH', 0))
                    self.body = environ['wsgi.input'].read(content_length) if content_length > 0 else b''
                except (ValueError, TypeError):
                    self.body = b''
        
        # Crear handler
        handler = CommunicationHandler(MockRequest(environ), None, None)
        
        # Procesar según el método
        try:
            if environ['REQUEST_METHOD'] == 'GET':
                response_data = handler.do_GET()
            elif environ['REQUEST_METHOD'] == 'POST':
                response_data = handler.do_POST()
            elif environ['REQUEST_METHOD'] == 'OPTIONS':
                response_data = handler.do_OPTIONS()
            else:
                response_data = {'error': 'Method not allowed'}, 405
            
            # Preparar respuesta
            if isinstance(response_data, tuple):
                data, status_code = response_data
            else:
                data, status_code = response_data, 200
            
            # Headers CORS
            headers = [
                ('Content-Type', 'application/json'),
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
                ('Access-Control-Allow-Headers', 'Content-Type, Authorization'),
            ]
            
            start_response(f'{status_code} OK', headers)
            
            if isinstance(data, dict):
                return [json.dumps(data).encode('utf-8')]
            else:
                return [str(data).encode('utf-8')]
                
        except Exception as e:
            start_response('500 Internal Server Error', [('Content-Type', 'application/json')])
            return [json.dumps({'error': str(e)}).encode('utf-8')]

# Crear la aplicación WSGI
application = WSGIApp()

if __name__ == '__main__':
    # Para testing local
    port = int(os.environ.get('PORT', 8000))
    httpd = make_server('', port, application)
    print(f"Servidor WSGI ejecutándose en puerto {port}")
    httpd.serve_forever()