# IFC Digital Twin - Monitoring System

Sistema de monitoramento industrial com visualização 3D de plantas IFC e gestão de sensores em tempo real.

## 🚀 Deploy Rápido no Render

### Pré-requisitos
- Conta no [Render](https://render.com/)
- Repositório no GitHub

### Deploy em 3 passos

1. **Push para GitHub**
```bash
git add .
git commit -m "Deploy para Render"
git push origin master
```

2. **Criar no Render**
- Dashboard → New + → Blueprint
- Conectar repositório
- O `render.yaml` configurará tudo automaticamente

3. **Aguardar build** (5-10 min)

**Pronto!** Aplicação estará em: `https://digital-twin-django.onrender.com`

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
