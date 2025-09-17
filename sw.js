// Service Worker Optimizado v2.1 para Safari PWA
const CACHE_NAME = 'comunicaciones-internas-v2.1';
const CACHE_STATIC = 'static-v2.1';
const CACHE_DYNAMIC = 'dynamic-v2.1';

// Archivos esenciales que DEBEN estar en caché
const ESSENTIAL_FILES = [
    '/',
    '/index.html',
    '/safari-inicio.html',
    '/safari-test.html',
    '/login.html',
    '/manifest.json',
    '/css/styles.css',
    '/js/app.js',
    '/js/auth.js',
    '/img/app-icon.svg',
    '/safari-config.js',
    '/safari-fallback.js'
];

// Archivos opcionales para mejorar rendimiento
const OPTIONAL_FILES = [
    '/css/login.css',
    '/js/utils.js',
    '/favicon.ico'
];

// Instalación del Service Worker
self.addEventListener('install', event => {
    console.log('[SW] Instalando Service Worker v2.1');
    
    event.waitUntil(
        Promise.all([
            // Cache estático para archivos esenciales
            caches.open(CACHE_STATIC).then(cache => {
                console.log('[SW] Cacheando archivos esenciales');
                return cache.addAll(ESSENTIAL_FILES.map(url => {
                    return new Request(url, { cache: 'reload' });
                })).catch(error => {
                    console.warn('[SW] Error cacheando archivos esenciales:', error);
                    // No fallar la instalación por errores de cache
                    return Promise.resolve();
                });
            }),
            
            // Activar inmediatamente sin esperar
            self.skipWaiting()
        ])
    );
});

// Activación del Service Worker
self.addEventListener('activate', event => {
    console.log('[SW] Activando Service Worker v2.0');
    
    event.waitUntil(
        Promise.all([
            // Limpiar caches antiguos
            caches.keys().then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== STATIC_CACHE && 
                            cacheName !== DYNAMIC_CACHE && 
                            cacheName !== CACHE_NAME) {
                            console.log('[SW] Eliminando cache antiguo:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            }),
            
            // Tomar control inmediatamente
            self.clients.claim()
        ])
    );
});

// Manejar solicitudes de red
self.addEventListener('fetch', event => {
    // Solo manejar solicitudes HTTP/HTTPS
    if (!event.request.url.startsWith('http')) {
        return;
    }
    
    // Ignorar solicitudes de extensiones del navegador
    if (event.request.url.includes('extension://') || 
        event.request.url.includes('chrome-extension://') ||
        event.request.url.includes('moz-extension://')) {
        return;
    }
    
    // Estrategia diferente según el tipo de recurso
    if (event.request.mode === 'navigate') {
        event.respondWith(handleNavigationRequest(event.request));
    } else if (isStaticResource(event.request.url)) {
        event.respondWith(handleStaticResource(event.request));
    } else {
        event.respondWith(handleOtherRequests(event.request));
    }
});

// Manejar navegación (páginas HTML)
async function handleNavigationRequest(request) {
    const url = new URL(request.url);
    
    try {
        // Para Safari PWA, intentar caché primero para evitar pantallas negras
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            // Actualizar en segundo plano
            fetch(request).then(response => {
                if (response.ok) {
                    caches.open(CACHE_DYNAMIC).then(cache => {
                        cache.put(request, response.clone());
                    });
                }
            }).catch(() => {});
            
            return cachedResponse;
        }
        
        // Si no está en caché, intentar red con timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000);
        
        const networkResponse = await fetch(request, {
            signal: controller.signal,
            cache: 'no-cache'
        });
        
        clearTimeout(timeoutId);
        
        if (networkResponse.ok) {
            // Cachear la respuesta exitosa
            const cache = await caches.open(CACHE_DYNAMIC);
            cache.put(request, networkResponse.clone());
            return networkResponse;
        }
    } catch (error) {
        console.log('Error de red en navegación:', error);
    }
    
    // Fallback inteligente basado en la URL
    let fallbackPage = '/safari-inicio.html';
    
    if (url.pathname.includes('login')) {
        fallbackPage = '/login.html';
    } else if (url.pathname.includes('test')) {
        fallbackPage = '/safari-test.html';
    } else if (url.pathname === '/' || url.pathname.includes('index')) {
        fallbackPage = '/index.html';
    }
    
    const fallback = await caches.match(fallbackPage);
    if (fallback) {
        return fallback;
    }
    
    // Último recurso: página offline optimizada para Safari
    return new Response(`
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
            <meta name="apple-mobile-web-app-capable" content="yes">
            <title>Sin conexión - Comunicaciones Internas</title>
            <style>
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, sans-serif; 
                    text-align: center; 
                    padding: 50px 20px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    margin: 0;
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                }
                .container { 
                    background: rgba(255,255,255,0.1); 
                    padding: 30px; 
                    border-radius: 15px; 
                    backdrop-filter: blur(10px);
                }
                button { 
                    background: rgba(255,255,255,0.2); 
                    border: 2px solid rgba(255,255,255,0.3); 
                    color: white; 
                    padding: 15px 30px; 
                    border-radius: 25px; 
                    font-size: 16px; 
                    cursor: pointer; 
                    margin-top: 20px;
                }
                button:hover { background: rgba(255,255,255,0.3); }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📡 Sin conexión</h1>
                <p>No se puede cargar la página en este momento.</p>
                <p>Verifica tu conexión a internet e inténtalo de nuevo.</p>
                <button onclick="window.location.reload()">🔄 Reintentar</button>
                <button onclick="window.location.href='/safari-inicio.html'">🏠 Ir al inicio</button>
            </div>
        </body>
        </html>
    `, {
        status: 200,
        headers: { 'Content-Type': 'text/html; charset=utf-8' }
    });
}

// Manejar recursos estáticos (CSS, JS, imágenes)
async function handleStaticResource(request) {
    try {
        // Para recursos estáticos, cache first para mejor rendimiento
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            // Actualizar en segundo plano si es necesario
            fetch(request).then(response => {
                if (response.ok) {
                    caches.open(CACHE_STATIC).then(cache => {
                        cache.put(request, response.clone());
                    });
                }
            }).catch(() => {});
            
            return cachedResponse;
        }
        
        // Si no está en caché, obtener de la red con timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        
        const networkResponse = await fetch(request, {
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (networkResponse.ok) {
            const cache = await caches.open(CACHE_STATIC);
            cache.put(request, networkResponse.clone());
            return networkResponse;
        }
        
        throw new Error('Network response not ok');
        
    } catch (error) {
        console.log('Error cargando recurso estático:', request.url);
        
        // Fallbacks específicos por tipo de recurso
        const url = request.url.toLowerCase();
        
        if (url.includes('.css')) {
            return new Response(`
                /* Fallback CSS para ${request.url} */
                body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
                .error-fallback { 
                    background: #f44336; 
                    color: white; 
                    padding: 10px; 
                    text-align: center; 
                    position: fixed; 
                    top: 0; 
                    left: 0; 
                    right: 0; 
                    z-index: 9999; 
                }
            `, {
                headers: { 'Content-Type': 'text/css; charset=utf-8' }
            });
        }
        
        if (url.includes('.js')) {
            return new Response(`
                // Fallback JS para ${request.url}
                console.warn('Recurso JS no disponible: ${request.url}');
                if (typeof window !== 'undefined') {
                    window.addEventListener('load', function() {
                        const errorDiv = document.createElement('div');
                        errorDiv.className = 'error-fallback';
                        errorDiv.textContent = 'Algunos recursos no están disponibles. Verifica tu conexión.';
                        document.body.insertBefore(errorDiv, document.body.firstChild);
                        setTimeout(() => errorDiv.remove(), 5000);
                    });
                }
            `, {
                headers: { 'Content-Type': 'application/javascript; charset=utf-8' }
            });
        }
        
        if (url.includes('.svg') || url.includes('.png') || url.includes('.jpg') || url.includes('.jpeg')) {
            // SVG de fallback para imágenes
            return new Response(`
                <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
                    <rect width="100" height="100" fill="#f0f0f0"/>
                    <text x="50" y="50" text-anchor="middle" dy=".3em" font-family="Arial" font-size="12" fill="#999">
                        Imagen no disponible
                    </text>
                </svg>
            `, {
                headers: { 'Content-Type': 'image/svg+xml' }
            });
        }
        
        // Para otros recursos, devolver error 404
        return new Response('Resource not available', { 
            status: 404,
            headers: { 'Content-Type': 'text/plain' }
        });
    }
}

// Manejar otras solicitudes (APIs, etc.)
async function handleOtherRequests(request) {
    try {
        // Network first para APIs y otros recursos dinámicos
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 8000);
        
        const networkResponse = await fetch(request, {
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (networkResponse.ok) {
            // Cachear respuestas GET exitosas
            if (request.method === 'GET' && networkResponse.status === 200) {
                const cache = await caches.open(CACHE_DYNAMIC);
                cache.put(request, networkResponse.clone()).catch(() => {});
            }
            return networkResponse;
        }
        
        throw new Error(`Network response not ok: ${networkResponse.status}`);
        
    } catch (error) {
        console.log('Error en solicitud:', request.url, error);
        
        // Intentar caché como fallback solo para GET
        if (request.method === 'GET') {
            const cachedResponse = await caches.match(request);
            if (cachedResponse) {
                return cachedResponse;
            }
        }
        
        // Respuesta de error apropiada según el tipo de solicitud
        if (request.url.includes('/api/')) {
            return new Response(JSON.stringify({
                error: 'Service temporarily unavailable',
                message: 'Please check your connection and try again',
                offline: true
            }), { 
                status: 503,
                headers: { 
                    'Content-Type': 'application/json',
                    'Cache-Control': 'no-cache'
                }
            });
        }
        
        return new Response('Service unavailable', { 
            status: 503,
            headers: { 'Content-Type': 'text/plain' }
        });
    }
}

// Verificar si es un recurso estático
function isStaticResource(url) {
    const staticExtensions = [
        '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', 
        '.woff', '.woff2', '.ttf', '.eot', '.webp', '.avif'
    ];
    return staticExtensions.some(ext => url.toLowerCase().includes(ext));
}

// Manejar mensajes del cliente
self.addEventListener('message', event => {
    console.log('[SW] Mensaje recibido:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'GET_VERSION') {
        event.ports[0].postMessage({ version: '2.0' });
    }
});

// Manejar errores no capturados
self.addEventListener('error', event => {
    console.error('[SW] Error no capturado:', event.error);
});

// Manejar promesas rechazadas
self.addEventListener('unhandledrejection', event => {
    console.error('[SW] Promesa rechazada:', event.reason);
    event.preventDefault();
});

console.log('[SW] Service Worker v2.1 cargado correctamente');