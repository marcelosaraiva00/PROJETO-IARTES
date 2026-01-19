"""
Exemplo: Como integrar com seus casos de teste reais
Template para adaptação
"""
import sys
from pathlib import Path

# Adicionar o diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from datetime import datetime
from typing import List
from src.models.test_case import (
    TestCase, Action, TestSuite,
    ActionType, ActionImpact, ExecutionFeedback
)
from src.recommender.ml_recommender import MLTestRecommender


# ============================================================================
# PASSO 1: ADAPTAR SEUS DADOS PARA O FORMATO DO SISTEMA
# ============================================================================

def convert_from_your_format(your_test_data: dict) -> TestCase:
    """
    Converte dados do seu formato atual para TestCase
    
    ADAPTE esta função conforme sua estrutura de dados atual
    (ex: JSON, CSV, API de TestRail, Jira, etc.)
    """
    
    # Exemplo: seus dados podem vir assim
    # your_test_data = {
    #     'id': 'TEST-123',
    #     'name': 'Verificar Login',
    #     'module': 'Authentication',
    #     'priority': 'High',
    #     'steps': [
    #         {'step': 'Abrir página de login', 'type': 'navigation'},
    #         {'step': 'Inserir credenciais', 'type': 'input'},
    #         {'step': 'Verificar sucesso', 'type': 'verification'},
    #     ]
    # }
    
    # Converter prioridade para número
    priority_map = {
        'Critical': 5,
        'High': 4,
        'Medium': 3,
        'Low': 2,
        'Trivial': 1
    }
    priority = priority_map.get(your_test_data.get('priority', 'Medium'), 3)
    
    # Converter steps para Actions
    actions = []
    for idx, step in enumerate(your_test_data.get('steps', []), 1):
        # Mapear tipo de step para ActionType
        step_type_map = {
            'navigation': ActionType.NAVIGATION,
            'input': ActionType.CREATION,
            'verification': ActionType.VERIFICATION,
            'update': ActionType.MODIFICATION,
            'delete': ActionType.DELETION,
        }
        
        action_type = step_type_map.get(
            step.get('type', 'verification'),
            ActionType.VERIFICATION
        )
        
        # Determinar impacto
        if action_type == ActionType.VERIFICATION:
            impact = ActionImpact.NON_DESTRUCTIVE
        elif action_type in [ActionType.CREATION, ActionType.DELETION]:
            impact = ActionImpact.DESTRUCTIVE
        else:
            impact = ActionImpact.PARTIALLY_DESTRUCTIVE
        
        action = Action(
            id=f"{your_test_data['id']}_A{idx:03d}",
            description=step.get('step', ''),
            action_type=action_type,
            impact=impact,
            estimated_time=step.get('estimated_time', 5.0),
            priority=priority
        )
        actions.append(action)
    
    # Criar TestCase
    test_case = TestCase(
        id=your_test_data['id'],
        name=your_test_data['name'],
        description=your_test_data.get('description', ''),
        actions=actions,
        priority=priority,
        module=your_test_data.get('module', 'Unknown'),
        tags=set(your_test_data.get('tags', []))
    )
    
    return test_case


# ============================================================================
# PASSO 2: CARREGAR SEUS TESTES REAIS
# ============================================================================

def load_your_tests() -> List[TestCase]:
    """
    Carrega seus casos de teste do seu sistema/formato
    
    ADAPTE esta função conforme sua fonte de dados:
    - Banco de dados
    - Arquivos JSON/CSV
    - API (TestRail, Jira, etc.)
    - Planilhas Excel
    """
    
    # EXEMPLO 1: Carregando de JSON
    # import json
    # with open('my_tests.json', 'r') as f:
    #     data = json.load(f)
    #     return [convert_from_your_format(test) for test in data['tests']]
    
    # EXEMPLO 2: Carregando de CSV
    # import csv
    # tests = []
    # with open('my_tests.csv', 'r') as f:
    #     reader = csv.DictReader(f)
    #     for row in reader:
    #         tests.append(convert_from_your_format(row))
    # return tests
    
    # EXEMPLO 3: Carregando de API
    # import requests
    # response = requests.get('https://api.example.com/tests')
    # data = response.json()
    # return [convert_from_your_format(test) for test in data['tests']]
    
    # Para este exemplo, vamos criar alguns testes manualmente
    example_tests = [
        {
            'id': 'TEST-001',
            'name': 'Verificar Login com Credenciais Válidas',
            'module': 'Authentication',
            'priority': 'Critical',
            'description': 'Testa login com usuário e senha válidos',
            'steps': [
                {'step': 'Navegar para página de login', 'type': 'navigation', 'estimated_time': 2.0},
                {'step': 'Inserir username válido', 'type': 'input', 'estimated_time': 3.0},
                {'step': 'Inserir senha válida', 'type': 'input', 'estimated_time': 2.0},
                {'step': 'Clicar em Login', 'type': 'input', 'estimated_time': 1.0},
                {'step': 'Verificar redirecionamento para dashboard', 'type': 'verification', 'estimated_time': 2.0},
            ],
            'tags': ['login', 'smoke', 'critical']
        },
        {
            'id': 'TEST-002',
            'name': 'Criar Novo Produto',
            'module': 'Products',
            'priority': 'High',
            'description': 'Testa criação de produto no sistema',
            'steps': [
                {'step': 'Navegar para lista de produtos', 'type': 'navigation', 'estimated_time': 2.0},
                {'step': 'Clicar em Novo Produto', 'type': 'navigation', 'estimated_time': 1.0},
                {'step': 'Preencher nome do produto', 'type': 'input', 'estimated_time': 3.0},
                {'step': 'Preencher descrição', 'type': 'input', 'estimated_time': 4.0},
                {'step': 'Definir preço', 'type': 'input', 'estimated_time': 2.0},
                {'step': 'Salvar produto', 'type': 'input', 'estimated_time': 2.0},
                {'step': 'Verificar produto na lista', 'type': 'verification', 'estimated_time': 3.0},
            ],
            'tags': ['products', 'crud', 'create']
        },
        {
            'id': 'TEST-003',
            'name': 'Visualizar Detalhes do Produto',
            'module': 'Products',
            'priority': 'Medium',
            'description': 'Visualiza informações de um produto existente',
            'steps': [
                {'step': 'Navegar para lista de produtos', 'type': 'navigation', 'estimated_time': 2.0},
                {'step': 'Selecionar um produto', 'type': 'navigation', 'estimated_time': 2.0},
                {'step': 'Verificar nome exibido', 'type': 'verification', 'estimated_time': 1.0},
                {'step': 'Verificar descrição exibida', 'type': 'verification', 'estimated_time': 1.0},
                {'step': 'Verificar preço exibido', 'type': 'verification', 'estimated_time': 1.0},
            ],
            'tags': ['products', 'read', 'view']
        },
    ]
    
    return [convert_from_your_format(test) for test in example_tests]


# ============================================================================
# PASSO 3: COLETAR FEEDBACK REAL
# ============================================================================

def collect_feedback_interactive(test_case: TestCase) -> ExecutionFeedback:
    """
    Coleta feedback interativo do testador após execução
    
    ADAPTE conforme sua interface (pode ser CLI, web, etc.)
    """
    print(f"\n📋 Feedback para: {test_case.name}")
    print("─" * 60)
    
    # Tempo real de execução
    try:
        actual_time = float(input("⏱️  Tempo real de execução (segundos): "))
    except ValueError:
        actual_time = test_case.get_total_estimated_time()
    
    # Sucesso
    success_input = input("✅ Teste passou? (s/n): ").lower()
    success = success_input == 's'
    
    # Seguiu recomendação
    followed_input = input("🎯 Seguiu a ordem recomendada? (s/n): ").lower()
    followed = followed_input == 's'
    
    # Rating
    try:
        rating = int(input("⭐ Avaliação da execução (1-5): "))
        rating = max(1, min(5, rating))  # Garantir entre 1 e 5
    except ValueError:
        rating = 3
    
    # Reset necessário
    reset_input = input("🔄 Precisou reinicializar o sistema? (s/n): ").lower()
    required_reset = reset_input == 's'
    
    # Notas
    notes = input("📝 Observações (opcional): ")
    
    return ExecutionFeedback(
        test_case_id=test_case.id,
        executed_at=datetime.now(),
        actual_execution_time=actual_time,
        success=success,
        followed_recommendation=followed,
        tester_rating=rating,
        required_reset=required_reset,
        notes=notes
    )


# ============================================================================
# PASSO 4: WORKFLOW COMPLETO
# ============================================================================

def main():
    """Workflow completo de integração"""
    print("=" * 80)
    print("INTEGRAÇÃO COM CASOS DE TESTE REAIS")
    print("=" * 80)
    print()
    
    # 1. Carregar testes
    print("📂 Carregando casos de teste...")
    test_cases = load_your_tests()
    print(f"✓ {len(test_cases)} testes carregados")
    print()
    
    # Mostrar testes carregados
    print("Testes carregados:")
    for tc in test_cases:
        print(f"  • {tc.id} - {tc.name} ({tc.module})")
    print()
    
    # 2. Criar/Carregar recomendador
    print("🤖 Inicializando recomendador...")
    recommender = MLTestRecommender()
    
    # Tentar carregar modelo existente
    try:
        recommender.load_model("models/my_real_tests_model.pkl")
        print("✓ Modelo existente carregado")
    except FileNotFoundError:
        print("✓ Novo modelo inicializado (será treinado com feedback)")
    print()
    
    # 3. Obter recomendação
    print("🎯 Gerando recomendação de ordenação...")
    recommendation = recommender.recommend_order(test_cases)
    
    print(f"\n📊 Recomendação:")
    print(f"  - Confiança: {recommendation.confidence_score:.1%}")
    print(f"  - Tempo total estimado: {recommendation.estimated_total_time:.1f}s")
    print(f"  - Resets estimados: {recommendation.estimated_resets}")
    print()
    
    print("📝 Ordem sugerida:")
    for idx, test_id in enumerate(recommendation.recommended_order, 1):
        test = next(tc for tc in test_cases if tc.id == test_id)
        print(f"  {idx}. {test.id} - {test.name}")
        print(f"     └─ Tempo: {test.get_total_estimated_time():.1f}s | " +
              f"Ações: {len(test.actions)} | Prioridade: {test.priority}")
    print()
    
    # 4. Executar testes (simulado/real)
    print("🧪 Executando testes...")
    print("(Execute seus testes na ordem recomendada)")
    print()
    
    # Modo interativo ou automático
    mode = input("Coletar feedback agora? (s/n): ").lower()
    
    if mode == 's':
        # Organizar testes na ordem recomendada
        ordered_tests = [
            tc for tc in test_cases 
            if tc.id in recommendation.recommended_order
        ]
        
        feedbacks = []
        for test in ordered_tests:
            feedback = collect_feedback_interactive(test)
            feedbacks.append(feedback)
            recommender.add_feedback(feedback, ordered_tests)
            print("✓ Feedback registrado")
        
        # 5. Salvar modelo atualizado
        print("\n💾 Salvando modelo...")
        recommender.save_model("models/my_real_tests_model.pkl")
        print("✓ Modelo salvo!")
        
        # Estatísticas
        print("\n📈 Estatísticas da execução:")
        avg_rating = sum(f.tester_rating for f in feedbacks) / len(feedbacks)
        success_rate = sum(1 for f in feedbacks if f.success) / len(feedbacks)
        num_resets = sum(1 for f in feedbacks if f.required_reset)
        
        print(f"  - Rating médio: {avg_rating:.2f}/5")
        print(f"  - Taxa de sucesso: {success_rate:.1%}")
        print(f"  - Resets necessários: {num_resets}")
    
    print()
    print("=" * 80)
    print("✅ PROCESSO CONCLUÍDO!")
    print("=" * 80)
    print()
    print("💡 Dicas:")
    print("  - Execute este script regularmente para melhorar o modelo")
    print("  - Quanto mais feedback, melhores as recomendações")
    print("  - O modelo se adapta ao seu estilo de teste")
    print()


if __name__ == "__main__":
    main()
