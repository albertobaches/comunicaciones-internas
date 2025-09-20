#!/usr/bin/env python3
"""
WSGI entry point para Render.com
Simple Flask application for production deployment
"""

import os
from app import app
            
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