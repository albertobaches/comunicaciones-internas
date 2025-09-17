#!/bin/bash

# Script para crear un certificado SSL más completo para Safari

echo "🔒 Creando certificado SSL mejorado para Safari..."

# Crear archivo de configuración para el certificado
cat > server.conf << EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C=ES
ST=Madrid
L=Madrid
O=Comunicaciones Internas
OU=IT Department
CN=192.168.1.123

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = 192.168.1.123
IP.1 = 192.168.1.123
IP.2 = 127.0.0.1
EOF

# Eliminar certificados anteriores
rm -f server.crt server.key

# Crear nueva clave privada
openssl genrsa -out server.key 2048

# Crear certificado con la configuración mejorada
openssl req -new -x509 -key server.key -out server.crt -days 365 -config server.conf -extensions v3_req

# Verificar el certificado
echo "✅ Certificado creado exitosamente"
echo "📋 Información del certificado:"
openssl x509 -in server.crt -text -noout | grep -A 5 "Subject Alternative Name"

# Limpiar archivo temporal
rm server.conf

echo "🎉 ¡Certificado SSL mejorado listo!"
echo "🔄 Reinicia el servidor HTTPS para usar el nuevo certificado"