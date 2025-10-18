import { ref, onUnmounted } from 'vue'

export function useWebSocket(url, options = {}) {
  const {
    onMessage = () => {},
    onError = () => {},
    onOpen = () => {},
    onClose = () => {},
    reconnect = true,
    reconnectAttempts = 5,
    reconnectDelay = 1000
  } = options

  const ws = ref(null)
  const isConnected = ref(false)
  const reconnectCount = ref(0)
  const reconnectTimer = ref(null)

  function connect() {
    try {
      ws.value = new WebSocket(url)

      ws.value.onopen = (event) => {
        console.log('WebSocket conectado')
        isConnected.value = true
        reconnectCount.value = 0
        onOpen(event)
      }

      ws.value.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          onMessage(data)
        } catch (error) {
          console.error('Erro ao parsear mensagem WebSocket:', error)
        }
      }

      ws.value.onerror = (event) => {
        console.error('Erro no WebSocket:', event)
        onError(event)
      }

      ws.value.onclose = (event) => {
        console.log('WebSocket desconectado')
        isConnected.value = false
        onClose(event)

        if (reconnect && reconnectCount.value < reconnectAttempts) {
          attemptReconnect()
        }
      }
    } catch (error) {
      console.error('Erro ao criar WebSocket:', error)
      if (reconnect && reconnectCount.value < reconnectAttempts) {
        attemptReconnect()
      }
    }
  }

  function attemptReconnect() {
    reconnectCount.value++
    const delay = reconnectDelay * Math.pow(2, reconnectCount.value - 1)

    console.log(`Tentando reconectar em ${delay}ms (tentativa ${reconnectCount.value}/${reconnectAttempts})`)

    reconnectTimer.value = setTimeout(() => {
      connect()
    }, delay)
  }

  function send(data) {
    if (ws.value && ws.value.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify(data))
      return true
    }
    console.warn('WebSocket não está conectado')
    return false
  }

  function close() {
    if (reconnectTimer.value) {
      clearTimeout(reconnectTimer.value)
    }
    if (ws.value) {
      ws.value.close()
    }
  }

  // Conectar automaticamente
  connect()

  // Cleanup ao desmontar componente
  onUnmounted(() => {
    close()
  })

  return {
    ws,
    isConnected,
    send,
    close,
    reconnect: connect
  }
}

