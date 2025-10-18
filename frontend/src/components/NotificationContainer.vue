<template>
  <div class="notification-container" role="region" aria-label="Notificações">
    <transition-group name="notification">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="notification"
        :class="[
          `notification-${notification.type}`,
          { 'notification-exit': !notification.visible }
        ]"
        role="alert"
        :aria-live="notification.type === 'error' ? 'assertive' : 'polite'"
      >
        <div class="notification-icon">
          <i :class="getIcon(notification.type)"></i>
        </div>
        
        <div class="notification-content">
          <div class="notification-title">{{ getTitle(notification.type) }}</div>
          <div class="notification-message">{{ notification.message }}</div>
        </div>
        
        <button
          class="notification-close"
          @click="removeNotification(notification.id)"
          aria-label="Fechar notificação"
        >
          <i class="fas fa-times"></i>
        </button>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { useNotifications } from '../composables/useNotifications'

const { notifications, removeNotification } = useNotifications()

function getIcon(type) {
  const icons = {
    success: 'fas fa-check-circle',
    error: 'fas fa-exclamation-circle',
    warning: 'fas fa-exclamation-triangle',
    info: 'fas fa-info-circle'
  }
  return icons[type] || icons.info
}

function getTitle(type) {
  const titles = {
    success: 'Sucesso',
    error: 'Erro',
    warning: 'Aviso',
    info: 'Informação'
  }
  return titles[type] || 'Notificação'
}
</script>

<style scoped>
/* Estilos já definidos em components.css, mas podemos adicionar animações específicas */
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.notification-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>

