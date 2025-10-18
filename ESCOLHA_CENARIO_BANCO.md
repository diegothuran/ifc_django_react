# 🗄️ IMPORTANTE: Escolha o Cenário do Banco de Dados

## ❓ Qual é a Sua Situação?

Antes de fazer deploy, você precisa escolher uma das opções abaixo:

---

## 📊 Cenário A: Banco JÁ EXISTE (Outro projeto já deployado)

✅ **Use este cenário se:**
- Você já fez deploy do projeto FastAPI (`ifc-backend` + `ifc-frontend-streamlit`)
- O banco `ifc-database` já está criado no Render
- Você quer que o Django use o MESMO banco do FastAPI

### 🔧 O Que Fazer:

**1. Remova a seção `databases:` do `render.yaml`**

Abra o arquivo `render.yaml` e **DELETE estas linhas**:

```yaml
# ❌ REMOVER ESTAS LINHAS:
databases:
  - name: ifc-database
    plan: free
    databaseName: ifc_monitoring
    user: ifc_user
```

O arquivo final deve ficar assim:

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
          name: ifc-database  # ← Aponta para banco existente
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: "False"
      - key: WEB_CONCURRENCY
        value: "4"
      - key: ALLOWED_HOSTS
        value: ".onrender.com"
      - key: DJANGO_SETTINGS_MODULE
        value: "ifc_monitoring.settings"
      - key: RENDER
        value: "true"
      - key: AUTO_SETUP_DATA
        value: "true"
      - key: PYTHON_VERSION
        value: "3.11.10"

# ✅ SEM seção databases: - o banco já existe!
```

**2. Faça o deploy normalmente**

```bash
git add .
git commit -m "Deploy Django usando banco existente"
git push origin main
```

**3. Resultado:**
- ✅ Django usará o mesmo banco PostgreSQL do FastAPI
- ✅ Sem custos adicionais (1 banco em vez de 2)
- ✅ Tabelas do Django e FastAPI coexistem sem conflito

---

## 📊 Cenário B: Banco NÃO EXISTE (Primeiro deploy)

✅ **Use este cenário se:**
- Este é o primeiro projeto que você está deployando no Render
- Você ainda NÃO tem o banco `ifc-database` criado
- Você quer criar o banco através deste projeto

### 🔧 O Que Fazer:

**1. MANTENHA a seção `databases:` no `render.yaml`**

Não precisa fazer nada! O arquivo já está configurado corretamente:

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
  - name: ifc-database  # ← Cria o banco automaticamente
    plan: free
    databaseName: ifc_monitoring
    user: ifc_user
```

**2. Faça o deploy normalmente**

```bash
git add .
git commit -m "Deploy Django com banco novo"
git push origin main
```

**3. Depois, ajuste o outro projeto:**

Quando for deployar o projeto FastAPI, remova a seção `databases:` do `render.yaml` dele e faça ele apontar para o banco criado aqui.

---

## 🔍 Como Verificar Qual Cenário Usar?

### Verificar no Render Dashboard:

1. Acesse: https://dashboard.render.com/
2. Vá em **Databases** no menu lateral
3. Procure por um banco chamado **`ifc-database`**

**Se encontrar o banco:**
- ✅ Use **Cenário A** (remova seção databases:)

**Se NÃO encontrar:**
- ✅ Use **Cenário B** (mantenha seção databases:)

---

## ⚡ Comando Rápido

### Se banco EXISTE (Cenário A):

```bash
# Remover seção databases do render.yaml
# (faça manualmente ou use o comando abaixo)

# Windows PowerShell:
(Get-Content render.yaml) | Where-Object {$_ -notmatch 'databases:|  - name: ifc-database|    plan: free|    databaseName: ifc_monitoring|    user: ifc_user'} | Set-Content render.yaml

# Ou edite manualmente e remova as linhas
```

### Se banco NÃO EXISTE (Cenário B):

```bash
# Não fazer nada! O arquivo já está correto.
```

---

## 🎯 Checklist Rápido

Antes de fazer deploy, confirme:

- [ ] Verificou se banco `ifc-database` existe no Render Dashboard
- [ ] Escolheu o cenário correto (A ou B)
- [ ] Ajustou o `render.yaml` conforme o cenário
- [ ] Fez commit das alterações
- [ ] Pronto para deploy!

---

## 💡 Dica

**Recomendação:** Se você tem dúvida, use o **Cenário B** (manter a seção databases). Se o banco já existir, o Render mostrará um erro mas não causará problemas. Aí você remove a seção e faz deploy novamente.

---

## 📞 Dúvidas?

Consulte: `RENDER_DATABASE_CONFIG.md` para detalhes completos sobre banco de dados compartilhado.


