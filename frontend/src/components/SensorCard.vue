<template>
  <div 
    class="card sensor-card" 
    :class="{ 'sensor-card--active': sensor.is_active }"
    @click="$emit('select', sensor)"
  >
    <div class="card-header">
      <h3 class="card-title">
        <i class="fas fa-microchip"></i>
        {{ sensor.name }}
      </h3>
      <span 
        class="badge" 
        :class="statusClass"
        role="status"
        :aria-label="`Status: ${statusText}`"
      >
        <i :class="statusIcon"></i>
        {{ statusText }}
      </span>
    </div>
    
    <div class="card-body">
      <div class="sensor-info">
        <div class="sensor-info-item">
          <span class="sensor-info-label">Tipo:</span>
          <span class="sensor-info-value">{{ sensor.sensor_type_display }}</span>
        </div>
        
        <div class="sensor-info-item">
          <span class="sensor-info-label">IP:</span>
          <span class="sensor-info-value">{{ sensor.ip_address }}:{{ sensor.port }}</span>
        </div>
        
        <div v-if="sensor.location_id" class="sensor-info-item">
          <span class="sensor-info-label">Localização:</span>
          <span class="sensor-info-value">{{ sensor.location_id }}</span>
        </div>
        
        <div class="sensor-info-item">
          <span class="sensor-info-label">Última Coleta:</span>
          <span class="sensor-info-value">
            <template v-if="sensor.last_data_collected">
              {{ formatTimestamp(sensor.last_data_collected) }}
            </template>
            <template v-else>
              <span class="text-muted">Nunca</span>
            </template>
          </span>
        </div>
        
        <div v-if="latestValue" class="sensor-reading">
          <div class="sensor-reading-value">
            {{ latestValue.value }}
            <span class="sensor-reading-unit">{{ latestValue.unit }}</span>
          </div>
          <div class="sensor-reading-label">Leitura Atual</div>
        </div>
      </div>
    </div>
    
    <div class="card-footer">
      <button 
        class="btn btn-primary btn-sm btn-full"
        @click.stop="viewDetails"
        :aria-label="`Ver detalhes do sensor ${sensor.name}`"
      >
        <i class="fas fa-eye"></i>
        Ver Detalhes
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  sensor: {
    type: Object,
    required: true
  },
  latestValue: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['select', 'view-details'])

const statusClass = computed(() => {
  if (!props.sensor.is_active) return 'badge-danger'
  if (props.sensor.last_data_collected) {
    const lastCollected = new Date(props.sensor.last_data_collected)
    const now = new Date()
    const diffMinutes = (now - lastCollected) / 1000 / 60
    
    if (diffMinutes < 5) return 'badge-success'
    if (diffMinutes < 30) return 'badge-warning'
  }
  return 'badge-danger'
})

const statusIcon = computed(() => {
  const classMap = {
    'badge-success': 'fas fa-check-circle',
    'badge-warning': 'fas fa-exclamation-triangle',
    'badge-danger': 'fas fa-times-circle'
  }
  return classMap[statusClass.value]
})

const statusText = computed(() => {
  if (!props.sensor.is_active) return 'Inativo'
  if (props.sensor.last_data_collected) {
    const lastCollected = new Date(props.sensor.last_data_collected)
    const now = new Date()
    const diffMinutes = (now - lastCollected) / 1000 / 60
    
    if (diffMinutes < 5) return 'Online'
    if (diffMinutes < 30) return 'Sem Dados Recentes'
  }
  return 'Offline'
})

function formatTimestamp(timestamp) {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'Agora'
  if (diffMins < 60) return `${diffMins} min atrás`
  if (diffHours < 24) return `${diffHours}h atrás`
  if (diffDays < 7) return `${diffDays}d atrás`
  
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function viewDetails() {
  emit('view-details', props.sensor)
}
</script>

<style scoped>
.sensor-card {
  cursor: pointer;
  transition: all var(--transition-base);
}

.sensor-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.sensor-card--active {
  border-left: 4px solid var(--color-success);
}

.sensor-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.sensor-info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: var(--spacing-2);
  border-bottom: 1px solid var(--color-gray-100);
}

.sensor-info-item:last-child {
  border-bottom: none;
}

.sensor-info-label {
  font-weight: var(--font-weight-medium);
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

.sensor-info-value {
  color: var(--text-primary);
  font-size: var(--font-size-sm);
}

.sensor-reading {
  text-align: center;
  padding: var(--spacing-4);
  background: var(--gradient-primary);
  border-radius: var(--border-radius-lg);
  color: var(--text-inverse);
  margin-top: var(--spacing-2);
}

.sensor-reading-value {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  line-height: 1;
}

.sensor-reading-unit {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-normal);
  opacity: 0.9;
  margin-left: var(--spacing-1);
}

.sensor-reading-label {
  font-size: var(--font-size-sm);
  opacity: 0.8;
  margin-top: var(--spacing-2);
}
</style>

