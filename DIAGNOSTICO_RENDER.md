# 🔍 Diagnóstico Completo para Deploy no Render

## ✅ Arquivos Verificados

| Arquivo | Status | Observação |
|---------|--------|------------|
| `render.yaml` | ✅ OK | Corrigido: usa `bash` em vez de `chmod +x` |
| `build.sh` | ✅ OK | Script de build completo |
| `start_simple.sh` | ✅ OK | Script de inicialização Gunicorn |
| `requirements.txt` | ✅ OK | Dependências presentes |
| `runtime.txt` | ✅ OK | Python 3.11.10 |
| `static/` | ✅ OK | Diretório existe |

---

## 🔧 Correções Aplicadas

### 1. **Comando de build corrigido**

**Antes:**
```yaml
buildCommand: "chmod +x build.sh && ./build.sh"
startCommand: "chmod +x start_simple.sh && ./start_simple.sh"
```

**Depois:**
```yaml
buildCommand: "bash build.sh"
startCommand: "bash start_simple.sh"
```

**Motivo**: No Render, os arquivos .sh já são executáveis, e usar `bash` é mais confiável.

---

## ⚠️ Possíveis Problemas e Soluções

### Problema 1: Banco de Dados não encontrado

**Erro**: `Database "ifc-database" not found`

**Solução**:
1. Ir em Dashboard → Databases
2. Verificar se `ifc-database` existe
3. Se NÃO existe:
   - Opção A: Criar manualmente o banco
   - Opção B: Adicionar seção `databases:` no `render.yaml`

```yaml
# Adicionar ao final do render.yaml se banco não existir:
databases:
  - name: ifc-database
    plan: free
    databaseName: ifc_monitoring
    user: ifc_user
```

### Problema 2: Branch não encontrada

**Erro**: `branch master could not be found`

**Solução**:
```bash
# Verificar qual branch você usa:
git branch --show-current

# Se for "main", alterar no render.yaml:
branch: main  # em vez de master
```

### Problema 3: Build falha ao coletar static files

**Erro**: `FileNotFoundError: [Errno 2] No such file or directory: 'static'`

**Solução**: Os arquivos static já existem, mas verifique se foram enviados ao GitHub:
```bash
git add static/
git commit -m "Add static files"
git push origin master
```

### Problema 4: Dependências não instaladas

**Erro**: `ModuleNotFoundError: No module named 'xxx'`

**Solução**: Verificar se todas as dependências estão no `requirements.txt`:
```bash
# Verificar arquivo
cat requirements.txt

# Se faltar alguma, adicionar:
echo "nome-do-pacote==versao" >> requirements.txt
git add requirements.txt
git commit -m "Add missing dependency"
git push origin master
```

### Problema 5: SECRET_KEY ou DATABASE_URL não configurados

**Erro**: `KeyError: 'SECRET_KEY'` ou `django.core.exceptions.ImproperlyConfigured`

**Solução**: O `render.yaml` já configura, mas verifique no Dashboard:
1. Dashboard → Seu Web Service → Environment
2. Verificar se existe:
   - `DATABASE_URL` (vindo do banco)
   - `SECRET_KEY` (auto-gerado)
   - `DEBUG=False`

---

## 📋 Checklist Final

Antes de tentar deploy novamente:

- [ ] Repositório GitHub está atualizado?
  ```bash
  git add .
  git commit -m "Fix: Corrigir configuração Render"
  git push origin master
  ```

- [ ] Branch correta no `render.yaml`?
  - Se seu repo usa `main`, mudar para `branch: main`
  - Se usa `master`, deixar `branch: master`

- [ ] Banco `ifc-database` existe no Render?
  - Verificar em Dashboard → Databases
  - Se não existe, adicionar seção `databases:` no `render.yaml`

- [ ] Todos os arquivos foram enviados ao GitHub?
  ```bash
  git status  # Não deve ter nada pendente
  ```

- [ ] O repositório é público ou o Render tem permissão?
  - Verificar em Settings do repositório

---

## 🚀 Como Fazer Deploy Agora

### Opção 1: Via Dashboard (Manual)

1. **Dashboard** → **New +** → **Web Service**
2. **Connect Repository**: Selecione `diegothuran/ifc_django_project`
3. **Configure**:
   ```
   Name: digital-twin-django
   Runtime: Python 3
   Branch: master  (ou main)
   Build Command: bash build.sh
   Start Command: bash start_simple.sh
   ```
4. **Environment Variables**:
   - Adicione `DATABASE_URL` manualmente (copiar do banco `ifc-database`)
   - Outras variáveis serão configuradas automaticamente

5. **Create Web Service**

### Opção 2: Via Blueprint (Recomendado)

1. **Dashboard** → **New +** → **Blueprint**
2. **Connect Repository**: Selecione `diegothuran/ifc_django_project`
3. **Render detectará** `render.yaml` automaticamente
4. **Review** e clique em **Apply**

### Opção 3: Via render.yaml atualizado

Se já tem um service criado:
1. **Dashboard** → **Blueprints** → Seu blueprint
2. **Sync Blueprint** → Aplicará as mudanças do `render.yaml`

---

## 📊 Logs para Verificar

Após iniciar deploy, verifique logs em tempo real:

**Dashboard → Seu Service → Logs**

Procure por:
- ✅ `Build started`
- ✅ `Installing dependencies`
- ✅ `Collecting static files`
- ✅ `Running migrations`
- ✅ `Build succeeded`
- ✅ `Starting server`
- ✅ `Listening on 0.0.0.0:10000`

Se houver erro, copie a mensagem e investigue.

---

## 🆘 Se Ainda Não Funcionar

Copie e envie:
1. **Logs completos** do build (Dashboard → Logs)
2. **Mensagem de erro** específica
3. **URL do seu repositório** GitHub

Possíveis erros comuns:
- `git branch not found` → Corrigir branch no render.yaml
- `Database not found` → Criar banco ou adicionar seção databases:
- `ModuleNotFoundError` → Adicionar dependência no requirements.txt
- `FileNotFoundError: static` → git add static/ && git push
- `Port already in use` → Reiniciar o service

---

## ✅ Arquivo Corrigidos Nesta Sessão

1. ✅ `render.yaml` - Comando de build corrigido
2. ✅ `check_deploy.py` - Script de verificação criado
3. ✅ `VERIFICACAO_DEPLOY.md` - Guia de verificação
4. ✅ `DIAGNOSTICO_RENDER.md` - Este arquivo

---

**Próximo passo**: Fazer commit e push, depois tentar deploy novamente!

```bash
git add .
git commit -m "Fix: Corrigir comandos Render e adicionar verificação"
git push origin master
```

