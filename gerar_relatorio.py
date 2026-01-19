"""
Gerador de Relatórios em CSV/Excel do banco de dados
"""
import sys
import io
from pathlib import Path
from datetime import datetime
import csv

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from src.utils.database import get_database

print("="*70)
print("📊 GERADOR DE RELATÓRIOS")
print("="*70)

try:
    db = get_database("iartes.db")
    
    # Relatório 1: Todos os feedbacks
    print("\n1️⃣  Gerando relatório de feedbacks...")
    feedbacks = db.get_all_feedbacks()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_feedbacks = f"relatorio_feedbacks_{timestamp}.csv"
    
    with open(filename_feedbacks, 'w', newline='', encoding='utf-8-sig') as f:
        if len(feedbacks) > 0:
            writer = csv.DictWriter(f, fieldnames=feedbacks[0].keys())
            writer.writeheader()
            writer.writerows(feedbacks)
            print(f"   ✓ Salvo: {filename_feedbacks} ({len(feedbacks)} registros)")
        else:
            print("   ⚠️  Nenhum feedback encontrado")
    
    # Relatório 2: Estatísticas por teste
    print("\n2️⃣  Gerando relatório de estatísticas por teste...")
    test_stats = db.get_test_statistics()
    
    filename_stats = f"relatorio_testes_{timestamp}.csv"
    
    with open(filename_stats, 'w', newline='', encoding='utf-8-sig') as f:
        if len(test_stats) > 0:
            fieldnames = ['test_case_id', 'executions', 'success_rate', 
                         'avg_time', 'avg_rating', 'resets', 'last_executed']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(test_stats)
            print(f"   ✓ Salvo: {filename_stats} ({len(test_stats)} testes)")
        else:
            print("   ⚠️  Nenhuma estatística encontrada")
    
    # Relatório 3: Resumo geral
    print("\n3️⃣  Gerando relatório resumo...")
    general_stats = db.get_statistics()
    
    filename_summary = f"relatorio_resumo_{timestamp}.txt"
    
    with open(filename_summary, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("RELATÓRIO RESUMO - SISTEMA IARTES\n")
        f.write("="*70 + "\n\n")
        f.write(f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
        f.write("ESTATÍSTICAS GERAIS:\n")
        f.write("-"*70 + "\n")
        f.write(f"Total de feedbacks: {general_stats['total_feedbacks']}\n")
        f.write(f"Taxa de sucesso: {general_stats['success_rate']:.1f}%\n")
        f.write(f"Avaliação média: {general_stats['avg_rating']:.1f}/5\n")
        f.write(f"Seguiu recomendação: {general_stats['followed_recommendation_count']}\n")
        f.write(f"Resets necessários: {general_stats['resets_count']}\n")
        f.write(f"Tempo médio: {general_stats['avg_execution_time']:.1f}s\n\n")
        
        f.write("TOP 10 TESTES MAIS EXECUTADOS:\n")
        f.write("-"*70 + "\n")
        for i, stat in enumerate(test_stats[:10], 1):
            f.write(f"{i}. {stat['test_case_id']}\n")
            f.write(f"   Execuções: {stat['executions']} | ")
            f.write(f"Sucesso: {stat['success_rate']:.1f}% | ")
            f.write(f"Tempo: {stat['avg_time']:.1f}s\n")
    
    print(f"   ✓ Salvo: {filename_summary}")
    
    print("\n" + "="*70)
    print("✅ RELATÓRIOS GERADOS COM SUCESSO!")
    print("="*70)
    print("\n📁 Arquivos criados:")
    print(f"  - {filename_feedbacks}")
    print(f"  - {filename_stats}")
    print(f"  - {filename_summary}")
    print("\n💡 Abra os arquivos .csv no Excel ou LibreOffice")
    print("="*70)

except Exception as e:
    print(f"\n❌ Erro ao gerar relatórios: {e}")
    import traceback
    traceback.print_exc()
finally:
    if 'db' in locals():
        db.close()
