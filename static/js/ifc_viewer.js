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
        
        if (!canvas) {
            throw new Error(`Canvas com ID "${this.canvasId}" não encontrado`);
        }
        
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
        // Verificar se OrbitControls está disponível (pode ser módulo ES6)
        const initControls = () => {
            let OrbitControlsClass = null;
            
            // Tentar THREE.OrbitControls (script tradicional)
            if (typeof THREE !== 'undefined' && THREE.OrbitControls) {
                OrbitControlsClass = THREE.OrbitControls;
            }
            // Tentar OrbitControls global (módulo ES6)
            else if (typeof OrbitControls !== 'undefined') {
                OrbitControlsClass = OrbitControls;
            }
            else {
                console.warn('OrbitControls não encontrado, tentando novamente...');
                setTimeout(initControls, 100);
                return;
            }
            
            this.controls = new OrbitControlsClass(this.camera, this.renderer.domElement);
        
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
            
            console.log('OrbitControls configurado com sucesso');
        };
        
        // Iniciar após um pequeno delay para garantir que os módulos carregaram
        setTimeout(initControls, 200);
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
        // Verificar se IFCLoader está disponível (aguardar carregamento se necessário)
        const checkIFCLoader = () => {
            // Verificar múltiplas formas de acesso
            const IFCLoaderClass = window.IFCLoaderClass || window.IFCLoader;
            
            if (!IFCLoaderClass) {
                // Verificar se houve erro no carregamento
                if (window.IFCLoaderError) {
                    console.error('IFCLoader falhou ao carregar:', window.IFCLoaderError);
                    this.useRealGeometry = false;
                    return;
                }
                
                // Tentar novamente
                console.warn('IFCLoader ainda não carregado, aguardando...');
                setTimeout(checkIFCLoader, 200);
                return;
            }
            
            try {
                // Criar IFCLoader com THREE como dependência
                if (typeof THREE === 'undefined') {
                    throw new Error('THREE.js não está disponível');
                }
                
                // IFCLoader precisa ser instanciado - verificar documentação
                // web-ifc-three pode precisar da cena ou pode ser sem parâmetros
                if (this.scene) {
                    try {
                        // Tentar primeiro sem parâmetros
                        this.ifcLoader = new IFCLoaderClass();
                        // Se funcionar, configurar a cena depois
                        if (this.ifcLoader && this.ifcLoader.setup) {
                            this.ifcLoader.setup(this.scene);
                        }
                    } catch (e1) {
                        try {
                            // Tentar com cena como parâmetro
                            this.ifcLoader = new IFCLoaderClass(this.scene);
                        } catch (e2) {
                            console.error('Todas as tentativas de criar IFCLoader falharam:', e1, e2);
                            throw e2;
                        }
                    }
                } else {
                    this.ifcLoader = new IFCLoaderClass();
                }
                
                // Configurar caminho do WASM
                if (this.ifcLoader && this.ifcLoader.ifcManager) {
                    this.ifcLoader.ifcManager.setWasmPath('https://cdn.jsdelivr.net/npm/web-ifc@0.0.51/');
                }
                
                console.log('✅ IFCLoader configurado com sucesso');
                this.useRealGeometry = true;
                
            } catch (error) {
                console.error('❌ Erro ao configurar IFCLoader:', error);
                console.error('Stack:', error.stack);
                this.useRealGeometry = false;
            }
        };
        
        // Aguardar evento de carregamento ou timeout
        const timeout = setTimeout(() => {
            console.warn('Timeout aguardando IFCLoader (10 segundos)');
            checkIFCLoader();
        }, 10000);
        
        // Escutar evento de carregamento
        window.addEventListener('ifcjs-loaded', () => {
            clearTimeout(timeout);
            checkIFCLoader();
        });
        
        // Também tentar imediatamente após um delay inicial
        setTimeout(checkIFCLoader, 1000);
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
            
            // Verificar se tem arquivo IFC (API retorna 'ifc_url' ou 'ifc_file')
            const ifcUrl = plantData.ifc_url || (plantData.ifc_file ? plantData.ifc_file.url : null);
            
            if (!ifcUrl) {
                console.warn('Arquivo IFC não encontrado na planta, tentando carregar via metadados...');
                await this.loadIFCFromAPI(plantId);
                return;
            }
            
            // Tentar carregar com geometria real
            if (this.useRealGeometry && this.ifcLoader) {
                console.log('Carregando geometria IFC real...');
                await this.loadRealIFCGeometry(ifcUrl);
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
            
            // Aguardar IFCLoader estar pronto
            if (!this.ifcLoader) {
                console.warn('IFCLoader ainda não está pronto, aguardando...');
                await new Promise((resolve, reject) => {
                    const checkLoader = setInterval(() => {
                        if (this.ifcLoader) {
                            clearInterval(checkLoader);
                            resolve();
                        }
                    }, 100);
                    // Timeout após 5 segundos
                    setTimeout(() => {
                        clearInterval(checkLoader);
                        reject(new Error('IFCLoader não carregou em tempo hábil'));
                    }, 5000);
                });
            }
            
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
            let elementsWithCoords = 0;
            let elementsWithoutCoords = 0;
            
            // Calcular bounds para centralização se necessário
            let minX = Infinity, minY = Infinity, minZ = Infinity;
            let maxX = -Infinity, maxY = -Infinity, maxZ = -Infinity;
            
            // Primeiro passo: coletar todas as coordenadas disponíveis
            for (const [elementType, elements] of Object.entries(building_elements)) {
                elements.forEach((element) => {
                    if (element.has_coordinates && 
                        typeof element.x_coordinate === 'number' && 
                        typeof element.y_coordinate === 'number' && 
                        typeof element.z_coordinate === 'number') {
                        minX = Math.min(minX, element.x_coordinate);
                        minY = Math.min(minY, element.y_coordinate);
                        minZ = Math.min(minZ, element.z_coordinate);
                        maxX = Math.max(maxX, element.x_coordinate);
                        maxY = Math.max(maxY, element.y_coordinate);
                        maxZ = Math.max(maxZ, element.z_coordinate);
                    }
                });
            }
            
            // Calcular centro para ajuste
            const centerX = (minX + maxX) / 2;
            const centerY = (minY + maxY) / 2;
            const centerZ = (minZ + maxZ) / 2;
            
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
                    
                    // Posicionar usando coordenadas reais se disponíveis
                    let x, y, z;
                    if (element.has_coordinates && 
                        typeof element.x_coordinate === 'number' && 
                        typeof element.y_coordinate === 'number' && 
                        typeof element.z_coordinate === 'number') {
                        // Usar coordenadas reais (ajustadas ao centro)
                        x = element.x_coordinate - centerX;
                        y = element.y_coordinate - centerY;
                        z = element.z_coordinate - centerZ;
                        elementsWithCoords++;
                    } else {
                        // Fallback para grid se não tiver coordenadas
                        const gridSize = Math.ceil(Math.sqrt(elementsWithoutCoords + 1));
                        x = (elementsWithoutCoords % gridSize) * 3 - (gridSize * 1.5);
                        z = Math.floor(elementsWithoutCoords / gridSize) * 3 - (gridSize * 1.5);
                        y = 1;
                        elementsWithoutCoords++;
                    }
                    
                    mesh.position.set(x, y, z);
                    mesh.castShadow = true;
                    mesh.receiveShadow = true;
                    
                    // Salvar dados do elemento
                    mesh.name = element.name;
                    mesh.userData.ifcId = element.id;
                    mesh.userData.type = elementType;
                    mesh.userData.global_id = element.global_id;
                    mesh.userData.description = element.description || '';
                    mesh.userData.hasRealCoordinates = element.has_coordinates || false;
                    
                    this.model.add(mesh);
                    elementIndex++;
                });
            }
            
            console.log(`Posicionamento: ${elementsWithCoords} elementos com coordenadas reais, ${elementsWithoutCoords} em grid`);
            
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
            
            // Mostrar mensagem apropriada
            if (elementsWithCoords > 0) {
                const message = `Exibindo ${elementIndex} elementos como cubos coloridos. ${elementsWithCoords} elementos posicionados usando coordenadas reais do IFC. Para ver geometria 3D completa, verifique se o arquivo IFC está acessível.`;
                this.showWarningMessage(message);
            } else {
                this.showWarningMessage(`Exibindo ${elementIndex} elementos como cubos coloridos em grid. Coordenadas reais não disponíveis. Para ver geometria real, verifique se o arquivo IFC está acessível.`);
            }
            
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
        // Tentar múltiplos IDs para suportar diferentes templates
        const overlayIds = ['loading-overlay-public', 'loadingOverlay', 'loading-overlay'];
        let overlay = null;
        
        for (const id of overlayIds) {
            overlay = document.getElementById(id);
            if (overlay) break;
        }
        
        if (overlay) {
            overlay.style.display = show ? 'flex' : 'none';
            // Tentar encontrar a mensagem por diferentes seletores
            const text = overlay.querySelector('span') || 
                        overlay.querySelector('#loading-message-public') || 
                        overlay.querySelector('.loading-message');
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
    
    // Métodos para sensores IoT
    async loadSensors() {
        console.log('Carregando sensores...');
        
        try {
            // Buscar dados dos sensores via API (apenas ativos)
            const response = await fetch('/sensors/api/sensors/?is_active=true');
            
            if (!response.ok) {
                console.warn('Erro ao buscar sensores:', response.status);
                return;
            }
            
            const data = await response.json();
            // A API retorna {results: [...], count: ...}
            const sensors = data.results || data;
            console.log('Sensores encontrados:', sensors.length || sensors.count || 0);
            
            // Remover marcadores existentes
            this.removeSensorMarkers();
            
            // Adicionar marcadores para sensores com localização
            if (Array.isArray(sensors)) {
                sensors.forEach(sensor => {
                    if (sensor.location_id) {
                        this.addSensorMarker(sensor);
                    }
                });
            }
            
        } catch (error) {
            console.error('Erro ao carregar sensores:', error);
        }
    }
    
    addSensorMarker(sensor) {
        // Criar marcador visual para sensor
        const geometry = new THREE.SphereGeometry(0.5, 16, 16);
        const material = new THREE.MeshStandardMaterial({
            color: 0xff0000,
            emissive: 0xff0000,
            emissiveIntensity: 0.5
        });
        
        const marker = new THREE.Mesh(geometry, material);
        
        // Posicionar usando location_id (precisa ser parseado ou mapeado)
        // Por enquanto, colocar em posição aleatória
        marker.position.set(
            Math.random() * 20 - 10,
            2,
            Math.random() * 20 - 10
        );
        
        marker.userData.sensor = sensor;
        marker.name = `sensor-${sensor.id}`;
        
        this.scene.add(marker);
        this.sensorMarkers.push(marker);
    }
    
    removeSensorMarkers() {
        this.sensorMarkers.forEach(marker => {
            this.scene.remove(marker);
            if (marker.geometry) marker.geometry.dispose();
            if (marker.material) marker.material.dispose();
        });
        this.sensorMarkers = [];
    }
}
