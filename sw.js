const CACHE_NAME = 'comunicaciones-internas-v1.0.0';
const urlsToCache = [
  '/',
  '/simple.html',
  '/manifest.json',
  '/icon-192x192.svg',
  // Cache de recursos estáticos
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
];

// Instalación del Service Worker
self.addEventListener('install', event => {
  console.log('Service Worker: Instalando...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Cache abierto');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        console.log('Service Worker: Recursos cacheados');
        return self.skipWaiting();
      })
  );
});

// Activación del Service Worker
self.addEventListener('activate', event => {
  console.log('Service Worker: Activando...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Service Worker: Eliminando cache antiguo', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('Service Worker: Activado');
      return self.clients.claim();
    })
  );
});

// Interceptar peticiones de red
self.addEventListener('fetch', event => {
  // Solo cachear peticiones GET
  if (event.request.method !== 'GET') {
    return;
  }

  // Estrategia: Network First para APIs, Cache First para recursos estáticos
  if (event.request.url.includes('/api/') || event.request.url.includes('server.py')) {
    // Network First para APIs (datos dinámicos)
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // Si la respuesta es válida, actualizar cache
          if (response.status === 200) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then(cache => {
              cache.put(event.request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // Si falla la red, intentar desde cache
          return caches.match(event.request);
        })
    );
  } else {
    // Cache First para recursos estáticos
    event.respondWith(
      caches.match(event.request)
        .then(response => {
          // Si está en cache, devolverlo
          if (response) {
            return response;
          }
          
          // Si no está en cache, buscar en red
          return fetch(event.request)
            .then(response => {
              // Si la respuesta es válida, guardar en cache
              if (response.status === 200) {
                const responseClone = response.clone();
                caches.open(CACHE_NAME).then(cache => {
                  cache.put(event.request, responseClone);
                });
              }
              return response;
            });
        })
    );
  }
});

// Manejar notificaciones push
self.addEventListener('push', event => {
  console.log('Service Worker: Push recibido');
  
  let notificationData = {};
  
  if (event.data) {
    try {
      notificationData = event.data.json();
    } catch (e) {
      notificationData = {
        title: 'Nuevo mensaje',
        body: event.data.text() || 'Has recibido un nuevo mensaje',
        icon: '/icon-192x192.svg',
        badge: '/icon-192x192.svg'
      };
    }
  }

  const options = {
    title: notificationData.title || 'Comunicaciones Internas',
    body: notificationData.body || 'Tienes una nueva notificación',
    icon: notificationData.icon || '/icon-192x192.svg',
    badge: notificationData.badge || '/icon-192x192.svg',
    tag: 'comunicacion-nueva',
    requireInteraction: true,
    actions: [
      {
        action: 'view',
        title: 'Ver mensaje',
        icon: '/icon-192x192.svg'
      },
      {
        action: 'close',
        title: 'Cerrar'
      }
    ],
    data: {
      url: notificationData.url || '/',
      timestamp: Date.now()
    }
  };

  event.waitUntil(
    self.registration.showNotification(options.title, options)
  );
});

// Manejar clicks en notificaciones
self.addEventListener('notificationclick', event => {
  console.log('Service Worker: Click en notificación');
  
  event.notification.close();

  if (event.action === 'view' || !event.action) {
    // Abrir o enfocar la aplicación
    event.waitUntil(
      clients.matchAll({ type: 'window', includeUncontrolled: true })
        .then(clientList => {
          // Si ya hay una ventana abierta, enfocarla
          for (let client of clientList) {
            if (client.url.includes(self.location.origin) && 'focus' in client) {
              return client.focus();
            }
          }
          
          // Si no hay ventana abierta, abrir una nueva
          if (clients.openWindow) {
            return clients.openWindow(event.notification.data.url || '/');
          }
        })
    );
  }
});

// Sincronización en segundo plano
self.addEventListener('sync', event => {
  console.log('Service Worker: Sincronización en segundo plano');
  
  if (event.tag === 'background-sync') {
    event.waitUntil(
      // Aquí puedes implementar lógica para sincronizar datos
      // cuando se recupere la conexión
      console.log('Sincronizando datos...')
    );
  }
});

// Manejo de mensajes del cliente
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// Hot Reload para desarrollo
let lastModified = {};

// Función para verificar cambios en archivos
async function checkForUpdates() {
  try {
    const response = await fetch('/api/dev/check-updates', {
      method: 'GET',
      cache: 'no-cache'
    });
    
    if (response.ok) {
      const data = await response.json();
      
      // Verificar si hay cambios
      let hasChanges = false;
      for (const [file, timestamp] of Object.entries(data.files)) {
        if (!lastModified[file] || lastModified[file] !== timestamp) {
          hasChanges = true;
          lastModified[file] = timestamp;
        }
      }
      
      if (hasChanges && Object.keys(lastModified).length > 0) {
        // Notificar a todos los clientes sobre los cambios
        const clients = await self.clients.matchAll();
        clients.forEach(client => {
          client.postMessage({
            type: 'HOT_RELOAD',
            message: 'Archivos actualizados - Recargando...'
          });
        });
        
        // Limpiar cache para forzar actualización
        await caches.delete(CACHE_NAME);
        
        // Recargar todos los clientes
        setTimeout(() => {
          clients.forEach(client => {
            client.navigate(client.url);
          });
        }, 500);
      }
    }
  } catch (error) {
    console.log('Hot reload check failed:', error);
  }
}

// Verificar cambios cada 2 segundos en modo desarrollo
if (self.location.hostname === 'localhost' || self.location.hostname.includes('localhost.run')) {
  setInterval(checkForUpdates, 2000);
}