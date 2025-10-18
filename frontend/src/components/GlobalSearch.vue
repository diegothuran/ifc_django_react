<template>
  <teleport to="body">
    <div v-if="isOpen" class="search-modal active" @click.self="close">
      <div class="search-modal-overlay" @click="close"></div>
      
      <div class="search-modal-content">
        <div class="search-input-wrapper">
          <i class="fas fa-search search-icon"></i>
          <input
            ref="searchInput"
            v-model="query"
            type="text"
            class="search-input"
            placeholder="Buscar sensores, plantas, páginas..."
            autocomplete="off"
            @keydown="handleKeyDown"
            aria-label="Campo de busca global"
          />
          <kbd class="search-shortcut">ESC</kbd>
        </div>
        
        <div class="search-results">
          <template v-if="query && results.length">
            <div
              v-for="(result, index) in results"
              :key="result.id"
              class="search-result-item"
              :class="{ selected: selectedIndex === index }"
              @click="selectResult(result)"
              @mouseenter="selectedIndex = index"
            >
              <i :class="`fas fa-${result.icon} search-result-icon`"></i>
              <div class="search-result-content">
                <div class="search-result-title" v-html="highlight(result.title)"></div>
                <div class="search-result-type">{{ result.type }}</div>
              </div>
            </div>
          </template>
          
          <div v-else-if="query && !results.length" class="search-empty">
            <i class="fas fa-search fa-2x text-muted mb-3"></i>
            <p>Nenhum resultado encontrado para "{{ query }}"</p>
          </div>
          
          <div v-else class="search-empty">
            <i class="fas fa-keyboard fa-2x text-muted mb-3"></i>
            <p>Digite para buscar sensores, plantas ou páginas</p>
          </div>
        </div>
        
        <div class="search-footer">
          <div class="search-hints">
            <span><kbd>↑</kbd><kbd>↓</kbd> Navegar</span>
            <span><kbd>Enter</kbd> Selecionar</span>
            <span><kbd>ESC</kbd> Fechar</span>
          </div>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  searchIndex: {
    type: Array,
    default: () => []
  }
})

const isOpen = ref(false)
const query = ref('')
const selectedIndex = ref(0)
const searchInput = ref(null)

// Resultados filtrados
const results = computed(() => {
  if (!query.value) return []
  
  const search = query.value.toLowerCase()
  return props.searchIndex
    .filter(item => 
      item.title.toLowerCase().includes(search) ||
      item.type.toLowerCase().includes(search)
    )
    .slice(0, 10) // Limitar a 10 resultados
})

// Watch para resetar seleção quando query mudar
watch(query, () => {
  selectedIndex.value = 0
})

// Watch para focar input quando abrir
watch(isOpen, async (newValue) => {
  if (newValue) {
    await nextTick()
    searchInput.value?.focus()
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

function open() {
  isOpen.value = true
}

function close() {
  isOpen.value = false
  query.value = ''
  selectedIndex.value = 0
}

function handleKeyDown(event) {
  switch (event.key) {
    case 'Escape':
      close()
      break
    case 'ArrowDown':
      event.preventDefault()
      selectedIndex.value = Math.min(selectedIndex.value + 1, results.value.length - 1)
      break
    case 'ArrowUp':
      event.preventDefault()
      selectedIndex.value = Math.max(selectedIndex.value - 1, 0)
      break
    case 'Enter':
      event.preventDefault()
      if (results.value[selectedIndex.value]) {
        selectResult(results.value[selectedIndex.value])
      }
      break
  }
}

function selectResult(result) {
  window.location.href = result.url
  close()
}

function highlight(text) {
  if (!query.value) return text
  
  const regex = new RegExp(`(${query.value})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

// Atalho de teclado global
function handleGlobalKeyDown(event) {
  if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
    event.preventDefault()
    open()
  }
}

// Event listener customizado
function handleOpenSearch() {
  open()
}

onMounted(() => {
  document.addEventListener('keydown', handleGlobalKeyDown)
  window.addEventListener('open-global-search', handleOpenSearch)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleGlobalKeyDown)
  window.removeEventListener('open-global-search', handleOpenSearch)
})

// Expor método para uso externo
defineExpose({
  open,
  close
})
</script>

<style scoped>
/* Estilos já definidos em components.css */
.mb-3 {
  margin-bottom: var(--spacing-3);
}
</style>

