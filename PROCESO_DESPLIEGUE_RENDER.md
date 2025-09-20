# 🚀 Proceso Completo de Despliegue en Render

## 📋 Resumen del Proyecto
**Aplicación:** Sistema de Comunicaciones Internas  
**Tecnología:** Python Flask + PostgreSQL  
**Plataforma:** Render.com  
**Repositorio:** albertobaches/comunicaciones-internas

---

## ✅ PASOS COMPLETADOS

### 1. Preparación de Archivos de Configuración
- ✅ **render.yaml** - Configuración automática de servicios
- ✅ **wsgi.py** - Punto de entrada WSGI para Gunicorn
- ✅ **requirements.txt** - Dependencias (gunicorn, psycopg2-binary)
- ✅ **Procfile** - Comando de inicio alternativo
- ✅ **database_postgres.py** - Configuración de base de datos PostgreSQL

### 2. Configuración de Base de Datos PostgreSQL
- ✅ **Creada en Render:** `comunicaciones-db`
- ✅ **Región:** Oregon (US West)
- ✅ **Plan:** Free
- ✅ **DATABASE_URL obtenida:** `postgresql://comunicaciones_db_user:...@dpg-...oregon-postgres.render.com/comunicaciones_db`

### 3. Conexión de Repositorio GitHub
- ✅ **Repositorio detectado:** albertobaches/comunicaciones-internas
- ✅ **Acceso configurado** desde Render a GitHub

---

## 🔧 CONFIGURACIÓN PENDIENTE

### 4. Ajustes del Web Service (PRÓXIMO PASO)

#### **Campos a modificar en Render:**

1. **Start Command** (CAMBIAR):
   ```bash
   # ACTUAL (incorrecto):
   gunicorn app:app
   
   # DEBE SER:
   gunicorn --bind 0.0.0.0:$PORT wsgi:application
   ```

2. **Root Directory** (LIMPIAR):
   ```
   # Dejar completamente vacío
   # (actualmente dice "e.g. src")
   ```

3. **Mantener como está:**
   - ✅ **Name:** comunicaciones-internas
   - ✅ **Region:** Oregon (US West)
   - ✅ **Branch:** main
   - ✅ **Runtime:** Python 3
   - ✅ **Instance Type:** Free

#### **Variables de Entorno Automáticas:**
- `DATABASE_URL` - Se conectará automáticamente a la base de datos PostgreSQL
- `JWT_SECRET` - Se generará automáticamente
- `PORT` - Asignado automáticamente por Render

---

## 🎯 PASOS FINALES

### 5. Despliegue
1. **Hacer clic en "Create Web Service"**
2. **Esperar el build** (puede tomar 5-10 minutos)
3. **Verificar logs** durante el despliegue

### 6. Verificación Post-Despliegue
- [ ] Aplicación accesible en URL de Render
- [ ] Base de datos conectada correctamente
- [ ] Funcionalidades principales operativas
- [ ] Logs sin errores críticos

---

## 📁 Estructura de Archivos Clave

```
comunicaciones-internas/
├── render.yaml          # Configuración principal de Render
├── wsgi.py             # Punto de entrada WSGI
├── requirements.txt    # Dependencias Python
├── server.py          # Servidor principal
├── database_postgres.py # Configuración BD PostgreSQL
└── Procfile           # Comando de inicio alternativo
```

---

## 🔍 Archivos de Configuración Detallados

### render.yaml
```yaml
services:
  - type: web
    name: comunicaciones-internas
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn --bind 0.0.0.0:$PORT wsgi:application"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: comunicaciones-db
          property: connectionString
      - key: JWT_SECRET
        generateValue: true

databases:
  - name: comunicaciones-db
    databaseName: comunicaciones_db
    user: comunicaciones_db_user
```

### wsgi.py (Punto de entrada)
```python
# Configurado para usar con Gunicorn
# Importa la aplicación Flask desde server.py
# Define 'application' como punto de entrada WSGI
```

### requirements.txt
```
gunicorn
psycopg2-binary
# ... otras dependencias
```

---

## 🚨 Puntos Críticos

### ⚠️ **Start Command Correcto**
```bash
gunicorn --bind 0.0.0.0:$PORT wsgi:application
```
- `--bind 0.0.0.0:$PORT` - Escucha en todas las interfaces en el puerto asignado
- `wsgi:application` - Apunta al objeto 'application' en wsgi.py

### ⚠️ **Root Directory Vacío**
- Debe estar completamente vacío
- La aplicación está en la raíz del repositorio

### ⚠️ **Variables de Entorno**
- `DATABASE_URL` se conecta automáticamente
- `JWT_SECRET` se genera automáticamente
- No requiere configuración manual adicional

---

## 📞 Información de Contacto y URLs

### Base de Datos PostgreSQL
- **Nombre:** comunicaciones-db
- **Host:** dpg-...oregon-postgres.render.com
- **Puerto:** 5432
- **Database:** comunicaciones_db
- **Usuario:** comunicaciones_db_user

### Web Service (Después del despliegue)
- **URL:** https://comunicaciones-internas.onrender.com (aproximada)
- **Región:** Oregon (US West)
- **Plan:** Free

---

## 🔄 Estado Actual del Proceso

```
[✅] 1. Configuración de archivos
[✅] 2. Creación de base de datos PostgreSQL
[✅] 3. Obtención de DATABASE_URL
[✅] 4. Conexión de repositorio GitHub
[🔄] 5. Ajuste de configuración Web Service (EN PROGRESO)
[⏳] 6. Despliegue de aplicación
[⏳] 7. Verificación final
```

---

## 📝 Notas Adicionales

- **Tiempo estimado de despliegue:** 5-10 minutos
- **Plan Free de Render:** Suficiente para desarrollo y pruebas
- **Región Oregon:** Misma región para BD y Web Service (mejor rendimiento)
- **Monitoreo:** Disponible en dashboard de Render
- **Logs:** Accesibles en tiempo real durante y después del despliegue

---

**Fecha de documentación:** $(date)  
**Estado:** Listo para despliegue final  
**Próximo paso:** Ajustar Start Command y crear Web Service