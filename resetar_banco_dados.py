"""
Script para RESETAR o banco de dados (limpar tabelas)
Mais seguro que deletar o arquivo
"""
import sys
import io
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from src.utils.database import get_database

print("="*70)
print("🗑️  RESETAR BANCO DE DADOS")
print("="*70)

print("\n⚠️  Isso vai DELETAR todos os dados do banco:")
print("   - Todos os feedbacks (172)")
print("   - Todas as recomendações")
print("   - Todas as execuções")

resposta = input("\n❓ Confirma? (sim/nao): ")

if resposta.lower() != 'sim':
    print("\n❌ Operação cancelada.")
    sys.exit(0)

try:
    db = get_database("iartes.db")
    
    print("\n🔄 Limpando tabelas...")
    print("-"*70)
    
    # Limpar feedbacks
    cursor = db.conn.cursor()
    cursor.execute("DELETE FROM feedbacks")
    deleted_feedbacks = cursor.rowcount
    print(f"✅ Deletados {deleted_feedbacks} feedbacks")
    
    # Limpar recommendations
    cursor.execute("DELETE FROM recommendations")
    deleted_recs = cursor.rowcount
    print(f"✅ Deletadas {deleted_recs} recomendações")
    
    # Limpar executions
    cursor.execute("DELETE FROM executions")
    deleted_execs = cursor.rowcount
    print(f"✅ Deletadas {deleted_execs} execuções")
    
    db.conn.commit()
    
    # Verificar
    stats = db.get_statistics()
    
    print("\n" + "="*70)
    print("✅ BANCO DE DADOS RESETADO!")
    print("="*70)
    print(f"\n📊 Status atual:")
    print(f"   Feedbacks: {stats['total_feedbacks']}")
    print(f"   Taxa de sucesso: {stats['success_rate']:.1f}%")
    
    db.close()
    
    print("\n🎯 Banco limpo e pronto para novos dados!")
    print("="*70)

except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()
