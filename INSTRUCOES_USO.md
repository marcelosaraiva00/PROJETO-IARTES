# 📘 INSTRUÇÕES DE USO - SISTEMA IARTES

## 🎯 O Que Foi Desenvolvido

Um **sistema completo de Machine Learning** que:
- ✅ Ordena casos de teste manuais de forma inteligente
- ✅ Reduz tempo de execução e reinicializações
- ✅ Aprende com feedback humano
- ✅ Melhora progressivamente a cada uso

---

## ⚡ Início Rápido (3 minutos)

### 1️⃣ Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2️⃣ Testar Instalação
```bash
python test_install.py
```

Se tudo estiver ✅, prossiga!

### 3️⃣ Executar Demo
```bash
python examples/demo_basic.py
```

Isso mostra o sistema funcionando com dados de exemplo.

---

## 📚 Opções de Uso

### Opção A: Demo Básico (Entender o Sistema)
```bash
python examples/demo_basic.py
```

**O que faz:**
- Cria 5 casos de teste de exemplo
- Gera recomendação de ordenação
- Simula feedback
- Salva modelo

**Tempo:** ~30 segundos

---

### Opção B: Treinamento Avançado (Treinar o Modelo)
```bash
python examples/advanced_training.py
```

**O que faz:**
- Gera 10 suítes com 15 testes cada (150 testes)
- Simula 150 execuções com feedback
- Treina modelo de ML
- Compara desempenho: modelo vs. heurística
- Salva modelo treinado

**Tempo:** ~2-3 minutos

---

### Opção C: Integração Real (Usar seus Testes)
```bash
python examples/integrate_real_tests.py
```

**O que faz:**
- Template para integrar com seus dados
- Coleta feedback interativo
- Salva modelo personalizado

**Adapte o código conforme seus dados!**

---

## 🔧 Como Integrar com Seus Testes

### Passo 1: Preparar Seus Dados

Edite `examples/integrate_real_tests.py`:

```python
def load_your_tests() -> List[TestCase]:
    # OPÇÃO 1: Carregar de JSON
    import json
    with open('meus_testes.json', 'r') as f:
        data = json.load(f)
        return [convert_from_your_format(test) for test in data]
    
    # OPÇÃO 2: Carregar de CSV
    # import csv
    # ...
    
    # OPÇÃO 3: Carregar de API (TestRail, Jira, etc.)
    # import requests
    # ...
```

### Passo 2: Adaptar Formato de Dados

```python
def convert_from_your_format(your_data: dict) -> TestCase:
    """Adapte conforme sua estrutura de dados"""
    return TestCase(
        id=your_data['id'],
        name=your_data['name'],
        # ... mapear seus campos
    )
```

### Passo 3: Executar

```bash
python examples/integrate_real_tests.py
```

---

## 💡 Usando Programaticamente

### Código Mínimo

```python
from src.models.test_case import TestCase, Action, ActionType, ActionImpact
from src.recommender.ml_recommender import MLTestRecommender

# 1. Criar ou carregar seus testes
meus_testes = [...]  # Lista de TestCase

# 2. Criar recomendador
recommender = MLTestRecommender()

# 3. Obter recomendação
recomendacao = recommender.recommend_order(meus_testes)

# 4. Ver ordem sugerida
print(recomendacao.recommended_order)  # ['TC001', 'TC003', 'TC002', ...]
print(f"Confiança: {recomendacao.confidence_score:.1%}")
print(f"Tempo estimado: {recomendacao.estimated_total_time:.1f}s")
```

### Dar Feedback

```python
from src.models.test_case import ExecutionFeedback
from datetime import datetime

# Após executar um teste
feedback = ExecutionFeedback(
    test_case_id="TC001",
    executed_at=datetime.now(),
    actual_execution_time=7.5,  # tempo real
    success=True,               # passou?
    followed_recommendation=True, # seguiu ordem?
    tester_rating=5,            # 1-5 estrelas
    required_reset=False,       # precisou reiniciar?
    notes="Executou perfeitamente"
)

recommender.add_feedback(feedback, meus_testes)
```

### Salvar/Carregar Modelo

```python
# Salvar
recommender.save_model("meu_modelo.pkl")

# Carregar
recommender.load_model("meu_modelo.pkl")
```

---

## 📊 Estrutura dos Dados

### Criar uma Ação

```python
from src.models.test_case import Action, ActionType, ActionImpact

acao = Action(
    id="A001",
    description="Inserir username",
    action_type=ActionType.CREATION,  # CREATION, VERIFICATION, etc.
    impact=ActionImpact.DESTRUCTIVE,  # NON_DESTRUCTIVE, DESTRUCTIVE, etc.
    preconditions={"on_login_page"},  # Estados necessários
    postconditions={"username_entered"},  # Estados resultantes
    estimated_time=3.0,  # segundos
    priority=4,
    tags={"input", "authentication"}
)
```

### Criar um Teste

```python
from src.models.test_case import TestCase

teste = TestCase(
    id="TC001",
    name="Test Login",
    description="Verifica login com credenciais válidas",
    actions=[acao1, acao2, acao3],  # Lista de ações
    priority=5,  # 1-5
    module="Authentication",
    tags={"login", "critical"},
    dependencies={"TC000"}  # IDs de testes que devem executar antes
)
```

---

## 🎓 Tipos de Ação e Impacto

### Tipos de Ação (ActionType)

| Tipo | Quando Usar | Exemplo |
|------|-------------|---------|
| `NAVIGATION` | Navegar entre telas | "Ir para página de produtos" |
| `CREATION` | Criar dados | "Criar novo usuário" |
| `VERIFICATION` | Verificar algo | "Verificar mensagem exibida" |
| `MODIFICATION` | Modificar dados | "Editar perfil do usuário" |
| `DELETION` | Deletar dados | "Remover produto" |

### Impacto no Estado (ActionImpact)

| Impacto | Descrição | Exemplos |
|---------|-----------|----------|
| `NON_DESTRUCTIVE` | Não altera estado | Verificações, navegação |
| `PARTIALLY_DESTRUCTIVE` | Altera parcialmente | Edições, atualizações |
| `DESTRUCTIVE` | Altera completamente | Criações, deleções |

**💡 Dica:** O sistema prioriza ações não-destrutivas antes de destrutivas no mesmo módulo!

---

## 🔍 Monitoramento e Métricas

### Ver Estatísticas do Modelo

```python
print(f"Modelo treinado: {recommender.is_trained}")
print(f"Feedbacks coletados: {len(recommender.feedback_history)}")
print(f"Amostras de treinamento: {len(recommender.training_data['y'])}")
```

### Interpretar Recomendação

```python
recomendacao = recommender.recommend_order(testes)

# Confiança
if recomendacao.confidence_score > 0.8:
    print("✅ Alta confiança - modelo bem treinado")
elif recomendacao.confidence_score > 0.6:
    print("⚠️  Confiança média - mais dados ajudariam")
else:
    print("⏳ Baixa confiança - modelo ainda aprendendo")

# Método usado
print(f"Método: {recomendacao.reasoning['method']}")
# 'heuristic' = heurísticas inteligentes
# 'ml' = machine learning treinado
```

---

## ❓ FAQ

### P: Preciso de muitos dados para começar?
**R:** Não! O sistema usa heurísticas inteligentes quando não treinado. Com apenas 10-20 feedbacks já começa a melhorar significativamente.

### P: Como o sistema aprende?
**R:** Com seu feedback! Cada vez que você executa testes e fornece feedback (tempo, sucesso, rating), o modelo aprende.

### P: Posso usar sem Machine Learning?
**R:** Sim! As heurísticas funcionam muito bem. O ML é um "plus" que melhora com o tempo.

### P: Funciona com testes automatizados?
**R:** O foco são testes manuais, mas os princípios se aplicam. Para automatizados, considere ferramentas específicas.

### P: Como adaptar para minha ferramenta (Jira, TestRail)?
**R:** Edite `load_your_tests()` em `integrate_real_tests.py` para ler da API da sua ferramenta.

---

## 🆘 Troubleshooting

### Erro: ModuleNotFoundError
```bash
# Instalar dependências
pip install -r requirements.txt
```

### Erro: No module named 'src'
```bash
# Execute do diretório raiz do projeto
cd IARTES
python examples/demo_basic.py
```

### Modelo não melhora
- **Solução:** Forneça mais feedback variado
- **Dica:** Execute pelo menos 10-20 feedbacks antes de avaliar

### Recomendações estranhas
- **Causa:** Dependências inconsistentes
- **Solução:** Verifique se as dependências entre testes estão corretas

---

## 📞 Próximos Passos

1. ✅ Execute o demo básico
2. ✅ Execute o treinamento avançado  
3. ✅ Adapte para seus testes
4. ✅ Colete feedback real
5. ✅ Monitore melhorias

---

## 📖 Documentação Adicional

- `README.md` - Documentação técnica completa
- `QUICK_START.md` - Guia de início rápido
- `PROJETO_DESENVOLVIDO.md` - Detalhes da implementação
- Código comentado em todos os módulos

---

**Desenvolvido para:** Projeto de Pesquisa IARTES  
**Autor:** Marcelo dos Santos Saraiva Junior  
**Data:** Janeiro 2026

**Bons testes! 🚀**
