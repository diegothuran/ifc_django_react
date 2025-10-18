# 📁 Estrutura do Projeto

## Visão Geral

```
ifc_django_project/
├── 📦 Apps Django
│   ├── core/                    # App principal
│   ├── plant_viewer/            # Visualizador IFC
│   ├── sensor_management/       # Gestão de sensores
│   └── dashboard/               # Dashboard de monitoramento
│
├── ⚙️ Configuração
│   ├── ifc_monitoring/          # Settings do Django
│   ├── requirements.txt         # Dependências Python
│   ├── runtime.txt             # Versão do Python
│   └── build.sh                # Script de build (Render)
│
├── 🎨 Frontend
│   ├── static/                 # Arquivos estáticos
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── staticfiles/            # Coletados (produção)
│
├── 📚 Documentação
│   ├── docs/                   # Documentação atual
│   │   ├── QUICK_START_RENDER.md
│   │   ├── DEPLOY_CORRIGIDO.md
│   │   ├── MELHORIAS_APLICADAS.md
│   │   ├── FIX_STATIC_FILES_RENDER.md
│   │   └── archive/            # Histórico
│   └── README.md               # Este arquivo
│
└── 🗄️ Banco de Dados
    ├── db.sqlite3              # Desenvolvimento
    └── migrations/             # Migrações Django
```

---

## 📦 Apps Django

### core/
**App principal do sistema**

```
core/
├── management/commands/         # Comandos customizados
│   ├── auto_setup_render.py   # Setup automático
│   ├── create_admin.py         # Criar admin
│   └── setup_initial_data.py  # Dados iniciais
├── templates/                  # Templates HTML
│   └── core/
│       ├── base.html          # Template base
│       ├── dashboard.html     # Dashboard principal
│       └── login.html         # Página de login
├── models.py                   # Modelos de dados
├── views.py                    # Views
└── urls.py                     # URLs
```

### plant_viewer/
**Visualizador IFC e API REST**

```
plant_viewer/
├── management/commands/
│   ├── cleanup_missing_files.py
│   └── convert_ifc_to_gltf.py
├── templates/plant_viewer/
│   ├── main_plant_view.html   # Visualizador 3D
│   ├── plant_list.html        # Lista de plantas
│   └── plant_detail.html      # Detalhes da planta
├── migrations/
│   ├── 0001_initial.py
│   ├── 0002_alter_buildingplan_ifc_file_and_more.py
│   └── 0003_buildingplan_metadata.py  # ⭐ Novo
├── ifc_processor.py            # ⭐ Processador IFC
├── serializers.py              # ⭐ API Serializers
├── models.py                   # Modelo BuildingPlan
├── views.py                    # Views + ViewSet
└── urls.py                     # URLs + API Router
```

**Arquivos Principais:**
- `ifc_processor.py` - Extração de metadados IFC
- `serializers.py` - 7 serializers para API REST
- `views.py` - BuildingPlanViewSet com 13+ endpoints

### sensor_management/
**Gestão de sensores**

```
sensor_management/
├── management/commands/
│   └── collect_sensor_data.py
├── migrations/
├── models.py                   # Sensor, SensorReading
├── views.py
└── urls.py
```

### dashboard/
**Dashboard de monitoramento**

```
dashboard/
├── templates/dashboard/
│   ├── admin_dashboard.html
│   └── public_dashboard.html
├── models.py
├── views.py
└── urls.py
```

---

## 🎨 Frontend

### static/
**Arquivos estáticos do projeto**

```
static/
├── css/
│   ├── custom.css              # Estilos customizados
│   └── main.css                # Estilos principais
├── js/
│   ├── custom.js               # Scripts customizados
│   ├── ifc_viewer.js           # ⭐ Visualizador 3D avançado
│   └── main.js                 # Scripts principais
└── images/                     # Imagens do projeto
```

**Arquivo Principal:**
- `ifc_viewer.js` - Classe `AdvancedIFCViewer` com 600+ linhas

### staticfiles/
**Arquivos coletados para produção**

```
staticfiles/
├── admin/                      # Django Admin estáticos
├── rest_framework/             # DRF estáticos
├── css/                        # CSS coletados
├── js/                         # JS coletados
└── images/                     # Imagens coletadas
```

**Gerado por:** `python manage.py collectstatic`

---

## ⚙️ Configuração

### ifc_monitoring/
**Configurações do Django**

```
ifc_monitoring/
├── settings.py                 # ⭐ Settings (cache PostgreSQL)
├── urls.py                     # URLs principais
├── wsgi.py                     # WSGI para produção
└── asgi.py                     # ASGI (futuro)
```

**settings.py principais mudanças:**
- Cache DatabaseCache (PostgreSQL)
- STATICFILES_STORAGE = WhiteNoise
- ALLOWED_HOSTS para Render

### Arquivos de Deploy

| Arquivo | Descrição |
|---------|-----------|
| `build.sh` | Script de build para Render |
| `start.sh` | Script de início (alternativo) |
| `Procfile` | Comandos para Heroku/Render |
| `runtime.txt` | Versão do Python (3.11.10) |
| `requirements.txt` | Dependências Python |
| `render.yaml` | Configuração Render |

---

## 📚 Documentação

### docs/
**Documentação atual do projeto**

| Arquivo | Descrição |
|---------|-----------|
| `QUICK_START_RENDER.md` | Deploy em 5 minutos |
| `DEPLOY_CORRIGIDO.md` | Solução de problemas |
| `MELHORIAS_APLICADAS.md` | Changelog v2.0 → v2.1 |
| `CONFIGURACAO_RENDER_SEM_REDIS.md` | Guia completo Render |
| `MELHORIAS_RENDERIZACAO_PLANTA.md` | Recomendações técnicas |
| `FIX_STATIC_FILES_RENDER.md` | Corrigir arquivos estáticos |
| `ESTRUTURA_PROJETO.md` | Este arquivo |

### docs/archive/
**Documentação histórica**

Documentos antigos do desenvolvimento inicial, mantidos para referência histórica.

---

## 🗄️ Banco de Dados

### Desenvolvimento (SQLite)
```
db.sqlite3
```

### Produção (PostgreSQL)
- Gerenciado pelo Render
- Variável: `DATABASE_URL`
- Tabelas:
  - Django default (auth, sessions, etc.)
  - plant_viewer_buildingplan
  - sensor_management_sensor
  - sensor_management_sensorreading
  - ifc_cache_table ⭐ (cache)

---

## 📦 Dependências Principais

### Backend
```txt
django==5.2.7
djangorestframework==3.14.0
gunicorn==21.2.0
psycopg[binary]==3.2.10
ifcopenshell>=0.8.0
whitenoise==6.5.0
```

### Processamento IFC
```txt
ifcopenshell>=0.8.0
lxml>=4.9.0
numpy>=1.24.0,<2.0.0
```

---

## 🔑 Arquivos Importantes

### Raiz do Projeto

| Arquivo | Tipo | Descrição |
|---------|------|-----------|
| `manage.py` | Python | Django management |
| `README.md` | Doc | Documentação principal |
| `requirements.txt` | Config | Dependências |
| `build.sh` | Shell | Build script |
| `env.example` | Config | Exemplo variáveis ambiente |
| `.gitignore` | Config | Ignorar arquivos Git |

### Logs
```
logs/
└── django.log              # Logs do Django
```

### Testes
```
test_database.py            # Teste de banco
test_static.html            # Teste de estáticos
verify_deploy.py            # Verificar deploy
```

---

## 🎯 Arquivos Criados nas Melhorias

### Novos Arquivos Python
- ✅ `plant_viewer/ifc_processor.py` (400+ linhas)
- ✅ `plant_viewer/serializers.py` (180+ linhas)
- ✅ `plant_viewer/migrations/0003_buildingplan_metadata.py`

### Novos Templates
- ✅ `plant_viewer/templates/plant_viewer/plant_list.html`
- ✅ `plant_viewer/templates/plant_viewer/plant_detail.html`
- ✅ `plant_viewer/templates/plant_viewer/main_plant_view.html` (reescrito)

### Novos Scripts JavaScript
- ✅ `static/js/ifc_viewer.js` (600+ linhas)

### Nova Documentação
- ✅ `docs/` - Pasta organizada
- ✅ `docs/archive/` - Documentação histórica
- ✅ 7 novos guias em `docs/`

---

## 📊 Estatísticas

### Código
- **Total de linhas:** ~15,000+
- **Apps Django:** 4
- **Modelos:** 8+
- **Views:** 20+
- **Templates:** 15+
- **API Endpoints:** 13+

### Documentação
- **Guias atuais:** 7
- **Documentos históricos:** 15
- **README atualizado:** ✅

### Melhorias v2.0 → v2.1
- **Linhas adicionadas:** ~2,500
- **Arquivos criados:** 10
- **Arquivos modificados:** 5
- **Documentos criados:** 7

---

## 🚀 Como Usar Esta Estrutura

### Para Desenvolvimento
1. Apps em `core/`, `plant_viewer/`, etc.
2. Static em `static/`
3. Templates em cada app

### Para Deploy
1. Build: `bash build.sh`
2. Static: `staticfiles/`
3. Config: `settings.py`

### Para Documentação
1. Guias atuais: `docs/`
2. Histórico: `docs/archive/`
3. README principal: `README.md`

---

*Última atualização: Outubro 2025*
*Versão: 2.1*

