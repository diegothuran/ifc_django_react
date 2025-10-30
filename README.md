# IFC Digital Twin - Monitoring System

Sistema de monitoramento industrial com visualização 3D de plantas IFC e gestão de sensores em tempo real.

## 🌟 VERSÃO 2.3.0 "Twinzo Features" (Outubro 2024)

**🎉 TRANSFORMAÇÃO EM DIGITAL TWIN COMPLETO!**

Esta versão marca a evolução do sistema para uma **plataforma completa de Digital Twin** inspirada no [Twinzo](https://twinzo.eu/), implementando recursos avançados de visualização, análise temporal e mapas de calor.

### ✨ Principais Recursos Novos:

- 🏗️ **Dashboard Redesenhado**: Visualização 3D central (70% da tela) estilo cockpit profissional
- 📍 **Overlay de Sensores IoT**: Marcadores 3D coloridos sobre a planta em tempo real
- 🔥 **Sistema de Heatmaps**: Visualize atividade, temperatura, pressão e fluxo por área
- ⏱️ **Timeline Temporal**: Navegue no histórico com controles play/pause/slider
- 🔗 **Integração Completa**: Timeline, heatmap e sensores sincronizados
- 📊 **60% das funcionalidades do Twinzo implementadas!**

**📖 Documentação Completa:**
- 🌟 [**Recursos Twinzo v2.3.0**](docs/TWINZO_FEATURES_V2.3.md) - Guia completo de funcionalidades
- 📝 [**Changelog v2.3.0**](CHANGELOG_v2.3.0.md) - Todas as mudanças desta versão
- 🎉 [**Melhorias v2.2.0**](docs/MELHORIAS_IMPLEMENTADAS_2024.md) - Segurança e performance
- 🚀 [**Deploy no Render**](docs/RENDER_DEPLOY_V2.2.md) - Guia completo de deployment

---

## 🚀 Deploy Rápido no Render (v2.3.0)

### Pré-requisitos
- Conta no [Render](https://render.com/)
- Repositório no GitHub
- **NOVO:** SECRET_KEY será gerada automaticamente

### Deploy em 3 passos

1. **Push para GitHub**
```bash
git add .
git commit -m "Deploy v2.3.0 Twinzo Features para Render"
git push origin master
```

2. **Criar no Render**
- Dashboard → New + → Blueprint
- Conectar repositório
- O `render.yaml` configurará tudo automaticamente
- **Aguarde** a geração automática do SECRET_KEY

3. **Aguardar build** (5-10 min)

**Pronto!** Aplicação estará em: `https://digital-twin-django.onrender.com`

### 🆕 Endpoints Principais v2.3.0
- **Dashboard Digital Twin**: `/core/` - Dashboard com visualização 3D, sensores e heatmaps
- **API Docs**: `/api/docs/` - Documentação Swagger completa
- **Heatmap API**: `/dashboard/api/heatmap/` - Dados de mapas de calor
- **Health Check**: `/core/health/` - Status do sistema
- **Admin**: `/admin/` - Painel administrativo

### ⚙️ Configurações Opcionais (Recomendadas)
- **Redis**: Para cache e Celery → Adicione no Render
- **Sentry**: Para monitoramento de erros → Configure SENTRY_DSN
- **Celery Workers**: Para tarefas assíncronas → Background Workers no Render

📖 **Guia completo**: [docs/RENDER_DEPLOY_V2.2.md](docs/RENDER_DEPLOY_V2.2.md)

---

## 🔧 Desenvolvimento Local

### Instalação

```bash
# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Configurar banco de dados
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
```

### Acessar

- **Admin**: http://localhost:8000/admin/
- **Dashboard**: http://localhost:8000/dashboard/
- **API**: http://localhost:8000/api/

---

## 📦 Estrutura do Projeto

```
ifc_django_project/
├── core/              # App principal (usuários, autenticação)
├── plant_viewer/      # Visualização 3D de plantas IFC
├── sensor_management/ # Gestão de sensores e dados
├── dashboard/         # Dashboard público
├── ifc_monitoring/    # Configurações Django
├── static/            # Arquivos estáticos
├── docs/              # Documentação detalhada
├── build.sh           # Script de build (Render)
├── start_simple.sh    # Script de inicialização (Render)
├── render.yaml        # Configuração Render
└── requirements.txt   # Dependências Python
```

---

## 🗄️ Banco de Dados

- **Desenvolvimento**: SQLite (automático)
- **Produção**: PostgreSQL (configurado via `DATABASE_URL`)

O projeto usa o banco `ifc-database` compartilhado (configurado no Render).

---

## ⚙️ Variáveis de Ambiente

Criar arquivo `.env` (ver `env.example`):

```bash
SECRET_KEY=sua-chave-secreta
DEBUG=True
DATABASE_URL=postgresql://user:pass@host/db  # Produção
```

---

## 📚 Tecnologias

- **Backend**: Django 5.2.7
- **Database**: PostgreSQL / SQLite
- **Server**: Gunicorn + WhiteNoise
- **Admin**: Django Unfold
- **API**: Django REST Framework
- **3D Viewer**: IFCOpenShell

---

## 🔐 Acesso Pós-Deploy

**Admin padrão** (⚠️ trocar senha!):
- Usuário: `admin`
- Senha: `admin123`

---

## 📖 Documentação Completa

Consulte a pasta `docs/` para:
- Estrutura do projeto
- Guia de deploy detalhado
- API reference

---

## 💰 Custos Render

- **Free**: $0/mês (90 dias)
- **Starter**: $7/mês (Web) + $7/mês (DB) = $14/mês

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Add: MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto está sob a licença MIT.

---

## 📞 Suporte

Para dúvidas e suporte, consulte a documentação em `docs/` ou abra uma issue.
