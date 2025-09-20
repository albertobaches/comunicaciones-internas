#!/bin/bash

# 🚀 Script de Despliegue Automatizado para Render
# Autor: Sistema de Comunicaciones Internas
# Fecha: $(date)

set -e  # Salir si hay errores

echo "🚀 Iniciando despliegue automatizado..."
echo "=================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "render.yaml" ]; then
    error "No se encontró render.yaml. Ejecuta este script desde la raíz del proyecto."
    exit 1
fi

log "Verificando archivos de configuración..."

# Verificar archivos críticos
REQUIRED_FILES=("render.yaml" "wsgi.py" "requirements.txt" "server.py" "database_postgres.py")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        success "Encontrado: $file"
    else
        error "Archivo faltante: $file"
        exit 1
    fi
done

# Verificar configuración de render.yaml
log "Validando render.yaml..."
if grep -q "gunicorn --bind 0.0.0.0:\$PORT wsgi:application" render.yaml; then
    success "Start command correcto en render.yaml"
else
    warning "Actualizando start command en render.yaml..."
    # Backup del archivo original
    cp render.yaml render.yaml.backup
    
    # Actualizar el start command
    sed -i '' 's/startCommand: .*/startCommand: "gunicorn --bind 0.0.0.0:$PORT wsgi:application"/' render.yaml
    success "Start command actualizado"
fi

# Verificar dependencias
log "Verificando dependencias en requirements.txt..."
if grep -q "gunicorn" requirements.txt && grep -q "psycopg2-binary" requirements.txt; then
    success "Dependencias críticas encontradas"
else
    warning "Agregando dependencias faltantes..."
    if ! grep -q "gunicorn" requirements.txt; then
        echo "gunicorn" >> requirements.txt
    fi
    if ! grep -q "psycopg2-binary" requirements.txt; then
        echo "psycopg2-binary" >> requirements.txt
    fi
    success "Dependencias actualizadas"
fi

# Verificar Git
log "Verificando estado de Git..."
if [ -d ".git" ]; then
    success "Repositorio Git encontrado"
    
    # Verificar si hay cambios sin commit
    if [ -n "$(git status --porcelain)" ]; then
        warning "Hay cambios sin commit. Haciendo commit automático..."
        git add .
        git commit -m "🚀 Preparación automática para despliegue en Render

- Configuración de render.yaml verificada
- Dependencias actualizadas
- Start command corregido
- Archivos de configuración validados

Generado automáticamente por deploy.sh"
        success "Cambios commitados"
    else
        success "No hay cambios pendientes"
    fi
    
    # Push a GitHub
    log "Subiendo cambios a GitHub..."
    git push origin main
    success "Cambios subidos a GitHub"
else
    error "No se encontró repositorio Git"
    exit 1
fi

# Mostrar información de configuración
echo ""
echo "📋 INFORMACIÓN DE CONFIGURACIÓN"
echo "================================"
echo "🔧 Start Command: gunicorn --bind 0.0.0.0:\$PORT wsgi:application"
echo "📁 Root Directory: (vacío)"
echo "🌍 Región recomendada: Oregon (US West)"
echo "💰 Plan recomendado: Free"
echo "🗄️  Base de datos: comunicaciones-db (PostgreSQL)"
echo ""

# Generar URL de despliegue manual
echo "🌐 PRÓXIMOS PASOS MANUALES"
echo "=========================="
echo "1. Ve a: https://dashboard.render.com"
echo "2. Haz clic en 'New +' → 'Web Service'"
echo "3. Selecciona tu repositorio: albertobaches/comunicaciones-internas"
echo "4. Configuración automática detectada ✅"
echo "5. Haz clic en 'Create Web Service'"
echo ""

# Crear archivo de estado
cat > deployment_status.json << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "status": "ready_for_deployment",
  "files_verified": true,
  "git_pushed": true,
  "render_yaml_valid": true,
  "dependencies_updated": true,
  "next_step": "manual_web_service_creation"
}
EOF

success "Estado de despliegue guardado en deployment_status.json"

echo ""
echo "🎉 DESPLIEGUE PREPARADO EXITOSAMENTE"
echo "===================================="
echo "Tu aplicación está lista para desplegarse en Render."
echo "Todos los archivos están configurados correctamente."
echo "Los cambios han sido subidos a GitHub."
echo ""
echo "💡 Para completar el despliegue:"
echo "   Ejecuta: open https://dashboard.render.com"
echo ""

# Abrir Render Dashboard automáticamente (macOS)
if command -v open &> /dev/null; then
    read -p "¿Quieres abrir Render Dashboard automáticamente? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "Abriendo Render Dashboard..."
        open "https://dashboard.render.com"
        success "Dashboard abierto en el navegador"
    fi
fi

echo "🚀 ¡Listo para despegar!"