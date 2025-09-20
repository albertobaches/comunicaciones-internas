# 🚀 INSTRUCCIONES DE DESPLIEGUE EN RENDER

## ✅ **SOLUCIÓN PERMANENTE - URL GLOBAL 24/7**

Tu aplicación estará disponible en una URL como: `https://comunicaciones-internas.onrender.com`

### **📋 PASOS PARA DESPLEGAR:**

#### **1. Crear cuenta en Render**
- Ve a [render.com](https://render.com)
- Regístrate con GitHub (recomendado) o email

#### **2. Conectar repositorio**
- Sube tu código a GitHub (si no lo has hecho)
- En Render: "New" → "Web Service"
- Conecta tu repositorio de GitHub

#### **3. Configuración automática**
- Render detectará automáticamente que es Python
- Usará el archivo `render.yaml` para configuración
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn --bind 0.0.0.0:$PORT wsgi:application`

#### **4. Variables de entorno (automáticas)**
- `JWT_SECRET`: Se genera automáticamente
- `DATABASE_URL`: Se conecta automáticamente a PostgreSQL
- `PORT`: Se asigna automáticamente

#### **5. Base de datos PostgreSQL**
- Se crea automáticamente (gratis)
- Se conecta automáticamente a tu app
- Datos persistentes (no se pierden)

### **🌍 RESULTADO FINAL:**

✅ **URL permanente**: `https://tu-app.onrender.com/simple.html`
✅ **Acceso global**: Desde cualquier dispositivo, cualquier red
✅ **24/7 disponible**: Sin suspensiones ni límites de tiempo
✅ **Base de datos**: PostgreSQL persistente incluida
✅ **SSL/HTTPS**: Certificado automático
✅ **200+ usuarios**: Sin problemas de capacidad

### **📱 ACCESO MÓVIL:**
- Abre `https://tu-app.onrender.com/simple.html` en cualquier móvil
- Funciona con datos móviles o WiFi
- Desde cualquier país del mundo
- Guarda en pantalla de inicio para acceso rápido

### **⚡ VENTAJAS DE RENDER:**
- **Gratis para siempre** (no como Railway que se suspende)
- **Sin límites de tiempo** (no como Heroku que se apaga)
- **Despliegue automático** desde GitHub
- **SSL incluido** (HTTPS automático)
- **Backups automáticos** de la base de datos

### **🔧 MANTENIMIENTO:**
- Cada vez que hagas cambios en GitHub, se redespliega automáticamente
- La URL nunca cambia
- Los datos se mantienen siempre

---

## 🎯 **¿POR QUÉ RENDER ES PERFECTO PARA TU CASO?**

1. **URL PERMANENTE**: Una vez desplegado, la URL nunca cambia
2. **ACCESO GLOBAL**: 200 personas pueden acceder desde cualquier lugar
3. **GRATIS**: Sin costos ocultos ni límites de tiempo
4. **PROFESIONAL**: SSL, backups, monitoreo incluido
5. **FÁCIL**: Un solo despliegue y listo para siempre

**¡Esta es la solución definitiva que necesitas!** 🚀