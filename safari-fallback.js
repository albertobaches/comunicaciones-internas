// Sistema de fallbacks múltiples para Safari PWA
// Maneja errores de conectividad, certificados y otros problemas

(function() {
    'use strict';
    
    // Configuración de fallbacks
    const FALLBACK_CONFIG = {
        maxRetries: 3,
        retryDelay: 1000,
        timeoutDuration: 10000,
        fallbackUrls: [
            window.location.origin,
            'https://' + window.location.hostname,
            'http://' + window.location.hostname + ':8080',
            'http://' + window.location.hostname + ':3000'
        ]
    };
    
    // Estado del sistema de fallbacks
    let fallbackState = {
        currentRetry: 0,
        lastError: null,
        isOffline: false,
        certificateError: false
    };
    
    // Detectar tipo de error
    function detectErrorType(error) {
        const errorMessage = error.message || error.toString();
        
        if (errorMessage.includes('certificate') || 
            errorMessage.includes('SSL') || 
            errorMessage.includes('TLS') ||
            errorMessage.includes('security')) {
            return 'certificate';
        }
        
        if (errorMessage.includes('network') || 
            errorMessage.includes('fetch') ||
            errorMessage.includes('connection') ||
            !navigator.onLine) {
            return 'network';
        }
        
        if (errorMessage.includes('timeout')) {
            return 'timeout';
        }
        
        return 'unknown';
    }
    
    // Función de retry con backoff exponencial
    async function retryWithBackoff(fn, maxRetries = FALLBACK_CONFIG.maxRetries) {
        for (let i = 0; i < maxRetries; i++) {
            try {
                const result = await fn();
                fallbackState.currentRetry = 0; // Reset en éxito
                return result;
            } catch (error) {
                fallbackState.currentRetry = i + 1;
                fallbackState.lastError = error;
                
                console.warn(`[Safari Fallback] Intento ${i + 1} falló:`, error);
                
                if (i === maxRetries - 1) {
                    throw error; // Último intento
                }
                
                // Backoff exponencial: 1s, 2s, 4s...
                const delay = FALLBACK_CONFIG.retryDelay * Math.pow(2, i);
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }
    
    // Verificar conectividad con múltiples métodos
    async function checkConnectivity() {
        const checks = [
            // Método 1: Navigator online
            () => Promise.resolve(navigator.onLine),
            
            // Método 2: Fetch a un recurso pequeño
            async () => {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 5000);
                
                try {
                    const response = await fetch('/manifest.json', {
                        method: 'HEAD',
                        cache: 'no-cache',
                        signal: controller.signal
                    });
                    clearTimeout(timeoutId);
                    return response.ok;
                } catch (error) {
                    clearTimeout(timeoutId);
                    return false;
                }
            },
            
            // Método 3: Ping a Google DNS (si CORS lo permite)
            async () => {
                try {
                    const response = await fetch('https://8.8.8.8', {
                        method: 'HEAD',
                        mode: 'no-cors',
                        cache: 'no-cache'
                    });
                    return true;
                } catch (error) {
                    return false;
                }
            }
        ];
        
        // Ejecutar checks en paralelo
        const results = await Promise.allSettled(
            checks.map(check => check())
        );
        
        // Si al menos uno es exitoso, consideramos que hay conectividad
        const isOnline = results.some(result => 
            result.status === 'fulfilled' && result.value === true
        );
        
        fallbackState.isOffline = !isOnline;
        return isOnline;
    }
    
    // Manejar errores de certificado
    function handleCertificateError() {
        fallbackState.certificateError = true;
        
        console.warn('[Safari Fallback] Error de certificado detectado');
        
        // Mostrar mensaje al usuario
        showFallbackMessage(
            'Problema de Seguridad',
            'Hay un problema con el certificado de seguridad. Intentando conexión alternativa...',
            'warning'
        );
        
        // Intentar con HTTP si HTTPS falla
        if (window.location.protocol === 'https:') {
            const httpUrl = window.location.href.replace('https:', 'http:');
            console.log('[Safari Fallback] Intentando con HTTP:', httpUrl);
            
            setTimeout(() => {
                window.location.href = httpUrl;
            }, 3000);
        }
    }
    
    // Manejar errores de red
    async function handleNetworkError() {
        console.warn('[Safari Fallback] Error de red detectado');
        
        showFallbackMessage(
            'Sin Conexión',
            'Verificando conectividad y activando modo offline...',
            'info'
        );
        
        // Verificar si realmente estamos offline
        const isOnline = await checkConnectivity();
        
        if (!isOnline) {
            // Activar modo offline
            activateOfflineMode();
        } else {
            // Hay conectividad, pero algo más está mal
            showFallbackMessage(
                'Problema de Conexión',
                'Hay conectividad pero el servidor no responde. Reintentando...',
                'warning'
            );
            
            // Intentar URLs alternativas
            await tryAlternativeUrls();
        }
    }
    
    // Intentar URLs alternativas
    async function tryAlternativeUrls() {
        for (const url of FALLBACK_CONFIG.fallbackUrls) {
            try {
                console.log('[Safari Fallback] Intentando URL:', url);
                
                const response = await fetch(url + '/manifest.json', {
                    method: 'HEAD',
                    cache: 'no-cache'
                });
                
                if (response.ok) {
                    console.log('[Safari Fallback] URL alternativa funciona:', url);
                    
                    if (url !== window.location.origin) {
                        showFallbackMessage(
                            'Redirigiendo',
                            'Conectando a servidor alternativo...',
                            'success'
                        );
                        
                        setTimeout(() => {
                            window.location.href = url + window.location.pathname;
                        }, 2000);
                    }
                    return true;
                }
            } catch (error) {
                console.warn('[Safari Fallback] URL falló:', url, error);
            }
        }
        
        // Ninguna URL funcionó
        activateOfflineMode();
        return false;
    }
    
    // Activar modo offline
    function activateOfflineMode() {
        console.log('[Safari Fallback] Activando modo offline');
        
        showFallbackMessage(
            'Modo Offline',
            'Trabajando sin conexión. Funcionalidad limitada disponible.',
            'info'
        );
        
        // Configurar la aplicación para modo offline
        document.body.classList.add('offline-mode');
        
        // Deshabilitar funciones que requieren red
        const networkButtons = document.querySelectorAll('[data-requires-network]');
        networkButtons.forEach(button => {
            button.disabled = true;
            button.title = 'Requiere conexión a internet';
        });
        
        // Mostrar indicador de offline
        showOfflineIndicator();
    }
    
    // Mostrar indicador de offline
    function showOfflineIndicator() {
        let indicator = document.getElementById('offline-indicator');
        
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'offline-indicator';
            indicator.innerHTML = `
                <div style="
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    background: #ff6b6b;
                    color: white;
                    text-align: center;
                    padding: 8px;
                    font-size: 14px;
                    z-index: 10000;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                ">
                    📡 Sin conexión - Modo offline activo
                    <button onclick="window.safariFallback.checkConnection()" style="
                        background: rgba(255,255,255,0.2);
                        border: 1px solid rgba(255,255,255,0.3);
                        color: white;
                        padding: 4px 8px;
                        margin-left: 10px;
                        border-radius: 4px;
                        cursor: pointer;
                    ">Reintentar</button>
                </div>
            `;
            document.body.appendChild(indicator);
        }
    }
    
    // Mostrar mensaje de fallback
    function showFallbackMessage(title, message, type = 'info') {
        const colors = {
            info: '#3498db',
            warning: '#f39c12',
            error: '#e74c3c',
            success: '#27ae60'
        };
        
        const messageDiv = document.createElement('div');
        messageDiv.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: ${colors[type]};
            color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 10001;
            text-align: center;
            max-width: 300px;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        `;
        
        messageDiv.innerHTML = `
            <h3 style="margin: 0 0 10px 0; font-size: 18px;">${title}</h3>
            <p style="margin: 0; font-size: 14px;">${message}</p>
        `;
        
        document.body.appendChild(messageDiv);
        
        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, 5000);
    }
    
    // Verificar conexión manualmente
    async function checkConnection() {
        showFallbackMessage('Verificando', 'Comprobando conexión...', 'info');
        
        const isOnline = await checkConnectivity();
        
        if (isOnline) {
            // Remover modo offline
            document.body.classList.remove('offline-mode');
            
            const indicator = document.getElementById('offline-indicator');
            if (indicator) {
                indicator.remove();
            }
            
            // Reactivar botones
            const networkButtons = document.querySelectorAll('[data-requires-network]');
            networkButtons.forEach(button => {
                button.disabled = false;
                button.title = '';
            });
            
            showFallbackMessage('Conectado', 'Conexión restaurada', 'success');
            
            // Recargar la página para sincronizar
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            showFallbackMessage('Sin Conexión', 'Aún no hay conexión disponible', 'warning');
        }
    }
    
    // Manejar errores globales
    function handleGlobalError(error) {
        const errorType = detectErrorType(error);
        
        console.error('[Safari Fallback] Error global:', errorType, error);
        
        switch (errorType) {
            case 'certificate':
                handleCertificateError();
                break;
            case 'network':
                handleNetworkError();
                break;
            case 'timeout':
                showFallbackMessage(
                    'Tiempo Agotado',
                    'La conexión está tardando mucho. Reintentando...',
                    'warning'
                );
                setTimeout(() => window.location.reload(), 3000);
                break;
            default:
                showFallbackMessage(
                    'Error Inesperado',
                    'Algo salió mal. Reintentando automáticamente...',
                    'error'
                );
                setTimeout(() => window.location.reload(), 5000);
        }
    }
    
    // Configurar listeners de eventos
    window.addEventListener('error', (event) => {
        handleGlobalError(event.error || event);
    });
    
    window.addEventListener('unhandledrejection', (event) => {
        handleGlobalError(event.reason);
    });
    
    window.addEventListener('online', () => {
        console.log('[Safari Fallback] Conexión restaurada');
        checkConnection();
    });
    
    window.addEventListener('offline', () => {
        console.log('[Safari Fallback] Conexión perdida');
        activateOfflineMode();
    });
    
    // API pública
    window.safariFallback = {
        checkConnectivity,
        checkConnection,
        retryWithBackoff,
        getState: () => ({ ...fallbackState }),
        activateOfflineMode,
        handleCertificateError,
        handleNetworkError
    };
    
    console.log('[Safari Fallback] Sistema de fallbacks inicializado');
    
})();