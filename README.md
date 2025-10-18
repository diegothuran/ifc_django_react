# 🏭 IFC Digital Twin - Sistema de Monitoramento Industrial

Sistema completo de visualização 3D e monitoramento de plantas industriais usando arquivos IFC (Industry Foundation Classes).

[![Deploy Status](https://img.shields.io/badge/deploy-render-success)](https://ifc-django.onrender.com)
[![Python](https://img.shields.io/badge/python-3.11.10-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.2.7-green)](https://www.djangoproject.com/)

---

## 🎯 Funcionalidades Principais

### 🏗️ Visualizador 3D de Plantas IFC
- **Renderização 3D** com Three.js e IFC.js
- **Seleção e Inspeção** de elementos
- **Controles Profissionais** (OrbitControls)
- **Wireframe e Projeções** ortográfica/perspectiva
- **Atalhos de Teclado** (R, W, O, ESC)

### 📊 Dashboard de Monitoramento
- **Planta Industrial Ativa** - Visualização central em destaque
- **Status dos Sensores** - Monitoramento em tempo real
- **Alertas Críticos** - Notificações e avisos
- **Estatísticas** - Métricas do sistema

### 🔌 API REST Completa
- **13+ endpoints** para gerenciamento de plantas
- Extração de metadados IFC
- Busca de elementos por nome/tipo
- Estatísticas do modelo
- Estrutura espacial hierárquica

### 📈 Sistema de Sensores
- Gestão de sensores IoT
- Coleta automática de dados
- Sistema de alertas configurável
- Dashboard administrativo avançado

---

## 🚀 Quick Start

### Desenvolvimento Local

```bash
# 1. Clonar repositório
git clone https://github.com/seu-usuario/ifc_django_project.git
cd ifc_django_project

# 2. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar banco de dados
python manage.py migrate
python manage.py createcachetable

# 5. Criar superusuário
python manage.py createsuperuser

# 6. Coletar arquivos estáticos
python manage.py collectstatic --noinput

# 7. Iniciar servidor
python manage.py runserver
```

**Acesse:** http://localhost:8000

**Login Padrão:**
- Usuário: `admin`
- Senha: `admin123`
- ⚠️ **Altere em produção!**

---

### Deploy no Render

1. **Criar Web Service**
   - Conectar repositório GitHub
   - Build Command: `bash build.sh`
   - Start Command: `gunicorn ifc_monitoring.wsgi:application`

2. **Adicionar PostgreSQL Database**

3. **Configurar Environment Variables:**
   ```
   DEBUG=False
   SECRET_KEY=<sua-chave-segura>
   PYTHON_VERSION=3.11.10
   ```

**Deploy ao vivo:** https://ifc-django.onrender.com

---

## 📁 Estrutura do Projeto

```
ifc_django_project/
├── core/                      # App principal
├── plant_viewer/              # Visualizador IFC
│   ├── ifc_processor.py      # Processamento IFC
│   ├── serializers.py        # API serializers
│   └── templates/            # Templates HTML
├── sensor_management/         # Gestão de sensores
├── dashboard/                 # Dashboard de monitoramento
├── static/
│   ├── js/
│   │   └── ifc_viewer.js     # Visualizador 3D avançado
│   └── css/                   # Estilos customizados
├── docs/                      # Documentação
│   ├── ESTRUTURA_PROJETO.md
│   └── QUICK_START_RENDER.md
├── requirements.txt           # Dependências Python
├── build.sh                   # Script de build (Render)
└── manage.py
```

---

## 🔌 API Endpoints

### Plantas IFC

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/plant-viewer/api/plants/` | Lista todas as plantas |
| GET | `/plant-viewer/api/plants/{id}/` | Detalhes da planta |
| GET | `/plant-viewer/api/plants/{id}/metadata/` | Metadados IFC completos |
| GET | `/plant-viewer/api/plants/{id}/elements/` | Elementos por tipo |
| GET | `/plant-viewer/api/plants/{id}/statistics/` | Estatísticas do modelo |
| GET | `/plant-viewer/api/plants/{id}/search/?q=nome` | Buscar elementos |

### Exemplo de Uso

```bash
# Listar plantas
curl https://ifc-django.onrender.com/plant-viewer/api/plants/

# Obter estatísticas
curl https://ifc-django.onrender.com/plant-viewer/api/plants/1/statistics/

# Buscar paredes
curl https://ifc-django.onrender.com/plant-viewer/api/plants/1/search/?q=wall
```

---

## 🎮 Controles do Visualizador 3D

### Mouse
- **Arrastar (Esquerdo)** → Rotacionar
- **Arrastar (Direito)** → Pan
- **Scroll** → Zoom
- **Click** → Selecionar elemento

### Teclado
- `R` → Resetar visualização
- `W` → Toggle wireframe
- `O` → Toggle perspectiva/ortográfica
- `ESC` → Desselecionar

---

## 🛠️ Tecnologias

### Backend
- **Django 5.2.7** - Framework web
- **Django REST Framework 3.14** - API REST
- **Django Unfold 0.44** - Interface admin moderna
- **IfcOpenShell 0.8+** - Processamento IFC
- **PostgreSQL** - Banco de dados
- **Gunicorn 21.2** - WSGI server
- **WhiteNoise 6.5** - Servir arquivos estáticos

### Frontend
- **Three.js** - Renderização 3D
- **IFC.js** - Visualização IFC
- **Bootstrap 5** - UI Framework
- **Font Awesome** - Ícones

### DevOps
- **Render** - Hospedagem cloud
- **PostgreSQL** - Cache de metadados

---

## 📊 Dashboard

O dashboard principal apresenta três áreas:

### Coluna Esquerda
- **Links Rápidos** (Visualizador 3D, Lista de Sensores, Admin)
- **Alertas Críticos** (notificações em tempo real)

### Coluna Central ⭐
- **Planta Industrial Ativa** (visualização em destaque)
- Card visual com ícone da indústria
- Informações detalhadas (nome, descrição, tamanho, status)
- Botão de acesso direto ao Visualizador 3D

### Coluna Direita
- **Status dos Sensores** (monitoramento em tempo real)
- Lista de sensores com status online/offline
- Últimas leituras e valores

---

## 📚 Documentação

### Guias Disponíveis
- 📘 [**QUICK_START_GUIDE.md**](QUICK_START_GUIDE.md) - Início rápido em 5 minutos
- 📗 [**GUIA_DO_USUARIO.md**](GUIA_DO_USUARIO.md) - Manual completo do usuário
- 📕 [**docs/ESTRUTURA_PROJETO.md**](docs/ESTRUTURA_PROJETO.md) - Arquitetura do sistema
- 📙 [**docs/QUICK_START_RENDER.md**](docs/QUICK_START_RENDER.md) - Deploy no Render

---

## 🧪 Testes

```bash
# Rodar testes
python manage.py test

# Verificar cache
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'ok')
>>> print(cache.get('test'))

# Testar processador IFC
python manage.py shell
>>> from plant_viewer.ifc_processor import IFCProcessor
>>> processor = IFCProcessor('path/to/file.ifc')
>>> processor.open()
>>> stats = processor.get_statistics()
```

---

## 🚨 Troubleshooting

### Build Falha no Render
```bash
# Verificar Build Command
Build Command: bash build.sh
Start Command: gunicorn ifc_monitoring.wsgi:application
```

### Arquivos Estáticos Não Carregam
```bash
# Executar manualmente
python manage.py collectstatic --noinput
```

### Cache Não Funciona
```bash
# Criar tabela de cache
python manage.py createcachetable
```

### Planta Não Aparece no Dashboard
1. Verifique se há plantas cadastradas no admin
2. Certifique-se de que pelo menos uma está ativa (checkbox marcado)
3. Verifique se o arquivo IFC foi uploaded corretamente
4. Veja os logs para mensagens de erro

---

## 🔐 Segurança

### Produção
- ✅ `DEBUG=False`
- ✅ `SECRET_KEY` segura
- ✅ HTTPS enforced
- ✅ CSRF protection
- ✅ Secure cookies
- ✅ ALLOWED_HOSTS configurado

### Desenvolvimento
- ⚠️ User padrão: `admin` / `admin123`
- ⚠️ **MUDE A SENHA EM PRODUÇÃO!**

---

## 💰 Custos (Render)

| Serviço | Plano | Custo/mês |
|---------|-------|-----------|
| Web Service | Starter | $7 |
| PostgreSQL | Starter | $7 |
| **Total** | | **$14/mês** |

**Free Tier:** $0/mês por 90 dias (depois expira)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## 📝 Changelog

### v2.2 (Outubro 2025) - Dashboard Reorganizado
- ✅ Planta ativa em destaque na coluna central
- ✅ Status dos sensores reorganizado
- ✅ Logs de debug adicionados
- ✅ Documentação consolidada e organizada

### v2.1 (Outubro 2025) - Render sem Redis
- ✅ Cache adaptado para PostgreSQL
- ✅ Removido dependência de Redis
- ✅ Economia de $5-10/mês

### v2.0 (Outubro 2025) - Melhorias IFC
- ✅ IFC.js v2.x atualizado
- ✅ OrbitControls profissionais
- ✅ API REST completa (13+ endpoints)
- ✅ Visualizador 3D avançado
- ✅ Django Unfold admin theme

---

## 📞 Suporte

- **Documentação:** [`docs/`](docs/)
- **Guia do Usuário:** [GUIA_DO_USUARIO.md](GUIA_DO_USUARIO.md)
- **Quick Start:** [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)

---

## 📜 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🙏 Agradecimentos

- [Django](https://www.djangoproject.com/)
- [Django Unfold](https://github.com/unfoldadmin/django-unfold)
- [IfcOpenShell](http://ifcopenshell.org/)
- [IFC.js](https://ifcjs.github.io/info/)
- [Three.js](https://threejs.org/)
- [Render](https://render.com/)

---

**🚀 Deploy:** https://ifc-django.onrender.com

---

*Desenvolvido com ❤️ para o futuro da construção digital*
