#!/bin/bash

echo "🌐 Exponiendo aplicación para acceso global..."
echo "📱 Tu aplicación será accesible desde cualquier dispositivo"
echo ""
echo "⚠️  IMPORTANTE: Mantén este terminal abierto mientras uses la app"
echo ""
echo "🔗 Una vez conectado, usa la URL que aparezca seguida de '/simple.html'"
echo "   Ejemplo: https://xxxxx.lhr.life/simple.html"
echo ""

# Usar localhost.run para crear túnel público
ssh -R 80:localhost:8000 nokey@localhost.run

echo ""
echo "🔒 Túnel cerrado. La aplicación ya no es accesible externamente."