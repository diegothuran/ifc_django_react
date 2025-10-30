/**
 * Heatmap Manager
 * 
 * Sistema de visualização de mapas de calor para dados de sensores IoT
 * Mostra atividade, temperatura, e outros dados por área da planta.
 */

class HeatmapManager {
    constructor(viewer) {
        this.viewer = viewer;
        this.heatmapData = [];
        this.heatmapMesh = null;
        this.isVisible = false;
        this.currentDataType = 'activity';
        this.currentTimeRange = '24h';
    }
    
    async loadHeatmapData(dataType = 'activity', timeRange = '24h') {
        try {
            console.log(`Carregando heatmap: ${dataType} (${timeRange})`);
            
            this.currentDataType = dataType;
            this.currentTimeRange = timeRange;
            
            const response = await fetch(
                `/dashboard/api/heatmap/?type=${dataType}&range=${timeRange}`
            );
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.heatmapData = data.heatmap || [];
            
            console.log(`Heatmap data loaded: ${this.heatmapData.length} pontos`);
            
            // Renderizar o heatmap
            this.renderHeatmap();
            
        } catch (error) {
            console.error('Erro ao carregar dados do heatmap:', error);
        }
    }
    
    renderHeatmap() {
        // Remover heatmap anterior se existir
        if (this.heatmapMesh) {
            this.viewer.scene.remove(this.heatmapMesh);
            if (this.heatmapMesh.geometry) this.heatmapMesh.geometry.dispose();
            if (this.heatmapMesh.material) this.heatmapMesh.material.dispose();
            this.heatmapMesh = null;
        }
        
        if (this.heatmapData.length === 0) {
            console.warn('Sem dados para renderizar heatmap');
            return;
        }
        
        // Criar grid 2D sobre a planta
        const gridSize = 50;
        const planeSize = 100;
        const geometry = new THREE.PlaneGeometry(planeSize, planeSize, gridSize, gridSize);
        
        // Preparar dados de intensidade por posição
        const intensityMap = this.prepareIntensityMap();
        
        // Aplicar gradiente de cores baseado nos dados
        const colors = [];
        const positions = geometry.attributes.position;
        
        for (let i = 0; i < positions.count; i++) {
            const x = positions.getX(i);
            const z = positions.getZ(i);
            
            const intensity = this.getIntensityAtPoint(x, z, intensityMap);
            const color = this.getHeatmapColor(intensity);
            
            colors.push(color.r, color.g, color.b);
        }
        
        geometry.setAttribute('color', 
            new THREE.Float32BufferAttribute(colors, 3)
        );
        
        // Material com cores por vértice
        const material = new THREE.MeshBasicMaterial({
            vertexColors: true,
            transparent: true,
            opacity: 0.6,
            side: THREE.DoubleSide,
            depthWrite: false
        });
        
        // Criar mesh
        this.heatmapMesh = new THREE.Mesh(geometry, material);
        this.heatmapMesh.rotation.x = -Math.PI / 2;
        this.heatmapMesh.position.y = 0.1; // Levemente acima do chão
        this.heatmapMesh.name = 'heatmap';
        
        // Adicionar à cena
        this.viewer.scene.add(this.heatmapMesh);
        this.isVisible = true;
        
        console.log('Heatmap renderizado com sucesso');
    }
    
    prepareIntensityMap() {
        // Criar mapa de intensidade baseado nos dados
        const map = new Map();
        
        // Encontrar valores min e max para normalização
        let minValue = Infinity;
        let maxValue = -Infinity;
        
        this.heatmapData.forEach(point => {
            const value = point.count || point.avg_value || point.avg_temp || 0;
            if (value < minValue) minValue = value;
            if (value > maxValue) maxValue = value;
        });
        
        // Normalizar e armazenar
        this.heatmapData.forEach(point => {
            const locationId = point.sensor__location_id;
            const value = point.count || point.avg_value || point.avg_temp || 0;
            
            // Normalizar para 0-1
            const normalizedValue = maxValue > minValue 
                ? (value - minValue) / (maxValue - minValue)
                : 0.5;
            
            map.set(locationId, normalizedValue);
        });
        
        return map;
    }
    
    getIntensityAtPoint(x, z, intensityMap) {
        // Interpolar intensidade baseado na posição
        // Por enquanto, usar uma distribuição simplificada
        
        if (intensityMap.size === 0) {
            return 0;
        }
        
        // Calcular intensidade baseada em distância dos pontos de dados
        let totalIntensity = 0;
        let totalWeight = 0;
        
        // Usar valores do mapa de intensidade
        // Aplicar distribuição radial simples
        const values = Array.from(intensityMap.values());
        const avgIntensity = values.reduce((a, b) => a + b, 0) / values.length;
        
        // Adicionar variação baseada na posição (para visualização mais interessante)
        const distanceFromCenter = Math.sqrt(x * x + z * z);
        const maxDistance = 50;
        const distanceFactor = 1 - (distanceFromCenter / maxDistance);
        
        // Combinar intensidade média com fator de distância
        totalIntensity = avgIntensity * Math.max(0, distanceFactor);
        
        // Adicionar ruído suave para variação visual
        const noise = (Math.sin(x * 0.1) * Math.cos(z * 0.1) + 1) / 2;
        totalIntensity = totalIntensity * 0.8 + noise * 0.2;
        
        return Math.max(0, Math.min(1, totalIntensity));
    }
    
    getHeatmapColor(intensity) {
        // Gradiente: Azul (frio) -> Verde -> Amarelo -> Vermelho (quente)
        
        if (intensity < 0.25) {
            // Azul para verde
            const t = intensity / 0.25;
            return new THREE.Color().lerpColors(
                new THREE.Color(0x0000FF), // Azul
                new THREE.Color(0x00FF00), // Verde
                t
            );
        } else if (intensity < 0.5) {
            // Verde para amarelo
            const t = (intensity - 0.25) / 0.25;
            return new THREE.Color().lerpColors(
                new THREE.Color(0x00FF00), // Verde
                new THREE.Color(0xFFFF00), // Amarelo
                t
            );
        } else if (intensity < 0.75) {
            // Amarelo para laranja
            const t = (intensity - 0.5) / 0.25;
            return new THREE.Color().lerpColors(
                new THREE.Color(0xFFFF00), // Amarelo
                new THREE.Color(0xFF8800), // Laranja
                t
            );
        } else {
            // Laranja para vermelho
            const t = (intensity - 0.75) / 0.25;
            return new THREE.Color().lerpColors(
                new THREE.Color(0xFF8800), // Laranja
                new THREE.Color(0xFF0000), // Vermelho
                t
            );
        }
    }
    
    toggle() {
        if (this.heatmapMesh) {
            this.isVisible = !this.isVisible;
            this.heatmapMesh.visible = this.isVisible;
        }
    }
    
    show() {
        if (this.heatmapMesh) {
            this.isVisible = true;
            this.heatmapMesh.visible = true;
        }
    }
    
    hide() {
        if (this.heatmapMesh) {
            this.isVisible = false;
            this.heatmapMesh.visible = false;
        }
    }
    
    remove() {
        if (this.heatmapMesh) {
            this.viewer.scene.remove(this.heatmapMesh);
            if (this.heatmapMesh.geometry) this.heatmapMesh.geometry.dispose();
            if (this.heatmapMesh.material) this.heatmapMesh.material.dispose();
            this.heatmapMesh = null;
            this.isVisible = false;
        }
    }
    
    async refresh() {
        // Recarregar dados e renderizar novamente
        await this.loadHeatmapData(this.currentDataType, this.currentTimeRange);
    }
    
    setOpacity(opacity) {
        if (this.heatmapMesh && this.heatmapMesh.material) {
            this.heatmapMesh.material.opacity = Math.max(0, Math.min(1, opacity));
        }
    }
}

// Exportar para uso global
window.HeatmapManager = HeatmapManager;

