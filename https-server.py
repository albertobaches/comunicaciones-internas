#!/usr/bin/env python3
import http.server
import ssl
import socketserver
import os
from pathlib import Path

# Configuración del servidor
PORT = 8443
DIRECTORY = "."

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Agregar headers para PWA
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

def create_self_signed_cert():
    """Crear certificado autofirmado si no existe"""
    cert_file = "server.crt"
    key_file = "server.key"
    
    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        print("Creando certificado autofirmado...")
        os.system(f"""
openssl req -x509 -newkey rsa:4096 -keyout {key_file} -out {cert_file} -days 365 -nodes -subj "/C=ES/ST=Madrid/L=Madrid/O=ComInternas/CN=192.168.1.123"
        """)
        print(f"Certificado creado: {cert_file}")
        print(f"Clave privada creada: {key_file}")
    
    return cert_file, key_file

def main():
    # Crear certificado si no existe
    cert_file, key_file = create_self_signed_cert()
    
    # Configurar servidor
    with socketserver.TCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler) as httpd:
        # Configurar SSL
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        
        print(f"🔒 Servidor HTTPS iniciado en puerto {PORT}")
        print(f"📱 Accede desde tu móvil a: https://192.168.1.123:{PORT}/inicio.html")
        print(f"💻 Accede desde tu Mac a: https://localhost:{PORT}/inicio.html")
        print("\n⚠️  IMPORTANTE: Tendrás que aceptar el certificado autofirmado en Safari")
        print("   1. Safari mostrará 'Esta conexión no es privada'")
        print("   2. Toca 'Avanzado'")
        print("   3. Toca 'Continuar a 192.168.1.123 (no seguro)'")
        print("\n🛑 Presiona Ctrl+C para detener el servidor")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Servidor detenido")

if __name__ == "__main__":
    main()