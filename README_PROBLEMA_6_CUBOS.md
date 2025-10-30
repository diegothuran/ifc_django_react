# 🐛 Problema: Sistema Sempre Mostra 6 Cubos

## 🔍 Diagnóstico

Você está vendo sempre o mesmo plot com **6 cubos coloridos** porque:

- ❌ **Não há arquivo IFC cadastrado no banco de dados Django**
- ⚠️ O sistema está usando um modelo de exemplo (fallback)
- 📁 Seu arquivo `Ifc2s3_Duplex_Electrical.ifc` está no Downloads mas não foi importado

## ✅ Solução Rápida (3 minutos)

### Windows (Opção 1 - Mais Fácil)

Dê duplo clique em:
```
carregar_ifc.bat
```

### Windows (Opção 2 - PowerShell)

Abra PowerShell nesta pasta e execute:
```powershell
.\carregar_ifc.ps1
```

### Linux/Mac

Execute:
```bash
python load_ifc_file.py
```

### Modo Direto

```bash
python load_ifc_file.py "C:\Users\diego\Downloads\Ifc2s3_Duplex_Electrical.ifc"
```

## 📝 O que o script faz?

1. ✅ Verifica plantas já cadastradas
2. ✅ Importa seu arquivo IFC para o banco de dados
3. ✅ Extrai metadados automaticamente
4. ✅ Ativa a planta para visualização

## 🎯 Resultado Esperado

Após executar:

1. Abra http://localhost:8000/plant/view/
2. Você verá o **modelo 3D do Duplex** em vez dos 6 cubos
3. Poderá clicar nos elementos para ver propriedades
4. Alternar entre visualização 3D e 2D

## 📚 Documentação Completa

Veja `GUIA_CARREGAMENTO_IFC.md` para:
- Outros métodos de carregamento (Admin, Shell)
- Troubleshooting detalhado
- FAQ

## 🆘 Precisa de Ajuda?

Execute o script e ele vai diagnosticar o problema:
```bash
python load_ifc_file.py
```

---

**Feito?** Recarregue http://localhost:8000/plant/view/ e veja a mágica acontecer! ✨

