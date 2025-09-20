# 🚀 Guía de Despliegue - Comunicaciones Internas PWA

## 📱 Opciones para Acceso Global

### 🌐 Opción 1: Túnel Temporal (Inmediato)

**Para probar rápidamente desde cualquier dispositivo:**

1. **Ejecuta tu servidor local:**
   ```bash
   python3 server.py
   ```

2. **En otra terminal, ejecuta:**
   ```bash
   ./expose_app.sh
   ```

3. **Obtendrás una URL pública como:**
   ```
   https://abc123.localhost.run
   ```

4. **Accede desde cualquier dispositivo** usando esa URL
5. **Instala la PWA** desde el navegador móvil

**✅ Ventajas:** Inmediato, gratuito, HTTPS automático
**⚠️ Limitaciones:** Temporal, requiere mantener terminal abierto

---

### 🚂 Opción 2: Railway (Hosting Gratuito Permanente)

**Para despliegue permanente gratuito:**

1. **Crea cuenta en Railway:** https://railway.app
2. **Conecta tu repositorio Git**
3. **Railway detectará automáticamente** tu aplicación Python
4. **Obtendrás una URL permanente** como: `https://tu-app.railway.app`

**✅ Ventajas:** Permanente, gratuito, HTTPS, escalable
**⚠️ Limitaciones:** 500 horas/mes gratis

---

### ☁️ Opción 3: Render (Alternativa Robusta)

1. **Crea cuenta en Render:** https://render.com
2. **Conecta repositorio**
3. **Configura como Web Service**
4. **Build Command:** `pip install -r requirements.txt`
5. **Start Command:** `python server.py`

**✅ Ventajas:** Muy confiable, SSL automático
**⚠️ Limitaciones:** 750 horas/mes gratis

---

### 🔧 Opción 4: Vercel (Para Frontend + Serverless)

**Requiere modificaciones para funciones serverless**

---

## 🔒 Consideraciones de Seguridad

### Para Producción Real:
- [ ] Cambiar `JWT_SECRET` por uno seguro
- [ ] Implementar rate limiting
- [ ] Usar HTTPS obligatorio
- [ ] Configurar CORS apropiadamente
- [ ] Usar base de datos externa (PostgreSQL)

### Variables de Entorno Recomendadas:
```bash
JWT_SECRET=tu_clave_super_secreta_aqui
DATABASE_URL=postgresql://...
PORT=8000
```

---

## 📱 Instalación PWA

Una vez desplegada, los usuarios pueden:

### En Android (Chrome):
1. Visitar la URL
2. Tocar "Agregar a pantalla de inicio"
3. Confirmar instalación

### En iOS (Safari):
1. Visitar la URL
2. Tocar botón compartir
3. "Agregar a pantalla de inicio"

---

## 🚀 Próximos Pasos

1. **Elige una opción de despliegue**
2. **Prueba la instalación PWA**
3. **Configura notificaciones push** (opcional)
4. **Implementa autenticación OAuth** (opcional)

---

## 🆘 Soporte

Si necesitas ayuda con el despliegue, revisa:
- Logs del servidor
- Configuración de puertos
- Variables de entorno
- Permisos de archivos