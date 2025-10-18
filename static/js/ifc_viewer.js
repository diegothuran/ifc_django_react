/**
 * Visualizador IFC Avançado
 * 
 * Sistema completo de visualização 3D para arquivos IFC com:
 * - Seleção e inspeção de elementos
 * - Controles de câmera profissionais
 * - Integração com API REST
 * - Painel de propriedades interativo
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
        this.selectedElement = null;
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        this.highlightedMesh = null;
        
        // Estado
        this.isWireframe = false;
        this.isPerspective = true;
        
        this.init();
    }
    
    async init() {
        console.log('Inicializando visualizador IFC avançado...');
        
        this.setupScene();
        this.setupCamera();
        this.setupRenderer();
        this.setupLighting();
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
        
        // Adicionar axes helper (opcional, útil para debug)
        // const axesHelper = new THREE.AxesHelper(5);
        // axesHelper.name = 'axesHelper';
        // this.scene.add(axesHelper);
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
        this.renderer.outputEncoding = THREE.sRGBEncoding;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.0;
        
        // Configurar OrbitControls
        this.setupOrbitControls();
    }
    
    setupOrbitControls() {
        // Verificar se OrbitControls está disponível
        if (typeof THREE.OrbitControls === 'undefined') {
            console.warn('OrbitControls não encontrado, usando controles básicos');
            this.setupBasicControls();
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
        
        // Auto-rotate (desabilitado por padrão)
        this.controls.autoRotate = false;
        this.controls.autoRotateSpeed = 0.5;
    }
    
    setupBasicControls() {
        // Controles básicos como fallback
        const canvas = this.renderer.domElement;
        let isMouseDown = false;
        let mouseX = 0, mouseY = 0;
        
        canvas.addEventListener('mousedown', (e) => {
            if (e.button === 2) { // Botão direito
                isMouseDown = true;
                mouseX = e.clientX;
                mouseY = e.clientY;
                e.preventDefault();
            }
        });
        
        canvas.addEventListener('mouseup', () => {
            isMouseDown = false;
        });
        
        canvas.addEventListener('mousemove', (e) => {
            if (!isMouseDown) return;
            
            const deltaX = e.clientX - mouseX;
            const deltaY = e.clientY - mouseY;
            
            // Rotação orbital
            const rotationSpeed = 0.005;
            const theta = this.camera.position.x;
            const phi = this.camera.position.y;
            
            this.camera.position.x += deltaX * rotationSpeed;
            this.camera.position.y -= deltaY * rotationSpeed;
            
            mouseX = e.clientX;
            mouseY = e.clientY;
        });
        
        canvas.addEventListener('wheel', (e) => {
            const zoomSpeed = 0.001;
            const distance = this.camera.position.length();
            const newDistance = distance + e.deltaY * zoomSpeed * distance;
            
            this.camera.position.multiplyScalar(newDistance / distance);
            e.preventDefault();
        });
        
        canvas.addEventListener('contextmenu', (e) => e.preventDefault());
    }
    
    setupLighting() {
        // Luz ambiente
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        ambientLight.name = 'ambientLight';
        this.scene.add(ambientLight);
        
        // Luz direcional principal (Sol)
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(50, 50, 50);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        directionalLight.shadow.camera.near = 0.5;
        directionalLight.shadow.camera.far = 500;
        directionalLight.shadow.camera.left = -50;
        directionalLight.shadow.camera.right = 50;
        directionalLight.shadow.camera.top = 50;
        directionalLight.shadow.camera.bottom = -50;
        directionalLight.name = 'mainLight';
        this.scene.add(directionalLight);
        
        // Luz de preenchimento
        const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
        fillLight.position.set(-50, 0, -50);
        fillLight.name = 'fillLight';
        this.scene.add(fillLight);
        
        // Luz hemisférica (opcional, simula luz do céu e chão)
        const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.4);
        hemiLight.position.set(0, 50, 0);
        hemiLight.name = 'hemiLight';
        this.scene.add(hemiLight);
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
            
            if (!plantData.ifc_url) {
                console.warn('Planta sem arquivo IFC, carregando modelo de exemplo');
                this.createExampleModel();
                this.showLoading(false);
                return;
            }
            
            // Tentar carregar modelo IFC real
            await this.loadIFCModel(plantData.ifc_url);
            
        } catch (error) {
            console.error('Erro ao carregar planta:', error);
            console.log('Carregando modelo de exemplo como fallback');
            this.createExampleModel();
            this.showLoading(false);
        }
    }
    
    async loadIFCModel(ifcUrl) {
        this.showLoading(true, 'Carregando modelo IFC...');
        
        // Verificar se IFCLoader está disponível
        if (typeof THREE.IFCLoader === 'undefined') {
            console.warn('IFCLoader não disponível, usando modelo de exemplo');
            this.createExampleModel();
            this.showLoading(false);
            return;
        }
        
        try {
            const loader = new THREE.IFCLoader();
            
            // Configurar caminho do WASM
            await loader.ifcManager.setWasmPath('https://unpkg.com/web-ifc@0.0.57/');
            
            // Carregar modelo
            this.model = await loader.loadAsync(ifcUrl, (event) => {
                if (event.lengthComputable) {
                    const percentComplete = (event.loaded / event.total) * 100;
                    this.showLoading(true, `Carregando modelo: ${Math.round(percentComplete)}%`);
                }
            });
            
            this.scene.add(this.model);
            console.log('Modelo IFC carregado:', this.model);
            
            // Ajustar câmera
            this.fitCameraToModel();
            
            this.showLoading(false);
            
        } catch (error) {
            console.error('Erro ao carregar modelo IFC:', error);
            this.createExampleModel();
            this.showLoading(false);
        }
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
        
        console.log('Câmera ajustada para o modelo');
    }
    
    async onMouseClick(event) {
        const intersection = this.getIntersection(event);
        
        if (intersection && intersection.object.name !== 'floor' && intersection.object.name !== 'gridHelper') {
            // Deselecionar anterior
            if (this.selectedElement) {
                this.deselectElement(this.selectedElement);
            }
            
            // Selecionar novo
            this.selectedElement = intersection.object;
            this.selectElement(this.selectedElement);
            
            // Mostrar propriedades
            await this.showElementProperties(this.selectedElement);
            
        } else {
            // Click no vazio - deselecionar
            if (this.selectedElement) {
                this.deselectElement(this.selectedElement);
                this.selectedElement = null;
                this.hideElementProperties();
            }
        }
    }
    
    onMouseMove(event) {
        const intersection = this.getIntersection(event);
        const canvas = this.renderer.domElement;
        
        // Highlight on hover
        if (intersection && intersection.object !== this.selectedElement && 
            intersection.object.name !== 'floor' && intersection.object.name !== 'gridHelper') {
            canvas.style.cursor = 'pointer';
            
            // Remover highlight anterior
            if (this.highlightedMesh && this.highlightedMesh !== this.selectedElement) {
                this.removeHighlight(this.highlightedMesh);
            }
            
            // Adicionar highlight
            if (intersection.object !== this.selectedElement) {
                this.addHighlight(intersection.object);
                this.highlightedMesh = intersection.object;
            }
        } else {
            canvas.style.cursor = 'default';
            
            // Remover highlight
            if (this.highlightedMesh && this.highlightedMesh !== this.selectedElement) {
                this.removeHighlight(this.highlightedMesh);
                this.highlightedMesh = null;
            }
        }
    }
    
    getIntersection(event) {
        const canvas = this.renderer.domElement;
        const rect = canvas.getBoundingClientRect();
        
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        
        this.raycaster.setFromCamera(this.mouse, this.camera);
        
        // Intersectar apenas com o modelo, não com helpers
        const intersectables = [];
        if (this.model) {
            this.model.traverse((child) => {
                if (child.isMesh) {
                    intersectables.push(child);
                }
            });
        }
        
        const intersects = this.raycaster.intersectObjects(intersectables, false);
        
        return intersects.length > 0 ? intersects[0] : null;
    }
    
    addHighlight(mesh) {
        if (!mesh.material) return;
        
        if (!mesh.userData.originalEmissive) {
            mesh.userData.originalEmissive = mesh.material.emissive ? mesh.material.emissive.clone() : new THREE.Color(0x000000);
            mesh.userData.originalEmissiveIntensity = mesh.material.emissiveIntensity || 0;
        }
        
        mesh.material.emissive = new THREE.Color(0x444444);
        mesh.material.emissiveIntensity = 0.5;
    }
    
    removeHighlight(mesh) {
        if (!mesh.material || !mesh.userData.originalEmissive) return;
        
        mesh.material.emissive = mesh.userData.originalEmissive;
        mesh.material.emissiveIntensity = mesh.userData.originalEmissiveIntensity;
    }
    
    selectElement(mesh) {
        if (!mesh.material) return;
        
        // Salvar material original
        if (!mesh.userData.originalColor) {
            mesh.userData.originalColor = mesh.material.color.clone();
        }
        
        // Criar outline effect
        mesh.material.emissive = new THREE.Color(0xff6600);
        mesh.material.emissiveIntensity = 0.8;
        
        console.log('Elemento selecionado:', mesh.name);
    }
    
    deselectElement(mesh) {
        if (!mesh.material || !mesh.userData.originalColor) return;
        
        // Restaurar material original
        mesh.material.emissive = mesh.userData.originalEmissive || new THREE.Color(0x000000);
        mesh.material.emissiveIntensity = mesh.userData.originalEmissiveIntensity || 0;
    }
    
    async showElementProperties(mesh) {
        const panel = document.getElementById('element-properties-panel');
        if (!panel) return;
        
        // Dados básicos do mesh
        let html = `
            <div class="element-header">
                <h4>${mesh.name || 'Elemento sem nome'}</h4>
                <button class="btn btn-sm btn-secondary" onclick="window.ifcViewer.deselectAll()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="element-info">
                <p><strong>Tipo:</strong> ${mesh.userData.type || mesh.type}</p>
        `;
        
        if (mesh.userData.description) {
            html += `<p><strong>Descrição:</strong> ${mesh.userData.description}</p>`;
        }
        
        html += `
                <p><strong>Posição:</strong> (${mesh.position.x.toFixed(2)}, ${mesh.position.y.toFixed(2)}, ${mesh.position.z.toFixed(2)})</p>
            </div>
        `;
        
        // Se tiver ID IFC, buscar propriedades via API
        if (mesh.userData.ifcId && this.plantId) {
            try {
                const response = await fetch(`/plant/api/plants/${this.plantId}/element/${mesh.userData.ifcId}/`);
                if (response.ok) {
                    const properties = await response.json();
                    html += this.formatPropertiesHTML(properties);
                }
            } catch (error) {
                console.warn('Erro ao buscar propriedades do elemento:', error);
            }
        }
        
        panel.innerHTML = html;
        panel.style.display = 'block';
    }
    
    formatPropertiesHTML(properties) {
        let html = '<div class="element-properties">';
        
        if (properties.properties && Object.keys(properties.properties).length > 0) {
            html += '<h5>Propriedades IFC:</h5>';
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
        return html;
    }
    
    hideElementProperties() {
        const panel = document.getElementById('element-properties-panel');
        if (panel) {
            panel.style.display = 'none';
        }
    }
    
    deselectAll() {
        if (this.selectedElement) {
            this.deselectElement(this.selectedElement);
            this.selectedElement = null;
            this.hideElementProperties();
        }
    }
    
    onWindowResize() {
        const canvas = this.renderer.domElement;
        const width = canvas.clientWidth;
        const height = canvas.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }
    
    showLoading(show, message = 'Carregando...') {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            if (show) {
                overlay.style.display = 'flex';
                const messageEl = overlay.querySelector('span');
                if (messageEl) messageEl.textContent = message;
            } else {
                overlay.style.display = 'none';
            }
        }
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        if (this.controls && this.controls.update) {
            this.controls.update();
        }
        
        this.renderer.render(this.scene, this.camera);
    }
    
    // ==================== Métodos de controle público ====================
    
    resetView() {
        if (this.model) {
            this.fitCameraToModel();
        }
    }
    
    toggleWireframe() {
        this.isWireframe = !this.isWireframe;
        
        this.scene.traverse((child) => {
            if (child.isMesh && child.material && child.name !== 'gridHelper') {
                child.material.wireframe = this.isWireframe;
            }
        });
    }
    
    toggleOrthographic() {
        const position = this.camera.position.clone();
        const target = this.controls ? this.controls.target.clone() : new THREE.Vector3(0, 0, 0);
        
        if (this.isPerspective) {
            // Trocar para ortográfica
            const aspect = this.camera.aspect;
            const frustumSize = 30;
            this.camera = new THREE.OrthographicCamera(
                -frustumSize * aspect / 2,
                frustumSize * aspect / 2,
                frustumSize / 2,
                -frustumSize / 2,
                0.1,
                2000
            );
            this.isPerspective = false;
        } else {
            // Trocar para perspectiva
            this.camera = new THREE.PerspectiveCamera(
                60,
                window.innerWidth / window.innerHeight,
                0.1,
                2000
            );
            this.isPerspective = true;
        }
        
        this.camera.position.copy(position);
        
        if (this.controls) {
            this.controls.object = this.camera;
            this.controls.target.copy(target);
            this.controls.update();
        }
    }
    
    toggleAutoRotate() {
        if (this.controls) {
            this.controls.autoRotate = !this.controls.autoRotate;
            return this.controls.autoRotate;
        }
        return false;
    }
    
    getStatistics() {
        let geometries = 0;
        let materials = 0;
        let meshes = 0;
        
        this.scene.traverse((child) => {
            if (child.isMesh) {
                meshes++;
                if (child.geometry) geometries++;
                if (child.material) materials++;
            }
        });
        
        return {
            'Objetos na cena': this.scene.children.length,
            'Meshes': meshes,
            'Triângulos': this.renderer.info.render.triangles,
            'Chamadas de desenho': this.renderer.info.render.calls,
            'Geometrias': geometries,
            'Materiais': materials,
            'Memória (texturas)': this.renderer.info.memory.textures
        };
    }
}

// Exportar para uso global
window.AdvancedIFCViewer = AdvancedIFCViewer;

