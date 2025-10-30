# Guia Rápido - IFC Digital Twin v2.3.0

Guia prático para usar os recursos de Digital Twin estilo Twinzo.

---

## 🚀 Início Rápido

### 1. Acessar o Dashboard

```
http://localhost:8000/core/
ou
https://seu-app.onrender.com/core/
```

**Login padrão** (altere em produção!):
- Usuário: `admin`
- Senha: `admin123`

---

## 📊 Dashboard Digital Twin

### Visão Geral

O dashboard principal apresenta:
- **Lado Esquerdo (30%)**: Cards com estatísticas
  - Sensores Ativos
  - Alertas Ativos
  - Leituras Recentes (24h)
  - Total de Dados
- **Centro (70%)**: Visualização 3D da planta industrial
- **Abaixo**: Timeline/Heatmap e tabelas de dados

---

## 🏗️ Visualização 3D

### Carregamento Automático

A planta ativa mais recente carrega automaticamente ao acessar o dashboard.

### Controles Disponíveis

**Barra superior direita:**
- 🔄 **Reset**: Volta à visão inicial
- 📡 **Sensores**: Mostra/oculta marcadores de sensores
- 🖼️ **Fullscreen**: Modo tela cheia

**Barra inferior esquerda:**
- 🔲 **Wireframe**: Alterna modo aramado
- 📐 **Ortográfico**: Alterna projeção ortográfica

### Navegação

- **Rotação**: Clique e arraste (botão esquerdo)
- **Zoom**: Scroll do mouse
- **Pan**: Clique botão direito e arraste

---

## 📍 Sensores IoT

### Como Funcionam

Após 2 segundos do carregamento da planta, marcadores 3D aparecem automaticamente sobre os sensores ativos.

### Cores dos Sensores

- 🟢 **Verde**: Sensor funcionando normalmente
- 🟠 **Laranja**: Sem dados recentes
- 🔴 **Vermelho**: Erro ou alerta ativo
- ⚫ **Cinza**: Sensor offline/inativo

### Interação

- Marcadores pulsam suavemente
- Clique no botão **Sensores** para mostrar/ocultar
- Sensores são posicionados automaticamente baseado no `location_id` do modelo IFC

---

## 🔥 Sistema de Heatmaps

### Ativar Heatmap

1. Role para baixo até ver "Timeline e Análise Temporal"
2. Clique no botão **🔥 Heatmap**
3. Controles aparecerão

### Configurar Heatmap

**Tipo de Dados:**
- **Atividade**: Frequência de leituras por área
- **Temperatura**: Distribuição de temperatura
- **Pressão**: Distribuição de pressão
- **Fluxo**: Distribuição de fluxo

**Período:**
- **24h**: Últimas 24 horas
- **7d**: Últimos 7 dias
- **30d**: Últimos 30 dias

**Opacidade:**
- Ajuste o slider (0-100%)
- Veja mudança em tempo real

### Controles

- **⟳ Carregar**: Busca dados e renderiza heatmap
- **👁️ Toggle**: Mostra/oculta heatmap
- **✕ Limpar**: Remove heatmap da cena

### Legenda

Gradiente de cores indica intensidade:
- 🔵 **Azul**: Baixo
- 🟢 **Verde**: Médio-Baixo
- 🟡 **Amarelo**: Médio
- 🟠 **Laranja**: Médio-Alto
- 🔴 **Vermelho**: Alto

---

## ⏱️ Timeline Temporal

### Ativar Timeline

1. Na seção "Timeline e Análise Temporal"
2. Clique no botão **📈 Timeline**
3. Controles de timeline aparecerão

### Controles da Timeline

**Botões:**
- ▶️ **Play**: Inicia replay automático
- ⏸️ **Pause**: Pausa o replay
- ⏹️ **Stop**: Para e volta para o presente
- ⏪ **Voltar**: Recua 1 hora
- ⏩ **Avançar**: Avança 1 hora

**Slider:**
- Arraste para navegar rapidamente no tempo
- Abrange últimos 30 dias

**Velocidade:**
- 0.5x: Mais lento (análise detalhada)
- 1x: Velocidade normal
- 2x, 5x, 10x: Replay rápido

### Como Usar

```
1. Clique em Play
2. Observe data/hora mudando
3. Heatmap atualiza automaticamente
4. Cores dos sensores refletem estado histórico
5. Pause para analisar momento específico
6. Use slider para pular para data específica
```

---

## 🔗 Integração Timeline + Heatmap

### Análise Temporal Completa

1. **Ative o Heatmap primeiro:**
   - Escolha tipo (ex: Temperatura)
   - Escolha período (ex: 7 dias)
   - Clique em Carregar

2. **Depois ative a Timeline:**
   - Clique no botão Timeline
   - Use Play ou navegue manualmente

3. **Observe a sincronização:**
   - Heatmap reflete o momento da timeline
   - Sensores mudam de cor conforme histórico
   - Console do navegador mostra logs (F12)

### Casos de Uso

**Investigar Incidente:**
1. Navegue timeline até horário do incidente
2. Observe heatmap de temperatura naquele momento
3. Identifique área problema
4. Verifique quais sensores estavam em alerta

**Análise de Padrões:**
1. Ative heatmap de atividade
2. Use timeline em velocidade 5x
3. Observe padrões ao longo do dia/semana
4. Identifique horários de pico

**Comparação Temporal:**
1. Anote posição do slider em um momento
2. Navegue para outro período
3. Compare heatmaps visualmente
4. Identifique mudanças

---

## 📊 Tabelas de Dados

### Últimas Leituras

Mostra as 10 leituras mais recentes de todos os sensores com:
- Nome do sensor
- Valor da leitura
- Data e hora

### Alertas Não Reconhecidos

Lista alertas ativos que requerem atenção:
- Sensor que gerou o alerta
- Descrição
- Nível (crítico, erro, aviso, info)

---

## 🎯 Fluxo de Trabalho Recomendado

### Monitoramento Diário

```
1. Acesse dashboard
2. Verifique cards de estatísticas
3. Observe planta 3D com sensores
4. Revise tabela de alertas
5. Se houver alertas:
   - Use heatmap para localizar área
   - Verifique sensores próximos
   - Tome ação necessária
```

### Análise Semanal

```
1. Ative heatmap de atividade (7d)
2. Identifique áreas com uso anormal
3. Use timeline para replay da semana (10x)
4. Identifique padrões e anomalias
5. Gere relatórios (screenshots)
```

### Investigação de Problemas

```
1. Identifique horário do problema
2. Use timeline para navegar até o momento
3. Ative heatmap relevante (temperatura, pressão, etc)
4. Observe estado dos sensores naquele momento
5. Navegue para antes/depois para entender contexto
6. Documente achados
```

---

## 🔧 Configuração de Sensores

### Adicionar location_id

Para sensores aparecerem na planta 3D:

1. Acesse **Admin** (`/admin/`)
2. Navegue até **Sensores**
3. Edite um sensor
4. No campo **Location ID**, adicione o ID do elemento IFC
5. Salve

**Dica**: Use a API `/plant/api/plants/{id}/elements/` para listar elementos IFC disponíveis.

---

## 📱 Atalhos de Teclado

(Planejado para versão futura)

- `Space`: Play/Pause timeline
- `←`: Voltar 1 hora
- `→`: Avançar 1 hora
- `H`: Toggle heatmap
- `S`: Toggle sensores
- `R`: Reset view
- `F`: Fullscreen

---

## 🐛 Troubleshooting

### Planta não aparece

**Causa**: Nenhuma planta ativa no sistema  
**Solução**: 
1. Acesse `/plant/`
2. Faça upload de arquivo IFC
3. Marque como "Ativa"

### Sensores não aparecem

**Causa**: Sensores sem `location_id` ou inativos  
**Solução**:
1. Verifique se sensores estão ativos
2. Adicione `location_id` válido
3. Aguarde 2 segundos após carregamento

### Heatmap vazio

**Causa**: Sem dados no período selecionado  
**Solução**:
1. Verifique se sensores estão coletando dados
2. Tente período maior (7d ou 30d)
3. Verifique logs do console (F12)

### Timeline não carrega dados

**Causa**: API de dados históricos indisponível  
**Solução**:
1. Abra console do navegador (F12)
2. Verifique erros de rede
3. Confirme que tem dados históricos no banco

---

## 📚 Recursos Adicionais

- **Documentação Completa**: [TWINZO_FEATURES_V2.3.md](docs/TWINZO_FEATURES_V2.3.md)
- **Changelog**: [CHANGELOG_v2.3.0.md](CHANGELOG_v2.3.0.md)
- **Deploy**: [RENDER_DEPLOY_V2.2.md](docs/RENDER_DEPLOY_V2.2.md)
- **API Docs**: `/api/docs/` (no seu servidor)

---

## 🤝 Suporte

**Problemas ou Dúvidas?**
- Abra issue no GitHub
- Consulte documentação completa
- Verifique console do navegador para erros

---

**Desenvolvido com ❤️ para transformar dados industriais em insights acionáveis!**

*Versão: 2.3.0 | Data: Outubro 2024*

