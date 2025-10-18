// Digital Twin - Visualizador IFC com integração de sensores
// Autor: Desenvolvedor Frontend Sênior

// Variáveis globais
let viewer;
let sensorData = [];
let highlightedElements = new Map();
let tooltip = null;
let isInitialized = false;

// Configurações
const CONFIG = {
    UPDATE_INTERVAL: 5000, // 5 segundos
    API_ENDPOINT: '/dashboard/api/sensor-data/',
    TOOLTIP_OFFSET: 10,
    HIGHLIGHT_COLOR: 0x00ff00,
    INACTIVE_COLOR: 0xff0000,
    HIGHLIGHT_OPACITY: 0.5
};

// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    console.log('Digital Twin - Inicializando...');
    
    // Verificar se estamos em uma página que precisa do visualizador 3D
    const viewerContainer = document.getElementById('viewer-container');
    const needsViewer = viewerContainer !== null;
    
    if (needsViewer) {
        // Verificar dependências apenas se necessário
        if (typeof THREE === 'undefined') {
            console.error('Three.js não foi carregado');
            showNotification('Erro: Three.js não foi carregado', 'error');
            return;
        }
        
        if (typeof IfcViewer === 'undefined') {
            console.warn('Web-IFC-Viewer não foi carregado, usando modo fallback');
            // Não retornar, continuar sem o viewer 3D
        } else {
            console.log('Todas as dependências carregadas com sucesso');
            initializeViewer();
            initializeTooltip();
            initializeEventListeners();
        }
        
        startDataUpdates();
    }
    
    // Sempre atualizar relógio
    updateClock();
});

/**
 * Inicializa o visualizador IFC
 */
async function initializeViewer() {
    try {
        showLoading();
        
        // Verificar se há arquivo IFC disponível
        const ifcURL = document.body.dataset.ifcUrl;
        if (!ifcURL) {
            console.warn('Nenhum arquivo IFC disponível');
            hideLoading();
            return;
        }
        
        // Obter referência do container
        const container = document.getElementById('viewer-container');
        if (!container) {
            throw new Error('Container do visualizador não encontrado');
        }

        // Instanciar o IfcViewer
        viewer = new IfcViewer({
            container: container,
            backgroundColor: new THREE.Color(0xf0f0f0)
        });

        // Configurar o visualizador
        await configureViewer();
        
        // Carregar modelo IFC
        await loadIfcModel();
        
        // Carregar dados iniciais dos sensores
        await loadInitialSensorData();
        
        hideLoading();
        isInitialized = true;
        
        console.log('Visualizador IFC inicializado com sucesso');
        
    } catch (error) {
        console.error('Erro ao inicializar visualizador:', error);
        showNotification('Erro ao carregar visualizador 3D', 'error');
        hideLoading();
    }
}

/**
 * Configura o visualizador IFC
 */
async function configureViewer() {
    try {
        // Configurar grade e eixos
        viewer.grid.setGrid();
        viewer.axes.setAxes();
        
        // Configurar controles de câmera
        viewer.IFC.selector.preselection.material.color.setHex(0x00ff00);
        viewer.IFC.selector.preselection.material.opacity = 0.3;
        
        // Configurar iluminação
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(10, 10, 10);
        viewer.context.getScene().add(directionalLight);
        
        // Configurar luz ambiente
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        viewer.context.getScene().add(ambientLight);
        
        console.log('Visualizador configurado');
        
    } catch (error) {
        console.error('Erro ao configurar visualizador:', error);
        throw error;
    }
}

/**
 * Carrega o modelo IFC
 */
async function loadIfcModel() {
    try {
        // Obter URL do arquivo IFC do atributo data-ifc-url
        const ifcURL = document.body.dataset.ifcUrl;
        
        if (!ifcURL) {
            console.warn('URL do arquivo IFC não encontrada');
            showNotification('Nenhum arquivo IFC disponível. Faça upload de um modelo para visualizar.', 'warning');
            return;
        }
        
        console.log('Carregando modelo IFC:', ifcURL);
        
        // Carregar o modelo
        await viewer.IFC.loadIfcUrl(ifcURL);
        
        console.log('Modelo IFC carregado com sucesso');
        
    } catch (error) {
        console.error('Erro ao carregar modelo IFC:', error);
        showNotification('Erro ao carregar modelo IFC. Verifique se o arquivo existe.', 'error');
        throw error;
    }
}

/**
 * Inicializa o tooltip
 */
function initializeTooltip() {
    tooltip = document.getElementById('tooltip');
    if (!tooltip) {
        console.warn('Elemento tooltip não encontrado');
        return;
    }
    
    // Configurar estilos iniciais
    tooltip.style.display = 'none';
    tooltip.style.position = 'absolute';
    tooltip.style.zIndex = '10000';
    
    console.log('Tooltip inicializado');
}

/**
 * Inicializa os event listeners
 */
function initializeEventListeners() {
    // Event listener para movimento do mouse
    window.addEventListener('mousemove', handleMouseMove);
    
    // Event listener para redimensionamento da janela
    window.addEventListener('resize', handleWindowResize);
    
    // Event listener para teclas de atalho
    document.addEventListener('keydown', handleKeyDown);
    
    console.log('Event listeners inicializados');
}

/**
 * Carrega dados iniciais dos sensores
 */
async function loadInitialSensorData() {
    try {
        const data = await fetchSensorData();
        if (data && data.length > 0) {
            sensorData = data;
            await updateSceneWithData(data);
            console.log('Dados iniciais dos sensores carregados:', data.length, 'sensores');
        }
    } catch (error) {
        console.error('Erro ao carregar dados iniciais dos sensores:', error);
    }
}

/**
 * Busca dados dos sensores da API
 */
async function fetchSensorData() {
    try {
        const response = await fetch(CONFIG.API_ENDPOINT, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
        
    } catch (error) {
        console.error('Erro ao buscar dados dos sensores:', error);
        throw error;
    }
}

/**
 * Atualiza a cena 3D com os dados dos sensores
 */
async function updateSceneWithData(sensorData) {
    try {
        if (!viewer || !isInitialized) {
            console.warn('Visualizador não inicializado');
            return;
        }
        
        console.log('Atualizando cena com dados dos sensores:', sensorData.length);
        
        // Limpar destaques anteriores
        clearHighlights();
        
        // Processar cada sensor
        for (const sensor of sensorData) {
            if (sensor.location_id) {
                await highlightSensorElement(sensor);
            }
        }
        
        // Atualizar painel de sensores
        updateSensorPanel(sensorData);
        
        console.log('Cena atualizada com sucesso');
        
    } catch (error) {
        console.error('Erro ao atualizar cena:', error);
    }
}

/**
 * Destaca um elemento do sensor no modelo 3D
 */
async function highlightSensorElement(sensor) {
    try {
        // Buscar o subset do elemento pelo location_id
        const subset = viewer.IFC.getSubset(0, null, sensor.location_id);
        
        if (!subset) {
            console.warn(`Elemento não encontrado para sensor ${sensor.name} (ID: ${sensor.location_id})`);
            return;
        }
        
        // Criar material baseado no status do sensor
        const material = createSensorMaterial(sensor);
        
        // Aplicar material ao subset
        viewer.IFC.subsets.setSubsetMaterial(subset, material);
        
        // Armazenar dados do sensor no objeto
        subset.userData.sensorInfo = sensor;
        
        // Armazenar referência para limpeza posterior
        highlightedElements.set(sensor.location_id, subset);
        
        console.log(`Sensor ${sensor.name} destacado no elemento ${sensor.location_id}`);
        
    } catch (error) {
        console.error(`Erro ao destacar sensor ${sensor.name}:`, error);
    }
}

/**
 * Cria material para o sensor baseado no seu status
 */
function createSensorMaterial(sensor) {
    const color = sensor.is_active ? CONFIG.HIGHLIGHT_COLOR : CONFIG.INACTIVE_COLOR;
    
    return new THREE.MeshLambertMaterial({
        color: color,
        transparent: true,
        opacity: CONFIG.HIGHLIGHT_OPACITY
    });
}

/**
 * Limpa todos os destaques da cena
 */
function clearHighlights() {
    try {
        for (const [locationId, subset] of highlightedElements) {
            if (subset && subset.userData) {
                delete subset.userData.sensorInfo;
            }
        }
        highlightedElements.clear();
        
        // Remover todos os subsets destacados
        viewer.IFC.subsets.removeSubset(0, null);
        
        console.log('Destaques limpos');
        
    } catch (error) {
        console.error('Erro ao limpar destaques:', error);
    }
}

/**
 * Manipula o movimento do mouse
 */
function handleMouseMove(event) {
    if (!viewer || !isInitialized) return;
    
    try {
        // Obter elemento sob o cursor
        const item = viewer.IFC.pickIfcItem(event);
        
        if (item && item.userData && item.userData.sensorInfo) {
            // Mostrar tooltip com informações do sensor
            showTooltip(event, item.userData.sensorInfo);
            
            // Destacar elemento
            viewer.IFC.highlightIfcItem(item);
            
        } else {
            // Ocultar tooltip
            hideTooltip();
            
            // Remover destaque
            viewer.IFC.removeIfcHighlight();
        }
        
    } catch (error) {
        console.error('Erro ao manipular movimento do mouse:', error);
    }
}

/**
 * Mostra o tooltip com informações do sensor
 */
function showTooltip(event, sensorInfo) {
    if (!tooltip) return;
    
    try {
        // Atualizar conteúdo do tooltip
        document.getElementById('tooltip-title').textContent = sensorInfo.name;
        document.getElementById('tooltip-count').textContent = `Contagem: ${sensorInfo.latest_count}`;
        
        const statusElement = document.getElementById('tooltip-status');
        statusElement.textContent = `Status: ${sensorInfo.is_active ? 'Ativo' : 'Inativo'}`;
        statusElement.className = `sensor-status ${sensorInfo.is_active ? 'status-active' : 'status-inactive'}`;
        
        // Posicionar tooltip
        const x = event.clientX + CONFIG.TOOLTIP_OFFSET;
        const y = event.clientY + CONFIG.TOOLTIP_OFFSET;
        
        tooltip.style.left = `${x}px`;
        tooltip.style.top = `${y}px`;
        tooltip.style.display = 'block';
        
    } catch (error) {
        console.error('Erro ao mostrar tooltip:', error);
    }
}

/**
 * Oculta o tooltip
 */
function hideTooltip() {
    if (tooltip) {
        tooltip.style.display = 'none';
    }
}

/**
 * Manipula o redimensionamento da janela
 */
function handleWindowResize() {
    if (viewer && isInitialized) {
        try {
            viewer.context.getRenderer().setSize(window.innerWidth, window.innerHeight);
            viewer.context.getCamera().aspect = window.innerWidth / window.innerHeight;
            viewer.context.getCamera().updateProjectionMatrix();
        } catch (error) {
            console.error('Erro ao redimensionar visualizador:', error);
        }
    }
}

/**
 * Manipula teclas de atalho
 */
function handleKeyDown(event) {
    switch (event.key) {
        case 'r':
        case 'R':
            // Resetar câmera
            if (viewer && isInitialized) {
                viewer.IFC.cameraControls.reset();
            }
            break;
        case 'h':
        case 'H':
            // Toggle ajuda
            toggleHelp();
            break;
        case 'Escape':
            // Limpar seleção
            if (viewer && isInitialized) {
                viewer.IFC.removeIfcHighlight();
                hideTooltip();
            }
            break;
    }
}

/**
 * Atualiza o painel de sensores
 */
function updateSensorPanel(sensorData) {
    try {
        const sensorsList = document.getElementById('sensorsList');
        if (!sensorsList) return;
        
        // Limpar lista atual
        sensorsList.innerHTML = '';
        
        // Adicionar cada sensor
        sensorData.forEach(sensor => {
            const sensorElement = createSensorElement(sensor);
            sensorsList.appendChild(sensorElement);
        });
        
        console.log('Painel de sensores atualizado');
        
    } catch (error) {
        console.error('Erro ao atualizar painel de sensores:', error);
    }
}

/**
 * Cria elemento HTML para um sensor
 */
function createSensorElement(sensor) {
    const div = document.createElement('div');
    div.className = 'd-flex justify-content-between align-items-center mb-2';
    
    const statusClass = sensor.is_active ? 'status-online' : 'status-offline';
    
    div.innerHTML = `
        <div>
            <span class="sensor-status ${statusClass}"></span>
            <strong>${sensor.name}</strong>
            <br>
            <small class="text-muted">ID: ${sensor.location_id}</small>
        </div>
        <div class="text-end">
            <div class="fw-bold">${sensor.latest_count}</div>
            <small class="text-muted">${sensor.is_active ? 'Ativo' : 'Inativo'}</small>
        </div>
    `;
    
    // Adicionar evento de clique
    div.addEventListener('click', () => {
        focusOnSensor(sensor);
    });
    
    return div;
}

/**
 * Foca na câmera no sensor selecionado
 */
function focusOnSensor(sensor) {
    if (!viewer || !isInitialized) return;
    
    try {
        // Buscar elemento do sensor
        const subset = viewer.IFC.getSubset(0, null, sensor.location_id);
        
        if (subset) {
            // Calcular bounding box do elemento
            const box = new THREE.Box3().setFromObject(subset);
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());
            
            // Posicionar câmera
            const distance = Math.max(size.x, size.y, size.z) * 2;
            viewer.IFC.cameraControls.setLookAt(
                center.x + distance,
                center.y + distance,
                center.z + distance,
                center.x,
                center.y,
                center.z,
                true
            );
            
            console.log(`Foco no sensor ${sensor.name}`);
        }
        
    } catch (error) {
        console.error('Erro ao focar no sensor:', error);
    }
}

/**
 * Inicia as atualizações automáticas dos dados
 */
function startDataUpdates() {
    // Atualizar dados a cada intervalo configurado
    setInterval(async () => {
        try {
            const data = await fetchSensorData();
            if (data && data.length > 0) {
                sensorData = data;
                await updateSceneWithData(data);
                console.log('Dados dos sensores atualizados');
            }
        } catch (error) {
            console.error('Erro ao atualizar dados dos sensores:', error);
            showNotification('Erro ao atualizar dados dos sensores', 'error');
        }
    }, CONFIG.UPDATE_INTERVAL);
    
    console.log('Atualizações automáticas iniciadas');
}

/**
 * Atualiza o relógio
 */
function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('pt-BR');
    const clockElement = document.getElementById('currentTime');
    if (clockElement) {
        clockElement.textContent = timeString;
    }
}

/**
 * Mostra overlay de loading
 */
function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'flex';
    }
}

/**
 * Oculta overlay de loading
 */
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

/**
 * Mostra notificação
 */
function showNotification(message, type = 'info') {
    // Criar elemento de notificação
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="d-flex justify-content-between align-items-start">
            <div>
                <strong>${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
                <p class="mb-0 mt-1">${message}</p>
            </div>
            <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Remover automaticamente após 5 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

/**
 * Toggle ajuda
 */
function toggleHelp() {
    const helpText = `
        Atalhos do teclado:
        - R: Resetar câmera
        - H: Mostrar/ocultar ajuda
        - ESC: Limpar seleção
        
        Controles do mouse:
        - Clique e arraste: Rotacionar câmera
        - Scroll: Zoom in/out
        - Hover: Mostrar informações do sensor
    `;
    
    showNotification(helpText, 'info');
}

/**
 * Função para exportar dados (para debugging)
 */
function exportSensorData() {
    console.log('Dados dos sensores:', sensorData);
    return sensorData;
}

/**
 * Função para limpar todos os dados
 */
function clearAllData() {
    sensorData = [];
    clearHighlights();
    hideTooltip();
    console.log('Todos os dados limpos');
}

// Atualizar relógio a cada segundo
setInterval(updateClock, 1000);

// Exportar funções para uso global
window.DigitalTwin = {
    viewer,
    sensorData,
    fetchSensorData,
    updateSceneWithData,
    focusOnSensor,
    clearAllData,
    exportSensorData,
    showNotification,
    toggleHelp
};

console.log('Digital Twin - Sistema inicializado com sucesso!');
