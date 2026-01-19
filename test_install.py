"""
Script de teste rápido para verificar instalação
"""
import sys
from pathlib import Path

# Adicionar o diretório atual ao PYTHONPATH
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("🔍 Testando importações...")
    
    try:
        from src.models.test_case import TestCase, Action, ActionType, ActionImpact
        print("  ✓ src.models.test_case")
    except ImportError as e:
        print(f"  ✗ src.models.test_case - {e}")
        return False
    
    try:
        from src.features.feature_extractor import FeatureExtractor
        print("  ✓ src.features.feature_extractor")
    except ImportError as e:
        print(f"  ✗ src.features.feature_extractor - {e}")
        return False
    
    try:
        from src.recommender.ml_recommender import MLTestRecommender
        print("  ✓ src.recommender.ml_recommender")
    except ImportError as e:
        print(f"  ✗ src.recommender.ml_recommender - {e}")
        return False
    
    try:
        from src.utils.data_generator import SyntheticDataGenerator
        print("  ✓ src.utils.data_generator")
    except ImportError as e:
        print(f"  ✗ src.utils.data_generator - {e}")
        return False
    
    return True

def test_dependencies():
    """Testa se dependências externas estão instaladas"""
    print("\n🔍 Testando dependências...")
    
    dependencies = {
        'numpy': 'NumPy',
        'sklearn': 'scikit-learn',
        'pandas': 'Pandas',
    }
    
    all_ok = True
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - FALTANDO!")
            all_ok = False
    
    return all_ok

def test_basic_functionality():
    """Testa funcionalidade básica"""
    print("\n🔍 Testando funcionalidade básica...")
    
    try:
        from src.models.test_case import TestCase, Action, ActionType, ActionImpact
        from src.recommender.ml_recommender import MLTestRecommender
        
        # Criar ação simples
        action = Action(
            id="TEST_A001",
            description="Ação de teste",
            action_type=ActionType.VERIFICATION,
            impact=ActionImpact.NON_DESTRUCTIVE,
            estimated_time=1.0
        )
        print("  ✓ Criação de Action")
        
        # Criar teste
        test = TestCase(
            id="TEST_TC001",
            name="Teste de verificação",
            description="Teste básico",
            actions=[action],
            priority=3
        )
        print("  ✓ Criação de TestCase")
        
        # Criar recomendador
        recommender = MLTestRecommender()
        print("  ✓ Criação de MLTestRecommender")
        
        # Obter recomendação
        recommendation = recommender.recommend_order([test])
        print("  ✓ Geração de recomendação")
        
        assert len(recommendation.recommended_order) == 1
        assert recommendation.recommended_order[0] == "TEST_TC001"
        print("  ✓ Validação de resultado")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 70)
    print("TESTE DE INSTALAÇÃO - IARTES")
    print("=" * 70)
    print()
    
    # Testar importações
    imports_ok = test_imports()
    
    # Testar dependências
    deps_ok = test_dependencies()
    
    # Testar funcionalidade
    func_ok = test_basic_functionality()
    
    # Resultado final
    print("\n" + "=" * 70)
    if imports_ok and deps_ok and func_ok:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("=" * 70)
        print("\n🚀 Sistema pronto para uso!")
        print("\nPróximos passos:")
        print("  1. Execute: python examples/demo_basic.py")
        print("  2. Ou execute: python examples/advanced_training.py")
        print("  3. Consulte: QUICK_START.md para guia rápido")
        return 0
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("=" * 70)
        print("\n⚠️ Problemas encontrados!")
        
        if not deps_ok:
            print("\nInstale as dependências:")
            print("  pip install -r requirements.txt")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
