/**
 * Visualizador IFC Avançado com IFC.js
 * 
 * Sistema completo de visualização 3D para arquivos IFC com:
 * - Carregamento de geometria real usando IFC.js
 * - Seleção e inspeção de elementos
 * - Controles de câmera profissionais
 * - Integração com API REST
 * - Painel de propriedades interativo
 * 
 * Versão: 2.0 - Com suporte a IFC.js
 * Data: 31/10/2025
 */

class AdvancedIFCViewer {
    constructor(canvasId, plantId) {
        this.canvasId = canvasId;
        this.plantId = plantId;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.model = null;
        this.ifcLoader = null;
        this.selectedElement = null;
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        this.highlightedMesh = null;
        
        // Estado
        this.isWireframe = false;
        this.isPerspective = true;
        this.useRealGeometry = true; // Flag para usar geometria real do IFC
        
        // Sensores IoT
        this.sensorMarkers = [];
        this.sensorsData = [];
        
        this.init();
    }
    
    async init() {
        console.log('Inicializando visualizador IFC avançado com IFC.js...');
        
        this.setupScene();
        this.setupCamera();
        this.setupRenderer();
        this.setupLighting();
        this.setupIFCLoader();
        this.setupEventListeners();
        this.animate();
        
        // Carregar modelo se houver plantId
        if (this.plantId) {
            await this.loadPlant(this.plantId);
        }
    }
    
    setupScene() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0xf0f0f0);
        
        // Adicionar grid helper
        const gridHelper = new THREE.GridHelper(50, 50, 0x888888, 0xcccccc);
        gridHelper.name = 'gridHelper';
        this.scene.add(gridHelper);
    }
    
    setupCamera() {
        const canvas = document.getElementById(this.canvasId);
        const aspect = canvas.clientWidth / canvas.clientHeight;
        
        this.camera = new THREE.PerspectiveCamera(60, aspect, 0.1, 2000);
        this.camera.position.set(20, 20, 20);
        this.camera.lookAt(0, 0, 0);
    }
    
    setupRenderer() {
        const canvas = document.getElementById(this.canvasId);
        
        this.renderer = new THREE.WebGLRenderer({
            canvas: canvas,
            antialias: true,
            alpha: false
        });
        
        this.renderer.setSize(canvas.clientWidth, canvas.clientHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        
        // Configurar OrbitControls
        this.setupOrbitControls();
    }
    
    setupOrbitControls() {
        // Verificar se OrbitControls está disponível
        if (typeof THREE.OrbitControls === 'undefined') {
            console.warn('OrbitControls não encontrado');
            return;
        }
        
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        
        // Configurações avançadas
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.screenSpacePanning = true;
        this.controls.minDistance = 1;
        this.controls.maxDistance = 500;
        this.controls.maxPolarAngle = Math.PI;
        
        // Zoom suave
        this.controls.enableZoom = true;
        this.controls.zoomSpeed = 1.2;
        
        // Rotação
        this.controls.enableRotate = true;
        this.controls.rotateSpeed = 0.8;
        
        // Pan
        this.controls.enablePan = true;
        this.controls.panSpeed = 0.8;
    }
    
    setupLighting() {
        // Luz ambiente
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        ambientLight.name = 'ambientLight';
        this.scene.add(ambientLight);
        
        // Luz direcional principal
        const mainLight = new THREE.DirectionalLight(0xffffff, 0.8);
        mainLight.position.set(50, 100, 50);
        mainLight.castShadow = true;
        mainLight.shadow.mapSize.width = 2048;
        mainLight.shadow.mapSize.height = 2048;
        mainLight.shadow.camera.near = 0.5;
        mainLight.shadow.camera.far = 500;
        mainLight.name = 'mainLight';
        this.scene.add(mainLight);
        
        // Luz de preenchimento
        const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
        fillLight.position.set(-50, 0, -50);
        fillLight.name = 'fillLight';
        this.scene.add(fillLight);
        
        // Luz hemisférica
        const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.4);
        hemiLight.position.set(0, 50, 0);
        hemiLight.name = 'hemiLight';
        this.scene.add(hemiLight);
    }
    
    setupIFCLoader() {
        // Verificar se IFCLoader está disponível
        if (typeof IFCLoader === 'undefined') {
            console.error('IFCLoader não encontrado! Verifique se web-ifc-three foi carregado.');
            this.useRealGeometry = false;
            return;
        }
        
        try {
            this.ifcLoader = new IFCLoader();
            
            // Configurar caminho do WASM
            this.ifcLoader.ifcManager.setWasmPath('https://unpkg.com/web-ifc@0.0.51/');
            
            console.log('IFCLoader configurado com sucesso');
        } catch (error) {
            console.error('Erro ao configurar IFCLoader:', error);
            this.useRealGeometry = false;
        }
    }
    
    setupEventListeners() {
        const canvas = this.renderer.domElement;
        
        // Click para seleção
        canvas.addEventListener('click', (event) => {
            this.onMouseClick(event);
        });
        
        // Mousemove para hover
        canvas.addEventListener('mousemove', (event) => {
            this.onMouseMove(event);
        });
        
        // Resize
        window.addEventListener('resize', () => {
            this.onWindowResize();
        });
    }
    
    async loadPlant(plantId) {
        try {
            this.showLoading(true, 'Carregando dados da planta...');
            
            // Buscar dados da planta via API
            const response = await fetch(`/plant/api/plants/${plantId}/`);
            
            if (!response.ok) {
                throw new Error(`Erro ao buscar planta: ${response.status}`);
            }
            
            const plantData = await response.json();
            console.log('Dados da planta:', plantData);
            
            // Verificar se tem arquivo IFC
            if (!plantData.ifc_file) {
                throw new Error('Arquivo IFC não encontrado na planta');
            }
            
            // Tentar carregar com geometria real
            if (this.useRealGeometry && this.ifcLoader) {
                console.log('Carregando geometria IFC real...');
                await this.loadRealIFCGeometry(plantData.ifc_file);
            } else {
                console.log('Carregando representação simbólica (cubos)...');
                await this.loadIFCFromAPI(plantId);
            }
            
        } catch (error) {
            console.error('Erro ao carregar planta:', error);
            console.log('Carregando modelo de exemplo como fallback');
            this.createExampleModel();
            this.showLoading(false);
        }
    }
    
    async loadRealIFCGeometry(ifcFileUrl) {
        this.showLoading(true, 'Carregando arquivo IFC...');
        
        try {
            console.log('URL do arquivo IFC:', ifcFileUrl);
            
            // Carregar modelo IFC
            const ifcModel = await this.ifcLoader.loadAsync(ifcFileUrl);
            
            console.log('Modelo IFC carregado com sucesso!');
            console.log('Modelo:', ifcModel);
            
            // Adicionar à cena
            this.model = ifcModel;
            this.scene.add(this.model);
            
            // Ajustar câmera para visualizar o modelo
            this.fitCameraToModel();
            
            this.showLoading(false);
            
            // Mostrar mensagem de sucesso
            this.showSuccessMessage('Modelo IFC carregado com geometria real!');
            
        } catch (error) {
            console.error('Erro ao carregar geometria IFC real:', error);
            console.log('Tentando carregar representação simbólica...');
            
            // Fallback para representação simbólica
            this.useRealGeometry = false;
            await this.loadIFCFromAPI(this.plantId);
        }
    }
    
    async loadIFCFromAPI(plantId) {
        this.showLoading(true, 'Carregando dados do IFC...');
        
        try {
            // Buscar metadados e elementos
            const metadataResponse = await fetch(`/plant/api/plants/${plantId}/metadata/`);
            if (!metadataResponse.ok) {
                throw new Error('Erro ao buscar metadados');
            }
            
            const metadata = await metadataResponse.json();
            console.log('Metadados do IFC:', metadata);
            
            // Criar modelo baseado nos metadados
            this.model = new THREE.Group();
            this.model.name = 'ifcModel';
            
            // Criar geometrias para os elementos
            const building_elements = metadata.building_elements || {};
            let elementIndex = 0;
            
            for (const [elementType, elements] of Object.entries(building_elements)) {
                console.log(`Processando ${elements.length} elementos do tipo ${elementType}`);
                
                elements.forEach((element, idx) => {
                    // Criar uma geometria simples para cada elemento
                    const geometry = new THREE.BoxGeometry(2, 2, 2);
                    const color = this.getColorForElementType(elementType);
                    const material = new THREE.MeshStandardMaterial({
                        color: color,
                        roughness: 0.7,
                        metalness: 0.3
                    });
                    
                    const mesh = new THREE.Mesh(geometry, material);
                    
                    // Posicionar em grid
                    const gridSize = Math.ceil(Math.sqrt(elementIndex + 1));
                    const x = (elementIndex % gridSize) * 3 - (gridSize * 1.5);
                    const z = Math.floor(elementIndex / gridSize) * 3 - (gridSize * 1.5);
                    
                    mesh.position.set(x, 1, z);
                    mesh.castShadow = true;
                    mesh.receiveShadow = true;
                    
                    // Salvar dados do elemento
                    mesh.name = element.name;
                    mesh.userData.ifcId = element.id;
                    mesh.userData.type = elementType;
                    mesh.userData.global_id = element.global_id;
                    mesh.userData.description = element.description || '';
                    
                    this.model.add(mesh);
                    elementIndex++;
                });
            }
            
            // Adicionar piso
            const floorGeometry = new THREE.PlaneGeometry(50, 50);
            const floorMaterial = new THREE.MeshStandardMaterial({
                color: 0xcccccc,
                roughness: 0.8,
                metalness: 0.2
            });
            const floor = new THREE.Mesh(floorGeometry, floorMaterial);
            floor.rotation.x = -Math.PI / 2;
            floor.receiveShadow = true;
            floor.name = 'floor';
            this.model.add(floor);
            
            this.scene.add(this.model);
            console.log(`Modelo IFC criado com ${elementIndex} elementos (representação simbólica)`);
            
            // Ajustar câmera
            this.fitCameraToModel();
            this.showLoading(false);
            
            // Mostrar aviso
            this.showWarningMessage(`Exibindo ${elementIndex} elementos como cubos coloridos. Para ver geometria real, verifique se o arquivo IFC está acessível.`);
            
        } catch (error) {
            console.error('Erro ao carregar IFC via API:', error);
            console.log('Carregando modelo de exemplo como fallback');
            this.createExampleModel();
            this.showLoading(false);
        }
    }
    
    getColorForElementType(elementType) {
        const colors = {
            // Elementos arquitetônicos
            'IfcWall': 0xcccccc,
            'IfcSlab': 0x999999,
            'IfcColumn': 0x666666,
            'IfcBeam': 0x777777,
            'IfcDoor': 0x8B4513,
            'IfcWindow': 0x87CEEB,
            'IfcSpace': 0xE6E6FA,
            'IfcStair': 0xA9A9A9,
            'IfcRoof': 0xB22222,
            'IfcRailing': 0x4682B4,
            'IfcCovering': 0xDEB887,
            'IfcFurnishingElement': 0xD2691E,
            
            // Elementos MEP/Elétricos
            'IfcFlowTerminal': 0xFF6347,        // Vermelho tomate
            'IfcFlowSegment': 0x4169E1,         // Azul royal
            'IfcFlowFitting': 0xFF8C00,         // Laranja escuro
            'IfcFlowController': 0x9370DB,      // Roxo médio
            'IfcFlowMovingDevice': 0x20B2AA,    // Verde água
            'IfcDistributionControlElement': 0xFFD700,  // Dourado
            'IfcEnergyConversionDevice': 0xFF1493,      // Rosa profundo
            'IfcDistributionElement': 0x00CED1,         // Turquesa
            'IfcBuildingElementProxy': 0x808080,        // Cinza
        };
        return colors[elementType] || 0x808080;
    }
    
    createExampleModel() {
        console.log('Criando modelo de exemplo...');
        
        // Grupo para o modelo de exemplo
        this.model = new THREE.Group();
        this.model.name = 'exampleModel';
        
        // Piso
        const floorGeometry = new THREE.PlaneGeometry(30, 30);
        const floorMaterial = new THREE.MeshStandardMaterial({
            color: 0xcccccc,
            roughness: 0.8,
            metalness: 0.2
        });
        const floor = new THREE.Mesh(floorGeometry, floorMaterial);
        floor.rotation.x = -Math.PI / 2;
        floor.receiveShadow = true;
        floor.name = 'floor';
        this.model.add(floor);
        
        // Edifícios/estruturas da planta
        const buildings = [
            { x: -8, y: 0, z: -8, width: 4, height: 5, depth: 4, color: 0x4CAF50, name: 'Edifício A' },
            { x: 0, y: 0, z: -8, width: 5, height: 4, depth: 4, color: 0x2196F3, name: 'Edifício B' },
            { x: 8, y: 0, z: -8, width: 4, height: 6, depth: 4, color: 0xFF9800, name: 'Edifício C' },
            { x: -8, y: 0, z: 8, width: 4, height: 3, depth: 4, color: 0x9C27B0, name: 'Anexo 1' },
            { x: 0, y: 0, z: 8, width: 6, height: 4, depth: 4, color: 0xF44336, name: 'Anexo 2' },
            { x: 8, y: 0, z: 8, width: 4, height: 5, depth: 4, color: 0x607D8B, name: 'Anexo 3' }
        ];
        
        buildings.forEach(building => {
            const geometry = new THREE.BoxGeometry(building.width, building.height, building.depth);
            const material = new THREE.MeshStandardMaterial({
                color: building.color,
                roughness: 0.7,
                metalness: 0.3
            });
            const mesh = new THREE.Mesh(geometry, material);
            
            mesh.position.set(building.x, building.height / 2, building.z);
            mesh.castShadow = true;
            mesh.receiveShadow = true;
            mesh.name = building.name;
            mesh.userData.type = 'IfcBuilding';
            mesh.userData.description = `Estrutura ${building.name}`;
            
            this.model.add(mesh);
        });
        
        this.scene.add(this.model);
        this.fitCameraToModel();
    }
    
    fitCameraToModel() {
        if (!this.model) return;
        
        const box = new THREE.Box3().setFromObject(this.model);
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        
        const maxDim = Math.max(size.x, size.y, size.z);
        const fov = this.camera.fov * (Math.PI / 180);
        let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
        cameraZ *= 1.8; // Zoom out um pouco
        
        this.camera.position.set(
            center.x + cameraZ * 0.5,
            center.y + cameraZ * 0.7,
            center.z + cameraZ * 0.5
        );
        
        this.camera.lookAt(center);
        
        if (this.controls) {
            this.controls.target.copy(center);
            this.controls.update();
        }
    }
    
    onMouseClick(event) {
        // Calcular posição do mouse normalizada
        const rect = this.renderer.domElement.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        
        // Raycast
        this.raycaster.setFromCamera(this.mouse, this.camera);
        const intersects = this.raycaster.intersectObjects(this.scene.children, true);
        
        if (intersects.length > 0) {
            const object = intersects[0].object;
            
            // Ignorar grid e floor
            if (object.name === 'gridHelper' || object.name === 'floor') {
                return;
            }
            
            this.selectElement(object);
        } else {
            this.deselectAll();
        }
    }
    
    onMouseMove(event) {
        // Implementar hover highlight se necessário
    }
    
    selectElement(mesh) {
        // Desselecionar anterior
        this.deselectAll();
        
        // Selecionar novo
        this.selectedElement = mesh;
        
        // Highlight visual
        if (mesh.material) {
            mesh.userData.originalColor = mesh.material.color.getHex();
            mesh.material.color.setHex(0xffff00); // Amarelo
        }
        
        // Mostrar propriedades
        this.showElementProperties(mesh);
    }
    
    deselectAll() {
        if (this.selectedElement && this.selectedElement.material) {
            if (this.selectedElement.userData.originalColor !== undefined) {
                this.selectedElement.material.color.setHex(this.selectedElement.userData.originalColor);
            }
        }
        this.selectedElement = null;
        this.hideElementProperties();
    }
    
    async showElementProperties(mesh) {
        const panel = document.getElementById('element-properties-panel');
        if (!panel) return;
        
        panel.style.display = 'block';
        
        // Informações básicas
        let html = `
            <div class="element-header">
                <h4>${mesh.name || 'Elemento Sem Nome'}</h4>
                <button onclick="window.ifcViewer.deselectAll()" style="background: none; border: none; cursor: pointer; font-size: 1.5rem;">&times;</button>
            </div>
            <div class="element-info">
                <p><strong>Tipo:</strong> ${mesh.userData.type || 'N/A'}</p>
                <p><strong>ID:</strong> ${mesh.userData.ifcId || 'N/A'}</p>
                <p><strong>Global ID:</strong> ${mesh.userData.global_id || 'N/A'}</p>
                ${mesh.userData.description ? `<p><strong>Descrição:</strong> ${mesh.userData.description}</p>` : ''}
            </div>
        `;
        
        // Tentar buscar propriedades detalhadas via API
        if (mesh.userData.ifcId && this.plantId) {
            try {
                const response = await fetch(`/plant/api/plants/${this.plantId}/element/${mesh.userData.ifcId}/`);
                if (response.ok) {
                    const properties = await response.json();
                    
                    html += '<div class="element-properties"><h5>Propriedades</h5>';
                    
                    if (properties.properties) {
                        for (const [setName, props] of Object.entries(properties.properties)) {
                            html += `<h6>${setName}</h6><ul>`;
                            for (const [propName, propValue] of Object.entries(props)) {
                                html += `<li><strong>${propName}:</strong> ${propValue}</li>`;
                            }
                            html += '</ul>';
                        }
                    }
                    
                    if (properties.material) {
                        html += `<p><strong>Material:</strong> ${properties.material}</p>`;
                    }
                    
                    html += '</div>';
                }
            } catch (error) {
                console.error('Erro ao buscar propriedades:', error);
            }
        }
        
        panel.innerHTML = html;
    }
    
    hideElementProperties() {
        const panel = document.getElementById('element-properties-panel');
        if (panel) {
            panel.style.display = 'none';
        }
    }
    
    onWindowResize() {
        const canvas = document.getElementById(this.canvasId);
        this.camera.aspect = canvas.clientWidth / canvas.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        if (this.controls) {
            this.controls.update();
        }
        
        this.renderer.render(this.scene, this.camera);
    }
    
    // Métodos de controle
    
    resetView() {
        this.fitCameraToModel();
    }
    
    toggleWireframe() {
        this.isWireframe = !this.isWireframe;
        
        this.scene.traverse((object) => {
            if (object.isMesh && object.material) {
                object.material.wireframe = this.isWireframe;
            }
        });
    }
    
    toggleOrthographic() {
        // Implementar se necessário
        console.log('Toggle orthographic não implementado');
    }
    
    getStatistics() {
        let meshCount = 0;
        let vertexCount = 0;
        
        this.scene.traverse((object) => {
            if (object.isMesh) {
                meshCount++;
                if (object.geometry) {
                    vertexCount += object.geometry.attributes.position.count;
                }
            }
        });
        
        return {
            'Meshes': meshCount,
            'Vértices': vertexCount,
            'Modo': this.useRealGeometry ? 'Geometria Real' : 'Simbólico'
        };
    }
    
    // Métodos de UI
    
    showLoading(show, message = 'Carregando...') {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = show ? 'flex' : 'none';
            const text = overlay.querySelector('span');
            if (text) {
                text.textContent = message;
            }
        }
    }
    
    showSuccessMessage(message) {
        console.log('✅ ' + message);
        // Implementar toast/notification se necessário
    }
    
    showWarningMessage(message) {
        console.warn('⚠️ ' + message);
        // Implementar toast/notification se necessário
    }
}
