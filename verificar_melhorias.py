"""Script para verificar melhorias aplicadas aos testes."""
import sys
from pathlib import Path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from testes_motorola_melhorados import criar_testes_motorola
from testes_dialer_importados import criar_testes_dialer

motorola = criar_testes_motorola()
dialer = criar_testes_dialer()
todos = motorola + dialer

print("=" * 80)
print("VERIFICACAO DAS MELHORIAS APLICADAS")
print("=" * 80)
print()
print(f"Total de testes Motorola: {len(motorola)}")
print(f"Total de testes Dialer: {len(dialer)}")
print(f"Total de testes: {len(todos)}")
print()
print("Melhorias aplicadas:")
print(f"  - Testes com validation_point_action: {sum(1 for t in todos if hasattr(t, 'validation_point_action') and t.validation_point_action)}")
print(f"  - Testes context_preserving: {sum(1 for t in todos if hasattr(t, 'context_preserving') and t.context_preserving)}")
print(f"  - Testes teardown_restores: {sum(1 for t in todos if hasattr(t, 'teardown_restores') and t.teardown_restores)}")
print(f"  - Testes com hierarquia (pai ou filhos): {sum(1 for t in todos if (hasattr(t, 'parent_test_id') and t.parent_test_id) or (hasattr(t, 'child_test_ids') and t.child_test_ids))}")
print()
print("=" * 80)
