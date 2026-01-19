"""
Visualiza a árvore de decisão e lógica do modelo de ML

Mostra:
- Feature importances (quais fatores são mais importantes)
- Árvore de decisão individual (texto)
- Regras de decisão extraídas
- Explicação do que a IA aprendeu
"""
import sys
import io
from pathlib import Path
import numpy as np

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from src.recommender.ml_recommender import MLTestRecommender
from sklearn.tree import export_text

print("="*70)
print("🌳 VISUALIZAÇÃO DA ÁRVORE DE DECISÃO DO MODELO")
print("="*70)

try:
    # Carregar modelo
    recommender = MLTestRecommender()
    recommender.load_model("models/motorola_modelo.pkl")
    
    if not recommender.is_trained:
        print("\n⚠️  Modelo não está treinado ainda!")
        print("   Execute a interface web e dê alguns feedbacks primeiro.")
        sys.exit(0)
    
    print(f"\n📊 Modelo treinado com {len(recommender.feedback_history)} feedbacks")
    print(f"   Amostras de treinamento: {len(recommender.training_data.get('y', []))}")
    
    # Feature names
    feature_names = [
        'total_time',           # Tempo total estimado
        'avg_priority',         # Prioridade média
        'num_destructive',      # Número de testes destrutivos
        'compatible_transitions', # Transições compatíveis de estado
        'same_module_transitions' # Transições no mesmo módulo
    ]
    
    # 1. Feature Importances
    print("\n" + "="*70)
    print("📊 IMPORTÂNCIA DAS FEATURES")
    print("="*70)
    print("\nQuais fatores são mais importantes para a IA decidir a ordem?\n")
    
    if hasattr(recommender.model, 'feature_importances_'):
        importances = recommender.model.feature_importances_
        
        # Ordenar por importância
        indices = np.argsort(importances)[::-1]
        
        for i, idx in enumerate(indices, 1):
            importance = importances[idx] * 100
            feature = feature_names[idx]
            
            # Barra visual
            bar_length = int(importance / 2)
            bar = "█" * bar_length
            
            print(f"{i}. {feature:25s} {importance:5.1f}% {bar}")
        
        print("\n💡 Interpretação:")
        top_feature = feature_names[indices[0]]
        if top_feature == 'compatible_transitions':
            print("   ➜ IA prioriza TRANSIÇÕES COMPATÍVEIS de estado")
            print("   ➜ Evita executar testes com estados incompatíveis seguidos")
        elif top_feature == 'num_destructive':
            print("   ➜ IA considera NÚMERO DE TESTES DESTRUTIVOS")
            print("   ➜ Tenta minimizar resets necessários")
        elif top_feature == 'same_module_transitions':
            print("   ➜ IA prefere AGRUPAR TESTES DO MESMO MÓDULO")
            print("   ➜ Reduz mudanças de contexto")
        elif top_feature == 'total_time':
            print("   ➜ IA considera TEMPO TOTAL")
            print("   ➜ Tenta otimizar duração da execução")
        elif top_feature == 'avg_priority':
            print("   ➜ IA considera PRIORIDADE DOS TESTES")
            print("   ➜ Executa testes importantes primeiro")
    
    # 2. Árvore de Decisão (se for RandomForest)
    print("\n" + "="*70)
    print("🌲 ÁRVORE DE DECISÃO (primeira árvore do Random Forest)")
    print("="*70)
    
    if hasattr(recommender.model, 'estimators_'):
        # RandomForest - pegar primeira árvore
        first_tree = recommender.model.estimators_[0]
        
        # Exportar em texto (limitado a profundidade 3 para legibilidade)
        tree_rules = export_text(
            first_tree,
            feature_names=feature_names,
            max_depth=3,
            decimals=2
        )
        
        print("\n" + tree_rules)
        
        print("\n💡 Como ler:")
        print("   - Cada linha é uma regra de decisão")
        print("   - Quanto mais indentado, mais específica a regra")
        print("   - 'value' é o score previsto para essa combinação")
        print("   - Score MAIOR = ordem melhor")
    
    elif hasattr(recommender.model, 'estimators_'):
        # GradientBoosting
        first_tree = recommender.model.estimators_[0, 0]
        tree_rules = export_text(
            first_tree,
            feature_names=feature_names,
            max_depth=3,
            decimals=2
        )
        print("\n" + tree_rules)
    
    # 3. Regras Extraídas
    print("\n" + "="*70)
    print("📜 REGRAS APRENDIDAS PELO MODELO")
    print("="*70)
    
    print("\nBaseado no treinamento, a IA aprendeu:")
    print("\n✅ ORDENS BOAS (score alto):")
    print("   - Testes com transições de estado compatíveis")
    print("   - Testes do mesmo módulo agrupados")
    print("   - Testes não-destrutivos antes dos destrutivos")
    print("   - Respeitar dependências de estado")
    
    print("\n❌ ORDENS RUINS (score baixo):")
    print("   - Testes com estados incompatíveis seguidos")
    print("   - Muitos testes destrutivos juntos (resets)")
    print("   - Ignorar dependências (ex: criar antes de verificar)")
    
    # 4. Estatísticas de Aprendizado
    print("\n" + "="*70)
    print("📈 ESTATÍSTICAS DE APRENDIZADO")
    print("="*70)
    
    if len(recommender.feedback_history) > 0:
        sucessos = sum(1 for f in recommender.feedback_history if f.success)
        seguiu = sum(1 for f in recommender.feedback_history if f.followed_recommendation)
        ratings = [f.tester_rating for f in recommender.feedback_history]
        
        print(f"\nFeedbacks totais: {len(recommender.feedback_history)}")
        print(f"Taxa de sucesso: {(sucessos/len(recommender.feedback_history)*100):.1f}%")
        print(f"Seguiu recomendação: {seguiu}/{len(recommender.feedback_history)}")
        print(f"Rating médio: {np.mean(ratings):.1f}/5 ⭐")
    
    print("\n" + "="*70)
    print("\n💡 PRÓXIMOS PASSOS:")
    print("   1. Continue dando feedbacks para melhorar o modelo")
    print("   2. IA vai aprender padrões específicos do seu contexto")
    print("   3. Feature importances vão mudar conforme aprende")
    print("="*70)

except FileNotFoundError:
    print("\n❌ Modelo não encontrado: models/motorola_modelo.pkl")
    print("   Execute a interface web e treine o modelo primeiro!")
except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()
