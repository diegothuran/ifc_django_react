/**
 * Melhorias de acessibilidade para IFC Digital Twin
 * Implementa navegação por teclado e outras funcionalidades a11y
 */

class AccessibilityManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupKeyboardNavigation();
        this.setupSkipLinks();
        this.setupFocusManagement();
        this.setupARIALabels();
    }

    /**
     * Configura navegação por teclado
     */
    setupKeyboardNavigation() {
        // Atalhos de teclado globais
        document.addEventListener('keydown', (e) => {
            // Alt + H: Ir para home/dashboard
            if (e.altKey && e.key === 'h') {
                e.preventDefault();
                window.location.href = '/dashboard/';
            }

            // Alt + M: Abrir menu principal
            if (e.altKey && e.key === 'm') {
                e.preventDefault();
                const menu = document.querySelector('.main-menu, nav');
                if (menu) {
                    const firstLink = menu.querySelector('a');
                    if (firstLink) firstLink.focus();
                }
            }

            // Alt + S: Focar na busca
            if (e.altKey && e.key === 's') {
                e.preventDefault();
                const searchInput = document.querySelector('input[type="search"], input[name="search"]');
                if (searchInput) searchInput.focus();
            }

            // Escape: Fechar modals/overlays
            if (e.key === 'Escape') {
                this.closeTopModal();
            }
        });

        // Navegação em tabelas
        this.setupTableNavigation();

        // Navegação em cards/grids
        this.setupGridNavigation();
    }

    /**
     * Configura skip links para pular para conteúdo principal
     */
    setupSkipLinks() {
        // Criar skip link se não existir
        let skipLink = document.getElementById('skip-to-main');
        
        if (!skipLink) {
            skipLink = document.createElement('a');
            skipLink.id = 'skip-to-main';
            skipLink.href = '#main-content';
            skipLink.className = 'skip-link';
            skipLink.textContent = 'Pular para conteúdo principal';
            
            document.body.insertBefore(skipLink, document.body.firstChild);
        }

        // Garantir que o alvo existe
        let mainContent = document.getElementById('main-content');
        if (!mainContent) {
            mainContent = document.querySelector('main, [role="main"]');
            if (mainContent && !mainContent.id) {
                mainContent.id = 'main-content';
            }
        }

        // Fazer o alvo focável se necessário
        if (mainContent && !mainContent.hasAttribute('tabindex')) {
            mainContent.setAttribute('tabindex', '-1');
        }
    }

    /**
     * Gerenciamento de foco para modais e overlays
     */
    setupFocusManagement() {
        // Trap focus em modais
        document.addEventListener('focusin', (e) => {
            const modal = document.querySelector('.modal.active, .overlay.active');
            if (modal && !modal.contains(e.target)) {
                e.preventDefault();
                const focusable = modal.querySelectorAll(
                    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                );
                if (focusable.length > 0) {
                    focusable[0].focus();
                }
            }
        });
    }

    /**
     * Adiciona/melhora ARIA labels automaticamente
     */
    setupARIALabels() {
        // Botões sem label
        document.querySelectorAll('button:not([aria-label])').forEach(btn => {
            if (btn.textContent.trim()) {
                btn.setAttribute('aria-label', btn.textContent.trim());
            }
        });

        // Links sem texto
        document.querySelectorAll('a:not([aria-label])').forEach(link => {
            if (!link.textContent.trim() && link.querySelector('img')) {
                const img = link.querySelector('img');
                if (img.alt) {
                    link.setAttribute('aria-label', img.alt);
                }
            }
        });

        // Inputs sem label
        document.querySelectorAll('input:not([aria-label])').forEach(input => {
            if (input.placeholder) {
                input.setAttribute('aria-label', input.placeholder);
            }
        });
    }

    /**
     * Navegação por teclado em tabelas
     */
    setupTableNavigation() {
        document.querySelectorAll('table[data-keyboard-nav]').forEach(table => {
            const cells = Array.from(table.querySelectorAll('td, th'));
            
            cells.forEach((cell, index) => {
                cell.setAttribute('tabindex', index === 0 ? '0' : '-1');
                
                cell.addEventListener('keydown', (e) => {
                    const row = cell.parentElement;
                    const cellIndex = Array.from(row.children).indexOf(cell);
                    
                    let targetCell = null;
                    
                    switch(e.key) {
                        case 'ArrowRight':
                            targetCell = row.children[cellIndex + 1];
                            break;
                        case 'ArrowLeft':
                            targetCell = row.children[cellIndex - 1];
                            break;
                        case 'ArrowDown':
                            const nextRow = row.nextElementSibling;
                            if (nextRow) targetCell = nextRow.children[cellIndex];
                            break;
                        case 'ArrowUp':
                            const prevRow = row.previousElementSibling;
                            if (prevRow) targetCell = prevRow.children[cellIndex];
                            break;
                    }
                    
                    if (targetCell) {
                        e.preventDefault();
                        targetCell.focus();
                        targetCell.setAttribute('tabindex', '0');
                        cell.setAttribute('tabindex', '-1');
                    }
                });
            });
        });
    }

    /**
     * Navegação por teclado em grids de cards
     */
    setupGridNavigation() {
        document.querySelectorAll('[data-grid-nav]').forEach(grid => {
            const items = Array.from(grid.children);
            
            items.forEach((item, index) => {
                if (!item.hasAttribute('tabindex')) {
                    item.setAttribute('tabindex', index === 0 ? '0' : '-1');
                }
                
                item.addEventListener('keydown', (e) => {
                    const columns = parseInt(grid.dataset.columns || '3');
                    const currentIndex = items.indexOf(item);
                    
                    let targetIndex = null;
                    
                    switch(e.key) {
                        case 'ArrowRight':
                            targetIndex = currentIndex + 1;
                            break;
                        case 'ArrowLeft':
                            targetIndex = currentIndex - 1;
                            break;
                        case 'ArrowDown':
                            targetIndex = currentIndex + columns;
                            break;
                        case 'ArrowUp':
                            targetIndex = currentIndex - columns;
                            break;
                        case 'Home':
                            targetIndex = 0;
                            break;
                        case 'End':
                            targetIndex = items.length - 1;
                            break;
                    }
                    
                    if (targetIndex !== null && items[targetIndex]) {
                        e.preventDefault();
                        items[targetIndex].focus();
                        items[targetIndex].setAttribute('tabindex', '0');
                        item.setAttribute('tabindex', '-1');
                    }
                });
            });
        });
    }

    /**
     * Fecha o modal/overlay mais recente
     */
    closeTopModal() {
        const modals = document.querySelectorAll('.modal.active, .overlay.active');
        if (modals.length > 0) {
            const topModal = modals[modals.length - 1];
            const closeBtn = topModal.querySelector('.close, [data-close]');
            if (closeBtn) {
                closeBtn.click();
            } else {
                topModal.classList.remove('active');
            }
        }
    }

    /**
     * Anuncia mensagem para screen readers
     */
    announce(message, priority = 'polite') {
        let announcer = document.getElementById('aria-announcer');
        
        if (!announcer) {
            announcer = document.createElement('div');
            announcer.id = 'aria-announcer';
            announcer.setAttribute('aria-live', priority);
            announcer.setAttribute('aria-atomic', 'true');
            announcer.style.cssText = 'position:absolute;left:-10000px;width:1px;height:1px;overflow:hidden;';
            document.body.appendChild(announcer);
        }
        
        // Limpar e adicionar nova mensagem
        announcer.textContent = '';
        setTimeout(() => {
            announcer.textContent = message;
        }, 100);
    }
}

// Inicializar quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.a11y = new AccessibilityManager();
    });
} else {
    window.a11y = new AccessibilityManager();
}

// Adicionar estilos CSS
const style = document.createElement('style');
style.textContent = `
    /* Skip link */
    .skip-link {
        position: absolute;
        top: -40px;
        left: 0;
        background: #3b82f6;
        color: white;
        padding: 8px 16px;
        text-decoration: none;
        z-index: 100000;
        border-radius: 0 0 4px 0;
    }

    .skip-link:focus {
        top: 0;
    }

    /* Focus visible enhancement */
    *:focus-visible {
        outline: 2px solid #3b82f6;
        outline-offset: 2px;
    }

    /* Assistive text (screen reader only) */
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border-width: 0;
    }
`;
document.head.appendChild(style);

