"""
TEMPLATE: Use este arquivo para adicionar seus casos de teste reais
Substitua os exemplos com seus dados!
"""
import sys
from pathlib import Path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from datetime import datetime
from src.models.test_case import TestCase, Action, ActionType, ActionImpact, ExecutionFeedback
from src.recommender.ml_recommender import MLTestRecommender


# ============================================================================
# PASSO 1: DEFINA SEUS CASOS DE TESTE AQUI
# ============================================================================

def criar_meus_testes():
    """
    Substitua com seus casos de teste reais!
    
    INSTRUÇÕES:
    - Copie o template de teste abaixo para cada caso de teste
    - Preencha com os dados reais
    - Ajuste os tipos de ação e impactos conforme necessário
    """
    
    testes = []
    
    # ========================================================================
    # TESTE 1: [SUBSTITUA COM SEU PRIMEIRO TESTE]
    # ========================================================================
    teste1 = TestCase(
        id="MEU_TC001",  # ← Seu ID único
        name="[Nome do Teste]",  # ← Nome descritivo
        description="[O que este teste faz]",  # ← Descrição detalhada
        priority=5,  # ← 1-5 (5=crítico, 1=baixo)
        module="[Nome do Módulo]",  # ← Ex: "Autenticação", "Produtos"
        tags={"tag1", "tag2"},  # ← Tags para categorização
        
        actions=[
            # AÇÃO 1
            Action(
                id="MEU_A001",
                description="[Primeiro passo - ex: Abrir página]",
                action_type=ActionType.NAVIGATION,  # NAVIGATION, CREATION, VERIFICATION, MODIFICATION, DELETION
                impact=ActionImpact.NON_DESTRUCTIVE,  # NON_DESTRUCTIVE, PARTIALLY_DESTRUCTIVE, DESTRUCTIVE
                estimated_time=2.0,  # Tempo estimado em segundos
                preconditions=set(),  # Estados necessários: {"estado_x"}
                postconditions={"pagina_aberta"}  # Estados resultantes
            ),
            
            # AÇÃO 2
            Action(
                id="MEU_A002",
                description="[Segundo passo - ex: Preencher campo]",
                action_type=ActionType.CREATION,
                impact=ActionImpact.DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"pagina_aberta"},
                postconditions={"dados_preenchidos"}
            ),
            
            # AÇÃO 3
            Action(
                id="MEU_A003",
                description="[Terceiro passo - ex: Verificar resultado]",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"dados_preenchidos"},
                postconditions={"verificacao_ok"}
            ),
            
            # ← Adicione mais ações conforme necessário
        ]
    )
    testes.append(teste1)
    
    
    # ========================================================================
    # TESTE 2: [ADICIONE SEU SEGUNDO TESTE]
    # ========================================================================
    teste2 = TestCase(
        id="MEU_TC002",
        name="[Nome do Segundo Teste]",
        description="[Descrição]",
        priority=4,
        module="[Módulo]",
        tags={"tag3"},
        dependencies={"MEU_TC001"},  # ← Se depende de outro teste
        
        actions=[
            # Suas ações aqui...
            Action(
                id="MEU_A004",
                description="[Descrição da ação]",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=2.0
            ),
        ]
    )
    testes.append(teste2)
    
    
    # ========================================================================
    # ADICIONE MAIS TESTES COPIANDO O TEMPLATE ACIMA
    # ========================================================================
    
    return testes


# ============================================================================
# PASSO 2: FUNÇÃO PARA DAR FEEDBACK
# ============================================================================

def coletar_feedback_manual(test_case_id, meus_testes, recommender):
    """
    Use esta função para dar feedback após executar cada teste manualmente
    """
    print(f"\n{'='*70}")
    print(f"FEEDBACK PARA: {test_case_id}")
    print('='*70)
    
    # Encontrar o teste
    teste = next((t for t in meus_testes if t.id == test_case_id), None)
    if not teste:
        print(f"❌ Teste {test_case_id} não encontrado!")
        return
    
    print(f"Nome: {teste.name}")
    print(f"Tempo estimado: {teste.get_total_estimated_time():.1f}s")
    print()
    
    # Coletar dados
    try:
        tempo_real = float(input("⏱️  Tempo real de execução (segundos): "))
    except:
        tempo_real = teste.get_total_estimated_time()
    
    passou = input("✅ Teste passou? (s/n): ").lower() == 's'
    seguiu = input("🎯 Seguiu ordem recomendada? (s/n): ").lower() == 's'
    
    try:
        rating = int(input("⭐ Avaliação (1-5): "))
        rating = max(1, min(5, rating))
    except:
        rating = 3
    
    reset = input("🔄 Precisou reiniciar sistema? (s/n): ").lower() == 's'
    notas = input("📝 Observações (opcional): ")
    
    # Criar feedback
    feedback = ExecutionFeedback(
        test_case_id=test_case_id,
        executed_at=datetime.now(),
        actual_execution_time=tempo_real,
        success=passou,
        followed_recommendation=seguiu,
        tester_rating=rating,
        required_reset=reset,
        notes=notas
    )
    
    # Adicionar ao modelo
    recommender.add_feedback(feedback, meus_testes)
    print("\n✅ Feedback registrado!")
    
    return feedback


# ============================================================================
# PASSO 3: EXECUTAR O SISTEMA
# ============================================================================

def main():
    print("=" * 80)
    print("SISTEMA DE RECOMENDAÇÃO - SEUS CASOS DE TESTE")
    print("=" * 80)
    print()
    
    # 1. Carregar testes
    print("📂 Carregando seus casos de teste...")
    meus_testes = criar_meus_testes()
    print(f"✓ {len(meus_testes)} testes carregados")
    
    # Mostrar testes
    print("\nTestes disponíveis:")
    for tc in meus_testes:
        print(f"  • {tc.id} - {tc.name}")
        print(f"    Módulo: {tc.module} | Prioridade: {tc.priority} | " +
              f"Ações: {len(tc.actions)} | Tempo: {tc.get_total_estimated_time():.1f}s")
    print()
    
    # 2. Criar/Carregar recomendador
    print("🤖 Inicializando recomendador...")
    recommender = MLTestRecommender()
    
    try:
        recommender.load_model("models/meus_testes_modelo.pkl")
        print(f"✓ Modelo existente carregado ({len(recommender.feedback_history)} feedbacks)")
    except:
        print("✓ Novo modelo criado")
    print()
    
    # 3. Obter recomendação
    print("🎯 Gerando recomendação...")
    recomendacao = recommender.recommend_order(meus_testes)
    
    print(f"\n📊 RECOMENDAÇÃO:")
    print(f"  Confiança: {recomendacao.confidence_score:.1%}")
    print(f"  Tempo estimado: {recomendacao.estimated_total_time:.1f}s")
    print(f"  Resets estimados: {recomendacao.estimated_resets}")
    print(f"  Método: {recomendacao.reasoning.get('method', 'N/A')}")
    print()
    
    print("📝 Ordem sugerida de execução:")
    for idx, test_id in enumerate(recomendacao.recommended_order, 1):
        teste = next(tc for tc in meus_testes if tc.id == test_id)
        destrutivo = "🔴" if teste.has_destructive_actions() else "🟢"
        print(f"  {idx}. {destrutivo} {test_id} - {teste.name}")
    print()
    
    # 4. Opção de dar feedback
    print("=" * 80)
    print("PRÓXIMOS PASSOS:")
    print("=" * 80)
    print()
    print("1. Execute os testes NA ORDEM SUGERIDA acima")
    print("2. Para cada teste executado, dê feedback:")
    print()
    
    dar_feedback = input("Quer dar feedback agora? (s/n): ").lower()
    
    if dar_feedback == 's':
        print("\n" + "="*80)
        print("MODO FEEDBACK INTERATIVO")
        print("="*80)
        
        for test_id in recomendacao.recommended_order:
            executar = input(f"\nExecutou o teste {test_id}? (s/n): ").lower()
            if executar == 's':
                coletar_feedback_manual(test_id, meus_testes, recommender)
            else:
                print("Pulando para próximo teste...")
        
        # Salvar modelo atualizado
        print("\n💾 Salvando modelo...")
        recommender.save_model("models/meus_testes_modelo.pkl")
        print("✓ Modelo salvo!")
        
        # Estatísticas
        if recommender.feedback_history:
            print(f"\n📈 Estatísticas:")
            print(f"  Total de feedbacks: {len(recommender.feedback_history)}")
            print(f"  Modelo treinado: {recommender.is_trained}")
            
            if recommender.is_trained:
                print("\n🎉 Modelo já está aprendendo com seus dados!")
            else:
                faltam = max(0, 5 - len(recommender.feedback_history))
                print(f"\n📚 Faltam {faltam} feedbacks para começar treinamento ML")
    else:
        print("\n💡 Quando executar os testes, rode este script novamente")
        print("   e escolha 's' para dar feedback!")
    
    print()
    print("=" * 80)
    print("✅ CONCLUÍDO!")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()


# ============================================================================
# GUIA RÁPIDO DE REFERÊNCIA
# ============================================================================
"""
TIPOS DE AÇÃO (ActionType):
- NAVIGATION: Navegar entre telas
- CREATION: Criar/inserir dados
- VERIFICATION: Verificar algo
- MODIFICATION: Editar/atualizar
- DELETION: Deletar dados

IMPACTO (ActionImpact):
- NON_DESTRUCTIVE: Não altera dados (verificações, navegação)
- PARTIALLY_DESTRUCTIVE: Altera parcialmente (edições)
- DESTRUCTIVE: Altera completamente (criações, deleções)

PRIORIDADE (1-5):
- 5: Crítico (smoke tests, funcionalidades essenciais)
- 4: Alto (funcionalidades importantes)
- 3: Médio (funcionalidades normais)
- 2: Baixo (funcionalidades secundárias)
- 1: Trivial (testes cosméticos)

FEEDBACK:
- actual_execution_time: Tempo real em segundos
- success: True/False
- followed_recommendation: True/False
- tester_rating: 1-5 estrelas
- required_reset: True/False se precisou reiniciar
- notes: Observações textuais
"""
