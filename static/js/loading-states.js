/**
 * Sistema de estados de carregamento para IFC Digital Twin
 * Fornece feedback visual durante operações assíncronas
 */

class LoadingStateManager {
    constructor() {
        this.activeLoaders = new Set();
        this.overlay = null;
    }

    /**
     * Mostra indicador de loading em um elemento específico
     */
    show(element, message = 'Carregando...') {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }

        if (!element) {
            console.error('Elemento não encontrado para loading state');
            return;
        }

        // Salvar conteúdo original
        element.dataset.originalContent = element.innerHTML;
        element.dataset.originalDisabled = element.disabled;

        // Desabilitar elemento se for um botão/input
        if (element.tagName === 'BUTTON' || element.tagName === 'INPUT') {
            element.disabled = true;
        }

        // Adicionar spinner
        element.innerHTML = `
            <span class="loading-spinner"></span>
            <span class="loading-text">${message}</span>
        `;
        element.classList.add('loading-state');

        this.activeLoaders.add(element);
    }

    /**
     * Remove indicador de loading de um elemento
     */
    hide(element) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }

        if (!element) return;

        // Restaurar conteúdo original
        if (element.dataset.originalContent) {
            element.innerHTML = element.dataset.originalContent;
            delete element.dataset.originalContent;
        }

        // Restaurar estado disabled
        if (element.dataset.originalDisabled !== undefined) {
            element.disabled = element.dataset.originalDisabled === 'true';
            delete element.dataset.originalDisabled;
        }

        element.classList.remove('loading-state');
        this.activeLoaders.delete(element);
    }

    /**
     * Mostra overlay de loading em tela cheia
     */
    showOverlay(message = 'Carregando...') {
        if (this.overlay) {
            return; // Já existe um overlay
        }

        this.overlay = document.createElement('div');
        this.overlay.className = 'loading-overlay';
        this.overlay.setAttribute('role', 'alert');
        this.overlay.setAttribute('aria-live', 'assertive');
        this.overlay.innerHTML = `
            <div class="loading-overlay-content">
                <div class="loading-spinner-large"></div>
                <p class="loading-overlay-text">${message}</p>
            </div>
        `;

        document.body.appendChild(this.overlay);
        document.body.style.overflow = 'hidden';

        // Animar entrada
        setTimeout(() => {
            this.overlay.classList.add('show');
        }, 10);
    }

    /**
     * Remove overlay de loading
     */
    hideOverlay() {
        if (!this.overlay) return;

        this.overlay.classList.remove('show');
        setTimeout(() => {
            if (this.overlay && this.overlay.parentNode) {
                this.overlay.parentNode.removeChild(this.overlay);
            }
            this.overlay = null;
            document.body.style.overflow = '';
        }, 300);
    }

    /**
     * Mostra skeleton screen em um elemento
     */
    showSkeleton(element, count = 3) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }

        if (!element) return;

        element.dataset.originalContent = element.innerHTML;

        const skeleton = [];
        for (let i = 0; i < count; i++) {
            skeleton.push('<div class="skeleton-line"></div>');
        }

        element.innerHTML = `<div class="skeleton-container">${skeleton.join('')}</div>`;
        element.classList.add('skeleton-state');
    }

    /**
     * Remove skeleton screen
     */
    hideSkeleton(element) {
        this.hide(element); // Usa mesma lógica do hide
    }

    /**
     * Remove todos os estados de loading
     */
    clearAll() {
        this.activeLoaders.forEach(element => {
            this.hide(element);
        });
        this.hideOverlay();
    }
}

// Criar instância global
window.loading = new LoadingStateManager();

// Adicionar estilos CSS
const style = document.createElement('style');
style.textContent = `
    /* Loading spinner */
    .loading-spinner {
        display: inline-block;
        width: 16px;
        height: 16px;
        border: 2px solid #f3f3f3;
        border-top: 2px solid #3b82f6;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
        margin-right: 8px;
    }

    .loading-spinner-large {
        width: 48px;
        height: 48px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #3b82f6;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .loading-state {
        position: relative;
        pointer-events: none;
        opacity: 0.7;
    }

    .loading-text {
        vertical-align: middle;
    }

    /* Loading overlay */
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        opacity: 0;
        transition: opacity 0.3s;
    }

    .loading-overlay.show {
        opacity: 1;
    }

    .loading-overlay-content {
        background: white;
        padding: 32px 48px;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        text-align: center;
    }

    .loading-overlay-text {
        margin-top: 16px;
        color: #333;
        font-size: 16px;
    }

    /* Skeleton loading */
    .skeleton-container {
        padding: 16px 0;
    }

    .skeleton-line {
        height: 16px;
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: skeleton-loading 1.5s ease-in-out infinite;
        border-radius: 4px;
        margin-bottom: 12px;
    }

    .skeleton-line:last-child {
        margin-bottom: 0;
        width: 60%;
    }

    @keyframes skeleton-loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }

    .skeleton-state {
        pointer-events: none;
    }
`;
document.head.appendChild(style);

// Integração automática com formulários
document.addEventListener('DOMContentLoaded', () => {
    // Auto-loading em forms
    document.querySelectorAll('form[data-auto-loading]').forEach(form => {
        form.addEventListener('submit', (e) => {
            const submitBtn = form.querySelector('[type="submit"]');
            if (submitBtn) {
                loading.show(submitBtn, 'Enviando...');
            }
        });
    });

    // Auto-loading em links
    document.querySelectorAll('a[data-auto-loading]').forEach(link => {
        link.addEventListener('click', () => {
            loading.showOverlay('Carregando página...');
        });
    });
});

