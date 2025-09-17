#!/usr/bin/env python3
"""
Servidor HTTPS optimizado para desarrollo móvil
Diseñado para funcionar en Trae AI móvil con certificados auto-firmados
"""

import http.server
import ssl
import socketserver
import os
import tempfile
from datetime import datetime, timedelta

class MobileHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Headers optimizados para Safari móvil
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'SAMEORIGIN')
        # Headers específicos para PWA en Safari
        self.send_header('Cross-Origin-Embedder-Policy', 'unsafe-none')
        self.send_header('Cross-Origin-Opener-Policy', 'unsafe-none')
        super().end_headers()
    
    def log_message(self, format, *args):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")

def create_mobile_cert():
    """Crear certificado optimizado para móvil"""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import ipaddress
        
        # Generar clave privada
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Crear certificado
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Mobile"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Trae"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Comunicaciones"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("127.0.0.1"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                x509.IPAddress(ipaddress.IPv4Address("0.0.0.0")),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Guardar archivos temporales
        cert_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.crt')
        key_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.key')
        
        cert_file.write(cert.public_bytes(serialization.Encoding.PEM))
        key_file.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
        
        cert_file.close()
        key_file.close()
        
        return cert_file.name, key_file.name
        
    except ImportError:
        print("⚠️  cryptography no disponible, usando certificados existentes")
        return None, None

def main():
    PORT = 8443
    
    print("🚀 Iniciando servidor móvil optimizado...")
    print(f"📱 Puerto: {PORT}")
    
    # Intentar crear certificados
    cert_file, key_file = create_mobile_cert()
    
    if not cert_file:
        # Usar certificados existentes si están disponibles
        if os.path.exists('server.crt') and os.path.exists('server.key'):
            cert_file, key_file = 'server.crt', 'server.key'
            print("📜 Usando certificados existentes")
        else:
            print("❌ No se pueden crear certificados SSL")
            print("💡 Ejecuta: pip install cryptography")
            return
    else:
        print("🔐 Certificados temporales creados")
    
    # Configurar servidor
    with socketserver.TCPServer(("", PORT), MobileHTTPRequestHandler) as httpd:
        # Configurar SSL
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        
        # Configuración optimizada para móvil
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        
        print(f"✅ Servidor HTTPS ejecutándose en puerto {PORT}")
        print(f"🌐 URL: https://localhost:{PORT}/")
        print(f"📱 PWA: https://localhost:{PORT}/app-final.html")
        print("\n🔧 Optimizado para Safari móvil")
        print("📋 Presiona Ctrl+C para detener")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Servidor detenido")
        finally:
            # Limpiar archivos temporales
            if cert_file and cert_file.startswith('/tmp'):
                try:
                    os.unlink(cert_file)
                    os.unlink(key_file)
                except:
                    pass

if __name__ == "__main__":
    main()