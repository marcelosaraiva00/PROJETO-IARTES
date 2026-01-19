"""
Exemplo básico de uso do sistema de recomendação
"""
import sys
from pathlib import Path

# Adicionar o diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from datetime import datetime, timedelta
from src.models.test_case import (
    TestCase, Action, TestSuite, ExecutionFeedback,
    ActionType, ActionImpact
)
from src.recommender.ml_recommender import MLTestRecommender


def create_sample_test_suite() -> TestSuite:
    """Cria uma suíte de teste de exemplo"""
    
    # Teste 1: Login (pré-requisito para outros)
    test_login = TestCase(
        id="TC001",
        name="Test Login",
        description="Testa funcionalidade de login",
        priority=5,
        module="Authentication",
        tags={"login", "auth"},
        actions=[
            Action(
                id="A001",
                description="Navegar para página de login",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                postconditions={"on_login_page"},
                estimated_time=2.0
            ),
            Action(
                id="A002",
                description="Inserir credenciais válidas",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"on_login_page"},
                postconditions={"credentials_entered"},
                estimated_time=3.0
            ),
            Action(
                id="A003",
                description="Verificar login bem-sucedido",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"credentials_entered"},
                postconditions={"user_logged_in"},
                estimated_time=2.0
            )
        ],
        average_execution_time=7.0,
        success_rate=0.98,
        last_executed=datetime.now() - timedelta(days=1)
    )
    
    # Teste 2: Criar Produto (requer login)
    test_create_product = TestCase(
        id="TC002",
        name="Test Create Product",
        description="Testa criação de novo produto",
        priority=4,
        module="Products",
        tags={"products", "create"},
        dependencies={"TC001"},  # Depende do login
        actions=[
            Action(
                id="A004",
                description="Navegar para página de produtos",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"user_logged_in"},
                postconditions={"on_products_page"},
                estimated_time=2.0
            ),
            Action(
                id="A005",
                description="Clicar em 'Novo Produto'",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"on_products_page"},
                postconditions={"on_new_product_form"},
                estimated_time=1.0
            ),
            Action(
                id="A006",
                description="Preencher dados do produto",
                action_type=ActionType.CREATION,
                impact=ActionImpact.DESTRUCTIVE,
                preconditions={"on_new_product_form"},
                postconditions={"product_data_entered"},
                estimated_time=5.0
            ),
            Action(
                id="A007",
                description="Salvar produto",
                action_type=ActionType.CREATION,
                impact=ActionImpact.DESTRUCTIVE,
                preconditions={"product_data_entered"},
                postconditions={"product_created"},
                estimated_time=3.0
            )
        ],
        average_execution_time=11.0,
        success_rate=0.95
    )
    
    # Teste 3: Visualizar Lista de Produtos (não destrutivo)
    test_view_products = TestCase(
        id="TC003",
        name="Test View Product List",
        description="Testa visualização da lista de produtos",
        priority=3,
        module="Products",
        tags={"products", "view"},
        dependencies={"TC001"},
        actions=[
            Action(
                id="A008",
                description="Navegar para lista de produtos",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"user_logged_in"},
                postconditions={"on_products_page"},
                estimated_time=2.0
            ),
            Action(
                id="A009",
                description="Verificar produtos existentes",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"on_products_page"},
                postconditions={"products_displayed"},
                estimated_time=3.0
            ),
            Action(
                id="A010",
                description="Verificar filtros funcionando",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"products_displayed"},
                estimated_time=4.0
            )
        ],
        average_execution_time=9.0,
        success_rate=0.99
    )
    
    # Teste 4: Editar Produto (requer produto criado)
    test_edit_product = TestCase(
        id="TC004",
        name="Test Edit Product",
        description="Testa edição de produto existente",
        priority=4,
        module="Products",
        tags={"products", "edit"},
        dependencies={"TC002"},  # Precisa ter produto criado
        actions=[
            Action(
                id="A011",
                description="Selecionar produto para editar",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"product_created"},
                postconditions={"product_selected"},
                estimated_time=2.0
            ),
            Action(
                id="A012",
                description="Modificar dados do produto",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.DESTRUCTIVE,
                preconditions={"product_selected"},
                postconditions={"product_modified"},
                estimated_time=4.0
            ),
            Action(
                id="A013",
                description="Salvar alterações",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.DESTRUCTIVE,
                preconditions={"product_modified"},
                postconditions={"product_updated"},
                estimated_time=2.0
            )
        ],
        average_execution_time=8.0,
        success_rate=0.92
    )
    
    # Teste 5: Deletar Produto
    test_delete_product = TestCase(
        id="TC005",
        name="Test Delete Product",
        description="Testa deleção de produto",
        priority=3,
        module="Products",
        tags={"products", "delete"},
        dependencies={"TC002"},
        actions=[
            Action(
                id="A014",
                description="Selecionar produto para deletar",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"product_created"},
                postconditions={"product_selected"},
                estimated_time=2.0
            ),
            Action(
                id="A015",
                description="Clicar em deletar",
                action_type=ActionType.DELETION,
                impact=ActionImpact.DESTRUCTIVE,
                preconditions={"product_selected"},
                postconditions={"deletion_confirmed"},
                estimated_time=1.0
            ),
            Action(
                id="A016",
                description="Confirmar deleção",
                action_type=ActionType.DELETION,
                impact=ActionImpact.DESTRUCTIVE,
                preconditions={"deletion_confirmed"},
                postconditions={"product_deleted"},
                estimated_time=2.0
            )
        ],
        average_execution_time=5.0,
        success_rate=0.97
    )
    
    # Criar suíte
    suite = TestSuite(
        id="TS001",
        name="Product Management Test Suite",
        description="Suíte completa para testes de gerenciamento de produtos",
        test_cases=[
            test_login,
            test_create_product,
            test_view_products,
            test_edit_product,
            test_delete_product
        ]
    )
    
    return suite


def main():
    """Função principal de demonstração"""
    print("=" * 80)
    print("SISTEMA DE RECOMENDAÇÃO ADAPTATIVO PARA ORDENAÇÃO DE CASOS DE TESTE")
    print("Projeto IARTES - Demo Básico")
    print("=" * 80)
    print()
    
    # Criar suíte de teste de exemplo
    print("📋 Criando suíte de teste de exemplo...")
    suite = create_sample_test_suite()
    print(f"✓ Suíte criada: {suite.name}")
    print(f"  - Total de testes: {suite.get_total_tests()}")
    print(f"  - Tempo estimado total: {suite.get_total_estimated_time():.1f}s")
    print()
    
    # Criar recomendador
    print("🤖 Inicializando sistema de recomendação...")
    recommender = MLTestRecommender(model_type='random_forest')
    print("✓ Recomendador inicializado (modo: heurístico)")
    print()
    
    # Obter recomendação inicial
    print("🎯 Gerando recomendação de ordenação...")
    recommendation = recommender.recommend_order(suite.test_cases)
    
    print("\n📊 RECOMENDAÇÃO GERADA:")
    print(f"  - Confiança: {recommendation.confidence_score:.1%}")
    print(f"  - Tempo estimado: {recommendation.estimated_total_time:.1f}s")
    print(f"  - Reinicializações estimadas: {recommendation.estimated_resets}")
    print(f"  - Método: {recommendation.reasoning['method']}")
    print()
    
    print("📝 Ordem recomendada:")
    for idx, test_id in enumerate(recommendation.recommended_order, 1):
        test = next(tc for tc in suite.test_cases if tc.id == test_id)
        destructive_marker = "🔴" if test.has_destructive_actions() else "🟢"
        print(f"  {idx}. {destructive_marker} {test_id} - {test.name}")
        print(f"     Módulo: {test.module} | Prioridade: {test.priority} | " +
              f"Tempo: {test.get_total_estimated_time():.1f}s")
    print()
    
    # Simular feedback de execução
    print("💬 Simulando feedback de execução...")
    
    # Feedback positivo para o primeiro teste
    feedback1 = ExecutionFeedback(
        test_case_id="TC001",
        executed_at=datetime.now(),
        actual_execution_time=7.2,
        success=True,
        followed_recommendation=True,
        tester_rating=5,
        required_reset=False,
        notes="Login funcionou perfeitamente"
    )
    
    ordered_tests = [tc for tc in suite.test_cases 
                     if tc.id in recommendation.recommended_order]
    recommender.add_feedback(feedback1, ordered_tests[:1])
    print("✓ Feedback adicionado para TC001")
    
    # Adicionar mais feedbacks simulados
    feedback2 = ExecutionFeedback(
        test_case_id="TC002",
        executed_at=datetime.now(),
        actual_execution_time=11.5,
        success=True,
        followed_recommendation=True,
        tester_rating=4,
        required_reset=False
    )
    recommender.add_feedback(feedback2, ordered_tests[:2])
    print("✓ Feedback adicionado para TC002")
    print()
    
    print("📈 Status do aprendizado:")
    print(f"  - Feedbacks coletados: {len(recommender.feedback_history)}")
    print(f"  - Amostras de treinamento: {len(recommender.training_data['y'])}")
    print(f"  - Modelo treinado: {recommender.is_trained}")
    print()
    
    # Salvar modelo
    print("💾 Salvando modelo...")
    recommender.save_model("models/test_recommender.pkl")
    print("✓ Modelo salvo com sucesso!")
    print()
    
    print("=" * 80)
    print("✅ DEMONSTRAÇÃO CONCLUÍDA")
    print("=" * 80)
    print()
    print("Próximos passos:")
    print("  1. Execute testes reais e forneça feedback")
    print("  2. O modelo aprenderá com suas preferências")
    print("  3. As recomendações melhorarão com o tempo")
    print()


if __name__ == "__main__":
    main()
