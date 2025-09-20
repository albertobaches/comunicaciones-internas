#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI entry point para Render.com
Simple Flask application for production deployment
"""

import os
from app import app

# Esta es la aplicacion WSGI que Render usara
application = app

if __name__ == '__main__':
    # Para testing local
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)