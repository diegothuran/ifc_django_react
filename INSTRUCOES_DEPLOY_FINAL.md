# 🚀 Instruções Finais para Deploy no Render

## ✅ Correções Aplicadas

1. ✅ Branch corrigida: `master` (não `main`)
2. ✅ Seção `databases:` removida (banco já existe no outro projeto)
3. ✅ Configuração aponta para banco existente `ifc-database`

---

## 📝 Próximos Passos

### 1️⃣ **Fazer commit das alterações**

Execute estes comandos no PowerShell:

```powershell
# Adicionar arquivos modificados
git add render.yaml

# Fazer commit
git commit -m "Fix: Corrigir branch para master e usar banco existente"

# Fazer push
git push origin master
```

### 2️⃣ **Aguardar o Render detectar a mudança**

Após o push:
- O Render detectará automaticamente a mudança
- Iniciará novo build
- Acompanhe em: https://dashboard.render.com/

**OUforce manualmente:**
1. Dashboard do Render
2. Blueprints → Seu blueprint
3. Botão "Sync Blueprint"

---

## 🎯 O Que Vai Acontecer

```
✅ Render encontrará branch master
✅ Fará checkout do código
✅ Executará build.sh
   ├── Instalará dependências
   ├── Coletará arquivos estáticos
   ├── Rodará migrations no banco ifc-database
   └── Criará superusuário (se não existir)
✅ Executará start_simple.sh
   └── Iniciará Gunicorn
🎉 Deploy concluído!
```

---

## 📊 Configuração Final

### render.yaml (resumo):

```yaml
services:
  - type: web
    name: digital-twin-django
    branch: master  # ← Corrigido
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: ifc-database  # ← Banco compartilhado
          property: connectionString

# databases: ← REMOVIDO (banco já existe)
```

### Banco de Dados:
- **Nome**: `ifc-database`
- **Compartilhado**: FastAPI + Django
- **Localização**: Criado no outro projeto

---

## 🔍 Verificações Pós-Deploy

### 1. Verificar logs do build:
```
Dashboard → digital-twin-django → Logs
```

Procure por:
```
✅ Build concluído com sucesso
✅ Migrações executadas
✅ Arquivos estáticos coletados
✅ Servidor iniciado
```

### 2. Testar a aplicação:
```
https://digital-twin-django.onrender.com/
https://digital-twin-django.onrender.com/admin/
https://digital-twin-django.onrender.com/dashboard/
```

### 3. Acessar admin:
- **URL**: `/admin/`
- **Usuário**: `admin`
- **Senha**: `admin123`
- ⚠️ **TROCAR SENHA IMEDIATAMENTE!**

---

## ⚠️ Se der Erro

### Erro: "Could not find branch master"
- Verifique no GitHub qual branch você está usando
- Acesse: https://github.com/diegothuran/ifc_django_project
- Veja qual branch aparece como padrão

### Erro: "Database ifc-database not found"
1. Vá em Dashboard → Databases
2. Verifique se `ifc-database` existe
3. Se não existe, adicione de volta a seção `databases:` no render.yaml

### Erro: "Build failed"
- Veja os logs completos no Dashboard
- Verifique se todos os arquivos foram enviados ao GitHub:
  - `build.sh`
  - `start_simple.sh`
  - `requirements.txt`
  - `runtime.txt`

---

## 📋 Checklist Final

Antes de fazer push, confirme:

- [x] `render.yaml` tem `branch: master`
- [x] Seção `databases:` foi removida
- [x] Banco `ifc-database` existe no Render
- [ ] Fazer `git add render.yaml`
- [ ] Fazer `git commit -m "..."`
- [ ] Fazer `git push origin master`
- [ ] Aguardar build no Render
- [ ] Testar aplicação

---

## 🎉 Resultado Esperado

```
🌐 Aplicação no ar: https://digital-twin-django.onrender.com
📊 Admin: https://digital-twin-django.onrender.com/admin/
🏭 Dashboard: https://digital-twin-django.onrender.com/dashboard/

💾 Banco: ifc-database (compartilhado)
   ├── Tabelas FastAPI: users, sensors, readings, alerts...
   └── Tabelas Django: core_user, plant_viewer_*, sensor_management_*
```

---

## 💡 Dica

Se o primeiro deploy falhar, não se preocupe! Veja os logs, ajuste o que for necessário, e faça novo commit/push. O Render tentará novamente automaticamente.

---

**Status**: ✅ Pronto para commit e push!

Execute os comandos do passo 1️⃣ e aguarde o deploy! 🚀

