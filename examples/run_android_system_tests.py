"""
Execução AUTÔNOMA no Android real (Motorola) via Appium/UIAutomator2.

Pré-requisitos (resumo):
1) Habilitar Depuração USB no Motorola
2) `adb devices` deve listar o device
3) Instalar Appium + driver uiautomator2 e iniciar o servidor Appium:
   - `npm i -g appium`
   - `appium driver install uiautomator2`
   - `appium`
4) Instalar dependência Python:
   - `pip install appium-python-client`

Depois rode:
  python examples/run_android_system_tests.py --model-path models/motorola_modelo.pkl

Observação:
Automação de apps de sistema varia por versão/idioma/OEM. Este executor é heurístico:
ele tenta clicar por textos (PT-BR) e abrir activities conhecidas.
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
from src.execution.appium_executor import AndroidAppiumExecutor, AppiumConfig

from testes_motorola import criar_testes_motorola


def main():
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

    parser = argparse.ArgumentParser()
    parser.add_argument("--server-url", type=str, default="http://127.0.0.1:4723")
    parser.add_argument("--device-name", type=str, default="Android")
    parser.add_argument("--model-path", type=str, default="models/motorola_modelo.pkl")
    parser.add_argument("--max-tests", type=int, default=10, help="limitar quantidade de testes por rodada")
    args = parser.parse_args()

    testes = criar_testes_motorola()
    recommender = MLTestRecommender()
    try:
        recommender.load_model(args.model_path)
    except Exception:
        pass

    executor = AndroidAppiumExecutor(
        AppiumConfig(server_url=args.server_url, device_name=args.device_name)
    )

    # Recomenda e executa uma rodada
    rec = recommender.recommend_order(testes)
    ordered = [next(t for t in testes if t.id == tid) for tid in rec.recommended_order][: args.max_tests]

    print("=" * 80)
    print("EXECUÇÃO AUTÔNOMA - ANDROID REAL (HEURÍSTICO)")
    print("=" * 80)
    print(f"Testes selecionados: {len(ordered)} (max={args.max_tests})")
    print(f"Método recomendação: {rec.reasoning.get('method')}, confiança={rec.confidence_score:.0%}")
    print()

    state = executor.reset()

    for tc in ordered:
        print(f"➡️  Executando: {tc.id} - {tc.name}")
        result, state = executor.execute_test_case(tc, state)

        # Gerar feedback automático (rating simples)
        rating = 5 if result.success else 1
        feedback = ExecutionFeedback(
            test_case_id=tc.id,
            executed_at=datetime.now(),
            actual_execution_time=result.actual_execution_time,
            success=result.success,
            followed_recommendation=True,
            tester_rating=rating,
            required_reset=result.required_reset,
            notes=result.notes,
            initial_state=result.initial_state,
            final_state=result.final_state,
        )
        recommender.add_feedback(feedback, ordered)

        print(f"   Resultado: {'✅ OK' if result.success else '❌ FALHOU'} "
              f"(reset={result.required_reset}) "
              f"tempo={result.actual_execution_time:.1f}s")
        if not result.success:
            print(f"   Ação falha: {result.failed_action_id}")
            print(f"   Notas: {result.notes}")
        print()

        if result.required_reset:
            print("   🔄 Reset solicitado — tentando resetar executor...")
            state = executor.reset()

    recommender.save_model(args.model_path)
    print(f"💾 Modelo salvo em: {args.model_path}")


if __name__ == "__main__":
    main()

