/**
 * Visualizador 2D de Planta Baixa
 * 
 * Renderiza uma visualização 2D dos espaços IFC usando Canvas API,
 * similar à funcionalidade do sistema Streamlit com Plotly.
 * 
 * Baseado na funcionalidade do ifc_monitoring_system
 */

class FloorPlanViewer {
    constructor(canvasId, plantId) {
        this.canvasId = canvasId;
        this.plantId = plantId;
        this.canvas = null;
        this.ctx = null;
        this.spaces = [];
        this.bounds = null;
        this.scale = 1;
        this.offsetX = 0;
        this.offsetY = 0;
        this.padding = 50;
        this.selectedSpace = null;
        this.hoveredSpace = null;
        
        // Cores para os espaços
        this.colorPalette = [
            '#4CAF50', '#2196F3', '#FF9800', '#9C27B0',
            '#F44336', '#607D8B', '#00BCD4', '#CDDC39',
            '#FF5722', '#3F51B5', '#E91E63', '#009688'
        ];
        
        this.init();
    }
    
    init() {
        this.canvas = document.getElementById(this.canvasId);
        if (!this.canvas) {
            console.error(`Canvas ${this.canvasId} não encontrado`);
            return;
        }
        
        this.ctx = this.canvas.getContext('2d');
        
        // Configurar tamanho do canvas
        this.resizeCanvas();
        
        // Event listeners
        window.addEventListener('resize', () => this.resizeCanvas());
        this.canvas.addEventListener('mousemove', (e) => this.onMouseMove(e));
        this.canvas.addEventListener('click', (e) => this.onClick(e));
        
        // Carregar dados se houver plantId
        if (this.plantId) {
            this.loadSpaces();
        }
    }
    
    resizeCanvas() {
        const container = this.canvas.parentElement;
        this.canvas.width = container.clientWidth;
        this.canvas.height = container.clientHeight;
        
        // Redesenhar após redimensionar
        if (this.spaces.length > 0) {
            this.draw();
        }
    }
    
    async loadSpaces() {
        try {
            console.log(`Carregando espaços da planta ${this.plantId}...`);
            
            const response = await fetch(`/plant/api/plants/${this.plantId}/spaces/`);
            
            if (!response.ok) {
                throw new Error(`Erro ao buscar espaços: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Dados de espaços recebidos:', data);
            
            if (data.spaces && data.spaces.length > 0) {
                this.spaces = data.spaces;
                this.bounds = data.bounds;
                this.calculateScale();
                this.draw();
            } else {
                console.warn('Nenhum espaço encontrado, gerando dados de exemplo');
                this.generateExampleSpaces();
            }
            
        } catch (error) {
            console.error('Erro ao carregar espaços:', error);
            console.log('Gerando dados de exemplo como fallback');
            this.generateExampleSpaces();
        }
    }
    
    generateExampleSpaces() {
        // Gerar espaços de exemplo similar ao sistema Streamlit
        this.spaces = [
            { id: 1, name: 'Sala A1', x_coordinate: 0, y_coordinate: 0, area: 25, object_type: 'Office' },
            { id: 2, name: 'Sala A2', x_coordinate: 6, y_coordinate: 0, area: 30, object_type: 'Office' },
            { id: 3, name: 'Sala B1', x_coordinate: 0, y_coordinate: 6, area: 20, object_type: 'Meeting Room' },
            { id: 4, name: 'Sala B2', x_coordinate: 6, y_coordinate: 6, area: 28, object_type: 'Office' },
            { id: 5, name: 'Corredor', x_coordinate: 3, y_coordinate: 3, area: 15, object_type: 'Circulation' },
            { id: 6, name: 'Sala C1', x_coordinate: 12, y_coordinate: 0, area: 35, object_type: 'Conference' },
            { id: 7, name: 'Sala C2', x_coordinate: 12, y_coordinate: 6, area: 22, object_type: 'Storage' },
            { id: 8, name: 'Recepção', x_coordinate: 0, y_coordinate: -6, area: 40, object_type: 'Reception' }
        ];
        
        // Calcular bounds
        const xCoords = this.spaces.map(s => s.x_coordinate);
        const yCoords = this.spaces.map(s => s.y_coordinate);
        this.bounds = {
            min: { x: Math.min(...xCoords), y: Math.min(...yCoords) },
            max: { x: Math.max(...xCoords), y: Math.max(...yCoords) }
        };
        
        this.calculateScale();
        this.draw();
    }
    
    calculateScale() {
        if (!this.bounds || this.spaces.length === 0) return;
        
        const dataWidth = this.bounds.max.x - this.bounds.min.x;
        const dataHeight = this.bounds.max.y - this.bounds.min.y;
        
        const canvasWidth = this.canvas.width - 2 * this.padding;
        const canvasHeight = this.canvas.height - 2 * this.padding;
        
        // Calcular escala para caber tudo no canvas
        const scaleX = canvasWidth / (dataWidth || 1);
        const scaleY = canvasHeight / (dataHeight || 1);
        this.scale = Math.min(scaleX, scaleY) * 0.9; // 0.9 para margem extra
        
        // Calcular offset para centralizar
        this.offsetX = this.padding - this.bounds.min.x * this.scale + 
                       (canvasWidth - dataWidth * this.scale) / 2;
        this.offsetY = this.padding - this.bounds.min.y * this.scale + 
                       (canvasHeight - dataHeight * this.scale) / 2;
    }
    
    worldToCanvas(x, y) {
        return {
            x: x * this.scale + this.offsetX,
            y: this.canvas.height - (y * this.scale + this.offsetY) // Inverter Y
        };
    }
    
    canvasToWorld(canvasX, canvasY) {
        return {
            x: (canvasX - this.offsetX) / this.scale,
            y: (this.canvas.height - canvasY - this.offsetY) / this.scale
        };
    }
    
    draw() {
        if (!this.ctx) return;
        
        // Limpar canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Desenhar fundo
        this.ctx.fillStyle = '#f8f9fa';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Desenhar grid
        this.drawGrid();
        
        // Desenhar espaços
        this.spaces.forEach((space, index) => {
            this.drawSpace(space, index);
        });
        
        // Desenhar legenda
        this.drawLegend();
        
        // Desenhar título
        this.drawTitle();
    }
    
    drawGrid() {
        if (!this.bounds) return;
        
        this.ctx.strokeStyle = '#e0e0e0';
        this.ctx.lineWidth = 1;
        
        // Determinar espaçamento do grid
        const dataWidth = this.bounds.max.x - this.bounds.min.x;
        const dataHeight = this.bounds.max.y - this.bounds.min.y;
        const gridSpacing = Math.pow(10, Math.floor(Math.log10(Math.max(dataWidth, dataHeight) / 10)));
        
        // Linhas verticais
        const startX = Math.floor(this.bounds.min.x / gridSpacing) * gridSpacing;
        const endX = Math.ceil(this.bounds.max.x / gridSpacing) * gridSpacing;
        
        for (let x = startX; x <= endX; x += gridSpacing) {
            const canvasPos = this.worldToCanvas(x, this.bounds.min.y);
            const canvasEnd = this.worldToCanvas(x, this.bounds.max.y);
            
            this.ctx.beginPath();
            this.ctx.moveTo(canvasPos.x, canvasPos.y);
            this.ctx.lineTo(canvasEnd.x, canvasEnd.y);
            this.ctx.stroke();
            
            // Label
            this.ctx.fillStyle = '#999';
            this.ctx.font = '10px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(x.toFixed(1), canvasPos.x, this.canvas.height - 5);
        }
        
        // Linhas horizontais
        const startY = Math.floor(this.bounds.min.y / gridSpacing) * gridSpacing;
        const endY = Math.ceil(this.bounds.max.y / gridSpacing) * gridSpacing;
        
        for (let y = startY; y <= endY; y += gridSpacing) {
            const canvasPos = this.worldToCanvas(this.bounds.min.x, y);
            const canvasEnd = this.worldToCanvas(this.bounds.max.x, y);
            
            this.ctx.beginPath();
            this.ctx.moveTo(canvasPos.x, canvasPos.y);
            this.ctx.lineTo(canvasEnd.x, canvasEnd.y);
            this.ctx.stroke();
            
            // Label
            this.ctx.fillStyle = '#999';
            this.ctx.font = '10px Arial';
            this.ctx.textAlign = 'right';
            this.ctx.fillText(y.toFixed(1), 45, canvasPos.y + 3);
        }
    }
    
    drawSpace(space, index) {
        const pos = this.worldToCanvas(space.x_coordinate, space.y_coordinate);
        
        // Tamanho do marcador baseado na área
        const baseSize = Math.sqrt(space.area || 25) * this.scale * 0.5;
        const size = Math.max(15, Math.min(50, baseSize));
        
        // Cor baseada no índice
        const color = this.colorPalette[index % this.colorPalette.length];
        
        // Efeitos de hover e seleção
        let alpha = 0.7;
        let strokeWidth = 2;
        
        if (space === this.selectedSpace) {
            alpha = 1.0;
            strokeWidth = 3;
        } else if (space === this.hoveredSpace) {
            alpha = 0.9;
            strokeWidth = 2.5;
        }
        
        // Desenhar círculo
        this.ctx.fillStyle = this.hexToRgba(color, alpha);
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = strokeWidth;
        
        this.ctx.beginPath();
        this.ctx.arc(pos.x, pos.y, size, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.stroke();
        
        // Desenhar label
        this.ctx.fillStyle = '#333';
        this.ctx.font = 'bold 11px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'top';
        this.ctx.fillText(space.name, pos.x, pos.y + size + 5);
        
        // Área
        if (space.area > 0) {
            this.ctx.fillStyle = '#666';
            this.ctx.font = '9px Arial';
            this.ctx.fillText(`${space.area.toFixed(1)} m²`, pos.x, pos.y + size + 18);
        }
    }
    
    drawLegend() {
        const legendX = 10;
        const legendY = 10;
        const legendWidth = 180;
        const legendHeight = 100;
        
        // Fundo da legenda
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
        this.ctx.strokeStyle = '#ccc';
        this.ctx.lineWidth = 1;
        this.ctx.fillRect(legendX, legendY, legendWidth, legendHeight);
        this.ctx.strokeRect(legendX, legendY, legendWidth, legendHeight);
        
        // Título da legenda
        this.ctx.fillStyle = '#333';
        this.ctx.font = 'bold 12px Arial';
        this.ctx.textAlign = 'left';
        this.ctx.fillText('Legenda', legendX + 10, legendY + 15);
        
        // Informações
        this.ctx.font = '11px Arial';
        this.ctx.fillStyle = '#666';
        this.ctx.fillText(`Total de Espaços: ${this.spaces.length}`, legendX + 10, legendY + 35);
        
        const totalArea = this.spaces.reduce((sum, s) => sum + (s.area || 0), 0);
        this.ctx.fillText(`Área Total: ${totalArea.toFixed(1)} m²`, legendX + 10, legendY + 50);
        
        // Instruções
        this.ctx.font = '9px Arial';
        this.ctx.fillStyle = '#999';
        this.ctx.fillText('Clique nos círculos', legendX + 10, legendY + 70);
        this.ctx.fillText('para mais detalhes', legendX + 10, legendY + 82);
    }
    
    drawTitle() {
        this.ctx.fillStyle = '#333';
        this.ctx.font = 'bold 18px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('Planta Baixa - Vista 2D', this.canvas.width / 2, 25);
    }
    
    onMouseMove(event) {
        const rect = this.canvas.getBoundingClientRect();
        const canvasX = event.clientX - rect.left;
        const canvasY = event.clientY - rect.top;
        
        // Verificar se está sobre algum espaço
        const prevHovered = this.hoveredSpace;
        this.hoveredSpace = null;
        
        for (const space of this.spaces) {
            const pos = this.worldToCanvas(space.x_coordinate, space.y_coordinate);
            const size = Math.max(15, Math.min(50, Math.sqrt(space.area || 25) * this.scale * 0.5));
            
            const distance = Math.sqrt(
                Math.pow(canvasX - pos.x, 2) + 
                Math.pow(canvasY - pos.y, 2)
            );
            
            if (distance <= size) {
                this.hoveredSpace = space;
                this.canvas.style.cursor = 'pointer';
                break;
            }
        }
        
        if (!this.hoveredSpace) {
            this.canvas.style.cursor = 'default';
        }
        
        // Redesenhar se hover mudou
        if (prevHovered !== this.hoveredSpace) {
            this.draw();
        }
    }
    
    onClick(event) {
        if (this.hoveredSpace) {
            this.selectedSpace = this.hoveredSpace;
            this.draw();
            this.showSpaceDetails(this.selectedSpace);
        } else {
            this.selectedSpace = null;
            this.draw();
            this.hideSpaceDetails();
        }
    }
    
    showSpaceDetails(space) {
        console.log('Espaço selecionado:', space);
        
        // Criar ou atualizar painel de detalhes
        let panel = document.getElementById('floor-plan-details');
        
        if (!panel) {
            panel = document.createElement('div');
            panel.id = 'floor-plan-details';
            panel.style.cssText = `
                position: absolute;
                bottom: 20px;
                right: 20px;
                background: rgba(255, 255, 255, 0.95);
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                max-width: 300px;
                z-index: 200;
            `;
            this.canvas.parentElement.appendChild(panel);
        }
        
        panel.innerHTML = `
            <h5 style="margin: 0 0 10px 0; color: #333;">${space.name}</h5>
            <p style="margin: 5px 0; color: #666; font-size: 13px;">
                <strong>Tipo:</strong> ${space.object_type || 'N/A'}
            </p>
            <p style="margin: 5px 0; color: #666; font-size: 13px;">
                <strong>Área:</strong> ${space.area ? space.area.toFixed(2) + ' m²' : 'N/A'}
            </p>
            <p style="margin: 5px 0; color: #666; font-size: 13px;">
                <strong>Coordenadas:</strong><br>
                X: ${space.x_coordinate.toFixed(2)} m<br>
                Y: ${space.y_coordinate.toFixed(2)} m<br>
                Z: ${space.z_coordinate.toFixed(2)} m
            </p>
            ${space.description ? `<p style="margin: 5px 0; color: #666; font-size: 12px;"><em>${space.description}</em></p>` : ''}
            <button onclick="window.floorPlanViewer.closeDetails()" 
                    style="margin-top: 10px; padding: 5px 10px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer;">
                Fechar
            </button>
        `;
        
        panel.style.display = 'block';
    }
    
    hideSpaceDetails() {
        const panel = document.getElementById('floor-plan-details');
        if (panel) {
            panel.style.display = 'none';
        }
    }
    
    closeDetails() {
        this.selectedSpace = null;
        this.hideSpaceDetails();
        this.draw();
    }
    
    hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }
    
    // Método para atualizar com novos espaços
    updateSpaces(spaces, bounds) {
        this.spaces = spaces;
        this.bounds = bounds;
        this.calculateScale();
        this.draw();
    }
}

// Exportar para uso global
window.FloorPlanViewer = FloorPlanViewer;

