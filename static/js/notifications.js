/**
 * Sistema de notificações Toast para IFC Digital Twin
 * Fornece feedback visual consistente para ações do usuário
 */

class NotificationSystem {
    constructor() {
        this.container = this.createContainer();
        this.notifications = [];
    }

    createContainer() {
        let container = document.getElementById('notification-container');
        
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            container.setAttribute('role', 'region');
            container.setAttribute('aria-label', 'Notificações');
            document.body.appendChild(container);
        }
        
        return container;
    }

    show(message, type = 'info', duration = 5000) {
        const notification = this.createNotification(message, type);
        this.notifications.push(notification);
        this.container.appendChild(notification);
        
        // Animar entrada
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Auto-remover após duration
        if (duration > 0) {
            setTimeout(() => {
                this.remove(notification);
            }, duration);
        }
        
        return notification;
    }

    createNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.setAttribute('role', 'alert');
        notification.setAttribute('aria-live', 'assertive');
        
        const icon = this.getIcon(type);
        const closeBtn = document.createElement('button');
        closeBtn.className = 'notification-close';
        closeBtn.innerHTML = '&times;';
        closeBtn.setAttribute('aria-label', 'Fechar notificação');
        closeBtn.onclick = () => this.remove(notification);
        
        notification.innerHTML = `
            <span class="notification-icon">${icon}</span>
            <span class="notification-message">${message}</span>
        `;
        notification.appendChild(closeBtn);
        
        return notification;
    }

    getIcon(type) {
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };
        return icons[type] || icons.info;
    }

    remove(notification) {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
            const index = this.notifications.indexOf(notification);
            if (index > -1) {
                this.notifications.splice(index, 1);
            }
        }, 300);
    }

    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }

    clear() {
        this.notifications.forEach(notification => {
            this.remove(notification);
        });
    }
}

// Criar instância global
window.notify = new NotificationSystem();

// Adicionar estilos CSS
const style = document.createElement('style');
style.textContent = `
    .notification-container {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        max-width: 400px;
    }

    .notification {
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        padding: 16px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 12px;
        transform: translateX(calc(100% + 30px));
        transition: transform 0.3s ease-in-out, opacity 0.3s;
        opacity: 0;
    }

    .notification.show {
        transform: translateX(0);
        opacity: 1;
    }

    .notification-icon {
        font-size: 24px;
        flex-shrink: 0;
    }

    .notification-message {
        flex: 1;
        color: #333;
    }

    .notification-close {
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #999;
        padding: 0;
        width: 24px;
        height: 24px;
        flex-shrink: 0;
        transition: color 0.2s;
    }

    .notification-close:hover {
        color: #333;
    }

    .notification-success {
        border-left: 4px solid #10b981;
    }

    .notification-success .notification-icon {
        color: #10b981;
    }

    .notification-error {
        border-left: 4px solid #ef4444;
    }

    .notification-error .notification-icon {
        color: #ef4444;
    }

    .notification-warning {
        border-left: 4px solid #f59e0b;
    }

    .notification-warning .notification-icon {
        color: #f59e0b;
    }

    .notification-info {
        border-left: 4px solid #3b82f6;
    }

    .notification-info .notification-icon {
        color: #3b82f6;
    }

    @media (max-width: 640px) {
        .notification-container {
            right: 10px;
            left: 10px;
            max-width: none;
        }
    }
`;
document.head.appendChild(style);

