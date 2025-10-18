# 🗄️ Configuração de Banco de Dados no Render

## 📋 Estratégia: Um Único Banco de Dados

No Render, você pode compartilhar um único banco de dados PostgreSQL entre múltiplos serviços web. Esta é a abordagem mais econômica e eficiente.

---

## 🏗️ Arquitetura Atual

```
┌─────────────────────────────────────────┐
│         PostgreSQL Database             │
│         Nome: ifc-database              │
│         Database: ifc_monitoring        │
│         User: ifc_user                  │
│         Plan: Free                      │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌───────────────┐   ┌───────────────┐
│  ifc-backend  │   │digital-twin   │
│   (FastAPI)   │   │   (Django)    │
│               │   │               │
└───────────────┘   └───────────────┘
```

---

## ⚙️ Configuração no render.yaml

### Opção 1: Usar Banco Existente (Recomendado)

Se você já tem o banco `ifc-database` criado no outro projeto:

```yaml
services:
  - type: web
    name: digital-twin-django
    runtime: python
    plan: free
    buildCommand: "chmod +x build.sh && ./build.sh"
    startCommand: "chmod +x start_simple.sh && ./start_simple.sh"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: ifc-database  # ← Mesmo nome do outro projeto
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      # ... outras variáveis

# ❌ NÃO INCLUIR seção databases: 
# O banco já existe no outro projeto!
```

### Opção 2: Criar Banco com Blueprint (Se for primeiro deploy)

```yaml
services:
  - type: web
    name: digital-twin-django
    # ... configurações ...
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: ifc-database
          property: connectionString

databases:
  - name: ifc-database
    plan: free
    databaseName: ifc_monitoring
    user: ifc_user
```

---

## 🚀 Deploy - Cenários

### Cenário A: Banco já existe (outro projeto já deployado)

1. **Remova a seção `databases:`** do `render.yaml`
2. Mantenha apenas a referência em `fromDatabase`:
   ```yaml
   - key: DATABASE_URL
     fromDatabase:
       name: ifc-database  # Nome do banco existente
       property: connectionString
   ```
3. Faça deploy normalmente
4. O Django usará o mesmo banco do outro projeto

**⚠️ IMPORTANTE**: As tabelas do Django e do FastAPI coexistirão no mesmo banco. Django cria tabelas com prefixo (ex: `core_user`, `plant_viewer_buildingplan`).

### Cenário B: Primeiro deploy (banco não existe)

1. Mantenha a seção `databases:` no `render.yaml`
2. Faça deploy via Blueprint
3. O Render criará o banco automaticamente
4. Depois você pode adicionar outros serviços apontando para esse banco

---

## 🔄 Conectar Novo Serviço a Banco Existente

### Via Dashboard (Manual)

1. Crie novo Web Service
2. Em **Environment**, adicione variável:
   ```
   Name: DATABASE_URL
   Value: [Copiar do banco existente]
   ```
3. Para obter a URL do banco:
   - Dashboard → PostgreSQL Database → Connection String

### Via Blueprint (Automático)

```yaml
services:
  - type: web
    name: meu-novo-servico
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: ifc-database  # Referência ao banco existente
          property: connectionString
```

---

## 📊 Estrutura do Banco Compartilhado

```sql
-- Banco: ifc_monitoring
-- User: ifc_user

-- Tabelas do FastAPI (outro projeto)
├── users
├── sensors
├── readings
├── alerts
├── locations
├── ifc_files
└── ifc_spaces

-- Tabelas do Django (este projeto)
├── core_user
├── plant_viewer_buildingplan
├── sensor_management_sensor
├── sensor_management_sensordata
├── sensor_management_sensoralert
├── django_session
├── django_migrations
└── auth_group
```

**✅ Não há conflito!** Cada framework usa seus próprios nomes de tabela.

---

## 🔒 Segurança e Isolamento

### Isolamento de Tabelas
- Django usa prefixos automáticos (app_model)
- FastAPI usa nomes customizados
- Nenhum conflito entre os dois

### Permissões
- Ambos serviços usam mesmo usuário (`ifc_user`)
- Ambos têm acesso total ao banco
- **Atenção**: Um serviço pode modificar tabelas do outro se quiser

### Boas Práticas
```python
# Django - Não mexer em tabelas do FastAPI
# FastAPI - Não mexer em tabelas do Django

# Se precisar compartilhar dados:
# - Criar tabelas específicas para isso
# - Documentar claramente
# - Usar migrations em ambos
```

---

## 💰 Custos

### Um Banco (Atual)
- PostgreSQL Free: **$0/mês** (90 dias)
- PostgreSQL Starter: **$7/mês**

### Dois Serviços Web + Um Banco
- Web Service 1 (FastAPI): $7/mês
- Web Service 2 (Django): $7/mês  
- PostgreSQL: $7/mês
- **Total: $21/mês**

### Dois Serviços Web + Dois Bancos ❌
- Web Service 1: $7/mês
- Web Service 2: $7/mês
- PostgreSQL 1: $7/mês
- PostgreSQL 2: $7/mês
- **Total: $28/mês** (Mais caro e desnecessário!)

---

## 🛠️ Comandos Úteis

### Verificar Tabelas no Banco

```bash
# No Render Shell do Django
python manage.py dbshell

# Listar todas as tabelas
\dt

# Listar tabelas do Django
\dt core_*
\dt plant_viewer_*
\dt sensor_management_*

# Listar tabelas do FastAPI
SELECT tablename FROM pg_tables WHERE schemaname = 'public' 
  AND tablename NOT LIKE 'django_%' 
  AND tablename NOT LIKE 'auth_%'
  AND tablename NOT LIKE 'core_%';
```

### Backup do Banco Compartilhado

```bash
# Baixar dump completo
# Dashboard → PostgreSQL → Connect → External Connection

pg_dump -h <host> -U ifc_user -d ifc_monitoring > backup.sql

# Restaurar (se necessário)
psql -h <host> -U ifc_user -d ifc_monitoring < backup.sql
```

---

## ⚠️ Problemas Comuns

### Erro: "Database ifc-database not found"

**Causa**: Banco não foi criado ainda ou nome incorreto

**Solução**:
1. Verificar se banco existe: Dashboard → Databases
2. Verificar nome exato em `fromDatabase: name:`
3. Se não existe, adicionar seção `databases:` ao render.yaml

### Erro: "Permission denied for table..."

**Causa**: Usuário não tem permissão na tabela

**Solução**:
```sql
-- No psql do banco
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ifc_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ifc_user;
```

### Migrations do Django Falhando

**Causa**: Tabelas já existem ou conflito

**Solução**:
```bash
# Ver status das migrations
python manage.py showmigrations

# Fake migration se necessário (tabela já existe)
python manage.py migrate --fake <app_name> <migration_name>

# Limpar migrations e refazer (cuidado!)
python manage.py migrate <app_name> zero
python manage.py migrate <app_name>
```

---

## 📝 Checklist de Deploy

- [ ] Decidir: usar banco existente ou criar novo?
- [ ] Atualizar `render.yaml` com nome correto do banco
- [ ] Se banco existente: remover seção `databases:`
- [ ] Se banco novo: manter seção `databases:`
- [ ] Fazer commit e push
- [ ] Deploy via Blueprint ou Manual
- [ ] Verificar logs de build
- [ ] Testar conexão ao banco
- [ ] Verificar tabelas criadas
- [ ] Testar aplicação

---

## 🎯 Configuração Atual do Projeto

**Arquivo**: `render.yaml`

```yaml
databases:
  - name: ifc-database          # ← Nome compartilhado
    plan: free
    databaseName: ifc_monitoring
    user: ifc_user

services:
  - type: web
    name: digital-twin-django
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: ifc-database    # ← Referência ao banco acima
          property: connectionString
```

**Status**: ✅ Configurado para usar um único banco

---

## 📚 Documentação Relacionada

- `DEPLOY_CHECKLIST.md` - Guia completo de deploy
- `CORREÇÕES_DEPLOY_RENDER.md` - Correções aplicadas
- `docs/QUICK_START_RENDER.md` - Quick start

---

**Atualizado**: Outubro 2024  
**Arquitetura**: Django + PostgreSQL compartilhado

