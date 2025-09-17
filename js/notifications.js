// Sistema de notificaciones push y contador de mensajes
class NotificationManager {
    constructor() {
        this.unreadCount = 0;
        this.messages = JSON.parse(localStorage.getItem('messages') || '[]');
        this.init();
    }

    async init() {
        // Solicitar permisos de notificación
        if ('Notification' in window) {
            const permission = await Notification.requestPermission();
            console.log('Permiso de notificaciones:', permission);
        }

        // Configurar badge de la aplicación
        this.updateBadge();
        
        // Simular mensajes nuevos cada 30 segundos (para demo)
        this.startMessageSimulation();
    }

    // Solicitar permisos de notificación push
    async requestNotificationPermission() {
        if ('serviceWorker' in navigator && 'PushManager' in window) {
            try {
                const registration = await navigator.serviceWorker.ready;
                const subscription = await registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: this.urlBase64ToUint8Array('BEl62iUYgUivxIkv69yViEuiBIa40HI80YmqRJiTVOpbEVjmp2S_-SO3cf2p3jUfHZqUXZXcXvQDj5dDsJxuHZQ')
                });
                
                console.log('Suscripción push:', subscription);
                return subscription;
            } catch (error) {
                console.error('Error al suscribirse a push:', error);
            }
        }
    }

    // Convertir clave VAPID
    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    // Agregar nuevo mensaje
    addMessage(message) {
        const newMessage = {
            id: Date.now(),
            title: message.title || 'Nuevo comunicado',
            content: message.content || 'Tienes un nuevo mensaje',
            timestamp: new Date().toISOString(),
            read: false,
            sender: message.sender || 'Sistema',
            priority: message.priority || 'normal'
        };

        this.messages.unshift(newMessage);
        this.saveMessages();
        this.updateUnreadCount();
        this.showNotification(newMessage);
        this.updateBadge();
    }

    // Mostrar notificación
    showNotification(message) {
        if ('Notification' in window && Notification.permission === 'granted') {
            const notification = new Notification(message.title, {
                body: message.content,
                icon: '/img/app-icon.svg',
                badge: '/img/app-icon.svg',
                tag: `message-${message.id}`,
                vibrate: [200, 100, 200],
                data: { messageId: message.id },
                actions: [
                    {
                        action: 'view',
                        title: 'Ver mensaje'
                    },
                    {
                        action: 'dismiss',
                        title: 'Descartar'
                    }
                ]
            });

            notification.onclick = () => {
                window.focus();
                this.markAsRead(message.id);
                notification.close();
            };

            // Auto cerrar después de 5 segundos
            setTimeout(() => {
                notification.close();
            }, 5000);
        }
    }

    // Marcar mensaje como leído
    markAsRead(messageId) {
        const message = this.messages.find(m => m.id === messageId);
        if (message && !message.read) {
            message.read = true;
            this.saveMessages();
            this.updateUnreadCount();
            this.updateBadge();
        }
    }

    // Marcar todos como leídos
    markAllAsRead() {
        this.messages.forEach(message => {
            message.read = true;
        });
        this.saveMessages();
        this.updateUnreadCount();
        this.updateBadge();
    }

    // Actualizar contador de no leídos
    updateUnreadCount() {
        this.unreadCount = this.messages.filter(m => !m.read).length;
        
        // Actualizar UI si existe
        const badgeElement = document.querySelector('.notification-badge');
        if (badgeElement) {
            if (this.unreadCount > 0) {
                badgeElement.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
                badgeElement.style.display = 'block';
            } else {
                badgeElement.style.display = 'none';
            }
        }

        // Actualizar título de la página
        if (this.unreadCount > 0) {
            document.title = `(${this.unreadCount}) Comunicaciones Internas`;
        } else {
            document.title = 'Comunicaciones Internas';
        }
    }

    // Actualizar badge de la aplicación
    updateBadge() {
        if ('navigator' in window && 'setAppBadge' in navigator) {
            if (this.unreadCount > 0) {
                navigator.setAppBadge(this.unreadCount);
            } else {
                navigator.clearAppBadge();
            }
        }

        // Enviar mensaje al Service Worker
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.ready.then(registration => {
                if (registration.active) {
                    registration.active.postMessage({
                        type: 'UPDATE_BADGE',
                        count: this.unreadCount
                    });
                }
            });
        }
    }

    // Guardar mensajes en localStorage
    saveMessages() {
        localStorage.setItem('messages', JSON.stringify(this.messages));
    }

    // Obtener mensajes
    getMessages() {
        return this.messages;
    }

    // Obtener mensajes no leídos
    getUnreadMessages() {
        return this.messages.filter(m => !m.read);
    }

    // Simular llegada de mensajes (para demo)
    startMessageSimulation() {
        const sampleMessages = [
            {
                title: 'Reunión de equipo',
                content: 'Recordatorio: Reunión de equipo mañana a las 10:00 AM',
                sender: 'Recursos Humanos',
                priority: 'high'
            },
            {
                title: 'Nuevo protocolo',
                content: 'Se ha actualizado el protocolo de seguridad. Revisar documento adjunto.',
                sender: 'Administración',
                priority: 'normal'
            },
            {
                title: 'Felicitaciones',
                content: 'Felicitaciones por el excelente trabajo realizado este mes.',
                sender: 'Gerencia',
                priority: 'low'
            }
        ];

        // Simular mensaje cada 45 segundos
        setInterval(() => {
            if (Math.random() > 0.7) { // 30% de probabilidad
                const randomMessage = sampleMessages[Math.floor(Math.random() * sampleMessages.length)];
                this.addMessage(randomMessage);
            }
        }, 45000);
    }

    // Crear widget de notificaciones para la UI
    createNotificationWidget() {
        const widget = document.createElement('div');
        widget.className = 'notification-widget';
        widget.innerHTML = `
            <div class="notification-icon" onclick="notificationManager.toggleNotificationPanel()">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.89 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"/>
                </svg>
                <span class="notification-badge" style="display: none;">0</span>
            </div>
        `;

        const style = document.createElement('style');
        style.textContent = `
            .notification-widget {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
            }
            
            .notification-icon {
                position: relative;
                background: #667eea;
                color: white;
                padding: 12px;
                border-radius: 50%;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                transition: all 0.3s ease;
            }
            
            .notification-icon:hover {
                background: #5a67d8;
                transform: scale(1.1);
            }
            
            .notification-badge {
                position: absolute;
                top: -5px;
                right: -5px;
                background: #ff4757;
                color: white;
                border-radius: 50%;
                min-width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: bold;
            }
        `;

        document.head.appendChild(style);
        return widget;
    }

    // Alternar panel de notificaciones
    toggleNotificationPanel() {
        // Implementar panel de notificaciones aquí
        console.log('Mostrar panel de notificaciones');
        this.markAllAsRead(); // Por ahora, marcar todas como leídas al hacer click
    }
}

// Inicializar el gestor de notificaciones
let notificationManager;

document.addEventListener('DOMContentLoaded', () => {
    notificationManager = new NotificationManager();
    
    // Agregar widget a la página si no es la página de login
    if (!window.location.pathname.includes('login.html') && !window.location.pathname.includes('inicio.html')) {
        document.body.appendChild(notificationManager.createNotificationWidget());
    }
});

// Exportar para uso global
window.notificationManager = notificationManager;