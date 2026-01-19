"""
Exemplo avançado: Treinamento do modelo com dados sintéticos
"""
import sys
from pathlib import Path

# Adicionar o diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import numpy as np
from datetime import datetime, timedelta
import random

from src.models.test_case import ExecutionFeedback
from src.recommender.ml_recommender import MLTestRecommender
from src.utils.data_generator import SyntheticDataGenerator


def simulate_execution(
    test_order: list,
    recommender: MLTestRecommender,
    follow_recommendation_rate: float = 0.8
) -> list:
    """
    Simula execução de testes e gera feedback
    
    Args:
        test_order: Ordem dos testes
        recommender: Recomendador
        follow_recommendation_rate: Taxa de seguir recomendação
        
    Returns:
        Lista de feedbacks
    """
    feedbacks = []
    
    for i, test in enumerate(test_order):
        # Simular tempo de execução (com variação)
        base_time = test.get_total_estimated_time()
        actual_time = base_time * random.uniform(0.8, 1.3)
        
        # Simular sucesso (baseado na success_rate do teste)
        success = random.random() < test.success_rate
        
        # Simular se seguiu recomendação
        followed = random.random() < follow_recommendation_rate
        
        # Simular rating (melhor para testes rápidos e bem-sucedidos)
        if success and actual_time < base_time:
            rating = random.randint(4, 5)
        elif success:
            rating = random.randint(3, 5)
        else:
            rating = random.randint(1, 3)
        
        # Simular necessidade de reset (raro se ordem for boa)
        required_reset = False
        if i > 0:
            prev_test = test_order[i-1]
            # Reset se teste anterior foi destrutivo e atual precisa de estado limpo
            if (prev_test.has_destructive_actions() and 
                not test.has_destructive_actions() and
                random.random() < 0.1):
                required_reset = True
                rating = max(1, rating - 2)  # Penalizar rating
        
        feedback = ExecutionFeedback(
            test_case_id=test.id,
            executed_at=datetime.now() + timedelta(seconds=sum(
                t.get_total_estimated_time() for t in test_order[:i]
            )),
            actual_execution_time=actual_time,
            success=success,
            followed_recommendation=followed,
            tester_rating=rating,
            required_reset=required_reset,
            notes=f"Execução {'bem-sucedida' if success else 'falhou'}"
        )
        
        feedbacks.append(feedback)
    
    return feedbacks


def main():
    """Função principal de treinamento avançado"""
    print("=" * 80)
    print("TREINAMENTO AVANÇADO DO MODELO DE RECOMENDAÇÃO")
    print("=" * 80)
    print()
    
    # Configuração
    NUM_TRAINING_SUITES = 10
    TESTS_PER_SUITE = 15
    
    print("⚙️  Configuração:")
    print(f"  - Suítes de treinamento: {NUM_TRAINING_SUITES}")
    print(f"  - Testes por suíte: {TESTS_PER_SUITE}")
    print()
    
    # Gerar dados sintéticos
    print("🔄 Gerando dados sintéticos...")
    generator = SyntheticDataGenerator(seed=42)
    training_suites = generator.generate_multiple_suites(
        num_suites=NUM_TRAINING_SUITES,
        tests_per_suite=TESTS_PER_SUITE
    )
    print(f"✓ Geradas {len(training_suites)} suítes de teste")
    print()
    
    # Criar e treinar recomendador
    print("🤖 Inicializando recomendador...")
    recommender = MLTestRecommender(model_type='random_forest')
    print("✓ Recomendador inicializado")
    print()
    
    # Simular múltiplas sessões de teste
    print("📊 Simulando sessões de teste e coletando feedback...")
    print()
    
    total_feedbacks = 0
    
    for suite_idx, suite in enumerate(training_suites, 1):
        print(f"Suíte {suite_idx}/{NUM_TRAINING_SUITES}: {suite.name}")
        
        # Obter recomendação
        recommendation = recommender.recommend_order(suite.test_cases)
        
        # Organizar testes na ordem recomendada
        test_order = [
            tc for tc in suite.test_cases 
            if tc.id in recommendation.recommended_order
        ]
        
        # Simular execução e coletar feedback
        feedbacks = simulate_execution(test_order, recommender)
        
        # Adicionar feedbacks ao modelo
        for feedback in feedbacks:
            recommender.add_feedback(feedback, test_order)
            total_feedbacks += 1
        
        # Estatísticas da execução
        avg_rating = np.mean([f.tester_rating for f in feedbacks if f.tester_rating])
        num_resets = sum(1 for f in feedbacks if f.required_reset)
        success_rate = sum(1 for f in feedbacks if f.success) / len(feedbacks)
        
        print(f"  ├─ Feedbacks coletados: {len(feedbacks)}")
        print(f"  ├─ Rating médio: {avg_rating:.2f}/5")
        print(f"  ├─ Resets necessários: {num_resets}")
        print(f"  └─ Taxa de sucesso: {success_rate:.1%}")
        print()
    
    print(f"✓ Total de feedbacks coletados: {total_feedbacks}")
    print()
    
    # Treinar modelo final
    print("🎓 Treinando modelo com todos os dados...")
    recommender.train()
    print()
    
    # Avaliar modelo em nova suíte
    print("🧪 Avaliando modelo em suíte de teste...")
    generator_test = SyntheticDataGenerator(seed=999)
    test_suite = generator_test.generate_test_suite(num_tests=20)
    
    # Comparar recomendação do modelo vs. heurística
    print("\n📊 Comparação: Modelo Treinado vs. Heurística")
    print("-" * 80)
    
    # Recomendação do modelo treinado
    rec_ml = recommender.recommend_order(test_suite.test_cases, use_heuristics=False)
    print(f"\n🤖 Modelo ML:")
    print(f"  - Confiança: {rec_ml.confidence_score:.1%}")
    print(f"  - Tempo estimado: {rec_ml.estimated_total_time:.1f}s")
    print(f"  - Resets estimados: {rec_ml.estimated_resets}")
    
    # Recomendação heurística
    rec_heur = recommender.recommend_order(test_suite.test_cases, use_heuristics=True)
    print(f"\n📐 Heurística:")
    print(f"  - Confiança: {rec_heur.confidence_score:.1%}")
    print(f"  - Tempo estimado: {rec_heur.estimated_total_time:.1f}s")
    print(f"  - Resets estimados: {rec_heur.estimated_resets}")
    
    # Calcular melhorias
    time_improvement = (
        (rec_heur.estimated_total_time - rec_ml.estimated_total_time) / 
        rec_heur.estimated_total_time * 100
    )
    reset_reduction = rec_heur.estimated_resets - rec_ml.estimated_resets
    
    print(f"\n📈 Melhorias do Modelo:")
    print(f"  - Redução de tempo: {time_improvement:+.1f}%")
    print(f"  - Redução de resets: {reset_reduction:+d}")
    print()
    
    # Salvar modelo treinado
    print("💾 Salvando modelo treinado...")
    recommender.save_model("models/trained_recommender.pkl")
    print("✓ Modelo salvo: models/trained_recommender.pkl")
    print()
    
    # Resumo final
    print("=" * 80)
    print("✅ TREINAMENTO CONCLUÍDO COM SUCESSO!")
    print("=" * 80)
    print()
    print("📊 Resumo:")
    print(f"  - Total de suítes processadas: {NUM_TRAINING_SUITES}")
    print(f"  - Total de feedbacks: {total_feedbacks}")
    print(f"  - Modelo está treinado: {recommender.is_trained}")
    print(f"  - Amostras de treinamento: {len(recommender.training_data['y'])}")
    print()
    print("🚀 Próximos passos:")
    print("  1. Use o modelo treinado em suas suítes reais")
    print("  2. Continue fornecendo feedback para melhorar")
    print("  3. Monitore as métricas de desempenho")
    print()


if __name__ == "__main__":
    main()
