/**
 * Data Timeline
 * 
 * Widget para navegar no tempo e visualizar estados históricos
 * dos sensores e da planta industrial.
 */

class DataTimeline {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        
        if (!this.container) {
            console.error(`Container ${containerId} não encontrado`);
            return;
        }
        
        // Estado
        this.currentTime = new Date();
        this.minTime = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000); // 30 dias atrás
        this.maxTime = new Date();
        this.isPlaying = false;
        this.playbackSpeed = 1;
        this.playInterval = null;
        
        // Callbacks
        this.onTimeChange = null;
        this.onPlay = null;
        this.onPause = null;
        
        this.init();
    }
    
    init() {
        this.render();
        this.setupEventListeners();
        console.log('Timeline inicializada');
    }
    
    render() {
        this.container.innerHTML = `
            <div class="timeline-container">
                <div class="timeline-controls">
                    <div class="timeline-buttons">
                        <button id="timeline-play" class="btn btn-primary btn-sm" title="Play/Pause">
                            <i class="fas fa-play"></i>
                        </button>
                        <button id="timeline-stop" class="btn btn-secondary btn-sm" title="Stop">
                            <i class="fas fa-stop"></i>
                        </button>
                        <button id="timeline-backward" class="btn btn-secondary btn-sm" title="Voltar">
                            <i class="fas fa-backward"></i>
                        </button>
                        <button id="timeline-forward" class="btn btn-secondary btn-sm" title="Avançar">
                            <i class="fas fa-forward"></i>
                        </button>
                    </div>
                    
                    <div class="timeline-slider-container">
                        <input type="range" id="timeline-slider" 
                            class="form-range" 
                            min="0" max="100" value="100">
                    </div>
                    
                    <div class="timeline-info">
                        <span id="timeline-date" class="badge bg-primary">
                            ${this.formatDate(this.currentTime)}
                        </span>
                        <span id="timeline-time" class="badge bg-secondary">
                            ${this.formatTime(this.currentTime)}
                        </span>
                    </div>
                    
                    <div class="timeline-speed">
                        <label for="timeline-speed-select" class="small">Velocidade:</label>
                        <select id="timeline-speed-select" class="form-select form-select-sm">
                            <option value="0.5">0.5x</option>
                            <option value="1" selected>1x</option>
                            <option value="2">2x</option>
                            <option value="5">5x</option>
                            <option value="10">10x</option>
                        </select>
                    </div>
                </div>
            </div>
        `;
        
        // Adicionar CSS inline se necessário
        const style = document.createElement('style');
        style.textContent = `
            .timeline-container {
                background: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
            }
            
            .timeline-controls {
                display: flex;
                align-items: center;
                gap: 15px;
                flex-wrap: wrap;
            }
            
            .timeline-buttons {
                display: flex;
                gap: 5px;
            }
            
            .timeline-slider-container {
                flex: 1;
                min-width: 200px;
            }
            
            .timeline-info {
                display: flex;
                gap: 5px;
            }
            
            .timeline-speed {
                display: flex;
                align-items: center;
                gap: 5px;
            }
            
            .timeline-speed select {
                width: 80px;
            }
        `;
        document.head.appendChild(style);
    }
    
    setupEventListeners() {
        const playButton = document.getElementById('timeline-play');
        const stopButton = document.getElementById('timeline-stop');
        const backwardButton = document.getElementById('timeline-backward');
        const forwardButton = document.getElementById('timeline-forward');
        const slider = document.getElementById('timeline-slider');
        const speedSelect = document.getElementById('timeline-speed-select');
        
        // Play/Pause
        playButton.addEventListener('click', () => {
            this.togglePlayPause();
        });
        
        // Stop
        stopButton.addEventListener('click', () => {
            this.stop();
        });
        
        // Backward (voltar 1 hora)
        backwardButton.addEventListener('click', () => {
            this.stepBackward();
        });
        
        // Forward (avançar 1 hora)
        forwardButton.addEventListener('click', () => {
            this.stepForward();
        });
        
        // Slider
        slider.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            this.setTimeFromSlider(value);
        });
        
        // Speed
        speedSelect.addEventListener('change', (e) => {
            this.playbackSpeed = parseFloat(e.target.value);
            if (this.isPlaying) {
                this.pause();
                this.play();
            }
        });
    }
    
    togglePlayPause() {
        if (this.isPlaying) {
            this.pause();
        } else {
            this.play();
        }
    }
    
    play() {
        if (this.isPlaying) return;
        
        this.isPlaying = true;
        const playButton = document.getElementById('timeline-play');
        playButton.innerHTML = '<i class="fas fa-pause"></i>';
        playButton.classList.remove('btn-primary');
        playButton.classList.add('btn-warning');
        
        // Calcular intervalo baseado na velocidade
        const baseInterval = 1000; // 1 segundo = 1 minuto de dados
        const interval = baseInterval / this.playbackSpeed;
        
        this.playInterval = setInterval(() => {
            // Avançar 1 minuto
            const newTime = new Date(this.currentTime.getTime() + 60000);
            
            if (newTime <= this.maxTime) {
                this.currentTime = newTime;
                this.updateDisplay();
                this.loadDataAtTime(this.currentTime);
            } else {
                // Chegou no final, parar
                this.pause();
            }
        }, interval);
        
        if (this.onPlay) {
            this.onPlay();
        }
        
        console.log(`Timeline playing at ${this.playbackSpeed}x speed`);
    }
    
    pause() {
        if (!this.isPlaying) return;
        
        this.isPlaying = false;
        const playButton = document.getElementById('timeline-play');
        playButton.innerHTML = '<i class="fas fa-play"></i>';
        playButton.classList.remove('btn-warning');
        playButton.classList.add('btn-primary');
        
        if (this.playInterval) {
            clearInterval(this.playInterval);
            this.playInterval = null;
        }
        
        if (this.onPause) {
            this.onPause();
        }
        
        console.log('Timeline paused');
    }
    
    stop() {
        this.pause();
        this.currentTime = this.maxTime;
        this.updateDisplay();
        this.loadDataAtTime(this.currentTime);
        console.log('Timeline stopped');
    }
    
    stepBackward() {
        // Voltar 1 hora
        const newTime = new Date(this.currentTime.getTime() - 3600000);
        if (newTime >= this.minTime) {
            this.currentTime = newTime;
            this.updateDisplay();
            this.loadDataAtTime(this.currentTime);
        }
    }
    
    stepForward() {
        // Avançar 1 hora
        const newTime = new Date(this.currentTime.getTime() + 3600000);
        if (newTime <= this.maxTime) {
            this.currentTime = newTime;
            this.updateDisplay();
            this.loadDataAtTime(this.currentTime);
        }
    }
    
    setTimeFromSlider(value) {
        // Converter valor do slider (0-100) para timestamp
        const range = this.maxTime.getTime() - this.minTime.getTime();
        const offset = (value / 100) * range;
        this.currentTime = new Date(this.minTime.getTime() + offset);
        
        this.updateDisplay();
        this.loadDataAtTime(this.currentTime);
    }
    
    setTime(date) {
        if (date < this.minTime) date = this.minTime;
        if (date > this.maxTime) date = this.maxTime;
        
        this.currentTime = date;
        this.updateDisplay();
        this.loadDataAtTime(this.currentTime);
    }
    
    updateDisplay() {
        // Atualizar data e hora
        const dateElement = document.getElementById('timeline-date');
        const timeElement = document.getElementById('timeline-time');
        
        if (dateElement) {
            dateElement.textContent = this.formatDate(this.currentTime);
        }
        
        if (timeElement) {
            timeElement.textContent = this.formatTime(this.currentTime);
        }
        
        // Atualizar slider
        const slider = document.getElementById('timeline-slider');
        if (slider) {
            const range = this.maxTime.getTime() - this.minTime.getTime();
            const offset = this.currentTime.getTime() - this.minTime.getTime();
            const value = (offset / range) * 100;
            slider.value = value;
        }
    }
    
    async loadDataAtTime(timestamp) {
        try {
            const response = await fetch(
                `/dashboard/api/data/?timestamp=${timestamp.toISOString()}`
            );
            
            if (!response.ok) {
                console.warn('Dados históricos não disponíveis para esse timestamp');
                return;
            }
            
            const data = await response.json();
            
            // Disparar evento customizado com os dados
            window.dispatchEvent(new CustomEvent('timeline:dataLoaded', {
                detail: { data, timestamp }
            }));
            
            if (this.onTimeChange) {
                this.onTimeChange(timestamp, data);
            }
            
            console.log('Dados carregados para:', timestamp);
            
        } catch (error) {
            console.error('Erro ao carregar dados históricos:', error);
        }
    }
    
    formatDate(date) {
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        return `${day}/${month}/${year}`;
    }
    
    formatTime(date) {
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        return `${hours}:${minutes}:${seconds}`;
    }
    
    setDateRange(minDate, maxDate) {
        this.minTime = minDate;
        this.maxTime = maxDate;
        
        if (this.currentTime < this.minTime) {
            this.currentTime = this.minTime;
        }
        if (this.currentTime > this.maxTime) {
            this.currentTime = this.maxTime;
        }
        
        this.updateDisplay();
    }
    
    destroy() {
        this.pause();
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

// Exportar para uso global
window.DataTimeline = DataTimeline;

