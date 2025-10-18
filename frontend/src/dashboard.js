import { createApp } from 'vue'
import UnifiedDashboard from './components/UnifiedDashboard.vue'
import NotificationContainer from './components/NotificationContainer.vue'
import GlobalSearch from './components/GlobalSearch.vue'

// Inicializar aplicação Vue quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
  // Montar Dashboard Unificado
  const dashboardEl = document.getElementById('unified-dashboard-app')
  if (dashboardEl) {
    const initialData = window.DASHBOARD_INITIAL_DATA || {}
    
    const app = createApp(UnifiedDashboard, {
      initialData
    })
    
    app.mount(dashboardEl)
  }
  
  // Montar Notificações (global)
  const notificationsEl = document.createElement('div')
  notificationsEl.id = 'notifications-app'
  document.body.appendChild(notificationsEl)
  
  const notificationsApp = createApp(NotificationContainer)
  notificationsApp.mount(notificationsEl)
  
  // Montar Busca Global (global)
  const searchEl = document.createElement('div')
  searchEl.id = 'search-app'
  document.body.appendChild(searchEl)
  
  const searchIndex = window.SEARCH_INDEX || []
  const searchApp = createApp(GlobalSearch, {
    searchIndex
  })
  searchApp.mount(searchEl)
})

