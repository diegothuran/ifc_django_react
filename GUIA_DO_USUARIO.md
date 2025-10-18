# 📖 GUIA DO USUÁRIO - SISTEMA IFC MONITORING

> **Sistema Completo de Monitoramento e Visualização 3D de Plantas Industriais**

---

## 📋 ÍNDICE

1. [Introdução](#introdução)
2. [Sistema Django - IFC Digital Twin](#sistema-django---ifc-digital-twin)
3. [Sistema FastAPI + React](#sistema-fastapi--react)
4. [Funcionalidades Detalhadas](#funcionalidades-detalhadas)
5. [Guia de Uso Passo a Passo](#guia-de-uso-passo-a-passo)
6. [Dicas e Melhores Práticas](#dicas-e-melhores-práticas)
7. [Solução de Problemas](#solução-de-problemas)

---

## 🎯 INTRODUÇÃO

Este documento descreve todos os recursos e funcionalidades dos dois sistemas de monitoramento IFC disponíveis no workspace:

### Sistema 1: **IFC Django Project** (Digital Twin)
- **Localização**: `C:\Users\diego\Downloads\ifc_django_project\ifc_django_project\`
- **Tecnologia**: Django 5.2.7 + Three.js + IFC.js
- **Foco**: Visualização 3D avançada de plantas IFC com API REST completa

### Sistema 2: **IFC Monitoring System** (FastAPI + React)
- **Localização**: `C:\Users\diego\Documents\ifc_monitoring_deploy\ifc_monitoring_system\`
- **Tecnologia**: FastAPI + React + Material-UI
- **Foco**: Monitoramento de sensores em tempo real com processamento IFC

---

## 🏗️ SISTEMA DJANGO - IFC DIGITAL TWIN

### 🌐 URLs de Acesso

#### Produção
- **Site Principal**: https://ifc-django.onrender.com
- **Painel Admin**: https://ifc-django.onrender.com/admin/
- **API REST**: https://ifc-django.onrender.com/plant-viewer/api/
- **Dashboard**: https://ifc-django.onrender.com/dashboard/

#### Desenvolvimento Local
- **Site Principal**: http://localhost:8000
- **Painel Admin**: http://localhost:8000/admin/
- **Visualizador 3D**: http://localhost:8000/plant/
- **Dashboard Sensores**: http://localhost:8000/sensors/dashboard/

### 👤 Credenciais Padrão

| Usuário | Senha | Tipo | Permissões |
|---------|-------|------|------------|
| `admin` | `admin123` | Superusuário | Acesso total ao sistema |

> ⚠️ **IMPORTANTE**: Altere as credenciais em produção!

---

## 📦 FUNCIONALIDADES DO SISTEMA DJANGO

### 1️⃣ PAINEL ADMINISTRATIVO (Django Admin + Unfold)

#### Acesso
- URL: `/admin/`
- Requer autenticação de administrador
- Interface moderna com tema Unfold

#### O que você pode fazer:

##### **Gestão de Plantas IFC**
- ✅ **Upload de arquivos IFC**
  - Suporta arquivos `.ifc` (Industry Foundation Classes)
  - Upload com validação automática de extensão
  - Armazenamento organizado por data (`ifc_files/YYYY/MM/DD/`)
  
- ✅ **Visualizar lista de plantas**
  - Ver todas as plantas cadastradas
  - Filtrar por status (ativo/inativo)
  - Ordenar por data de upload
  - Ver tamanho do arquivo
  
- ✅ **Editar informações da planta**
  - Nome descritivo
  - Descrição detalhada
  - Status de ativação
  - Substituir arquivo IFC
  
- ✅ **Gerenciar metadados**
  - Ver metadados extraídos automaticamente
  - Forçar atualização de metadados
  - Cache de 7 dias (PostgreSQL em produção)

##### **Gestão de Sensores**
- ✅ **Cadastrar sensores**
  - Nome identificador
  - Tipo: Contador, Temperatura, Pressão, Vibração, Fluxo, Nível, Outro
  - Endereço IP e porta
  - Location ID (para vincular ao modelo 3D)
  - Intervalo de coleta (segundos)
  - Timeout de comunicação
  
- ✅ **Monitorar sensores**
  - Ver status em tempo real:
    - ✅ Ativo (dados recentes)
    - ⚠️ Sem dados recentes
    - ❌ Inativo
    - ❓ Nunca coletado
  - Ver última coleta de dados
  - Estatísticas por sensor
  
- ✅ **Gerenciar dados dos sensores**
  - Ver todos os dados coletados
  - Filtrar por sensor, data, status
  - Ver contagem, valores, unidades
  - Qualidade da leitura (0-100%)
  - Dados brutos em JSON

##### **Sistema de Alertas**
- ✅ **Visualizar alertas**
  - Tipos: Limite Atingido, Desconexão, Erro, Manutenção, Outro
  - Níveis: Informação, Aviso, Erro, Crítico
  - Status: Ativo ou Resolvido
  
- ✅ **Gerenciar alertas**
  - Marcar como resolvido
  - Adicionar notas
  - Filtrar por sensor, tipo, nível

##### **Gestão de Usuários**
- ✅ **Criar/editar usuários**
- ✅ **Definir permissões**
- ✅ **Gerenciar grupos**
- ✅ **Ver histórico de ações**

---

### 2️⃣ VISUALIZADOR 3D DE PLANTAS

#### Acesso
- URL Principal: `/plant/`
- Lista de Plantas: `/plant/plants/`
- Detalhes: `/plant/plants/{id}/`

#### Recursos do Visualizador 3D

##### **Controles do Mouse**
- 🖱️ **Botão Esquerdo + Arrastar**: Rotacionar modelo
- 🖱️ **Botão Direito + Arrastar**: Pan (mover lateralmente)
- 🖱️ **Scroll**: Zoom in/out
- 🖱️ **Click**: Selecionar elemento IFC

##### **Atalhos de Teclado**
- `R` - **Reset**: Volta à visualização inicial
- `W` - **Wireframe**: Alterna entre sólido e aramado
- `O` - **Ortográfica**: Alterna entre perspectiva e ortográfica
- `ESC` - **Desselecionar**: Remove seleção atual

##### **Funcionalidades Avançadas**

**Seleção de Elementos**
- Clique em qualquer elemento para ver propriedades
- Painel lateral mostra:
  - Nome do elemento
  - Tipo IFC (IfcWall, IfcSlab, IfcColumn, etc.)
  - GlobalID único
  - Propriedades customizadas
  - Dimensões e materiais

**Inspeção de Propriedades**
- Ver todas as propriedades IFC
- Propriedades agrupadas por categoria
- Valores formatados e legíveis

**Modos de Visualização**
- 🎨 **Sólido**: Visualização completa com materiais
- 📐 **Wireframe**: Apenas bordas dos elementos
- 👁️ **Perspectiva**: Visão realista com profundidade
- 📏 **Ortográfica**: Visão técnica sem distorção

**Performance**
- ⚡ Carregamento otimizado com lazy loading
- 🎯 OrbitControls com damping suave
- 💾 Cache de geometrias e materiais
- 🚀 Renderização eficiente com Three.js

---

### 3️⃣ API REST COMPLETA

#### Base URL
- Produção: `https://ifc-django.onrender.com/plant-viewer/api/`
- Local: `http://localhost:8000/plant-viewer/api/`

#### Endpoints Disponíveis

##### **Gestão de Plantas**

```
GET /plants/
```
**Descrição**: Lista todas as plantas ativas  
**Resposta**: Lista paginada de plantas com informações básicas

```
GET /plants/{id}/
```
**Descrição**: Detalhes completos de uma planta  
**Query Params**:
- `include_metadata` (boolean): Incluir metadados IFC (padrão: true)

```
POST /plants/
```
**Descrição**: Criar nova planta (requer autenticação)  
**Body**: FormData com arquivo IFC e informações

```
PUT /plants/{id}/
PATCH /plants/{id}/
```
**Descrição**: Atualizar planta existente (requer autenticação)

```
DELETE /plants/{id}/
```
**Descrição**: Remover planta (requer autenticação)

##### **Metadados IFC**

```
GET /plants/{id}/metadata/
```
**Descrição**: Metadados completos extraídos do IFC  
**Retorna**:
- `project_info`: Informações do projeto
- `building_elements`: Elementos organizados por tipo
- `spatial_structure`: Hierarquia espacial
- `statistics`: Estatísticas do modelo
- `bounds`: Limites (bounding box)

```
POST /plants/{id}/refresh_metadata/
```
**Descrição**: Força atualização dos metadados  
**Uso**: Quando o arquivo IFC foi modificado

##### **Elementos IFC**

```
GET /plants/{id}/elements/
```
**Descrição**: Elementos organizados por tipo  
**Retorna**: Dicionário com tipos como IfcWall, IfcSlab, etc.

```
GET /plants/{id}/element/{element_id}/
```
**Descrição**: Propriedades de um elemento específico  
**Params**: `element_id` - ExpressID do elemento IFC

```
GET /plants/{id}/search/?q={termo}
```
**Descrição**: Buscar elementos por nome  
**Query Params**:
- `q` (string): Termo de busca (obrigatório)

##### **Estatísticas**

```
GET /plants/{id}/statistics/
```
**Descrição**: Estatísticas do modelo  
**Retorna**:
- Total de elementos por tipo
- Contagem de pisos
- Contagem de espaços
- Dimensões do modelo

```
GET /plants/{id}/bounds/
```
**Descrição**: Limites (bounding box) do modelo  
**Retorna**:
- Coordenadas mínimas (x, y, z)
- Coordenadas máximas (x, y, z)
- Centro do modelo
- Dimensões (largura, altura, profundidade)

##### **Estrutura Espacial**

```
GET /plants/{id}/spatial_structure/
```
**Descrição**: Hierarquia espacial do IFC  
**Retorna**: Árvore hierárquica:
- Projeto → Site → Edifício → Andar → Espaço

```
GET /plants/{id}/spaces/
```
**Descrição**: Espaços IFC com coordenadas  
**Retorna**:
- Lista de espaços (IfcSpace)
- Coordenadas X, Y, Z
- Área, volume, altura
- Bounds dos espaços

#### Exemplos de Uso da API

**Exemplo 1: Listar todas as plantas**
```bash
curl https://ifc-django.onrender.com/plant-viewer/api/plants/
```

**Exemplo 2: Obter estatísticas**
```bash
curl https://ifc-django.onrender.com/plant-viewer/api/plants/1/statistics/
```

**Exemplo 3: Buscar paredes**
```bash
curl "https://ifc-django.onrender.com/plant-viewer/api/plants/1/search/?q=wall"
```

**Exemplo 4: Obter propriedades de elemento**
```bash
curl https://ifc-django.onrender.com/plant-viewer/api/plants/1/element/12345/
```

---

### 4️⃣ DASHBOARD DE MONITORAMENTO

#### Tipos de Dashboard

##### **Dashboard Público** (`/dashboard/`)
- ✅ Acesso sem autenticação
- ✅ Visualização da planta 3D
- ✅ Resumo de sensores ativos
- ✅ Alertas críticos apenas
- ✅ Dados da última hora

##### **Dashboard do Usuário** (`/dashboard/user/`)
- ✅ Requer autenticação
- ✅ Dados das últimas 6 horas
- ✅ Histórico detalhado de sensores
- ✅ Todos os níveis de alertas
- ✅ Estatísticas por sensor

##### **Dashboard Administrativo** (`/admin/`)
- ✅ Requer permissões de admin
- ✅ Dados das últimas 24 horas
- ✅ Gráficos por hora
- ✅ Top 5 sensores mais ativos
- ✅ Sensores com problemas
- ✅ Distribuição por tipo
- ✅ Alertas por nível

#### Recursos do Dashboard

**Estatísticas em Tempo Real**
- 📊 Total de sensores
- ✅ Sensores ativos
- 📈 Total de leituras
- 🚨 Alertas ativos
- ⚠️ Sensores com problemas

**Visualizações**
- 📉 Gráfico de leituras por hora
- 🥧 Distribuição de sensores por tipo
- 📊 Distribuição de alertas por nível
- 📈 Qualidade média das leituras

**APIs do Dashboard**

```
GET /dashboard/data/?type=summary&hours=1
```
**Retorna**: Resumo geral do sistema

```
GET /dashboard/data/?type=sensors&hours=6
```
**Retorna**: Dados detalhados de todos os sensores

```
GET /dashboard/data/?type=alerts&hours=24
```
**Retorna**: Alertas recentes

```
GET /dashboard/plant-data/
```
**Retorna**: Dados da planta ativa + sensores com localização

```
GET /dashboard/sensor-data/
```
**Retorna**: Formato específico para Digital Twin
```json
[
  {
    "id": 1,
    "name": "Sensor Linha 1",
    "location_id": "12345",
    "latest_count": 582,
    "is_active": true
  }
]
```

---

### 5️⃣ GESTÃO DE SENSORES

#### Visualizações Disponíveis

##### **Lista de Sensores** (`/sensors/`)
- Ver todos os sensores cadastrados
- Status visual de cada sensor
- Filtros e busca
- Paginação (20 por página)
- Estatísticas resumidas

##### **Detalhes do Sensor** (`/sensors/{id}/`)
- Informações completas
- Últimas 50 leituras (24h)
- Estatísticas:
  - Média, máximo, mínimo de contagem
  - Média, máximo, mínimo de valor
  - Qualidade média
- Alertas ativos do sensor
- Gráficos históricos

##### **Dashboard de Sensores** (`/sensors/dashboard/`)
- Visão geral de todos os sensores
- Sensores por tipo
- Sensores com problemas
- Alertas ativos recentes
- Métricas agregadas

#### APIs de Sensores

```
GET /sensors/api/{sensor_id}/data/?hours=24&limit=100
```
**Descrição**: Dados de um sensor específico  
**Params**:
- `hours`: Período em horas (padrão: 24)
- `limit`: Máximo de registros (padrão: 100)

**Retorna**:
```json
{
  "sensor": {
    "id": 1,
    "name": "Sensor Linha 1",
    "sensor_type": "counter",
    "ip_address": "192.168.1.100",
    "port": 80,
    "is_active": true,
    "status": "✅ Ativo"
  },
  "data": [
    {
      "id": 1,
      "timestamp": "2025-10-12T10:30:00Z",
      "count": 582,
      "value": 23.5,
      "unit": "°C",
      "status": "ok",
      "quality": 98.5,
      "display_value": "582"
    }
  ],
  "stats": {
    "count_avg": 580.5,
    "count_max": 600,
    "count_min": 550,
    "value_avg": 23.2,
    "quality_avg": 97.8,
    "total_readings": 24
  },
  "period_hours": 24,
  "total_data_points": 24
}
```

```
GET /sensors/api/all/?hours=1
```
**Descrição**: Dados de todos os sensores ativos  
**Params**: `hours` - Período em horas

---

## 🚀 SISTEMA FASTAPI + REACT

### 🌐 URLs de Acesso

#### Produção
- **API Backend**: https://ifc-backend-ph0n.onrender.com
- **Documentação**: https://ifc-backend-ph0n.onrender.com/docs
- **Frontend**: (configurável - Netlify/Vercel)

#### Desenvolvimento Local
- **API Backend**: http://localhost:8000
- **Frontend React**: http://localhost:3000
- **Docs Swagger**: http://localhost:8000/docs
- **Docs ReDoc**: http://localhost:8000/redoc

### 👤 Credenciais Padrão

| Função | Usuário | Senha | Permissões |
|--------|---------|-------|------------|
| Admin | `admin` | `admin123` | Acesso total ao sistema |
| Operador | `operator` | `operator123` | Gerenciar sensores e alertas |
| Visualizador | `viewer` | `viewer123` | Acesso somente leitura |

---

## 📦 FUNCIONALIDADES DO SISTEMA FASTAPI

### 1️⃣ AUTENTICAÇÃO E USUÁRIOS

#### Endpoints de Autenticação

```
POST /api/v1/auth/login
```
**Descrição**: Login no sistema  
**Body**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```
**Retorna**: Token JWT para autenticação

```
POST /api/v1/auth/register
```
**Descrição**: Registrar novo usuário  
**Body**:
```json
{
  "username": "novo_usuario",
  "email": "usuario@exemplo.com",
  "password": "senha_segura",
  "full_name": "Nome Completo"
}
```

```
GET /api/v1/auth/me
```
**Descrição**: Informações do usuário autenticado  
**Headers**: `Authorization: Bearer {token}`

#### Funções de Usuário

**Admin**
- ✅ Gerenciar todos os recursos
- ✅ Criar/editar/deletar sensores
- ✅ Gerenciar usuários
- ✅ Configurar sistema
- ✅ Upload de arquivos IFC
- ✅ Processar arquivos IFC

**Operador**
- ✅ Ver todos os dados
- ✅ Gerenciar sensores
- ✅ Reconhecer alertas
- ✅ Configurar limites
- ❌ Gerenciar usuários

**Visualizador**
- ✅ Ver dashboards
- ✅ Ver dados de sensores
- ✅ Ver alertas
- ❌ Modificar dados
- ❌ Configurar sistema

---

### 2️⃣ GESTÃO DE SENSORES

#### Endpoints de Sensores

```
GET /api/v1/sensors/
```
**Descrição**: Lista todos os sensores com filtros  
**Query Params**:
- `skip` (int): Offset para paginação (padrão: 0)
- `limit` (int): Limite de resultados (padrão: 100, máx: 1000)
- `sensor_type` (string): Filtrar por tipo
- `location_id` (int): Filtrar por localização
- `is_active` (boolean): Filtrar por status

**Retorna**:
```json
{
  "sensors": [
    {
      "id": 1,
      "name": "Sensor Temperatura 01",
      "sensor_type": "temperature",
      "device_id": "TEMP-001",
      "location_id": 1,
      "is_active": true,
      "min_value": -40.0,
      "max_value": 85.0,
      "unit": "°C",
      "alert_threshold_min": 5.0,
      "alert_threshold_max": 35.0,
      "update_interval": 60
    }
  ],
  "total": 10,
  "page": 1,
  "size": 100
}
```

```
GET /api/v1/sensors/{sensor_id}
```
**Descrição**: Detalhes de um sensor específico

```
POST /api/v1/sensors/
```
**Descrição**: Criar novo sensor (requer Admin)  
**Body**:
```json
{
  "name": "Sensor Umidade 01",
  "sensor_type": "humidity",
  "device_id": "HUM-001",
  "location_id": 1,
  "min_value": 0.0,
  "max_value": 100.0,
  "unit": "%",
  "alert_threshold_min": 30.0,
  "alert_threshold_max": 70.0,
  "update_interval": 300
}
```

```
PUT /api/v1/sensors/{sensor_id}
```
**Descrição**: Atualizar sensor (requer Admin)

```
DELETE /api/v1/sensors/{sensor_id}
```
**Descrição**: Deletar sensor (requer Admin)

#### Tipos de Sensores Suportados

- 🌡️ **temperature** - Temperatura
- 💧 **humidity** - Umidade
- 🎚️ **pressure** - Pressão
- 📊 **vibration** - Vibração
- 🌊 **flow** - Fluxo
- 📏 **level** - Nível
- ⚡ **power** - Energia
- 🔊 **sound** - Som/Ruído

---

### 3️⃣ LEITURAS DE SENSORES

#### Endpoints de Leituras

```
GET /api/v1/readings/
```
**Descrição**: Lista leituras com filtros  
**Query Params**:
- `skip`, `limit`: Paginação
- `sensor_id` (int): Filtrar por sensor
- `start_date` (datetime): Data inicial
- `end_date` (datetime): Data final

```
POST /api/v1/readings/
```
**Descrição**: Criar nova leitura  
**Body**:
```json
{
  "sensor_id": 1,
  "value": 23.5,
  "quality": "good",
  "timestamp": "2025-10-12T10:30:00Z"
}
```

```
GET /api/v1/readings/latest
```
**Descrição**: Últimas leituras de todos os sensores  
**Query Params**:
- `limit` (int): Número de sensores (padrão: 50)

**Retorna**: Última leitura de cada sensor ativo

---

### 4️⃣ SISTEMA DE ALERTAS

#### Endpoints de Alertas

```
GET /api/v1/alerts/
```
**Descrição**: Lista alertas com filtros  
**Query Params**:
- `skip`, `limit`: Paginação
- `sensor_id` (int): Filtrar por sensor
- `severity` (string): info, warning, error, critical
- `status` (string): active, acknowledged, resolved
- `start_date`, `end_date`: Período

```
GET /api/v1/alerts/{alert_id}
```
**Descrição**: Detalhes de um alerta específico

```
PUT /api/v1/alerts/{alert_id}
```
**Descrição**: Atualizar status do alerta  
**Body**:
```json
{
  "status": "acknowledged",
  "notes": "Técnico enviado para verificar"
}
```

#### Tipos de Alertas

**Por Severidade**:
- 🔵 **info** - Informação
- 🟡 **warning** - Aviso
- 🟠 **error** - Erro
- 🔴 **critical** - Crítico

**Por Status**:
- 🆕 **active** - Ativo, aguardando ação
- 👀 **acknowledged** - Reconhecido, em análise
- ✅ **resolved** - Resolvido

**Por Tipo**:
- 🎯 **threshold** - Limite ultrapassado
- 🔌 **disconnection** - Sensor desconectado
- ⚠️ **quality** - Qualidade baixa de leitura
- 🔧 **maintenance** - Manutenção necessária

---

### 5️⃣ GESTÃO DE LOCALIZAÇÕES

#### Endpoints de Localizações

```
GET /api/v1/locations/
```
**Descrição**: Lista localizações hierárquicas

```
POST /api/v1/locations/
```
**Descrição**: Criar nova localização  
**Body**:
```json
{
  "name": "Edifício A",
  "location_type": "building",
  "parent_id": null,
  "description": "Edifício principal da planta",
  "address": "Rua Industrial, 123",
  "latitude": -23.550520,
  "longitude": -46.633308
}
```

```
PUT /api/v1/locations/{location_id}
```
**Descrição**: Atualizar localização

```
DELETE /api/v1/locations/{location_id}
```
**Descrição**: Deletar localização

#### Tipos de Localização

- 🌍 **site** - Site/Campus
- 🏢 **building** - Edifício
- 📐 **floor** - Andar
- 🚪 **room** - Sala
- 📦 **zone** - Zona/Área específica

#### Hierarquia de Localizações

```
Site (Campus)
└── Building (Edifício A)
    ├── Floor (1º Andar)
    │   ├── Room (Sala 101)
    │   └── Room (Sala 102)
    └── Floor (2º Andar)
        ├── Room (Sala 201)
        └── Zone (Área de Produção)
```

---

### 6️⃣ PROCESSAMENTO DE ARQUIVOS IFC

#### Endpoints IFC

```
GET /api/v1/ifc/files
```
**Descrição**: Lista arquivos IFC processados  
**Retorna**: Lista com status de processamento

```
POST /api/v1/ifc/upload
```
**Descrição**: Upload de arquivo IFC  
**Body**: `multipart/form-data`
```
file: arquivo.ifc
name: "Planta Industrial"
description: "Descrição da planta"
```

**Processo**:
1. ✅ Upload do arquivo
2. ✅ Validação de formato
3. ✅ Criação de registro
4. ✅ Processamento em background
5. ✅ Extração de metadados
6. ✅ Extração de espaços (IfcSpace)
7. ✅ Atualização de status

```
GET /api/v1/ifc/files/{file_id}
```
**Descrição**: Detalhes do arquivo IFC  
**Retorna**:
```json
{
  "id": 1,
  "name": "Planta Industrial",
  "filename": "planta_industrial.ifc",
  "file_size": 15728640,
  "status": "processed",
  "uploaded_at": "2025-10-12T10:00:00Z",
  "processed_at": "2025-10-12T10:05:00Z",
  "metadata": {
    "project_name": "Industrial Plant",
    "building_count": 1,
    "floor_count": 3,
    "space_count": 45,
    "element_count": 1234
  }
}
```

```
GET /api/v1/ifc/files/{file_id}/spaces
```
**Descrição**: Espaços extraídos do IFC  
**Retorna**: Lista de IfcSpace com:
- GlobalID, Nome, Descrição
- Coordenadas (x, y, z)
- Área, Volume, Altura
- Tipo de espaço

```
POST /api/v1/ifc/files/{file_id}/process
```
**Descrição**: Reprocessar arquivo IFC  
**Uso**: Quando processamento falhou ou arquivo foi atualizado

#### Status de Processamento

- 📤 **uploaded** - Arquivo enviado, aguardando processamento
- ⚙️ **processing** - Processamento em andamento
- ✅ **processed** - Processado com sucesso
- ❌ **error** - Erro no processamento

---

### 7️⃣ INTERFACE REACT (FRONTEND)

#### Páginas Disponíveis

##### **Login** (`/login`)
- Formulário de autenticação
- Validação de credenciais
- Armazena token JWT
- Redirecionamento automático

##### **Dashboard** (`/`)
- Visão geral do sistema
- Estatísticas em tempo real:
  - Total de sensores ativos
  - Total de leituras (24h)
  - Alertas ativos
  - Status de localizações
- Gráficos interativos:
  - Leituras por hora
  - Distribuição de alertas
  - Sensores por tipo
- Cards com informações principais
- Atualização automática (30s)

##### **Sensores** (`/sensors`)
- Lista de todos os sensores
- Filtros:
  - Por tipo
  - Por localização
  - Por status (ativo/inativo)
- Ações:
  - ✅ Criar novo sensor (Admin)
  - ✏️ Editar sensor (Admin)
  - 🗑️ Deletar sensor (Admin)
  - 👁️ Ver detalhes
  - 📊 Ver leituras históricas
- Cards com informações:
  - Nome e tipo
  - Localização
  - Status (online/offline)
  - Última leitura
  - Qualidade do sinal

**Formulário de Criação/Edição**:
- Nome do sensor
- Tipo (dropdown)
- Device ID
- Localização (dropdown)
- Valores mín/máx
- Unidade de medida
- Limites de alerta
- Intervalo de atualização

##### **Alertas** (`/alerts`)
- Lista de alertas
- Filtros:
  - Por severidade
  - Por status
  - Por sensor
  - Por período
- Ações:
  - 👁️ Ver detalhes
  - ✅ Reconhecer alerta
  - ✔️ Resolver alerta
  - 📝 Adicionar notas
- Cores por severidade:
  - 🔵 Info - Azul
  - 🟡 Warning - Amarelo
  - 🟠 Error - Laranja
  - 🔴 Critical - Vermelho
- Notificações em tempo real

##### **Localizações** (`/locations`)
- Visualização hierárquica
- Árvore de localizações
- Ações:
  - ✅ Criar localização (Admin)
  - ✏️ Editar localização (Admin)
  - 🗑️ Deletar localização (Admin)
  - 📍 Ver no mapa (se coordenadas disponíveis)
  - 📊 Ver sensores da localização
- Informações:
  - Nome e tipo
  - Endereço
  - Coordenadas GPS
  - Contato
  - Sensores associados
  - Hierarquia (pai/filhos)

#### Componentes da Interface

**Navbar**
- Logo e título
- Links de navegação
- Informações do usuário
- Botão de logout
- Notificações de alertas

**Cards de Estatísticas**
- Números grandes e destacados
- Ícones ilustrativos
- Cores por categoria
- Tendência (↑↓)

**Tabelas de Dados**
- Paginação
- Ordenação por coluna
- Filtros avançados
- Ações por linha
- Exportar dados

**Gráficos**
- Line charts (séries temporais)
- Bar charts (comparações)
- Pie charts (distribuições)
- Área charts (tendências)
- Interativos com tooltips

**Formulários**
- Validação em tempo real
- Mensagens de erro claras
- Campos obrigatórios marcados
- Suporte a autocomplete
- Salvamento automático (rascunho)

---

## 📚 GUIA DE USO PASSO A PASSO

### 🎯 CENÁRIO 1: Upload e Visualização de Planta IFC (Django)

#### Passo 1: Fazer Login
1. Acesse: `http://localhost:8000/admin/`
2. Digite credenciais:
   - Usuário: `admin`
   - Senha: `admin123`
3. Clique em "Log in"

#### Passo 2: Upload da Planta
1. No menu lateral, clique em **"Plantas"**
2. Clique no botão **"ADICIONAR PLANO DE CONSTRUÇÃO"** (canto superior direito)
3. Preencha o formulário:
   - **Nome**: `Planta Industrial Principal`
   - **Arquivo IFC**: Clique em "Escolher arquivo" e selecione seu `.ifc`
   - **Descrição**: `Planta da fábrica com 3 andares`
   - **Ativo**: ✅ Marque a caixa
4. Clique em **"SALVAR"**
5. Aguarde o upload (barra de progresso aparece para arquivos grandes)

#### Passo 3: Visualizar em 3D
1. Após salvar, clique em **"Dashboard Público"** no menu lateral
   - Ou acesse diretamente: `http://localhost:8000/plant/`
2. A planta será carregada automaticamente no visualizador 3D
3. Use os controles:
   - **Rotacionar**: Arraste com botão esquerdo
   - **Zoom**: Scroll do mouse
   - **Pan**: Arraste com botão direito
4. Clique em qualquer elemento para ver propriedades no painel lateral

#### Passo 4: Explorar API
1. Abra o navegador em: `http://localhost:8000/plant-viewer/api/plants/`
2. Você verá a lista de plantas em JSON
3. Clique no ID da planta para ver detalhes
4. Experimente os endpoints:
   - `/plants/1/statistics/` - Estatísticas
   - `/plants/1/elements/` - Elementos por tipo
   - `/plants/1/spatial_structure/` - Hierarquia

---

### 🎯 CENÁRIO 2: Configurar Sistema de Monitoramento (Django)

#### Passo 1: Cadastrar Sensor
1. No Admin, vá em **"Sensores"**
2. Clique em **"ADICIONAR SENSOR"**
3. Preencha:
   - **Nome**: `Sensor Linha Produção 1`
   - **Tipo**: Selecione `Contador`
   - **IP**: `192.168.1.100`
   - **Porta**: `80`
   - **Location ID**: `12345` (ExpressID do elemento IFC)
   - **Ativo**: ✅ Sim
   - **Intervalo de Coleta**: `60` segundos
4. Clique em **"SALVAR"**

#### Passo 2: Verificar Dashboard
1. Acesse: `http://localhost:8000/sensors/dashboard/`
2. Você verá:
   - Total de sensores: 1
   - Sensores ativos: 1
   - Status: ❓ Nunca coletado (normal para sensor novo)
3. Clique no sensor para ver detalhes

#### Passo 3: Simular Coleta de Dados
Você pode adicionar dados manualmente pelo Admin:
1. Vá em **"Dados dos Sensores"**
2. Clique em **"ADICIONAR DADO DO SENSOR"**
3. Preencha:
   - **Sensor**: Selecione o sensor criado
   - **Count**: `582`
   - **Status**: `ok`
   - **Quality**: `98.5`
4. Salvar

Ou use a API para inserir dados programaticamente

#### Passo 4: Ver no Digital Twin
1. Acesse: `http://localhost:8000/dashboard/`
2. O dashboard mostrará:
   - Planta 3D com sensor
   - Último valor do sensor
   - Status (✅ Ativo se dados recentes)
3. Clique no elemento 3D associado (Location ID 12345)
4. Verá dados do sensor no painel lateral

---

### 🎯 CENÁRIO 3: Monitoramento Completo (FastAPI + React)

#### Passo 1: Iniciar o Sistema
```bash
# Terminal 1 - Backend
cd ifc_monitoring_system
python start_system.py

# O script irá:
# ✅ Verificar dependências
# ✅ Criar banco de dados
# ✅ Criar dados de exemplo
# ✅ Iniciar backend
# ✅ Iniciar frontend
# ✅ Abrir navegador
```

#### Passo 2: Login no Sistema
1. O navegador abrirá em `http://localhost:3000`
2. Faça login com:
   - **Admin**: `admin` / `admin123`
   - **Operador**: `operator` / `operator123`
   - **Visualizador**: `viewer` / `viewer123`

#### Passo 3: Explorar Dashboard
1. Após login, você verá o **Dashboard principal**
2. Observe:
   - Cards com estatísticas
   - Gráfico de leituras por hora
   - Lista de alertas ativos
   - Status dos sensores
3. Clique nos cards para ver mais detalhes

#### Passo 4: Gerenciar Sensores
1. Clique em **"Sensores"** no menu
2. Você verá lista de sensores de exemplo
3. Para criar novo sensor (como Admin):
   - Clique em **"+ NOVO SENSOR"**
   - Preencha o formulário
   - Clique em **"SALVAR"**
4. Para editar:
   - Clique no ícone ✏️
   - Modifique campos
   - Salve
5. Para ver detalhes:
   - Clique no ícone 👁️
   - Veja leituras históricas
   - Veja gráficos de tendência

#### Passo 5: Gerenciar Alertas
1. Clique em **"Alertas"** no menu
2. Você verá alertas ativos
3. Para reconhecer um alerta:
   - Clique no ícone ✅
   - Adicione notas se necessário
   - Status muda para "Acknowledged"
4. Para resolver:
   - Clique no ícone ✔️
   - Adicione comentário
   - Status muda para "Resolved"

#### Passo 6: Gerenciar Localizações
1. Clique em **"Localizações"** no menu
2. Veja a estrutura hierárquica
3. Para criar localização (como Admin):
   - Clique em **"+ NOVA LOCALIZAÇÃO"**
   - Selecione tipo
   - Preencha informações
   - Selecione localização pai (se aplicável)
   - Salve
4. Para editar/deletar:
   - Use os ícones na linha

#### Passo 7: Upload de Arquivo IFC
1. Clique em **"Arquivos IFC"** (se disponível)
2. Clique em **"+ UPLOAD IFC"**
3. Selecione arquivo `.ifc`
4. Preencha nome e descrição
5. Clique em **"ENVIAR"**
6. Acompanhe o processamento:
   - Status: "Processing..."
   - Barra de progresso
   - Notificação quando concluído
7. Após processamento:
   - Clique para ver detalhes
   - Veja espaços extraídos
   - Veja metadados

---

### 🎯 CENÁRIO 4: Integração via API

#### Exemplo: Criar Sensor via API (FastAPI)

```python
import requests

# 1. Fazer login
login_url = "http://localhost:8000/api/v1/auth/login"
login_data = {
    "username": "admin",
    "password": "admin123"
}

response = requests.post(login_url, json=login_data)
token = response.json()["access_token"]

# 2. Headers com token
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 3. Criar sensor
sensor_url = "http://localhost:8000/api/v1/sensors/"
sensor_data = {
    "name": "Sensor Temperatura 01",
    "sensor_type": "temperature",
    "device_id": "TEMP-001",
    "location_id": 1,
    "min_value": -40.0,
    "max_value": 85.0,
    "unit": "°C",
    "alert_threshold_min": 5.0,
    "alert_threshold_max": 35.0,
    "update_interval": 60
}

response = requests.post(sensor_url, json=sensor_data, headers=headers)
sensor = response.json()
print(f"Sensor criado: ID {sensor['id']}")

# 4. Adicionar leitura
reading_url = "http://localhost:8000/api/v1/readings/"
reading_data = {
    "sensor_id": sensor["id"],
    "value": 23.5,
    "quality": "good"
}

response = requests.post(reading_url, json=reading_data, headers=headers)
print("Leitura adicionada com sucesso!")
```

#### Exemplo: Buscar Elementos IFC (Django)

```python
import requests

# 1. Buscar plantas disponíveis
plants_url = "http://localhost:8000/plant-viewer/api/plants/"
response = requests.get(plants_url)
plants = response.json()

plant_id = plants["results"][0]["id"]

# 2. Buscar elementos do tipo IfcWall
elements_url = f"http://localhost:8000/plant-viewer/api/plants/{plant_id}/elements/"
response = requests.get(elements_url)
data = response.json()

walls = data["elements"].get("IfcWall", [])
print(f"Total de paredes: {len(walls)}")

# 3. Buscar propriedades de uma parede específica
if walls:
    wall_id = walls[0]["id"]
    props_url = f"http://localhost:8000/plant-viewer/api/plants/{plant_id}/element/{wall_id}/"
    response = requests.get(props_url)
    properties = response.json()
    
    print(f"Parede: {properties['name']}")
    print(f"Tipo: {properties['type']}")
    print(f"GlobalID: {properties['global_id']}")
```

---

## 💡 DICAS E MELHORES PRÁTICAS

### 🎨 Visualização 3D

**Performance**
- ✅ Use arquivos IFC otimizados (< 50 MB recomendado)
- ✅ Limpe geometrias desnecessárias antes do upload
- ✅ Use Wireframe (tecla `W`) para modelos muito grandes
- ✅ Aguarde o cache de metadados (7 dias) para melhor performance

**Navegação**
- 💡 Pressione `R` para resetar se perder a orientação
- 💡 Use ortográfica (`O`) para medições precisas
- 💡 Clique e `ESC` para comparar elementos rapidamente
- 💡 Use Pan (botão direito) para ajustar enquadramento

### 📡 Sensores

**Configuração**
- ✅ Use IPs fixos para sensores
- ✅ Defina intervalos de coleta adequados (60s recomendado)
- ✅ Configure limites de alerta realistas
- ✅ Documente Location IDs no modelo 3D
- ✅ Use nomes descritivos (ex: "Sensor Temp. Linha 1 - Sala 101")

**Monitoramento**
- 💡 Verifique dashboard pelo menos 2x/dia
- 💡 Configure alertas para condições críticas
- 💡 Documente ações tomadas em alertas
- 💡 Revise sensores sem dados recentes semanalmente
- 💡 Calibre sensores regularmente

### 🚨 Alertas

**Gerenciamento**
- ✅ Reconheça alertas assim que visualizar
- ✅ Adicione notas detalhadas sobre ações tomadas
- ✅ Resolva alertas apenas após verificar correção
- ✅ Configure diferentes severidades apropriadamente
- ✅ Revise histórico de alertas mensalmente

**Priorização**
- 🔴 **Critical**: Ação imediata (<15 min)
- 🟠 **Error**: Ação urgente (<1h)
- 🟡 **Warning**: Ação necessária (<4h)
- 🔵 **Info**: Para conhecimento

### 📊 API

**Autenticação**
- ✅ Armazene tokens de forma segura
- ✅ Implemente refresh de token
- ✅ Use HTTPS em produção
- ✅ Rotacione credenciais regularmente

**Rate Limiting**
- 💡 Limite requisições a 100/minuto por usuário
- 💡 Use paginação para grandes conjuntos de dados
- 💡 Implemente cache local quando possível
- 💡 Agrupe requisições em lotes

**Erro Handling**
- ✅ Sempre verifique status code
- ✅ Implemente retry com backoff exponencial
- ✅ Log todos os erros para análise
- ✅ Mostre mensagens amigáveis ao usuário

### 🗄️ Banco de Dados

**Manutenção**
- ✅ Faça backup diário em produção
- ✅ Limpe dados antigos periodicamente (> 90 dias)
- ✅ Monitore tamanho do banco
- ✅ Otimize queries lentas

**Performance**
- 💡 Use índices para campos filtrados
- 💡 Limite resultados com paginação
- 💡 Use cache para dados frequentes
- 💡 Implemente agregações no banco

### 🔐 Segurança

**Credenciais**
- ⚠️ **CRÍTICO**: Altere senhas padrão em produção!
- ✅ Use senhas fortes (12+ caracteres)
- ✅ Habilite 2FA quando disponível
- ✅ Não compartilhe credenciais
- ✅ Revogue acessos de ex-funcionários imediatamente

**Dados**
- ✅ Use HTTPS sempre (SSL/TLS)
- ✅ Criptografe dados sensíveis
- ✅ Implemente auditoria de acessos
- ✅ Restrinja IPs permitidos quando possível

---

## 🔧 SOLUÇÃO DE PROBLEMAS

### Problema: Visualizador 3D não carrega

**Sintomas**:
- Tela branca
- Erro no console do navegador
- Loading infinito

**Soluções**:
1. **Verifique o arquivo IFC**:
   ```python
   # No Django shell
   from plant_viewer.models import BuildingPlan
   plant = BuildingPlan.objects.first()
   print(plant.ifc_file.path)  # Verifica se arquivo existe
   ```

2. **Limpe o cache do navegador**:
   - Chrome: `Ctrl+Shift+Delete`
   - Selecione "Imagens e arquivos em cache"
   - Limpe

3. **Verifique metadados**:
   ```bash
   curl http://localhost:8000/plant-viewer/api/plants/1/metadata/
   ```

4. **Force atualização**:
   ```bash
   curl -X POST http://localhost:8000/plant-viewer/api/plants/1/refresh_metadata/
   ```

5. **Verifique logs**:
   ```bash
   # Django
   tail -f logs/django.log
   ```

---

### Problema: Sensor não coleta dados

**Sintomas**:
- Status: "❓ Nunca coletado"
- Status: "⚠️ Sem dados recentes"
- Alertas de desconexão

**Soluções**:
1. **Verifique conectividade**:
   ```bash
   ping 192.168.1.100
   telnet 192.168.1.100 80
   ```

2. **Verifique configuração**:
   - IP correto?
   - Porta correta?
   - Sensor está ativo?
   - Intervalo de coleta não muito curto?

3. **Teste manualmente**:
   ```bash
   # Via API
   curl http://192.168.1.100:80/data
   ```

4. **Adicione dados de teste**:
   - Via Admin Django
   - Ou via API FastAPI
   - Verifique se sensor aparece como ativo

5. **Verifique logs de erro**:
   ```python
   # Django
   from sensor_management.models import Sensor
   sensor = Sensor.objects.get(id=1)
   print(sensor.last_data_collected)
   ```

---

### Problema: API retorna 401 Unauthorized

**Sintomas**:
- Erro 401 em requisições
- "Not authenticated"
- "Invalid token"

**Soluções (FastAPI)**:
1. **Verificar token**:
   ```python
   # Token expirou?
   # Faça novo login
   response = requests.post(
       "http://localhost:8000/api/v1/auth/login",
       json={"username": "admin", "password": "admin123"}
   )
   token = response.json()["access_token"]
   ```

2. **Verificar headers**:
   ```python
   headers = {
       "Authorization": f"Bearer {token}",  # Não esqueça "Bearer "
       "Content-Type": "application/json"
   }
   ```

3. **Verificar permissões**:
   - Endpoint requer Admin?
   - Usuário tem permissão?

**Soluções (Django)**:
1. **Login via Admin**:
   - Acesse `/admin/`
   - Faça login

2. **Para API pública**:
   - Endpoints públicos não requerem autenticação
   - Verifique `REST_FRAMEWORK` settings

---

### Problema: Upload IFC falha

**Sintomas**:
- Erro ao fazer upload
- "Invalid file format"
- Upload para no meio

**Soluções**:
1. **Verifique extensão**:
   - Deve ser `.ifc`
   - Não `.ifcxml` ou `.ifczip`

2. **Verifique tamanho**:
   ```python
   # Django settings.py
   FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50 MB
   DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800
   ```

3. **Verifique validade do IFC**:
   - Abra em software IFC (ex: FreeCAD, BlenderBIM)
   - Verifique se abre sem erros
   - Exporte novamente se necessário

4. **Upload em partes** (se muito grande):
   - Divida modelo em múltiplos arquivos
   - Ou use compressão

5. **Verifique permissões**:
   ```bash
   # Linux
   chmod 755 media/ifc_files/
   ```

---

### Problema: Frontend React não conecta ao Backend

**Sintomas**:
- Erro de CORS
- "Network Error"
- "Failed to fetch"

**Soluções**:
1. **Verifique URL da API**:
   ```typescript
   // frontend/src/services/api.ts
   const API_BASE_URL = 'http://localhost:8000/api/v1';
   ```

2. **Verifique CORS**:
   ```python
   # main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Verifique backend rodando**:
   ```bash
   curl http://localhost:8000/health
   ```

4. **Verifique console do navegador**:
   - F12 → Console
   - F12 → Network
   - Ver requisições falhando

---

### Problema: Dados não aparecem no Dashboard

**Sintomas**:
- Dashboard vazio
- Estatísticas zeradas
- Gráficos sem dados

**Soluções**:
1. **Verifique se há dados**:
   ```python
   # Django
   from sensor_management.models import SensorData
   print(SensorData.objects.count())
   ```

2. **Verifique período**:
   - Dashboard mostra apenas dados recentes
   - Adicione dados novos ou ajuste período

3. **Limpe cache**:
   ```python
   # Django
   from django.core.cache import cache
   cache.clear()
   ```

4. **Force refresh**:
   - Recarregue página (F5)
   - Limpe cache do navegador
   - Feche e abra navegador

5. **Verifique filtros**:
   - Filtros aplicados?
   - Sensores ativos?
   - Período correto?

---

### Problema: Metadados IFC demoram muito

**Sintomas**:
- Extração leva > 60 segundos
- Timeout em produção
- Cache não funciona

**Soluções**:
1. **Use cache**:
   ```python
   # Django settings.py
   # Cache já configurado para 7 dias
   # Verifique se createcachetable foi executado
   python manage.py createcachetable
   ```

2. **Extraia em background**:
   ```python
   # Use Celery (futuro) ou cron job
   # Por enquanto, force extração via Admin
   ```

3. **Otimize arquivo IFC**:
   - Remova geometrias desnecessárias
   - Use Level of Detail (LOD) apropriado
   - Simplifique modelo se possível

4. **Aumente timeout** (produção):
   ```yaml
   # render.yaml
   services:
     - type: web
       env: python
       buildCommand: "bash build.sh"
       startCommand: "gunicorn ifc_monitoring.wsgi:application --timeout 300"
   ```

---

## 📞 SUPORTE E RECURSOS ADICIONAIS

### Documentação Técnica

**Sistema Django**:
- `README.md` - Visão geral e quick start
- `docs/QUICK_START_RENDER.md` - Deploy no Render
- `docs/DEPLOY_CORRIGIDO.md` - Solução de problemas
- `docs/MELHORIAS_APLICADAS.md` - Changelog
- `docs/ESTRUTURA_PROJETO.md` - Arquitetura

**Sistema FastAPI**:
- `README.md` - Documentação completa
- `HEROKU_DEPLOY_SUMMARY.md` - Deploy no Heroku
- `QUICK_DEPLOY.md` - Deploy rápido
- API Docs: `/docs` (Swagger UI)
- API Docs: `/redoc` (ReDoc)

### Comandos Úteis

**Django**:
```bash
# Criar superusuário
python manage.py createsuperuser

# Migrations
python manage.py makemigrations
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic

# Criar tabela de cache
python manage.py createcachetable

# Shell interativo
python manage.py shell

# Testes
python manage.py test
```

**FastAPI**:
```bash
# Criar dados de exemplo
python create_sample_data.py

# Criar usuário admin
python create_admin_user.py

# Setup banco de dados
python setup_database.py

# Iniciar sistema completo
python start_system.py

# Testar deploy
python test_deploy.py
```

### Logs e Debug

**Django Logs**:
```bash
# Ver logs em tempo real
tail -f logs/django.log

# Produção (Render)
# Ver logs no dashboard do Render
```

**FastAPI Logs**:
```bash
# Backend logs aparecem no console
# Nível de log configurável via LOG_LEVEL

# Heroku
heroku logs --tail -a seu-app
```

---

## 🎓 GLOSSÁRIO

**IFC** (Industry Foundation Classes)
- Formato de arquivo padrão para BIM (Building Information Modeling)
- Contém geometria 3D e dados semânticos
- Extensão: `.ifc`

**ExpressID**
- Identificador único de elemento no arquivo IFC
- Usado como Location ID para vincular sensores

**GlobalID**
- GUID (Globally Unique Identifier) de elemento IFC
- Permanece consistente entre versões do arquivo

**Spatial Structure**
- Hierarquia espacial: Projeto → Site → Edifício → Andar → Espaço

**IfcSpace**
- Elemento IFC representando espaço/sala
- Contém área, volume, coordenadas

**Digital Twin**
- Representação digital de ativo físico
- Combina modelo 3D com dados em tempo real

**IoT** (Internet of Things)
- Rede de sensores e dispositivos conectados
- Coleta dados do mundo físico

**JWT** (JSON Web Token)
- Formato de token para autenticação
- Contém claims codificados

**REST API**
- Interface de programação baseada em HTTP
- Usa métodos GET, POST, PUT, DELETE

**Cache**
- Armazenamento temporário para performance
- Evita reprocessamento de dados

**Webhook**
- Callback HTTP para notificações
- Permite integração em tempo real

---

## ✅ CHECKLIST DE INÍCIO RÁPIDO

### Para Administradores

**Setup Inicial (Django)**:
- [ ] Alterar senha do admin
- [ ] Configurar SECRET_KEY em produção
- [ ] Configurar DEBUG=False
- [ ] Setup PostgreSQL (produção)
- [ ] Executar migrations
- [ ] Criar tabela de cache
- [ ] Upload de planta IFC
- [ ] Cadastrar sensores
- [ ] Configurar alertas

**Setup Inicial (FastAPI)**:
- [ ] Alterar senhas padrão
- [ ] Configurar SECRET_KEY
- [ ] Setup banco de dados
- [ ] Criar usuários
- [ ] Configurar localizações
- [ ] Cadastrar sensores
- [ ] Upload arquivos IFC
- [ ] Testar alertas

### Para Usuários

**Primeiro Acesso**:
- [ ] Fazer login com credenciais fornecidas
- [ ] Alterar senha no primeiro acesso
- [ ] Explorar dashboard
- [ ] Entender hierarquia de localizações
- [ ] Ver sensores disponíveis
- [ ] Entender níveis de alerta

**Uso Diário**:
- [ ] Verificar dashboard 2x/dia
- [ ] Revisar alertas ativos
- [ ] Reconhecer/resolver alertas
- [ ] Verificar sensores sem dados
- [ ] Documentar ações tomadas

---

## 📈 PRÓXIMOS PASSOS E MELHORIAS FUTURAS

### Planejado para Sistema Django

- [ ] WebSocket para dados em tempo real
- [ ] Visualizador 2D de planta baixa
- [ ] Relatórios PDF automáticos
- [ ] Integração com sistemas externos
- [ ] Machine learning para alertas preditivos
- [ ] App mobile (iOS/Android)
- [ ] Suporte a múltiplos arquivos IFC
- [ ] Controle de versões de plantas

### Planejado para Sistema FastAPI

- [ ] Conexões WebSocket em tempo real
- [ ] Visualização avançada de dados
- [ ] Aplicativo móvel nativo
- [ ] ML para alertas preditivos
- [ ] Integração com redes de sensores
- [ ] Visualização 3D avançada de IFC
- [ ] Suporte multi-tenant
- [ ] Relatórios e análises avançadas

---

## 📝 NOTAS FINAIS

Este guia cobre todas as funcionalidades principais dos dois sistemas IFC Monitoring disponíveis. Para dúvidas específicas ou suporte técnico:

1. **Consulte a documentação técnica** em `/docs/`
2. **Verifique os logs** para diagnosticar problemas
3. **Use a API interativa** (`/docs`) para testar endpoints
4. **Consulte o código-fonte** para entendimento profundo

**Lembre-se**:
- 🔐 Segurança primeiro - altere credenciais padrão!
- 💾 Faça backups regulares em produção
- 📊 Monitore performance e uso de recursos
- 📝 Documente configurações e procedimentos
- 🧪 Teste mudanças em desenvolvimento primeiro

---

**Versão**: 1.0  
**Data**: Outubro 2025  
**Autor**: Sistema IFC Monitoring  
**Licença**: MIT

---

🏭 **IFC Digital Twin - Construindo o Futuro da Indústria 4.0**

