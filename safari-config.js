// Configuración específica para Safari PWA v2.1
// Evita pantalla negra y problemas de carga

(function() {
    'use strict';
    
    // Detectar entorno Safari con mayor precisión
    const userAgent = navigator.userAgent;
    const isSafari = /Safari/.test(userAgent) && 
                     !/Chrome/.test(userAgent) && 
                     !/CriOS/.test(userAgent) && 
                     !/FxiOS/.test(userAgent);
    const isIOS = /iPad|iPhone|iPod/.test(userAgent);
    const isPWA = window.navigator.standalone === true || 
                  (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) ||
                  (window.matchMedia && window.matchMedia('(display-mode: fullscreen)').matches) ||
                  window.location.search.includes('source=pwa');
    const isSafariPWA = isIOS && isPWA && isSafari;
    
    console.log('[Safari Config v2.1] Entorno detectado:', { 
        isSafari, 
        isIOS, 
        isPWA, 
        isSafariPWA,
        userAgent: userAgent.substring(0, 100) + '...'
    });
    
    // Configuración inmediata para Safari PWA
    if (isSafari || isIOS || isPWA) {
        // Prevenir zoom y comportamientos no deseados
        preventUnwantedBehaviors();
        
        // Configuraciones inmediatas para Safari PWA
        
        // 1. Prevenir pantalla negra con viewport fijo
        configureViewport();
        
        function configureViewport() {
            let viewport = document.querySelector('meta[name="viewport"]');
            if (!viewport) {
                viewport = document.createElement('meta');
                viewport.name = 'viewport';
                document.head.appendChild(viewport);
            }
            viewport.setAttribute('content', 
                'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover, shrink-to-fit=no'
            );
        }
        
        function preventUnwantedBehaviors() {
            // Prevenir zoom con gestos
            document.addEventListener('gesturestart', function(e) {
                e.preventDefault();
            });
            
            document.addEventListener('gesturechange', function(e) {
                e.preventDefault();
            });
            
            document.addEventListener('gestureend', function(e) {
                e.preventDefault();
            });
            
            // Prevenir selección de texto en elementos de interfaz
            document.addEventListener('selectstart', function(e) {
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                    return;
                }
                if (e.target.closest('.selectable')) {
                    return;
                }
                e.preventDefault();
            });
            
            // Prevenir menú contextual en elementos de interfaz
            document.addEventListener('contextmenu', function(e) {
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                    return;
                }
                if (e.target.closest('.contextmenu-allowed')) {
                    return;
                }
                e.preventDefault();
            });
        }
        
        // 2. Aplicar estilos CSS inmediatos
        const style = document.createElement('style');
        style.textContent = `
            html, body {
                height: 100vh;
                overflow-x: hidden;
                -webkit-overflow-scrolling: touch;
                overscroll-behavior: none;
                -webkit-touch-callout: none;
                -webkit-user-select: none;
                -webkit-tap-highlight-color: transparent;
            }
            
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                margin: 0;
                padding: 0;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            
            /* Prevenir zoom accidental */
            input, textarea, select {
                font-size: 16px !important;
                transform: translateZ(0);
                -webkit-appearance: none;
            }
            
            /* Optimizaciones de rendimiento */
            * {
                -webkit-transform: translateZ(0);
                transform: translateZ(0);
                -webkit-backface-visibility: hidden;
                backface-visibility: hidden;
            }
        `;
        document.head.appendChild(style);
        
        // 3. Configurar eventos táctiles
        document.addEventListener('touchstart', function(e) {
            // Prevenir zoom con múltiples toques
            if (e.touches.length > 1) {
                e.preventDefault();
            }
        }, { passive: false });
        
        document.addEventListener('touchmove', function(e) {
            // Prevenir scroll bounce
            if (e.touches.length > 1) {
                e.preventDefault();
            }
        }, { passive: false });
        
        // 4. Configurar Service Worker con manejo de errores robusto
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', function() {
                navigator.serviceWorker.register('/sw.js', {
                    scope: '/',
                    updateViaCache: 'none'
                }).then(function(registration) {
                    console.log('[Safari Config] SW registrado:', registration.scope);
                    
                    // Forzar actualización si hay una nueva versión
                    registration.addEventListener('updatefound', function() {
                        const newWorker = registration.installing;
                        newWorker.addEventListener('statechange', function() {
                            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                                // Hay una nueva versión disponible
                                newWorker.postMessage({ type: 'SKIP_WAITING' });
                            }
                        });
                    });
                    
                }).catch(function(error) {
                    console.warn('[Safari Config] Error registrando SW:', error);
                    // No fallar la aplicación por errores del SW
                });
            });
        }
        
        // 5. Manejar cambios de orientación
        window.addEventListener('orientationchange', function() {
            setTimeout(function() {
                window.scrollTo(0, 0);
                // Forzar repaint
                document.body.style.display = 'none';
                document.body.offsetHeight; // trigger reflow
                document.body.style.display = '';
            }, 100);
        });
        
        // 6. Prevenir comportamientos no deseados
        document.addEventListener('contextmenu', function(e) {
            e.preventDefault();
        });
        
        document.addEventListener('selectstart', function(e) {
            e.preventDefault();
        });
        
        // 7. Configurar manejo de errores global
        window.addEventListener('error', function(e) {
            console.error('[Safari Config] Error global:', e.error);
            // No mostrar errores al usuario en PWA
            e.preventDefault();
        });
        
        window.addEventListener('unhandledrejection', function(e) {
            console.error('[Safari Config] Promesa rechazada:', e.reason);
            e.preventDefault();
        });
        
        // 8. Optimizar carga de recursos
        document.addEventListener('DOMContentLoaded', function() {
            // Precargar recursos críticos
            const criticalResources = [
                '/css/styles.css',
                '/js/app.js',
                '/img/app-icon.svg'
            ];
            
            criticalResources.forEach(function(resource) {
                const link = document.createElement('link');
                link.rel = 'prefetch';
                link.href = resource;
                document.head.appendChild(link);
            });
        });
        
        // Configuración específica para PWA
        if (isPWA) {
            configurePWASpecific();
        }
        
        function configurePWASpecific() {
            // Ocultar barra de direcciones en Safari PWA
            window.scrollTo(0, 1);
            
            // Configurar altura de viewport para PWA
            function setViewportHeight() {
                const vh = window.innerHeight * 0.01;
                document.documentElement.style.setProperty('--vh', `${vh}px`);
            }
            
            setViewportHeight();
            window.addEventListener('resize', setViewportHeight);
            window.addEventListener('orientationchange', () => {
                setTimeout(setViewportHeight, 100);
            });
            
            // Prevenir scroll bounce en Safari PWA
            document.body.style.overscrollBehavior = 'none';
            document.documentElement.style.overscrollBehavior = 'none';
        }
        
        console.log('[Safari Config v2.1] Configuración de Safari PWA aplicada');
    }
    
    // Función para verificar estado de la aplicación
    window.safariConfigStatus = function() {
        return {
            isSafari,
            isIOS,
            isPWA,
            isSafariPWA,
            version: '2.1',
            timestamp: new Date().toISOString(),
            serviceWorker: 'serviceWorker' in navigator,
            online: navigator.onLine
        };
    };
    
})();