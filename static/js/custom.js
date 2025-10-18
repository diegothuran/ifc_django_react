// JavaScript personalizado para o Digital Twin Project

// Funções utilitárias
function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'flex';
    }
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// Função para atualizar relógio
function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('pt-BR');
    const clockElement = document.getElementById('currentTime');
    if (clockElement) {
        clockElement.textContent = timeString;
    }
}

// Função para fazer requisições AJAX
async function fetchData(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Erro ao buscar dados:', error);
        return null;
    }
}

// Função para atualizar dados dos sensores
async function updateSensorData() {
    try {
        const data = await fetchData('/sensors/api/sensors/all/');
        if (data && data.sensors) {
            updateSensorDisplay(data.sensors);
        }
    } catch (error) {
        console.error('Erro ao atualizar dados dos sensores:', error);
    }
}

// Função para atualizar exibição dos sensores
function updateSensorDisplay(sensors) {
    const container = document.getElementById('sensorsList');
    if (!container) return;
    
    container.innerHTML = '';
    
    sensors.forEach(sensor => {
        const sensorElement = createSensorElement(sensor);
        container.appendChild(sensorElement);
    });
}

// Função para criar elemento de sensor
function createSensorElement(sensor) {
    const div = document.createElement('div');
    div.className = 'd-flex justify-content-between align-items-center mb-2';
    
    const statusClass = sensor.is_online ? 'status-online' : 'status-offline';
    
    div.innerHTML = `
        <div>
            <span class="sensor-status ${statusClass}"></span>
            <strong>${sensor.name}</strong>
            <br>
            <small class="text-muted">${sensor.type}</small>
        </div>
        <div class="text-end">
            ${sensor.latest_data ? 
                `<div class="fw-bold">${sensor.latest_data.display_value}</div>
                 <small class="text-muted">${new Date(sensor.latest_data.timestamp).toLocaleTimeString()}</small>` : 
                '<div class="text-muted">Sem dados</div>'
            }
        </div>
    `;
    
    return div;
}

// Função para atualizar dados do dashboard
async function updateDashboardData() {
    try {
        const data = await fetchData('/dashboard/api/data/?type=summary');
        if (data) {
            updateDashboardStats(data);
        }
    } catch (error) {
        console.error('Erro ao atualizar dados do dashboard:', error);
    }
}

// Função para atualizar estatísticas do dashboard
function updateDashboardStats(data) {
    // Atualizar contadores se existirem
    const activeSensorsElement = document.getElementById('activeSensors');
    if (activeSensorsElement) {
        activeSensorsElement.textContent = data.active_sensors || 0;
    }
    
    const totalSensorsElement = document.getElementById('totalSensors');
    if (totalSensorsElement) {
        totalSensorsElement.textContent = data.active_sensors || 0;
    }
    
    const alertsElement = document.getElementById('activeAlerts');
    if (alertsElement) {
        alertsElement.textContent = data.active_alerts || 0;
    }
}

// Função para mostrar notificação
function showNotification(message, type = 'info') {
    // Criar elemento de notificação
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Remover automaticamente após 5 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Função para inicializar atualizações automáticas
function initializeAutoUpdates() {
    // Atualizar relógio a cada segundo
    setInterval(updateClock, 1000);
    updateClock();
    
    // Atualizar dados a cada 30 segundos
    setInterval(() => {
        updateSensorData();
        updateDashboardData();
    }, 30000);
    
    // Atualizar dados imediatamente
    updateSensorData();
    updateDashboardData();
}

// Função para tratar erros de rede
function handleNetworkError(error) {
    console.error('Erro de rede:', error);
    showNotification('Erro de conexão. Verificando automaticamente...', 'warning');
    
    // Tentar reconectar após 10 segundos
    setTimeout(() => {
        updateSensorData();
        updateDashboardData();
    }, 10000);
}

// Função para verificar conectividade
async function checkConnectivity() {
    try {
        const response = await fetch('/dashboard/api/data/?type=summary', {
            method: 'HEAD'
        });
        return response.ok;
    } catch (error) {
        return false;
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar atualizações automáticas
    initializeAutoUpdates();
    
    // Adicionar animação de fade-in aos elementos
    const elements = document.querySelectorAll('.stat-card, .alert-item');
    elements.forEach((element, index) => {
        element.style.animationDelay = `${index * 0.1}s`;
        element.classList.add('fade-in');
    });
    
    // Configurar tratamento de erros de rede
    window.addEventListener('online', () => {
        showNotification('Conexão restaurada!', 'success');
        updateSensorData();
        updateDashboardData();
    });
    
    window.addEventListener('offline', () => {
        showNotification('Conexão perdida. Tentando reconectar...', 'danger');
    });
});

// Funções específicas para visualização 3D
function initViewerControls() {
    // Esta função será sobrescrita pelos templates específicos
    console.log('Controles do visualizador 3D inicializados');
}

// Exportar funções para uso global
window.DigitalTwin = {
    showLoading,
    hideLoading,
    updateClock,
    fetchData,
    updateSensorData,
    updateDashboardData,
    showNotification,
    handleNetworkError,
    checkConnectivity,
    initViewerControls
};
