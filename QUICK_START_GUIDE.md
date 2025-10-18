# ⚡ GUIA RÁPIDO - IFC DIGITAL TWIN

> **5 minutos para começar a usar!**

---

## 🚀 INÍCIO RÁPIDO

### Passo 1: Iniciar Sistema (30 segundos)

```bash
# Navegar para o projeto
cd ifc_django_project

# Iniciar servidor
python manage.py runserver
```

### Passo 2: Acessar (10 segundos)

Abra no navegador: **http://localhost:8000**

---

## 🎯 3 FUNCIONALIDADES PRINCIPAIS

### 1️⃣ VISUALIZADOR 3D

**Acesso**: http://localhost:8000/plant/

**Controles Essenciais**:
- 🖱️ **Rotacionar**: Botão esquerdo + arrastar
- 🔍 **Zoom**: Scroll do mouse
- 🖱️ **Pan**: Botão direito + arrastar
- 👆 **Selecionar**: Click em elemento

**Atalhos**:
```
R = Reset visualização
W = Wireframe on/off
O = Perspectiva/Ortográfica
ESC = Desselecionar
```

---

### 2️⃣ PAINEL ADMIN

**Acesso**: http://localhost:8000/admin/

**Login**:
- Usuário: `admin`
- Senha: `admin123`

**O que fazer**:

#### Upload de Planta IFC
```
Admin → Plantas → ADICIONAR
├── Nome: "Minha Planta"
├── Arquivo: planta.ifc
└── Ativo: ✅
```

#### Cadastrar Sensor
```
Admin → Sensores → ADICIONAR
├── Nome: "Sensor Linha 1"
├── Tipo: Contador
├── IP: 192.168.1.100
├── Porta: 80
└── Location ID: 12345
```

---

### 3️⃣ API REST

**Base URL**: http://localhost:8000/plant-viewer/api/

**Endpoints Essenciais**:

```bash
# Listar plantas
curl http://localhost:8000/plant-viewer/api/plants/

# Metadados IFC
curl http://localhost:8000/plant-viewer/api/plants/1/metadata/

# Estatísticas
curl http://localhost:8000/plant-viewer/api/plants/1/statistics/

# Buscar elementos
curl "http://localhost:8000/plant-viewer/api/plants/1/search/?q=wall"

# Espaços com coordenadas
curl http://localhost:8000/plant-viewer/api/plants/1/spaces/
```

---

## 📊 DASHBOARDS

### Dashboard Público
**URL**: http://localhost:8000/dashboard/

**Mostra**:
- ✅ Planta 3D
- ✅ Sensores online
- ✅ Alertas críticos
- ✅ Dados última hora

### Dashboard Admin
**URL**: http://localhost:8000/admin/ (após login)

**Mostra**:
- 📊 Estatísticas 24h
- 📈 Gráficos por hora
- 🔝 Top 5 sensores
- ⚠️ Problemas detectados

---

## 🎨 RECURSOS DO VISUALIZADOR 3D

### Painel de Propriedades

Quando você clica em um elemento, vê:

```
╔══════════════════════════╗
║ PROPRIEDADES             ║
╠══════════════════════════╣
║ Nome: Wall_001           ║
║ Tipo: IfcWall            ║
║ GlobalID: 2a3b4c5d...    ║
║ Altura: 3.00 m           ║
║ Espessura: 0.20 m        ║
║ Material: Concreto       ║
╚══════════════════════════╝
```

### Modos de Visualização

```
[Sólido]     ◉  Visualização completa com materiais
[Wireframe]  ○  Apenas bordas (press W)
[Perspectiva] ◉  Visão realista
[Ortográfica] ○  Visão técnica (press O)
```

---

## 🔌 INTEGRAÇÃO COM SENSORES

### Como Vincular Sensor ao Modelo 3D

**Passo 1**: Obter Location ID
```
1. Abra planta no visualizador
2. Clique no elemento desejado
3. Copie o ExpressID ou GlobalID
```

**Passo 2**: Cadastrar Sensor
```
Admin → Sensores → ADICIONAR
├── Nome: "Sensor Temperatura Sala 101"
├── Location ID: [Cole o ID copiado]
└── Salvar
```

**Passo 3**: Ver no Dashboard
```
Dashboard → Verá sensor no elemento 3D!
```

---

## 📱 ACESSO RÁPIDO

### URLs Importantes

| Recurso | URL |
|---------|-----|
| 🏠 Home | http://localhost:8000 |
| 🎨 Visualizador 3D | http://localhost:8000/plant/ |
| 👨‍💼 Admin | http://localhost:8000/admin/ |
| 📊 Dashboard | http://localhost:8000/dashboard/ |
| 🔌 API | http://localhost:8000/plant-viewer/api/ |
| 📡 Sensores | http://localhost:8000/sensors/dashboard/ |

### Estrutura de Navegação

```
Navbar (Topo)
├── Home
├── Visualizador 3D
├── Plantas
│   ├── Lista
│   └── Detalhes
├── Sensores
│   ├── Lista
│   ├── Dashboard
│   └── Dados
└── Admin
    ├── Plantas
    ├── Sensores
    ├── Dados
    └── Alertas
```

---

## 🎯 CASOS DE USO COMUNS

### 1. Ver Planta em 3D
```
1. Acesse /plant/
2. Aguarde carregamento
3. Rotacione com mouse
4. Clique em elementos para propriedades
```

### 2. Adicionar Nova Planta
```
1. Login em /admin/
2. Plantas → ADICIONAR
3. Upload arquivo .ifc
4. Salvar
5. Ver em /plant/
```

### 3. Monitorar Sensores
```
1. Acesse /sensors/dashboard/
2. Veja status de todos sensores
3. Clique em sensor para detalhes
4. Veja gráficos e histórico
```

### 4. Verificar Alertas
```
1. Login em /admin/
2. Alertas do Sensor
3. Filtrar por nível/status
4. Marcar como resolvido
```

### 5. Buscar Elemento IFC
```
# Via API
curl "http://localhost:8000/plant-viewer/api/plants/1/search/?q=door"

# Retorna todos os elementos com "door" no nome
```

---

## 📊 ESTRUTURA DA API

### Hierarquia de Endpoints

```
/plant-viewer/api/
├── plants/                    # Lista de plantas
│   ├── {id}/                  # Detalhes da planta
│   ├── {id}/metadata/         # Metadados IFC
│   ├── {id}/elements/         # Elementos por tipo
│   ├── {id}/element/{eid}/    # Propriedades elemento
│   ├── {id}/statistics/       # Estatísticas
│   ├── {id}/spatial_structure/ # Hierarquia
│   ├── {id}/bounds/           # Bounding box
│   ├── {id}/search/           # Buscar elementos
│   └── {id}/spaces/           # Espaços com coordenadas
```

### Exemplo de Resposta

**GET /plants/1/statistics/**
```json
{
  "total_elements": 1234,
  "elements_by_type": {
    "IfcWall": 156,
    "IfcSlab": 48,
    "IfcColumn": 89,
    "IfcDoor": 42,
    "IfcWindow": 78
  },
  "floor_count": 3,
  "space_count": 45,
  "model_dimensions": {
    "width": 45.5,
    "height": 12.0,
    "depth": 28.3
  }
}
```

---

## 🔐 SEGURANÇA

### Alterar Senha Admin

```bash
# Via manage.py
python manage.py changepassword admin

# Digite nova senha 2x
```

### Configurar Produção

```python
# settings.py
DEBUG = False
SECRET_KEY = 'sua-chave-super-segura-aqui'
ALLOWED_HOSTS = ['seu-dominio.com']
```

---

## 🐛 PROBLEMAS COMUNS

### Visualizador não carrega

**Sintoma**: Tela branca ou loading infinito

**Solução**:
```bash
# Limpar cache
python manage.py createcachetable

# Force refresh metadados
curl -X POST http://localhost:8000/plant-viewer/api/plants/1/refresh_metadata/
```

### Arquivo estático não carrega

**Solução**:
```bash
# Coletar estáticos
python manage.py collectstatic --noinput

# Verificar STATIC_ROOT
python manage.py findstatic js/ifc_viewer.js
```

### Sensor não aparece

**Solução**:
1. Verifique se sensor está ativo
2. Verifique Location ID correto
3. Adicione dados de teste
4. Recarregue dashboard

---

## 💡 DICAS PRO

### Performance

```python
# Usar cache para metadados (já configurado)
# Cache dura 7 dias
# Força refresh apenas quando necessário
```

### Navegação 3D

```
💡 Perdido? Pressione R para resetar
💡 Modelo muito denso? Use Wireframe (W)
💡 Medidas precisas? Use Ortográfica (O)
💡 Comparar elementos? Click + ESC rápido
```

### API

```bash
# Use jq para formatar JSON
curl http://localhost:8000/plant-viewer/api/plants/1/statistics/ | jq

# Salvar resposta
curl http://localhost:8000/plant-viewer/api/plants/1/metadata/ > metadata.json

# Headers customizados
curl -H "Accept: application/json" http://localhost:8000/plant-viewer/api/plants/
```

---

## 📚 RECURSOS ADICIONAIS

### Documentação Completa

- **GUIA_DO_USUARIO.md** - Manual completo (180+ páginas)
- **README.md** - Visão geral técnica
- **docs/QUICK_START_RENDER.md** - Deploy em produção
- **docs/MELHORIAS_APLICADAS.md** - Changelog

### Comandos Úteis

```bash
# Criar superusuário
python manage.py createsuperuser

# Migrations
python manage.py migrate

# Shell interativo
python manage.py shell

# Testes
python manage.py test
```

---

## ⚡ ATALHOS DO TECLADO

### Visualizador 3D

| Tecla | Ação |
|-------|------|
| `R` | Reset câmera |
| `W` | Toggle wireframe |
| `O` | Toggle perspectiva/ortográfica |
| `ESC` | Desselecionar elemento |
| `+` | Zoom in |
| `-` | Zoom out |

### Admin Django

| Tecla | Ação |
|-------|------|
| `Alt+S` | Salvar |
| `Alt+A` | Salvar e adicionar outro |
| `Alt+C` | Salvar e continuar editando |
| `/` | Buscar |

---

## 🎓 GLOSSÁRIO RÁPIDO

**IFC**: Formato de arquivo BIM (Industry Foundation Classes)  
**ExpressID**: ID numérico único do elemento no IFC  
**GlobalID**: GUID único do elemento (persistente)  
**IfcSpace**: Elemento que representa sala/espaço  
**Location ID**: ID usado para vincular sensor ao modelo 3D  
**Bounding Box**: Limites (min/max) do modelo 3D

---

## ✅ CHECKLIST INICIAL

- [ ] Alterar senha do admin
- [ ] Fazer upload de uma planta IFC
- [ ] Ver planta no visualizador 3D
- [ ] Cadastrar um sensor
- [ ] Verificar dashboard
- [ ] Testar API REST
- [ ] Explorar Admin
- [ ] Ler documentação completa

---

## 🚀 PRÓXIMOS PASSOS

1. ✅ **Ler este guia** (você está aqui!)
2. 📖 **Explorar GUIA_DO_USUARIO.md** para detalhes
3. 🏗️ **Upload sua primeira planta IFC**
4. 📡 **Cadastrar sensores reais**
5. 📊 **Configurar alertas**
6. 🔐 **Configurar segurança**
7. 🚀 **Deploy em produção**

---

**Tempo estimado para dominar**: 2-4 horas  
**Dificuldade**: ⭐⭐☆☆☆ (Fácil)

---

🏭 **Visualize o Futuro Industrial em 3D!**

---

**Dúvidas?** Consulte **GUIA_DO_USUARIO.md** para documentação completa.

