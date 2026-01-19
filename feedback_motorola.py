"""
SCRIPT DE FEEDBACK INTERATIVO PARA TESTES MOTOROLA
Use este script para registrar feedback após executar cada teste
"""
import sys
from pathlib import Path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from datetime import datetime
from src.models.test_case import ExecutionFeedback
from src.recommender.ml_recommender import MLTestRecommender
from testes_motorola import criar_testes_motorola


def coletar_feedback_interativo(test_id, teste, recommender, testes):
    """Coleta feedback interativo do usuário"""
    
    print("\n" + "=" * 80)
    print(f"📝 FEEDBACK: {test_id}")
    print("=" * 80)
    print(f"\n📱 Teste: {teste.name}")
    print(f"📦 Módulo: {teste.module}")
    print(f"⏱️  Tempo estimado: {teste.get_total_estimated_time():.0f}s")
    print(f"🎯 Prioridade: {teste.priority}/5")
    print(f"📋 Ações: {len(teste.actions)}")
    print()
    
    print("Passos do teste:")
    for i, acao in enumerate(teste.actions, 1):
        print(f"  {i}. {acao.description}")
    print()
    
    print("-" * 80)
    print("PREENCHA OS DADOS DO FEEDBACK:")
    print("-" * 80)
    print()
    
    # Coletar dados
    try:
        # Tempo real
        while True:
            try:
                tempo_input = input(f"⏱️  Tempo real de execução (segundos) [{teste.get_total_estimated_time():.0f}s]: ").strip()
                if not tempo_input:
                    tempo_real = teste.get_total_estimated_time()
                else:
                    tempo_real = float(tempo_input)
                break
            except ValueError:
                print("   ❌ Por favor, digite um número válido!")
        
        # Sucesso
        sucesso_input = input("✅ Teste passou? (s/n) [s]: ").strip().lower()
        passou = sucesso_input != 'n'
        
        # Seguiu recomendação
        seguiu_input = input("🎯 Seguiu a ordem recomendada? (s/n) [s]: ").strip().lower()
        seguiu = seguiu_input != 'n'
        
        # Rating
        while True:
            try:
                rating_input = input("⭐ Avaliação da execução (1-5) [5]: ").strip()
                if not rating_input:
                    rating = 5
                else:
                    rating = int(rating_input)
                    if 1 <= rating <= 5:
                        break
                    print("   ❌ Digite um valor entre 1 e 5!")
            except ValueError:
                print("   ❌ Por favor, digite um número válido!")
        
        # Reset
        reset_input = input("🔄 Precisou reiniciar o dispositivo? (s/n) [n]: ").strip().lower()
        reset = reset_input == 's'
        
        # Notas
        notas = input("📝 Observações (opcional): ").strip()
        
        # Criar feedback
        feedback = ExecutionFeedback(
            test_case_id=test_id,
            executed_at=datetime.now(),
            actual_execution_time=tempo_real,
            success=passou,
            followed_recommendation=seguiu,
            tester_rating=rating,
            required_reset=reset,
            notes=notas if notas else None
        )
        
        # Adicionar ao modelo
        recommender.add_feedback(feedback, testes)
        
        # Mostrar resumo
        print()
        print("✅ FEEDBACK REGISTRADO!")
        print("-" * 80)
        print(f"   Tempo: {tempo_real:.1f}s (estimado: {teste.get_total_estimated_time():.0f}s)")
        diferenca = tempo_real - teste.get_total_estimated_time()
        if diferenca > 0:
            print(f"   ⚠️  {diferenca:.1f}s mais lento que estimado")
        elif diferenca < 0:
            print(f"   ✨ {abs(diferenca):.1f}s mais rápido que estimado")
        else:
            print(f"   🎯 Exatamente como estimado!")
        
        print(f"   Sucesso: {'✅ Sim' if passou else '❌ Não'}")
        print(f"   Avaliação: {'⭐' * rating}")
        if reset:
            print(f"   🔄 Precisou de reset")
        if notas:
            print(f"   📝 Nota: {notas}")
        print("-" * 80)
        
        return feedback
        
    except KeyboardInterrupt:
        print("\n\n❌ Feedback cancelado pelo usuário.")
        return None
    except Exception as e:
        print(f"\n\n❌ Erro ao coletar feedback: {e}")
        return None


def main():
    print("=" * 80)
    print("🎯 SISTEMA DE FEEDBACK - TESTES MOTOROLA")
    print("=" * 80)
    print()
    
    # Carregar testes
    print("📂 Carregando testes Motorola...")
    testes = criar_testes_motorola()
    print(f"✓ {len(testes)} testes carregados")
    print()
    
    # Carregar modelo
    print("🤖 Carregando modelo...")
    recommender = MLTestRecommender()
    
    try:
        recommender.load_model("models/motorola_modelo.pkl")
        feedbacks_anteriores = len(recommender.feedback_history)
        print(f"✓ Modelo carregado ({feedbacks_anteriores} feedbacks anteriores)")
    except:
        feedbacks_anteriores = 0
        print("✓ Novo modelo criado")
    
    print()
    
    # Obter recomendação
    print("📊 Gerando recomendação...")
    recomendacao = recommender.recommend_order(testes)
    
    print(f"\n{'=' * 80}")
    print(f"ORDEM RECOMENDADA ({recomendacao.confidence_score:.0%} confiança):")
    print(f"{'=' * 80}\n")
    
    modulo_atual = None
    for idx, test_id in enumerate(recomendacao.recommended_order, 1):
        teste = next(tc for tc in testes if tc.id == test_id)
        
        if teste.module != modulo_atual:
            if modulo_atual is not None:
                print()
            print(f"[{teste.module}]")
            modulo_atual = teste.module
        
        destrutivo = "🔴" if teste.has_destructive_actions() else "🟢"
        print(f"  {idx:2d}. {destrutivo} {test_id} - {teste.name}")
    
    print()
    print("=" * 80)
    print()
    
    # Menu de opções
    print("OPÇÕES:")
    print("  1. Dar feedback para um teste específico")
    print("  2. Dar feedback seguindo a ordem recomendada")
    print("  3. Ver estatísticas do modelo")
    print("  4. Sair")
    print()
    
    while True:
        try:
            opcao = input("Escolha uma opção (1-4): ").strip()
            
            if opcao == '1':
                # Feedback específico
                print("\nTestes disponíveis:")
                for i, tc in enumerate(testes, 1):
                    print(f"  {i:2d}. {tc.id} - {tc.name}")
                print()
                
                num = input("Número do teste (ou 'c' para cancelar): ").strip()
                if num.lower() == 'c':
                    continue
                
                try:
                    idx = int(num) - 1
                    if 0 <= idx < len(testes):
                        teste = testes[idx]
                        feedback = coletar_feedback_interativo(
                            teste.id, teste, recommender, testes
                        )
                        if feedback:
                            recommender.save_model("models/motorola_modelo.pkl")
                            print("\n💾 Modelo salvo!")
                    else:
                        print("❌ Número inválido!")
                except ValueError:
                    print("❌ Digite um número válido!")
            
            elif opcao == '2':
                # Feedback em ordem
                print("\n🎯 Modo: Seguir ordem recomendada")
                print("   (Pressione Ctrl+C a qualquer momento para parar)\n")
                
                feedbacks_dados = 0
                for test_id in recomendacao.recommended_order:
                    teste = next(tc for tc in testes if tc.id == test_id)
                    
                    executado = input(f"\nExecutou {test_id}? (s/n/q=sair): ").strip().lower()
                    if executado == 'q':
                        break
                    elif executado == 's':
                        feedback = coletar_feedback_interativo(
                            test_id, teste, recommender, testes
                        )
                        if feedback:
                            feedbacks_dados += 1
                            recommender.save_model("models/motorola_modelo.pkl")
                            print(f"\n💾 Modelo salvo! ({feedbacks_dados} feedbacks nesta sessão)")
                    else:
                        print("   ⏭️  Pulando...")
                
                if feedbacks_dados > 0:
                    print(f"\n✅ Sessão concluída! {feedbacks_dados} feedbacks registrados.")
            
            elif opcao == '3':
                # Estatísticas
                print("\n" + "=" * 80)
                print("📈 ESTATÍSTICAS DO MODELO")
                print("=" * 80)
                
                total_feedbacks = len(recommender.feedback_history)
                print(f"\n📊 Total de feedbacks: {total_feedbacks}")
                print(f"🎓 Modelo treinado: {'Sim ✅' if recommender.is_trained else 'Não ❌'}")
                print(f"🎯 Confiança atual: {recomendacao.confidence_score:.1%}")
                
                if total_feedbacks > 0:
                    # Taxa de sucesso
                    sucessos = sum(1 for f in recommender.feedback_history if f.success)
                    taxa_sucesso = (sucessos / total_feedbacks) * 100
                    print(f"✅ Taxa de sucesso: {taxa_sucesso:.1f}% ({sucessos}/{total_feedbacks})")
                    
                    # Rating médio
                    rating_medio = sum(f.tester_rating for f in recommender.feedback_history) / total_feedbacks
                    print(f"⭐ Avaliação média: {rating_medio:.1f}/5.0")
                    
                    # Resets
                    resets = sum(1 for f in recommender.feedback_history if f.required_reset)
                    print(f"🔄 Resets necessários: {resets}")
                    
                    # Seguiu recomendação
                    seguiu = sum(1 for f in recommender.feedback_history if f.followed_recommendation)
                    taxa_seguiu = (seguiu / total_feedbacks) * 100
                    print(f"🎯 Seguiu recomendação: {taxa_seguiu:.1f}% ({seguiu}/{total_feedbacks})")
                    
                    print()
                    print("Testes com feedback:")
                    testes_com_feedback = set(f.test_case_id for f in recommender.feedback_history)
                    for tc_id in sorted(testes_com_feedback):
                        tc = next((t for t in testes if t.id == tc_id), None)
                        if tc:
                            print(f"  ✓ {tc_id} - {tc.name}")
                
                else:
                    print("\n⚠️  Ainda sem feedbacks registrados.")
                    print("   Execute os testes e forneça feedback para treinar o modelo!")
                
                if not recommender.is_trained and total_feedbacks > 0:
                    faltam = max(0, 5 - total_feedbacks)
                    print(f"\n💡 Dica: Faltam {faltam} feedbacks para iniciar treinamento ML")
                
                print("=" * 80)
            
            elif opcao == '4':
                print("\n👋 Saindo...")
                break
            
            else:
                print("❌ Opção inválida! Digite 1, 2, 3 ou 4.")
            
            print()
        
        except KeyboardInterrupt:
            print("\n\n👋 Saindo...")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
    
    print()
    print("=" * 80)
    print("✅ SESSÃO FINALIZADA")
    print("=" * 80)
    print()
    
    if len(recommender.feedback_history) > feedbacks_anteriores:
        novos = len(recommender.feedback_history) - feedbacks_anteriores
        print(f"📊 {novos} novo(s) feedback(s) registrado(s) nesta sessão")
        print(f"💾 Modelo salvo: models/motorola_modelo.pkl")
        print()


if __name__ == "__main__":
    main()
