"""
Execução autônoma (offline/simulada) para o modelo aprender sozinho.

Fluxo:
1) Recomendador sugere ordem
2) Executor (simulador) executa cada teste nessa ordem
3) Converte resultados em ExecutionFeedback automaticamente
4) Alimenta o ML (add_feedback) e salva o modelo

Depois, você pode trocar o executor para AndroidAppiumExecutor quando tiver automação real.
"""

import sys
from pathlib import Path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import io
import argparse
from datetime import datetime

from src.models.test_case import ExecutionFeedback
from src.recommender.ml_recommender import MLTestRecommender
from src.execution.simulator_executor import SimulatorExecutor, SimulatorConfig

from testes_motorola import criar_testes_motorola


def main():
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=10, help="quantas rodadas completas de execução")
    parser.add_argument("--model-path", type=str, default="models/motorola_modelo.pkl")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    testes = criar_testes_motorola()
    recommender = MLTestRecommender()
    try:
        recommender.load_model(args.model_path)
    except Exception:
        pass

    executor = SimulatorExecutor(SimulatorConfig(seed=args.seed))

    print("=" * 80)
    print("EXECUÇÃO AUTÔNOMA (SIMULADA) - TREINO SEM HUMANO")
    print("=" * 80)
    print(f"Testes carregados: {len(testes)}")
    print(f"Feedbacks existentes: {len(recommender.feedback_history)}")
    print(f"Modelo treinado: {recommender.is_trained}")
    print()

    for ep in range(1, args.episodes + 1):
        # Sempre recalcular recomendação (pode mudar com o aprendizado)
        rec = recommender.recommend_order(testes)
        ordered = [next(t for t in testes if t.id == tid) for tid in rec.recommended_order]

        # Estado inicial do ambiente
        state = executor.reset()

        successes = 0
        failures = 0
        resets = 0
        total_time = 0.0

        for tc in ordered:
            result, state = executor.execute_test_case(tc, state)
            total_time += result.actual_execution_time
            if result.success:
                successes += 1
            else:
                failures += 1
            if result.required_reset:
                resets += 1

            # Gerar feedback automático
            rating = 5 if result.success else 1
            feedback = ExecutionFeedback(
                test_case_id=tc.id,
                executed_at=datetime.now(),
                actual_execution_time=result.actual_execution_time,
                success=result.success,
                followed_recommendation=True,
                tester_rating=rating,
                required_reset=result.required_reset,
                notes=result.notes or "",
                initial_state=result.initial_state,
                final_state=result.final_state,
            )
            recommender.add_feedback(feedback, ordered)

            # Se falhou e marcou reset, reseta estado (simulando “recuperação”)
            if result.required_reset:
                state = executor.reset()

        # Salvar modelo após cada episódio
        recommender.save_model(args.model_path)

        print(f"[Episódio {ep}/{args.episodes}] "
              f"sucessos={successes} falhas={failures} resets={resets} "
              f"tempo={total_time/60:.1f}min "
              f"amostras={len(recommender.training_data['y'])} "
              f"treinado={recommender.is_trained}")

    print()
    print("Concluído.")
    print(f"Modelo salvo em: {args.model_path}")


if __name__ == "__main__":
    main()

