# 🚀 Guia Rápido de Início - IARTES

## Instalação Rápida

### 1. Preparar Ambiente

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Executar Demo Básico

```bash
python examples/demo_basic.py
```

Este exemplo demonstra:
- ✓ Criação de casos de teste
- ✓ Geração de recomendação de ordenação
- ✓ Simulação de feedback
- ✓ Salvamento do modelo

### 3. Treinar Modelo com Dados Sintéticos

```bash
python examples/advanced_training.py
```

Este exemplo:
- ✓ Gera 10 suítes sintéticas com 15 testes cada
- ✓ Simula execuções e coleta feedback
- ✓ Treina o modelo de ML
- ✓ Compara modelo treinado vs. heurística
- ✓ Salva modelo treinado

## Uso no Seu Projeto

### 1. Criar Seus Casos de Teste

```python
from src.models.test_case import TestCase, Action, ActionType, ActionImpact

# Definir uma ação
action = Action(
    id="A001",
    description="Fazer login no sistema",
    action_type=ActionType.CREATION,
    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
    postconditions={"user_logged_in"},
    estimated_time=5.0
)

# Criar caso de teste
test_case = TestCase(
    id="TC001",
    name="Test Login",
    description="Verifica funcionalidade de login",
    priority=5,
    module="Authentication",
    actions=[action]
)
```

### 2. Obter Recomendação

```python
from src.recommender.ml_recommender import MLTestRecommender

# Criar recomendador
recommender = MLTestRecommender()

# Lista de testes
test_cases = [test1, test2, test3, ...]

# Obter recomendação
recommendation = recommender.recommend_order(test_cases)

# Ver ordem sugerida
print(recommendation.recommended_order)
```

### 3. Fornecer Feedback

```python
from src.models.test_case import ExecutionFeedback
from datetime import datetime

# Após executar um teste
feedback = ExecutionFeedback(
    test_case_id="TC001",
    executed_at=datetime.now(),
    actual_execution_time=5.2,
    success=True,
    followed_recommendation=True,
    tester_rating=5,
    required_reset=False
)

# Adicionar feedback ao modelo
recommender.add_feedback(feedback, test_cases)
```

### 4. Salvar/Carregar Modelo

```python
# Salvar modelo treinado
recommender.save_model("models/my_model.pkl")

# Carregar modelo
recommender.load_model("models/my_model.pkl")
```

## Estrutura do Projeto

```
IARTES/
├── src/
│   ├── models/              # Modelos de dados
│   │   └── test_case.py
│   ├── features/            # Extração de features
│   │   └── feature_extractor.py
│   ├── recommender/         # Sistema de recomendação
│   │   └── ml_recommender.py
│   └── utils/              # Utilitários
│       └── data_generator.py
├── examples/               # Exemplos de uso
│   ├── demo_basic.py
│   └── advanced_training.py
├── models/                # Modelos salvos (.pkl)
├── requirements.txt       # Dependências
└── README.md             # Documentação completa
```

## Próximos Passos

1. **Adapte para seu domínio**: Modifique os módulos, ações e tipos conforme necessário
2. **Integre com suas ferramentas**: TestRail, Jira, etc.
3. **Colete feedback real**: Quanto mais feedback, melhor o modelo
4. **Monitore métricas**: Acompanhe tempo, resets e satisfação

## Dúvidas?

Consulte o [README.md](README.md) completo para documentação detalhada.

## Exemplo Completo

```python
# 1. Imports
from src.models.test_case import TestCase, Action, ActionType, ActionImpact
from src.recommender.ml_recommender import MLTestRecommender
from src.models.test_case import ExecutionFeedback
from datetime import datetime

# 2. Criar testes (exemplo simplificado)
test1 = TestCase(id="TC001", name="Login", module="Auth", 
                 priority=5, actions=[...])
test2 = TestCase(id="TC002", name="Create Product", module="Products",
                 priority=4, actions=[...])
test3 = TestCase(id="TC003", name="View Products", module="Products",
                 priority=3, actions=[...])

# 3. Obter recomendação
recommender = MLTestRecommender()
recommendation = recommender.recommend_order([test1, test2, test3])

print(f"Ordem sugerida: {recommendation.recommended_order}")
print(f"Confiança: {recommendation.confidence_score:.1%}")

# 4. Executar testes na ordem sugerida e dar feedback
for test_id in recommendation.recommended_order:
    # Executar teste...
    
    # Dar feedback
    feedback = ExecutionFeedback(
        test_case_id=test_id,
        executed_at=datetime.now(),
        actual_execution_time=10.0,
        success=True,
        followed_recommendation=True,
        tester_rating=5
    )
    recommender.add_feedback(feedback, [test1, test2, test3])

# 5. Salvar modelo
recommender.save_model("models/my_recommender.pkl")
```

Bons testes! 🎯
