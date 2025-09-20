#!/usr/bin/env python3
"""
WSGI entry point para Render.com
Simple Flask application for production deployment
"""

import os
from app import app

# Esta es la aplicación WSGI que Render usará
application = app

if __name__ == '__main__':
    # Para testing local
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)