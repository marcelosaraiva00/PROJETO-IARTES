"""
Script para LIMPAR COMPLETAMENTE os dados da IA

ATENÇÃO: Isso vai APAGAR:
- Banco de dados SQLite (iartes.db)
- Modelo treinado pickle (models/motorola_modelo.pkl)
- Permitir re-treinamento do zero com dados corretos
"""
import sys
import io
from pathlib import Path
import os

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*70)
print("⚠️  LIMPEZA COMPLETA DOS DADOS DA IA")
print("="*70)

print("\n🚨 ATENÇÃO: Esta operação vai APAGAR:")
print("   - Banco de dados: iartes.db (172 feedbacks)")
print("   - Modelo treinado: models/motorola_modelo.pkl")
print("   - Permitir treinar do ZERO com classificações corretas")

resposta = input("\n❓ Tem certeza que deseja continuar? (sim/nao): ")

if resposta.lower() != 'sim':
    print("\n❌ Operação cancelada.")
    sys.exit(0)

print("\n🔄 Iniciando limpeza...")
print("-"*70)

deleted_files = []
errors = []

# 1. Deletar banco de dados
db_path = Path("iartes.db")
if db_path.exists():
    try:
        os.remove(db_path)
        deleted_files.append(str(db_path))
        print(f"✅ Deletado: {db_path}")
    except Exception as e:
        errors.append(f"Erro ao deletar {db_path}: {e}")
        print(f"❌ Erro: {e}")
else:
    print(f"⚠️  Não encontrado: {db_path}")

# 2. Deletar modelo pickle
model_path = Path("models/motorola_modelo.pkl")
if model_path.exists():
    try:
        os.remove(model_path)
        deleted_files.append(str(model_path))
        print(f"✅ Deletado: {model_path}")
    except Exception as e:
        errors.append(f"Erro ao deletar {model_path}: {e}")
        print(f"❌ Erro: {e}")
else:
    print(f"⚠️  Não encontrado: {model_path}")

# 3. Criar backup do modelo antigo (se existir)
backup_model = Path("models/motorola_modelo_OLD.pkl")
if backup_model.exists():
    print(f"ℹ️  Backup antigo existe: {backup_model}")

print("\n" + "="*70)

if len(errors) > 0:
    print("⚠️  LIMPEZA CONCLUÍDA COM ERROS")
    print("="*70)
    for error in errors:
        print(f"  ❌ {error}")
else:
    print("✅ LIMPEZA CONCLUÍDA COM SUCESSO!")
    print("="*70)
    print(f"\n📊 Arquivos deletados: {len(deleted_files)}")
    for file in deleted_files:
        print(f"  - {file}")

print("\n🎯 PRÓXIMOS PASSOS:")
print("-"*70)
print("1. Execute a interface web: python app_web.py")
print("2. Acesse http://localhost:5000")
print("3. Selecione testes e solicite recomendação")
print("4. Execute testes MANUALMENTE")
print("5. Dê feedback após cada teste")
print("6. A IA vai treinar do ZERO com dados corretos!")

print("\n💡 Agora as ações estão classificadas corretamente:")
print("   - 69% PARTIALLY_DESTRUCTIVE (eram 4.8%)")
print("   - 31% NON_DESTRUCTIVE (eram 64.1%)")
print("   - A IA vai aprender melhor!")

print("\n" + "="*70)
