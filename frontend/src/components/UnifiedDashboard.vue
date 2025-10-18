<template>
  <div class="unified-dashboard">
    <!-- Header do Dashboard -->
    <header class="dashboard-header">
      <div class="container-fluid">
        <div class="dashboard-header-content">
          <div>
            <h1 class="dashboard-title">
              <i class="fas fa-tachometer-alt"></i>
              IFC Monitoring - Dashboard
            </h1>
            <p class="dashboard-subtitle">
              Monitoramento em tempo real da planta industrial
            </p>
          </div>
          
          <div class="dashboard-actions">
            <div class="connection-status" :class="connectionStatusClass">
              <i :class="connectionIcon"></i>
              {{ connectionText }}
            </div>
            
            <button 
              class="btn btn-icon btn-outline"
              @click="openSearch"
              title="Busca Global (Ctrl+K)"
              aria-label="Abrir busca global"
            >
              <i class="fas fa-search"></i>
            </button>
          </div>
        </div>
        
        <!-- Navegação por Abas -->
        <nav class="dashboard-nav" role="tablist">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            class="nav-tab"
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
            role="tab"
            :aria-selected="activeTab === tab.id"
            :aria-controls="`panel-${tab.id}`"
          >
            <i :class="tab.icon"></i>
            {{ tab.label }}
          </button>
        </nav>
      </div>
    </header>
    
    <!-- Conteúdo do Dashboard -->
    <main class="dashboard-content">
      <div class="container-fluid">
        <!-- Aba: Visão Geral -->
        <section
          v-show="activeTab === 'overview'"
          id="panel-overview"
          class="dashboard-section"
          role="tabpanel"
        >
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon text-primary">
                <i class="fas fa-microchip"></i>
              </div>
              <div class="stat-value text-primary">{{ stats.totalSensors }}</div>
              <div class="stat-label">Sensores Totais</div>
            </div>
            
            <div class="stat-card">
              <div class="stat-icon text-success">
                <i class="fas fa-check-circle"></i>
              </div>
              <div class="stat-value text-success">{{ stats.onlineSensors }}</div>
              <div class="stat-label">Sensores Online</div>
            </div>
            
            <div class="stat-card">
              <div class="stat-icon text-info">
                <i class="fas fa-building"></i>
              </div>
              <div class="stat-value text-info">{{ stats.activePlants }}</div>
              <div class="stat-label">Plantas Ativas</div>
            </div>
            
            <div class="stat-card">
              <div class="stat-icon text-warning">
                <i class="fas fa-exclamation-triangle"></i>
              </div>
              <div class="stat-value text-warning">{{ stats.criticalAlerts }}</div>
              <div class="stat-label">Alertas Críticos</div>
            </div>
          </div>
          
          <!-- Planta Industrial Ativa -->
          <div v-if="activePlant" class="plant-showcase">
            <h2 class="section-title">
              <i class="fas fa-industry"></i>
              Planta Industrial Ativa
            </h2>
            
            <div class="plant-card">
              <div class="plant-preview">
                <div class="plant-icon">
                  <i class="fas fa-industry fa-5x"></i>
                </div>
                <div class="plant-info">
                  <h3 class="plant-name">{{ activePlant.name }}</h3>
                  <p v-if="activePlant.description" class="plant-description">
                    {{ activePlant.description }}
                  </p>
                  
                  <div class="plant-meta">
                    <div class="plant-meta-item">
                      <i class="fas fa-file"></i>
                      <span>{{ activePlant.file_size }}</span>
                    </div>
                    <div class="plant-meta-item">
                      <i class="fas fa-calendar"></i>
                      <span>{{ formatDate(activePlant.uploaded_at) }}</span>
                    </div>
                    <div class="plant-meta-item">
                      <span class="badge badge-success">
                        <i class="fas fa-check-circle"></i>
                        Ativa
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="plant-actions">
                <a 
                  :href="activePlant.viewer_url" 
                  class="btn btn-primary btn-lg"
                  aria-label="Abrir visualizador 3D da planta"
                >
                  <i class="fas fa-cube"></i>
                  Visualizador 3D
                </a>
                <button 
                  class="btn btn-outline btn-lg"
                  @click="showPlantDetails"
                  aria-label="Ver detalhes da planta"
                >
                  <i class="fas fa-info-circle"></i>
                  Detalhes
                </button>
              </div>
            </div>
          </div>
          
          <div v-else class="empty-state">
            <i class="fas fa-industry fa-4x text-muted"></i>
            <h3>Nenhuma planta ativa</h3>
            <p>Configure uma planta no painel administrativo</p>
          </div>
        </section>
        
        <!-- Aba: Sensores -->
        <section
          v-show="activeTab === 'sensors'"
          id="panel-sensors"
          class="dashboard-section"
          role="tabpanel"
        >
          <div class="section-header">
            <h2 class="section-title">
              <i class="fas fa-microchip"></i>
              Sensores ({{ sensors.length }})
            </h2>
            
            <div class="section-actions">
              <input
                v-model="sensorSearch"
                type="text"
                class="form-control"
                placeholder="Buscar sensores..."
                aria-label="Buscar sensores"
              />
            </div>
          </div>
          
          <div v-if="filteredSensors.length" class="sensors-grid">
            <SensorCard
              v-for="sensor in filteredSensors"
              :key="sensor.id"
              :sensor="sensor"
              :latest-value="getSensorLatestValue(sensor.id)"
              @view-details="viewSensorDetails"
            />
          </div>
          
          <div v-else class="empty-state">
            <i class="fas fa-microchip fa-4x text-muted"></i>
            <h3>Nenhum sensor encontrado</h3>
            <p v-if="sensorSearch">Tente ajustar sua busca</p>
            <p v-else>Adicione sensores no painel administrativo</p>
          </div>
        </section>
        
        <!-- Aba: Alertas -->
        <section
          v-show="activeTab === 'alerts'"
          id="panel-alerts"
          class="dashboard-section"
          role="tabpanel"
        >
          <h2 class="section-title">
            <i class="fas fa-exclamation-triangle"></i>
            Alertas Ativos ({{ alerts.length }})
          </h2>
          
          <div v-if="alerts.length" class="alerts-list">
            <div
              v-for="alert in alerts"
              :key="alert.id"
              class="alert-item"
              :class="`alert-item--${alert.severity}`"
            >
              <div class="alert-icon">
                <i :class="getAlertIcon(alert.severity)"></i>
              </div>
              
              <div class="alert-content">
                <div class="alert-header">
                  <strong>{{ alert.sensor_name }}</strong>
                  <span class="badge" :class="`badge-${alert.severity}`">
                    {{ alert.severity }}
                  </span>
                </div>
                <p class="alert-message">{{ alert.message }}</p>
                <div class="alert-meta">
                  <span>
                    <i class="fas fa-clock"></i>
                    {{ formatTimestamp(alert.created_at) }}
                  </span>
                </div>
              </div>
              
              <div class="alert-actions">
                <button
                  class="btn btn-sm btn-outline"
                  @click="acknowledgeAlert(alert.id)"
                  aria-label="Reconhecer alerta"
                >
                  <i class="fas fa-check"></i>
                  Reconhecer
                </button>
              </div>
            </div>
          </div>
          
          <div v-else class="empty-state">
            <i class="fas fa-check-circle fa-4x text-success"></i>
            <h3>Nenhum alerta ativo</h3>
            <p>Sistema operando normalmente</p>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import SensorCard from './SensorCard.vue'
import { useWebSocket } from '../composables/useWebSocket'
import { useNotifications } from '../composables/useNotifications'

const props = defineProps({
  initialData: {
    type: Object,
    required: true
  }
})

// Estado reativo
const activeTab = ref('overview')
const sensorSearch = ref('')
const sensors = ref(props.initialData.sensors || [])
const alerts = ref(props.initialData.alerts || [])
const activePlant = ref(props.initialData.activePlant || null)
const sensorValues = ref({})

// WebSocket para dados em tempo real
const { isConnected, send } = useWebSocket('ws://localhost:8000/ws/sensors/', {
  onMessage: handleWebSocketMessage
})

// Sistema de notificações
const { showNotification } = useNotifications()

// Tabs de navegação
const tabs = [
  { id: 'overview', label: 'Visão Geral', icon: 'fas fa-home' },
  { id: 'sensors', label: 'Sensores', icon: 'fas fa-microchip' },
  { id: 'alerts', label: 'Alertas', icon: 'fas fa-exclamation-triangle' }
]

// Estatísticas computadas
const stats = computed(() => ({
  totalSensors: sensors.value.length,
  onlineSensors: sensors.value.filter(s => {
    if (!s.is_active || !s.last_data_collected) return false
    const diffMinutes = (new Date() - new Date(s.last_data_collected)) / 60000
    return diffMinutes < 5
  }).length,
  activePlants: activePlant.value ? 1 : 0,
  criticalAlerts: alerts.value.filter(a => a.severity === 'critical').length
}))

// Status da conexão
const connectionStatusClass = computed(() => 
  isConnected.value ? 'connected' : 'disconnected'
)

const connectionIcon = computed(() => 
  isConnected.value ? 'fas fa-circle' : 'fas fa-exclamation-circle'
)

const connectionText = computed(() => 
  isConnected.value ? 'Conectado' : 'Desconectado'
)

// Sensores filtrados
const filteredSensors = computed(() => {
  if (!sensorSearch.value) return sensors.value
  
  const search = sensorSearch.value.toLowerCase()
  return sensors.value.filter(sensor => 
    sensor.name.toLowerCase().includes(search) ||
    sensor.sensor_type_display.toLowerCase().includes(search) ||
    sensor.location_id?.toLowerCase().includes(search)
  )
})

// Funções
function handleWebSocketMessage(data) {
  if (data.type === 'sensor_update') {
    updateSensorData(data.data)
  } else if (data.type === 'alert') {
    addAlert(data.data)
    showNotification(data.data.message, data.data.severity)
  }
}

function updateSensorData(data) {
  sensorValues.value[data.sensor_id] = data
  
  // Atualizar sensor na lista
  const sensorIndex = sensors.value.findIndex(s => s.id === data.sensor_id)
  if (sensorIndex !== -1) {
    sensors.value[sensorIndex].last_data_collected = data.timestamp
  }
}

function addAlert(alert) {
  alerts.value.unshift(alert)
}

function getSensorLatestValue(sensorId) {
  return sensorValues.value[sensorId] || null
}

function viewSensorDetails(sensor) {
  window.location.href = `/sensors/${sensor.id}/`
}

function showPlantDetails() {
  // Implementar modal ou navegação
  console.log('Mostrar detalhes da planta:', activePlant.value)
}

function acknowledgeAlert(alertId) {
  // Enviar requisição para backend
  fetch(`/api/alerts/${alertId}/acknowledge/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken()
    }
  })
  .then(response => response.json())
  .then(() => {
    alerts.value = alerts.value.filter(a => a.id !== alertId)
    showNotification('Alerta reconhecido com sucesso', 'success')
  })
  .catch(error => {
    console.error('Erro ao reconhecer alerta:', error)
    showNotification('Erro ao reconhecer alerta', 'error')
  })
}

function openSearch() {
  // Disparar evento para abrir busca global
  window.dispatchEvent(new CustomEvent('open-global-search'))
}

function getAlertIcon(severity) {
  const icons = {
    critical: 'fas fa-times-circle',
    error: 'fas fa-exclamation-circle',
    warning: 'fas fa-exclamation-triangle',
    info: 'fas fa-info-circle'
  }
  return icons[severity] || icons.info
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  })
}

function formatTimestamp(timestamp) {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  
  if (diffMins < 1) return 'Agora'
  if (diffMins < 60) return `${diffMins} min atrás`
  
  const diffHours = Math.floor(diffMs / 3600000)
  if (diffHours < 24) return `${diffHours}h atrás`
  
  return date.toLocaleString('pt-BR')
}

function getCsrfToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
}

// Lifecycle
onMounted(() => {
  // Carregar dados iniciais adicionais se necessário
})

onUnmounted(() => {
  // Cleanup
})
</script>

<style scoped>
.unified-dashboard {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.dashboard-header {
  background: var(--gradient-primary);
  color: var(--text-inverse);
  padding: var(--spacing-6) 0;
  box-shadow: var(--shadow-lg);
}

.dashboard-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-6);
}

.dashboard-title {
  margin: 0;
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
}

.dashboard-subtitle {
  margin: var(--spacing-2) 0 0 0;
  opacity: 0.9;
}

.dashboard-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
}

.connection-status {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-4);
  border-radius: var(--border-radius-full);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.connection-status.connected {
  background: rgba(40, 167, 69, 0.2);
}

.connection-status.disconnected {
  background: rgba(220, 53, 69, 0.2);
}

.dashboard-nav {
  display: flex;
  gap: var(--spacing-2);
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
}

.nav-tab {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  padding: var(--spacing-3) var(--spacing-6);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
  border-bottom: 3px solid transparent;
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.nav-tab:hover {
  color: var(--text-inverse);
  background: rgba(255, 255, 255, 0.1);
}

.nav-tab.active {
  color: var(--text-inverse);
  border-bottom-color: var(--text-inverse);
}

.dashboard-content {
  flex: 1;
  padding: var(--spacing-8) 0;
}

.dashboard-section {
  animation: fadeIn var(--transition-base);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-6);
  margin-bottom: var(--spacing-8);
}

.stat-card {
  background: var(--bg-primary);
  padding: var(--spacing-6);
  border-radius: var(--border-radius-xl);
  box-shadow: var(--shadow-md);
  text-align: center;
  transition: transform var(--transition-base);
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-icon {
  font-size: var(--font-size-4xl);
  margin-bottom: var(--spacing-4);
}

.stat-value {
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-bold);
  line-height: 1;
  margin-bottom: var(--spacing-2);
}

.stat-label {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

.section-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-6);
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-6);
}

.section-actions .form-control {
  min-width: 300px;
}

.plant-showcase {
  margin-top: var(--spacing-8);
}

.plant-card {
  background: var(--bg-primary);
  border-radius: var(--border-radius-xl);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

.plant-preview {
  display: flex;
  gap: var(--spacing-8);
  padding: var(--spacing-8);
  background: var(--gradient-primary);
  color: var(--text-inverse);
}

.plant-icon {
  flex-shrink: 0;
  opacity: 0.3;
}

.plant-info {
  flex: 1;
}

.plant-name {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  margin: 0 0 var(--spacing-3) 0;
}

.plant-description {
  font-size: var(--font-size-lg);
  opacity: 0.9;
  margin-bottom: var(--spacing-4);
}

.plant-meta {
  display: flex;
  gap: var(--spacing-6);
  flex-wrap: wrap;
}

.plant-meta-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-size: var(--font-size-sm);
}

.plant-actions {
  display: flex;
  gap: var(--spacing-4);
  padding: var(--spacing-6);
}

.sensors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--spacing-6);
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.alert-item {
  display: flex;
  gap: var(--spacing-4);
  padding: var(--spacing-4);
  background: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  border-left: 4px solid;
  box-shadow: var(--shadow-sm);
}

.alert-item--critical {
  border-left-color: var(--color-danger);
}

.alert-item--error {
  border-left-color: var(--color-danger);
}

.alert-item--warning {
  border-left-color: var(--color-warning);
}

.alert-item--info {
  border-left-color: var(--color-info);
}

.alert-icon {
  font-size: var(--font-size-2xl);
  flex-shrink: 0;
}

.alert-item--critical .alert-icon,
.alert-item--error .alert-icon {
  color: var(--color-danger);
}

.alert-item--warning .alert-icon {
  color: var(--color-warning);
}

.alert-content {
  flex: 1;
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-2);
}

.alert-message {
  margin: 0 0 var(--spacing-2) 0;
  color: var(--text-secondary);
}

.alert-meta {
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
}

.alert-actions {
  flex-shrink: 0;
}

.empty-state {
  text-align: center;
  padding: var(--spacing-16) var(--spacing-4);
  color: var(--text-tertiary);
}

.empty-state h3 {
  margin: var(--spacing-4) 0 var(--spacing-2) 0;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .dashboard-header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-4);
  }
  
  .dashboard-nav {
    overflow-x: auto;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .plant-preview {
    flex-direction: column;
    text-align: center;
  }
  
  .plant-actions {
    flex-direction: column;
  }
  
  .section-header {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing-4);
  }
  
  .section-actions .form-control {
    min-width: 100%;
  }
}
</style>

