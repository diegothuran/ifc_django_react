# Guia de Instalação das Melhorias - IFC Monitoring System

**Versão:** 3.0.0  
**Data:** 18 de Outubro de 2025

---

## 📋 Pré-requisitos

- Python 3.11+
- Node.js 18+ e npm
- Django 5.2.7
- PostgreSQL (recomendado) ou SQLite

---

## 🚀 Instalação Passo a Passo

### Passo 1: Instalar Dependências do Frontend

```bash
# Navegar para o diretório frontend
cd /caminho/para/ifc_django_project/frontend

# Instalar dependências npm
npm install

# Verificar instalação
npm list vue vite
```

**Saída esperada:**
```
ifc-monitoring-frontend@1.0.0
├── vue@3.4.0
└── vite@5.0.0
```

---

### Passo 2: Build do Frontend

```bash
# Ainda no diretório frontend

# Para desenvolvimento (com watch - recompila automaticamente)
npm run watch

# OU para produção (build otimizado)
npm run build
```

**Resultado:**
- Arquivos compilados serão gerados em `static/dist/`
- Manifest gerado em `static/dist/manifest.json`

---

### Passo 3: Instalar Dependências do Backend

```bash
# Voltar para o diretório raiz do projeto
cd /caminho/para/ifc_django_project

# Ativar ambiente virtual (se estiver usando)
source venv/bin/activate  # Linux/Mac
# OU
venv\Scripts\activate  # Windows

# Instalar Django Channels e dependências
pip install channels==4.0.0
pip install channels-redis==4.1.0
pip install daphne==4.0.0

# Atualizar requirements.txt
pip freeze > requirements.txt
```

---

### Passo 4: Atualizar Settings do Django

Editar `ifc_monitoring/settings.py`:

```python
# Adicionar 'channels' ao INSTALLED_APPS
INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Terceiros
    'rest_framework',
    'channels',  # ← ADICIONAR AQUI

    # Meus aplicativos
    'core',
    'plant_viewer',
    'sensor_management',
    'dashboard',
]

# Adicionar configuração do ASGI
ASGI_APPLICATION = 'ifc_monitoring.asgi.application'

# Configurar Channel Layers
CHANNEL_LAYERS = {
    'default': {
        # Para desenvolvimento (em memória)
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
        
        # Para produção (com Redis)
        # 'BACKEND': 'channels_redis.core.RedisChannelLayer',
        # 'CONFIG': {
        #     'hosts': [('127.0.0.1', 6379)],
        # },
    }
}
```

---

### Passo 5: Atualizar ASGI Configuration

Editar `ifc_monitoring/asgi.py`:

```python
"""
ASGI config for ifc_monitoring project.
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from core.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ifc_monitoring.settings')

# Inicializar Django ASGI application
django_asgi_app = get_asgi_application()

# Configurar ProtocolTypeRouter
application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
```

---

### Passo 6: Atualizar URLs

Editar `core/urls.py`:

```python
from django.urls import path
from .views_improved import unified_dashboard, login_view, logout_view

app_name = 'core'

urlpatterns = [
    # Dashboard unificado (nova rota principal)
    path('dashboard/', unified_dashboard, name='unified_dashboard'),
    path('', unified_dashboard, name='home'),  # Redirecionar home para dashboard
    
    # Autenticação
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
```

---

### Passo 7: Coletar Arquivos Estáticos

```bash
# Coletar todos os arquivos estáticos (incluindo os compilados do Vue)
python manage.py collectstatic --noinput
```

**Verificar:**
- Arquivos devem estar em `staticfiles/dist/`

---

### Passo 8: Executar Migrações (se necessário)

```bash
# Verificar se há migrações pendentes
python manage.py showmigrations

# Executar migrações
python manage.py migrate
```

---

### Passo 9: Executar o Servidor

```bash
# Opção 1: Usar Daphne (recomendado para WebSockets)
daphne -b 0.0.0.0 -p 8000 ifc_monitoring.asgi:application

# Opção 2: Usar runserver (Django 3.0+ suporta ASGI)
python manage.py runserver

# Opção 3: Para produção (Gunicorn + Daphne)
# Ver seção "Deploy em Produção" abaixo
```

---

### Passo 10: Testar a Aplicação

1. **Acessar Dashboard Unificado:**
   - URL: http://localhost:8000/dashboard/
   - Login com credenciais de admin

2. **Testar Busca Global:**
   - Pressionar `Ctrl+K` (ou `Cmd+K` no Mac)
   - Digitar para buscar

3. **Testar WebSocket:**
   - Abrir console do navegador (F12)
   - Verificar mensagem: "WebSocket conectado"

4. **Testar Notificações:**
   - Criar um alerta no admin
   - Verificar se notificação aparece automaticamente

---

## 🔧 Troubleshooting

### Problema: "Module 'channels' not found"

**Solução:**
```bash
pip install channels channels-redis daphne
```

---

### Problema: "Manifest file not found"

**Solução:**
```bash
cd frontend
npm run build
cd ..
python manage.py collectstatic --noinput
```

---

### Problema: WebSocket não conecta

**Verificar:**
1. Servidor rodando com Daphne ou ASGI support
2. `CHANNEL_LAYERS` configurado em settings
3. `core/routing.py` existe e está correto
4. Console do navegador para erros

**Solução temporária:**
- Comentar código WebSocket em `UnifiedDashboard.vue` se não for crítico

---

### Problema: Estilos não carregam

**Verificar:**
1. `design-tokens.css` e `components.css` em `static/css/`
2. Arquivos coletados com `collectstatic`
3. Template carrega os arquivos CSS

**Solução:**
```bash
python manage.py collectstatic --noinput --clear
```

---

### Problema: Vue.js não monta

**Verificar:**
1. Console do navegador para erros
2. `window.DASHBOARD_INITIAL_DATA` definido no template
3. Bundle JavaScript carregado corretamente

**Debug:**
```html
<!-- Adicionar no template -->
<script>
console.log('Initial Data:', window.DASHBOARD_INITIAL_DATA);
</script>
```

---

## 🚀 Deploy em Produção

### Opção 1: Render.com (Recomendado)

**1. Atualizar `build.sh`:**
```bash
#!/usr/bin/env bash
set -o errexit

# Instalar dependências Python
pip install -r requirements.txt

# Instalar Node.js e dependências frontend
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm install 18
nvm use 18

cd frontend
npm install
npm run build
cd ..

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Executar migrações
python manage.py migrate
```

**2. Atualizar `render.yaml`:**
```yaml
services:
  - type: web
    name: ifc-django
    env: python
    buildCommand: bash build.sh
    startCommand: daphne -b 0.0.0.0 -p $PORT ifc_monitoring.asgi:application
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.10
      - key: DEBUG
        value: False
```

**3. Adicionar Redis (para WebSockets em produção):**
```yaml
  - type: redis
    name: ifc-redis
    ipAllowList: []
```

**4. Atualizar settings para produção:**
```python
# settings.py
import os

if not DEBUG:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
            },
        }
    }
```

---

### Opção 2: VPS/Servidor Próprio

**1. Instalar Nginx:**
```bash
sudo apt update
sudo apt install nginx
```

**2. Configurar Nginx:**
```nginx
# /etc/nginx/sites-available/ifc-monitoring

upstream django {
    server 127.0.0.1:8000;
}

upstream daphne {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name seu-dominio.com;

    location /static/ {
        alias /caminho/para/ifc_django_project/staticfiles/;
    }

    location /media/ {
        alias /caminho/para/ifc_django_project/media/;
    }

    location /ws/ {
        proxy_pass http://daphne;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**3. Criar serviços systemd:**

```ini
# /etc/systemd/system/ifc-django.service
[Unit]
Description=IFC Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/caminho/para/ifc_django_project
ExecStart=/caminho/para/venv/bin/gunicorn ifc_monitoring.wsgi:application --bind 127.0.0.1:8000

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/ifc-daphne.service
[Unit]
Description=IFC Daphne WebSocket Server
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/caminho/para/ifc_django_project
ExecStart=/caminho/para/venv/bin/daphne -b 127.0.0.1 -p 8001 ifc_monitoring.asgi:application

[Install]
WantedBy=multi-user.target
```

**4. Ativar e iniciar serviços:**
```bash
sudo systemctl enable ifc-django ifc-daphne nginx
sudo systemctl start ifc-django ifc-daphne nginx
```

---

## 📊 Verificação Pós-Instalação

### Checklist:

- [ ] Frontend compilado (`static/dist/` existe)
- [ ] Arquivos estáticos coletados
- [ ] Django Channels instalado
- [ ] ASGI configurado
- [ ] URLs atualizadas
- [ ] Servidor rodando
- [ ] Dashboard unificado acessível
- [ ] Busca global funciona (Ctrl+K)
- [ ] WebSocket conecta (verificar console)
- [ ] Notificações aparecem
- [ ] Estilos carregam corretamente
- [ ] Responsivo em mobile

---

## 📚 Recursos Adicionais

- **Documentação Django Channels:** https://channels.readthedocs.io/
- **Documentação Vue.js 3:** https://vuejs.org/
- **Documentação Vite:** https://vitejs.dev/
- **WCAG 2.1 Guidelines:** https://www.w3.org/WAI/WCAG21/quickref/

---

## 🆘 Suporte

Se encontrar problemas durante a instalação:

1. Verificar logs do servidor
2. Verificar console do navegador (F12)
3. Consultar seção Troubleshooting acima
4. Revisar `MELHORIAS_IMPLEMENTADAS.md` para detalhes técnicos

---

## 🎉 Conclusão

Após seguir todos os passos, você terá:

✅ Dashboard moderno e unificado  
✅ Sistema de notificações em tempo real  
✅ Busca global funcional  
✅ WebSockets configurados  
✅ Design System consistente  
✅ Acessibilidade WCAG 2.1 AA  

**Parabéns! Seu sistema IFC Monitoring está modernizado! 🚀**

