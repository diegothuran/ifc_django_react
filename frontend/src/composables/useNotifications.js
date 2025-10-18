import { ref } from 'vue'

const notifications = ref([])
let notificationId = 0

export function useNotifications() {
  function showNotification(message, type = 'info', duration = 5000) {
    const id = ++notificationId
    const notification = {
      id,
      message,
      type,
      visible: true
    }

    notifications.value.push(notification)

    // Auto-remover após duration (se duration > 0)
    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, duration)
    }

    return id
  }

  function removeNotification(id) {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notifications.value[index].visible = false
      // Remover do array após animação
      setTimeout(() => {
        notifications.value = notifications.value.filter(n => n.id !== id)
      }, 300)
    }
  }

  function clearAll() {
    notifications.value = []
  }

  return {
    notifications,
    showNotification,
    removeNotification,
    clearAll
  }
}

