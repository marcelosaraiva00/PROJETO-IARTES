# 📱 CENÁRIOS DE TESTE MOTOROLA - DOCUMENTAÇÃO COMPLETA

## 📊 Visão Geral da Suíte

**Total:** 20 casos de teste  
**Total de ações:** 88 passos  
**Tempo estimado:** 6.7 minutos  
**Módulos cobertos:** 11

---

## 🎯 MÓDULOS E CENÁRIOS

### 1️⃣ SETUP E CONFIGURAÇÃO INICIAL (1 teste)

#### ✅ MOTO_SETUP_001 - Configuração Inicial do Dispositivo
**Prioridade:** 5 (Crítico) | **Tempo:** 53s | **Ações:** 5

**O que testa:**
- Ligar dispositivo pela primeira vez
- Selecionar idioma (Português Brasil)
- Conectar WiFi
- Login com Google Account
- Verificar tela inicial configurada

**Por que é importante:**
- Pré-requisito de todos os outros testes
- Valida processo OOBE (Out of Box Experience)
- Crítico para satisfação do cliente

---

### 2️⃣ CÂMERA (3 testes)

#### 📷 MOTO_CAM_001 - Captura de Foto Modo Normal
**Prioridade:** 5 (Crítico) | **Tempo:** 10s | **Ações:** 4

**O que testa:**
- Abrir app câmera
- Modo foto selecionado
- Capturar foto
- Verificar foto salva na galeria

**Funcionalidade testada:** Câmera básica (smoke test)

---

#### 📷 MOTO_CAM_002 - Câmera Modo Retrato
**Prioridade:** 4 (Alto) | **Tempo:** 14s | **Ações:** 4

**O que testa:**
- Alternar para modo retrato
- Enquadrar pessoa
- Capturar foto com bokeh
- Verificar efeito de desfoque aplicado

**Funcionalidade testada:** IA de reconhecimento + efeito bokeh

---

#### 📷 MOTO_CAM_003 - Gravação de Vídeo Full HD
**Prioridade:** 4 (Alto) | **Tempo:** 23s | **Ações:** 6

**O que testa:**
- Alternar para modo vídeo
- Configurar resolução 1080p
- Iniciar gravação
- Gravar por 10 segundos
- Parar gravação
- Verificar vídeo salvo

**Funcionalidade testada:** Gravação de vídeo + codecs

---

### 3️⃣ CONECTIVIDADE (3 testes)

#### 📡 MOTO_WIFI_001 - Conexão WiFi 2.4GHz
**Prioridade:** 5 (Crítico) | **Tempo:** 22s | **Ações:** 5

**O que testa:**
- Abrir configurações WiFi
- Selecionar rede 2.4GHz
- Inserir senha
- Estabelecer conexão
- Verificar conexão ativa

**Funcionalidade testada:** Conectividade WiFi básica

---

#### 📡 MOTO_WIFI_002 - Navegação Web via WiFi
**Prioridade:** 3 (Médio) | **Tempo:** 11s | **Ações:** 3

**Dependência:** MOTO_WIFI_001

**O que testa:**
- Abrir Chrome
- Acessar google.com
- Verificar página carregada

**Funcionalidade testada:** Internet funcional + DNS

---

#### 📡 MOTO_BT_001 - Pareamento Bluetooth com Fone
**Prioridade:** 4 (Alto) | **Tempo:** 26s | **Ações:** 5

**O que testa:**
- Ativar Bluetooth
- Colocar fone em modo pareamento
- Buscar dispositivos
- Parear com fone
- Verificar pareamento concluído

**Funcionalidade testada:** Bluetooth + pareamento de áudio

---

### 4️⃣ BATERIA E ENERGIA (2 testes)

#### 🔋 MOTO_BAT_001 - Carregamento de Bateria
**Prioridade:** 5 (Crítico) | **Tempo:** 67s | **Ações:** 4

**O que testa:**
- Verificar nível atual
- Conectar carregador USB-C
- Verificar ícone de carregamento
- Aguardar 1 minuto e verificar incremento

**Funcionalidade testada:** Sistema de carregamento + detecção USB-C

---

#### 🔋 MOTO_BAT_002 - Modo Economia de Bateria
**Prioridade:** 3 (Médio) | **Tempo:** 7s | **Ações:** 3

**O que testa:**
- Abrir configurações bateria
- Ativar economia de bateria
- Verificar indicador visual

**Funcionalidade testada:** Gerenciamento de energia

---

### 5️⃣ CHAMADAS E TELEFONIA (2 testes)

#### 📞 MOTO_CALL_001 - Realizar Chamada de Voz
**Prioridade:** 5 (Crítico) | **Tempo:** 16s | **Ações:** 5

**O que testa:**
- Abrir app Telefone
- Digitar número
- Iniciar chamada
- Verificar chamada ativa
- Encerrar chamada

**Funcionalidade testada:** Chamadas de voz (core feature)

---

#### 📞 MOTO_CALL_002 - Receber Chamada
**Prioridade:** 5 (Crítico) | **Tempo:** 19s | **Ações:** 4

**O que testa:**
- Aguardar chamada de entrada
- Verificar tela de chamada recebida
- Atender com swipe
- Verificar áudio funcionando

**Funcionalidade testada:** Recebimento de chamadas + UI

---

### 6️⃣ MENSAGENS SMS (1 teste)

#### 💬 MOTO_SMS_001 - Enviar SMS
**Prioridade:** 4 (Alto) | **Tempo:** 24s | **Ações:** 6

**O que testa:**
- Abrir app Mensagens
- Criar nova mensagem
- Inserir destinatário
- Digitar texto
- Enviar mensagem
- Verificar envio confirmado

**Funcionalidade testada:** SMS (core feature)

---

### 7️⃣ SEGURANÇA E BIOMETRIA (2 testes)

#### 🔒 MOTO_SEC_001 - Cadastrar Impressão Digital
**Prioridade:** 4 (Alto) | **Tempo:** 39s | **Ações:** 5

**O que testa:**
- Abrir configurações segurança
- Navegar para impressão digital
- Iniciar cadastro
- Escanear dedo múltiplas vezes
- Verificar cadastro concluído

**Funcionalidade testada:** Sensor biométrico + cadastro

---

#### 🔒 MOTO_SEC_002 - Desbloqueio com Impressão Digital
**Prioridade:** 4 (Alto) | **Tempo:** 6s | **Ações:** 4

**Dependência:** MOTO_SEC_001

**O que testa:**
- Bloquear dispositivo
- Acordar tela
- Posicionar dedo no sensor
- Verificar desbloqueio

**Funcionalidade testada:** Autenticação biométrica

---

### 8️⃣ GESTOS MOTO (Moto Actions) (2 testes)

#### ✋ MOTO_GESTURE_001 - Chacoalhar para Lanterna
**Prioridade:** 3 (Médio) | **Tempo:** 10s | **Ações:** 4

**O que testa:**
- Ativar Moto Actions
- Tela desligada
- Chacoalhar 2x rapidamente
- Verificar lanterna ativada

**Funcionalidade testada:** Gesto exclusivo Motorola + acelerômetro

---

#### ✋ MOTO_GESTURE_002 - Girar para Câmera
**Prioridade:** 3 (Médio) | **Tempo:** 6s | **Ações:** 3

**Dependência:** MOTO_GESTURE_001

**O que testa:**
- Dispositivo bloqueado
- Girar punho 2x rapidamente
- Verificar câmera aberta

**Funcionalidade testada:** Gesto exclusivo Motorola (Quick Capture)

---

### 9️⃣ MULTIMÍDIA - ÁUDIO (1 teste)

#### 🎵 MOTO_AUDIO_001 - Reprodução de Música
**Prioridade:** 3 (Médio) | **Tempo:** 21s | **Ações:** 5

**O que testa:**
- Abrir app música
- Selecionar faixa
- Reproduzir música
- Verificar áudio no alto-falante
- Ajustar volume

**Funcionalidade testada:** Reprodução de áudio + alto-falante

---

### 🔟 PERFORMANCE E ARMAZENAMENTO (2 testes)

#### ⚡ MOTO_PERF_001 - Verificar Armazenamento
**Prioridade:** 2 (Baixo) | **Tempo:** 9s | **Ações:** 3

**O que testa:**
- Abrir configurações
- Navegar para armazenamento
- Verificar espaço total e disponível

**Funcionalidade testada:** Gerenciamento de storage

---

#### ⚡ MOTO_PERF_002 - Multitarefa
**Prioridade:** 3 (Médio) | **Tempo:** 12s | **Ações:** 6

**O que testa:**
- Abrir Câmera
- Voltar para home
- Abrir Chrome
- Abrir menu recentes
- Trocar para Câmera
- Verificar estado preservado

**Funcionalidade testada:** Gerenciamento de memória + multitarefa

---

### 1️⃣1️⃣ DISPLAY (1 teste)

#### 🖥️ MOTO_DISP_001 - Ajustar Brilho
**Prioridade:** 2 (Baixo) | **Tempo:** 6s | **Ações:** 4

**O que testa:**
- Deslizar barra notificações
- Verificar controle de brilho
- Ajustar para 50%
- Verificar mudança visual

**Funcionalidade testada:** Controle de backlight

---

## 🎯 ORDEM RECOMENDADA PELO SISTEMA

O sistema analisou as **dependências** e **impactos** e sugeriu esta ordem:

### 📈 Lógica da Recomendação:

1. **SETUP primeiro** → Base de tudo
2. **Testes críticos (prioridade 5)** → Camera, WiFi, Bateria, Chamadas
3. **Testes de alta prioridade (4)** → Recursos importantes
4. **Testes médios (3)** → Funcionalidades complementares
5. **Testes baixos (2)** → Verificações simples

### 🔴🟢 Código de Cores:

- **🔴 Destrutivo:** Altera estado do sistema (maioria)
- **🟢 Não-destrutivo:** Apenas verifica (WiFi_002, PERF_001, PERF_002)

---

## 💡 COMO O MODELO APRENDE COM ESSES TESTES

### 📊 Dados que o Modelo Extrai:

1. **Features Textuais:**
   - Descrições (TF-IDF)
   - Tags (categorização)
   - Módulos (agrupamento)

2. **Features Numéricas:**
   - Número de ações
   - Tempo estimado
   - Prioridade
   - Quantidade de pré/pós-condições

3. **Features de Tipo:**
   - Tipos de ação (Navigation, Creation, Verification, etc.)
   - Impacto (Destrutivo vs Não-destrutivo)

4. **Features de Dependência:**
   - Testes que dependem de outros
   - Estados necessários
   - Estados resultantes

### 🧠 O Que o Modelo Aprenderá:

Quando você executar esses testes e fornecer feedback, o modelo aprenderá:

1. **Padrões de Sucesso:**
   - Setup deve ser sempre primeiro
   - Testes de conectividade antes de testes que usam internet
   - Cadastro de biometria antes de desbloqueio

2. **Tempo Real vs Estimado:**
   - Testes de câmera podem ser mais rápidos
   - Pareamento Bluetooth pode demorar mais
   - Carregamento de bateria depende do nível inicial

3. **Necessidade de Resets:**
   - Testes destrutivos podem corromper estado
   - Agrupar testes do mesmo módulo reduz resets
   - Testes de verificação não precisam de reset

4. **Preferências do Testador:**
   - Se você prefere testar módulos completos
   - Se você prefere intercalar testes críticos
   - Quais transições são mais naturais

---

## 🚀 PRÓXIMOS PASSOS

### Para Executar Esses Testes:

```bash
# 1. Gerar recomendação
python testes_motorola.py

# 2. Executar manualmente na ordem sugerida

# 3. Dar feedback (crie um script de feedback)
```

### Para Treinar o Modelo:

```python
from src.models.test_case import ExecutionFeedback
from src.recommender.ml_recommender import MLTestRecommender

recommender = MLTestRecommender()
recommender.load_model("models/motorola_modelo.pkl")

# Para cada teste executado:
feedback = ExecutionFeedback(
    test_case_id="MOTO_CAM_001",
    actual_execution_time=12.0,  # Tempo real
    success=True,
    followed_recommendation=True,
    tester_rating=5,
    required_reset=False
)

recommender.add_feedback(feedback, testes)
recommender.save_model("models/motorola_modelo.pkl")
```

---

## 📈 COBERTURA DE TESTES

### Funcionalidades Core (Críticas):
✅ Setup inicial  
✅ Câmera (foto)  
✅ WiFi  
✅ Chamadas (fazer e receber)  
✅ Bateria (carregamento)  

### Funcionalidades Importantes:
✅ Câmera (retrato e vídeo)  
✅ Bluetooth  
✅ SMS  
✅ Segurança biométrica  

### Funcionalidades Complementares:
✅ Gestos Moto  
✅ Multimídia  
✅ Performance  
✅ Display  

### Ainda Não Coberto (Sugestões para Expansão):
- 📶 Conectividade 5G/4G
- 📍 GPS e localização
- 📧 Email
- 🌐 NFC e pagamentos
- 📅 Calendário e Contatos
- 🔄 Atualizações de sistema
- 🎮 Jogos e performance gráfica
- 🔊 Gravação de áudio
- 📲 Notificações
- 🎨 Personalização (temas, wallpapers)

---

## 🎓 APRENDIZADOS DO MODELO POR FASE

### Fase 1 (0-5 feedbacks): Heurísticas
- Usa regras pré-definidas
- Prioriza por dependências
- Agrupa por módulo
- **Confiança:** 60%

### Fase 2 (5-20 feedbacks): Aprendizado Inicial
- Começa a identificar padrões
- Ajusta estimativas de tempo
- Aprende quais transições funcionam
- **Confiança:** 70-80%

### Fase 3 (20+ feedbacks): ML Completo
- Recomendações personalizadas
- Prediz necessidade de reset
- Otimiza para seu estilo de teste
- **Confiança:** 85-95%

---

**Total de cenários:** 20  
**Pronto para uso:** ✅  
**Modelo salvo:** `models/motorola_modelo.pkl`  
**Arquivo:** `testes_motorola.py`
