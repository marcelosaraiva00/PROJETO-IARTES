"""
Script para visualizar dados do banco de dados SQLite
"""
import sys
import io
from pathlib import Path
from datetime import datetime, timedelta

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from src.utils.database import get_database

print("="*70)
print("🗄️  VISUALIZADOR DO BANCO DE DADOS SQLITE")
print("="*70)

try:
    db = get_database("iartes.db")
    
    # Estatísticas gerais
    print("\n📊 ESTATÍSTICAS GERAIS")
    print("-"*70)
    stats = db.get_statistics()
    print(f"Total de feedbacks: {stats['total_feedbacks']}")
    print(f"Taxa de sucesso: {stats['success_rate']:.1f}%")
    print(f"Avaliação média: {stats['avg_rating']:.1f}/5 {'⭐' * round(stats['avg_rating'])}")
    print(f"Seguiu recomendação: {stats['followed_recommendation_count']}/{stats['total_feedbacks']}")
    print(f"Resets necessários: {stats['resets_count']}")
    print(f"Tempo médio de execução: {stats['avg_execution_time']:.1f}s")
    
    # Estatísticas por teste
    print("\n📱 ESTATÍSTICAS POR TESTE (Top 10)")
    print("-"*70)
    test_stats = db.get_test_statistics()
    for i, stat in enumerate(test_stats[:10], 1):
        print(f"\n{i}. {stat['test_case_id']}")
        print(f"   Execuções: {stat['executions']}")
        print(f"   Taxa de sucesso: {stat['success_rate']:.1f}%")
        print(f"   Tempo médio: {stat['avg_time']:.1f}s")
        print(f"   Avaliação média: {stat['avg_rating']:.1f}/5")
        print(f"   Resets: {stat['resets']}")
    
    # Feedbacks recentes
    print("\n📝 ÚLTIMOS 10 FEEDBACKS")
    print("-"*70)
    recent = db.get_recent_feedbacks(10)
    for i, fb in enumerate(recent, 1):
        exec_date = datetime.fromisoformat(fb['executed_at'])
        print(f"\n{i}. {fb['test_case_id']}")
        print(f"   Data: {exec_date.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"   Sucesso: {'✅' if fb['success'] else '❌'}")
        print(f"   Tempo: {fb['actual_execution_time']:.1f}s")
        print(f"   Avaliação: {'⭐' * (fb['tester_rating'] or 0)}")
        if fb['notes']:
            print(f"   Notas: {fb['notes'][:50]}...")
    
    print("\n" + "="*70)
    print("\n💡 Dicas:")
    print("  - Use DB Browser for SQLite para ver os dados graficamente")
    print("  - Arquivo do banco: iartes.db")
    print("  - Para gerar relatórios customizados, edite este script")
    print("="*70)

except FileNotFoundError:
    print("\n❌ Banco de dados não encontrado: iartes.db")
    print("   Execute primeiro: python migrar_pickle_para_sqlite.py")
except Exception as e:
    print(f"\n❌ Erro ao acessar banco: {e}")
    import traceback
    traceback.print_exc()
finally:
    if 'db' in locals():
        db.close()
