"""
Script de migração: Pickle → SQLite

Migra os feedbacks salvos no arquivo pickle para o banco de dados SQLite.
"""
import sys
import io
from pathlib import Path
from datetime import datetime

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from src.recommender.ml_recommender import MLTestRecommender
from src.utils.database import get_database

print("="*70)
print("🔄 MIGRAÇÃO: PICKLE → SQLITE")
print("="*70)

try:
    # 1. Carregar modelo pickle
    print("\n📦 Carregando modelo pickle...")
    recommender = MLTestRecommender()
    recommender.load_model("models/motorola_modelo.pkl")
    
    total_feedbacks = len(recommender.feedback_history)
    print(f"   ✓ {total_feedbacks} feedbacks encontrados no pickle")
    
    if total_feedbacks == 0:
        print("\n⚠️  Nenhum feedback para migrar.")
        sys.exit(0)
    
    # 2. Conectar ao banco de dados
    print("\n🗄️  Conectando ao banco de dados SQLite...")
    db = get_database("iartes.db")
    print(f"   ✓ Banco criado/conectado: iartes.db")
    
    # 3. Verificar se já existe dados
    existing = db.get_all_feedbacks()
    if len(existing) > 0:
        print(f"\n⚠️  ATENÇÃO: Já existem {len(existing)} feedbacks no banco!")
        resposta = input("   Deseja continuar e adicionar os dados do pickle? (s/n): ")
        if resposta.lower() != 's':
            print("\n❌ Migração cancelada.")
            sys.exit(0)
    
    # 4. Migrar feedbacks
    print(f"\n📊 Migrando {total_feedbacks} feedbacks...")
    print("-"*70)
    
    migrados = 0
    erros = 0
    
    for i, feedback in enumerate(recommender.feedback_history, 1):
        try:
            feedback_dict = {
                'test_case_id': feedback.test_case_id,
                'executed_at': feedback.executed_at.isoformat(),
                'actual_execution_time': feedback.actual_execution_time,
                'success': feedback.success,
                'followed_recommendation': feedback.followed_recommendation,
                'tester_rating': feedback.tester_rating,
                'required_reset': feedback.required_reset,
                'notes': feedback.notes,
                'initial_state': feedback.initial_state,
                'final_state': feedback.final_state
            }
            
            db.add_feedback(feedback_dict)
            migrados += 1
            
            # Progresso
            if i % 10 == 0 or i == total_feedbacks:
                print(f"   Progresso: {i}/{total_feedbacks} ({(i/total_feedbacks*100):.1f}%)")
        
        except Exception as e:
            erros += 1
            print(f"   ❌ Erro no feedback {i}: {e}")
    
    # 5. Resumo
    print("\n" + "="*70)
    print("✅ MIGRAÇÃO CONCLUÍDA!")
    print("="*70)
    print(f"\n📊 Resumo:")
    print(f"   Total no pickle: {total_feedbacks}")
    print(f"   Migrados com sucesso: {migrados}")
    print(f"   Erros: {erros}")
    
    # 6. Verificar banco
    print("\n🔍 Verificando banco de dados...")
    stats = db.get_statistics()
    print(f"   Total no banco: {stats['total_feedbacks']}")
    print(f"   Taxa de sucesso: {stats['success_rate']:.1f}%")
    print(f"   Avaliação média: {stats['avg_rating']:.1f}/5")
    
    print("\n" + "="*70)
    print("✅ Banco de dados pronto para uso!")
    print("="*70)
    print("\nPróximos passos:")
    print("  1. O sistema já está usando o SQLite")
    print("  2. Use: python ver_banco_dados.py (para consultar)")
    print("  3. Use: python app_web.py (interface web)")
    print("="*70)

except FileNotFoundError:
    print("\n❌ Arquivo pickle não encontrado: models/motorola_modelo.pkl")
    print("   Execute a interface web primeiro e dê alguns feedbacks.")
except Exception as e:
    print(f"\n❌ Erro durante migração: {e}")
    import traceback
    traceback.print_exc()
finally:
    if 'db' in locals():
        db.close()
