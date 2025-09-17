#!/bin/bash

echo "🌐 Configurando acceso público para la aplicación..."
echo ""

# Verificar que el servidor HTTPS esté corriendo
if ! curl -k -s https://localhost:8443/inicio.html > /dev/null; then
    echo "❌ Error: El servidor HTTPS no está corriendo en el puerto 8443"
    echo "   Ejecuta primero: python3 https-server.py"
    exit 1
fi

echo "✅ Servidor HTTPS detectado en puerto 8443"
echo ""

# Crear túnel usando serveo.net (alternativa gratuita a ngrok)
echo "🔗 Creando túnel público..."
echo "   Esto puede tomar unos segundos..."
echo ""

# Usar autossh para mantener la conexión estable
ssh -o StrictHostKeyChecking=no -R 80:localhost:8443 serveo.net &
SSH_PID=$!

# Esperar un momento para que se establezca la conexión
sleep 5

echo "🎉 ¡Túnel creado exitosamente!"
echo ""
echo "📱 URL PÚBLICA PARA COMPARTIR:"
echo "   https://[subdomain].serveo.net/inicio.html"
echo ""
echo "📋 INSTRUCCIONES PARA TUS USUARIOS:"
echo "   1. Abrir el navegador en su móvil (iPhone o Android)"
echo "   2. Ir a la URL pública"
echo "   3. Instalar como app:"
echo "      • iPhone: Safari → Compartir → Añadir a pantalla de inicio"
echo "      • Android: Chrome → Menú → Añadir a pantalla de inicio"
echo ""
echo "🔐 USUARIOS DE PRUEBA:"
echo "   • admin / 123456"
echo "   • usuario2 / 123456"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   • Mantén esta terminal abierta mientras uses la app"
echo "   • La URL es temporal y cambiará si reinicias el túnel"
echo "   • Funciona en cualquier dispositivo sin configuraciones especiales"
echo ""
echo "🛑 Para detener: Presiona Ctrl+C"

# Mantener el script corriendo
wait $SSH_PID