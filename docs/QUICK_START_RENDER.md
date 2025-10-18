# 🚀 Quick Start - Deploy no Render (Sem Redis)

## ⚡ Deploy em 5 Minutos

### Pré-requisitos:
- ✅ Conta no [Render](https://render.com/)
- ✅ Repositório no GitHub
- ✅ Código commitado e pushed

---

## 📋 Passo a Passo Rápido

### 1. Criar Web Service (2 min)

1. [Render Dashboard](https://dashboard.render.com/) → **New +** → **Web Service**
2. Conectar repositório GitHub
3. Configurar:
```
Name: ifc-digital-twin
Runtime: Python 3
Build Command: bash build.sh
Start Command: gunicorn ifc_monitoring.wsgi:application
```

### 2. Adicionar PostgreSQL (1 min)

1. No Web Service → **Environment** → **Add Database**
2. **PostgreSQL** → **Create Database**
3. Pronto! `DATABASE_URL` criada automaticamente

### 3. Variáveis de Ambiente (1 min)

Adicionar em **Environment Variables**:

```bash
DEBUG=False
SECRET_KEY=<gerar-uma-chave-segura-aqui>
PYTHON_VERSION=3.11.10
```

**Gerar SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Deploy! (1 min)

Clique em **"Create Web Service"**

Render automaticamente:
- ✅ Instala dependências
- ✅ Roda migrations
- ✅ **Cria tabela de cache** 💾
- ✅ Cria superusuário admin
- ✅ Coleta static files
- ✅ Inicia app

---

## 🎉 Pronto!

**Sua app está no ar:** `https://seu-app.onrender.com`

### Acessos:

| URL | Descrição |
|-----|-----------|
| `/admin/` | Admin (admin/admin123) ⚠️ mudar senha |
| `/plant-viewer/` | Visualizador 3D |
| `/plant-viewer/api/plants/` | API REST |

---

## ⚙️ O Que Acontece no Build

```bash
bash build.sh executará:

1. pip install -r requirements.txt      ✅
2. python manage.py collectstatic       ✅
3. python manage.py migrate             ✅
4. python manage.py createcachetable    ✅ NOVO (cache PostgreSQL)
5. Criar admin se não existir           ✅
```

---

## 🛠️ Comandos Úteis

### Acessar Shell Django no Render:
```
Dashboard → Seu Service → Shell → python manage.py shell
```

### Testar Cache:
```python
from django.core.cache import cache
cache.set('test', 'ok')
print(cache.get('test'))  # Deve: ok
```

### Ver Logs:
```
Dashboard → Seu Service → Logs
```

---

## 💰 Custos

| Serviço | Plano | Custo |
|---------|-------|-------|
| Web Service | Starter | $7/mês |
| PostgreSQL | Starter | $7/mês |
| **Total** | | **$14/mês** |

**Free Tier:** $0/mês (90 dias, depois expira)

---

## 🚨 Problemas Comuns

### Build Falha

**Solução:**
- Ver logs no Dashboard
- Confirmar `build.sh` tem `chmod +x`

### App não Inicia

**Solução:**
- Verificar `DATABASE_URL` existe
- Verificar `SECRET_KEY` está configurada

### Cache não Funciona

**Solução:**
```bash
python manage.py createcachetable
```

---

## 📚 Documentação Completa

- 📘 **CONFIGURACAO_RENDER_SEM_REDIS.md** - Guia detalhado
- 📗 **MELHORIAS_APLICADAS_RENDER.md** - Mudanças técnicas

---

## ✅ Checklist Pós-Deploy

- [ ] Admin acessível
- [ ] Mudar senha do admin
- [ ] Visualizador 3D funcionando
- [ ] API REST respondendo
- [ ] Upload de arquivo IFC testado
- [ ] Cache verificado

---

**Pronto! App no ar em 5 minutos! 🎊**

