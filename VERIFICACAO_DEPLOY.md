# 🔍 Verificação de Deploy no Render

## ❌ Problemas Identificados

### 1. **Falta especificar o repositório no render.yaml**

O `render.yaml` não tem a URL do repositório, o que pode causar problemas.

### 2. **Conflito entre Procfile e render.yaml**

- **Procfile** usa: `python manage.py auto_setup_render && gunicorn ...`
- **render.yaml** usa: `chmod +x start_simple.sh && ./start_simple.sh`

### 3. **Possível problema com banco de dados**

Se o banco `ifc-database` não existir, o deploy falhará.

---

## ✅ Correções Necessárias

Execute os comandos abaixo para verificar:

```bash
# 1. Verificar se todos os arquivos existem
ls -la build.sh start_simple.sh requirements.txt runtime.txt

# 2. Verificar permissões (Linux/Mac)
chmod +x build.sh start_simple.sh

# 3. Verificar se o repositório está atualizado
git status
git push origin master
```

---

## 🔧 Checklist de Verificação

- [ ] Banco `ifc-database` existe no Render?
- [ ] Branch `master` existe no GitHub?
- [ ] Arquivos `build.sh` e `start_simple.sh` estão no repositório?
- [ ] `requirements.txt` tem todas as dependências?
- [ ] `runtime.txt` especifica Python 3.11.10?

---

## 🌐 Como Verificar no Render

1. **Dashboard** → **Databases** → Verificar se `ifc-database` existe
2. **Dashboard** → **Blueprints** → Ver logs de erro
3. **Dashboard** → **Events** → Ver o que falhou

