# 🔧 Correção: Branch Git para Deploy no Render

## ❌ Problema Identificado

```
(git branch not found: "master" in https://api.github.com/repos/diegothuran/ifc_django_project/commits/master)
```

**Causa**: O Render está procurando pela branch `master`, mas o repositório usa `main`.

---

## ✅ Solução Aplicada

### Adicionada especificação de branch no `render.yaml`

```yaml
services:
  - type: web
    name: digital-twin-django
    runtime: python
    plan: free
    branch: main  # ← ADICIONADO: especifica a branch correta
    buildCommand: "chmod +x build.sh && ./build.sh"
    startCommand: "chmod +x start_simple.sh && ./start_simple.sh"
```

---

## 🚀 Próximos Passos

### 1️⃣ Fazer commit da correção

```bash
git add render.yaml
git commit -m "Fix: Especificar branch main no render.yaml"
git push origin main
```

### 2️⃣ Redeployar no Render

**Opção A - Automático (Recomendado):**
- O Render detectará o push e fará redeploy automaticamente
- Aguarde alguns minutos

**Opção B - Manual:**
1. Dashboard do Render
2. Vá em "Blueprints"
3. Clique no seu blueprint
4. Clique em "Sync Blueprint"

---

## 🔍 Verificações

### Confirmar branch correta no GitHub:

1. Acesse: https://github.com/diegothuran/ifc_django_project
2. Verifique qual branch está ativa (geralmente aparece no topo)
3. Deve mostrar `main` ou `master`

### Se for realmente "master":

Caso o repositório use `master` (não `main`), altere no `render.yaml`:

```yaml
branch: master  # em vez de main
```

---

## 📋 Status das Ações do Render

Baseado nas mensagens que você recebeu:

| Ação | Status | Descrição |
|------|--------|-----------|
| Associar banco ifc-database | ✅ OK | Banco vinculado ao Blueprint |
| Atualizar DATABASE_URL | ✅ OK | Variável configurada |
| Buscar branch master | ❌ ERRO | Branch não encontrada |
| Criar PYTHON_VERSION | ✅ OK | Variável criada |
| Buscar branch master | ❌ ERRO | Branch não encontrada (2ª vez) |

**Resultado**: Deploy falhou por causa da branch incorreta.

---

## 🎯 Após Corrigir

Quando você fizer o push da correção, o Render deve:

1. ✅ Detectar a branch `main` corretamente
2. ✅ Fazer checkout do código
3. ✅ Executar `build.sh`
4. ✅ Executar migrations
5. ✅ Coletar static files
6. ✅ Iniciar o servidor com `start_simple.sh`

---

## 🔧 Comandos de Troubleshooting

### Verificar branch local:
```bash
git branch --show-current
```

### Listar todas as branches:
```bash
git branch -a
```

### Ver branches remotas:
```bash
git remote show origin
```

### Mudar branch padrão (se necessário):
```bash
# No GitHub:
Settings → Branches → Default branch → Escolher main
```

---

## 💡 Dica

A partir de 2020, o GitHub mudou a branch padrão de `master` para `main`. Se você criou o repositório recentemente, provavelmente usa `main`.

---

**Status**: ✅ Correção aplicada - Pronta para commit e push!


