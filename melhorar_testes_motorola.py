"""
Script para melhorar os testes Motorola baseado nos padrões dos testes Dialer.

Analisa padrões dos testes Dialer e aplica melhorias aos testes Motorola:
- Adiciona validation_point_action
- Identifica context_preserving e teardown_restores
- Melhora pre/postconditions
- Cria hierarquias baseadas em dependências
- Melhora dependências entre testes relacionados
"""
import sys
from pathlib import Path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from typing import List, Dict, Set, Optional
from src.models.test_case import TestCase, Action, ActionType, ActionImpact
from testes_motorola import criar_testes_motorola
from testes_dialer_importados import criar_testes_dialer


def analyze_dialer_patterns(dialer_tests: List[TestCase]) -> Dict:
    """Analisa padrões dos testes Dialer para aplicar aos Motorola."""
    patterns = {
        'verification_tests': [],  # Testes que são apenas verificação
        'context_preserving_keywords': set(),
        'teardown_keywords': set(),
        'validation_patterns': {},
        'hierarchy_patterns': {},
        'precondition_patterns': {},
        'postcondition_patterns': {}
    }
    
    for test in dialer_tests:
        # Padrão: context_preserving
        if test.context_preserving:
            patterns['verification_tests'].append(test.id)
            # Identificar palavras-chave
            for action in test.actions:
                desc_lower = action.description.lower()
                if any(word in desc_lower for word in ['check', 'verify', 'validate', 'confirm']):
                    patterns['context_preserving_keywords'].update(['check', 'verify', 'validate', 'confirm'])
        
        # Padrão: teardown_restores
        if test.teardown_restores:
            for action in test.actions:
                desc_lower = action.description.lower()
                if any(word in desc_lower for word in ['check', 'open', 'display']):
                    patterns['teardown_keywords'].update(['check', 'open', 'display'])
        
        # Padrão: validation_point_action
        if test.validation_point_action:
            # Identificar qual ação é o ponto de validação
            for action in test.actions:
                if action.id == test.validation_point_action:
                    desc_lower = action.description.lower()
                    # Geralmente é a última ação de verificação ou ação principal
                    if action.action_type == ActionType.VERIFICATION:
                        patterns['validation_patterns']['verification_last'] = True
                    elif 'check' in desc_lower or 'verify' in desc_lower:
                        patterns['validation_patterns']['check_verify'] = True
        
        # Padrão: pre/postconditions
        for action in test.actions:
            if action.preconditions:
                for pre in action.preconditions:
                    patterns['precondition_patterns'].setdefault(pre, []).append(action.action_type)
            if action.postconditions:
                for post in action.postconditions:
                    patterns['postcondition_patterns'].setdefault(post, []).append(action.action_type)
    
    return patterns


def infer_validation_point(test: TestCase) -> Optional[str]:
    """Infere o validation_point_action baseado nos padrões."""
    if not test.actions:
        return None
    
    # Padrão 1: Última ação de verificação
    verification_actions = [a for a in test.actions if a.action_type == ActionType.VERIFICATION]
    if verification_actions:
        return verification_actions[-1].id
    
    # Padrão 2: Última ação que contém "verificar", "check", "validar"
    for action in reversed(test.actions):
        desc_lower = action.description.lower()
        if any(word in desc_lower for word in ['verificar', 'check', 'validar', 'verify', 'confirm']):
            return action.id
    
    # Padrão 3: Última ação do teste (ação principal)
    return test.actions[-1].id


def infer_context_preserving(test: TestCase) -> bool:
    """Infere se o teste preserva contexto (apenas verifica)."""
    # Se todas as ações são de verificação e não alteram estado
    if all(a.action_type == ActionType.VERIFICATION and 
           a.impact == ActionImpact.NON_DESTRUCTIVE 
           for a in test.actions):
        return True
    
    # Se a maioria das ações são verificações
    verification_count = sum(1 for a in test.actions if a.action_type == ActionType.VERIFICATION)
    if verification_count >= len(test.actions) * 0.7:  # 70% ou mais são verificações
        return True
    
    # Se o teste apenas verifica/confirma algo sem criar/modificar
    action_descriptions = ' '.join(a.description.lower() for a in test.actions)
    verification_keywords = ['verificar', 'check', 'validar', 'verify', 'confirm', 'visualizar', 'visualize']
    
    # Se contém palavras de verificação e não contém palavras de modificação
    has_verification = any(kw in action_descriptions for kw in verification_keywords)
    has_modification = any(kw in action_descriptions for kw in ['criar', 'create', 'modificar', 'modify', 'alterar', 'change', 'deletar', 'delete', 'remover', 'remove'])
    
    if has_verification and not has_modification:
        return True
    
    return False


def infer_teardown_restores(test: TestCase) -> bool:
    """Infere se o teste restaura estado no teardown."""
    # Testes que apenas verificam conteúdo de tela e voltam
    action_descriptions = ' '.join(a.description.lower() for a in test.actions)
    
    # Padrão 1: "verificar X" ou "check X" seguido de navegação de volta
    if ('verificar' in action_descriptions or 'check' in action_descriptions) and \
       ('menu' in action_descriptions or 'info' in action_descriptions or 'usage' in action_descriptions or 'configuração' in action_descriptions):
        # Se não há ações destrutivas
        if not any(a.impact == ActionImpact.DESTRUCTIVE for a in test.actions):
            return True
    
    # Padrão 2: Testes que apenas visualizam/verificam informações sem alterar
    if all(a.action_type == ActionType.VERIFICATION for a in test.actions) and \
       any('visualizar' in a.description.lower() or 'visualize' in a.description.lower() or 
           'verificar' in a.description.lower() or 'check' in a.description.lower() 
           for a in test.actions):
        return True
    
    # Padrão 3: Testes de "status" ou "informações" que apenas leem dados
    if 'status' in action_descriptions or 'informação' in action_descriptions or 'information' in action_descriptions:
        if not any(a.impact == ActionImpact.DESTRUCTIVE for a in test.actions):
            return True
    
    return False


def improve_preconditions_set(test: TestCase, all_tests: List[TestCase]) -> Set[str]:
    """Melhora preconditions baseado em dependências e padrões."""
    improved_preconditions = set()
    
    # Adicionar preconditions das dependências
    test_by_id = {t.id: t for t in all_tests}
    for dep_id in test.dependencies:
        if dep_id in test_by_id:
            dep_test = test_by_id[dep_id]
            # Adicionar postconditions do teste dependente
            improved_preconditions.update(dep_test.get_postconditions())
    
    # Adicionar preconditions padrão baseadas no módulo
    if test.module == "Setup":
        improved_preconditions.add("device_on")
    elif test.module in ["Camera", "Connectivity", "Telephony"]:
        improved_preconditions.add("setup_complete")
    
    # Adicionar preconditions das ações
    for action in test.actions:
        improved_preconditions.update(action.preconditions)
    
    return improved_preconditions


def improve_postconditions(test: TestCase) -> Set[str]:
    """Melhora postconditions baseado nas ações."""
    improved_postconditions = set()
    
    # Coletar todas as postconditions das ações
    for action in test.actions:
        improved_postconditions.update(action.postconditions)
    
    # Adicionar postconditions baseadas no módulo e tipo de teste
    if test.module == "Camera":
        if any('foto' in a.description.lower() or 'photo' in a.description.lower() for a in test.actions):
            improved_postconditions.add("photo_saved")
        if any('video' in a.description.lower() for a in test.actions):
            improved_postconditions.add("video_saved")
    
    elif test.module == "Connectivity":
        if 'wifi' in test.name.lower():
            improved_postconditions.add("wifi_connected")
        elif 'bluetooth' in test.name.lower():
            improved_postconditions.add("bluetooth_connected")
    
    elif test.module == "Telephony":
        if 'call' in test.name.lower() or 'chamada' in test.name.lower():
            improved_postconditions.add("call_active")
    
    return improved_postconditions


def create_hierarchy(test: TestCase, all_tests: List[TestCase]) -> tuple[Optional[str], Set[str]]:
    """Cria hierarquia baseada em dependências e módulos."""
    parent_id = None
    child_ids = set()
    
    test_by_id = {t.id: t for t in all_tests}
    
    # Se tem dependências, o primeiro pode ser considerado "pai" em alguns casos
    if test.dependencies:
        # Se há apenas uma dependência e ela é do mesmo módulo, pode ser pai
        if len(test.dependencies) == 1:
            dep_id = list(test.dependencies)[0]
            if dep_id in test_by_id:
                dep_test = test_by_id[dep_id]
                # Se são do mesmo módulo e o teste atual é uma extensão
                if dep_test.module == test.module:
                    # Verificar se é uma extensão lógica (ex: CAM_002 depende de CAM_001)
                    if test.id.endswith('002') and dep_test.id.endswith('001'):
                        parent_id = dep_id
                        # Adicionar este teste como filho do pai
                        if dep_id in test_by_id:
                            test_by_id[dep_id].child_test_ids.add(test.id)
    
    # Identificar filhos: testes que dependem deste
    for other_test in all_tests:
        if test.id in other_test.dependencies:
            child_ids.add(other_test.id)
    
    return parent_id, child_ids


def improve_test_case(test: TestCase, all_tests: List[TestCase], patterns: Dict) -> TestCase:
    """Melhora um caso de teste aplicando padrões."""
    
    # 1. Adicionar validation_point_action
    validation_point = infer_validation_point(test)
    if validation_point:
        test.validation_point_action = validation_point
    
    # 2. Inferir context_preserving (sempre verificar e atualizar)
    test.context_preserving = infer_context_preserving(test)
    
    # 3. Inferir teardown_restores (sempre verificar e atualizar)
    test.teardown_restores = infer_teardown_restores(test)
    
    # 4. Melhorar preconditions
    improved_preconditions = improve_preconditions_set(test, all_tests)
    # Aplicar às ações que não têm preconditions
    for action in test.actions:
        if not action.preconditions:
            # Adicionar preconditions relevantes baseadas em outras ações
            action_idx = test.actions.index(action)
            if action_idx > 0:
                # Precondition = postcondition da ação anterior
                prev_action = test.actions[action_idx - 1]
                action.preconditions.update(prev_action.postconditions)
    
    # 5. Melhorar postconditions
    improved_postconditions = improve_postconditions(test)
    # Garantir que a última ação tenha postconditions relevantes
    if test.actions:
        last_action = test.actions[-1]
        if not last_action.postconditions:
            # Adicionar postcondition baseada no módulo/teste
            if improved_postconditions:
                last_action.postconditions.update(improved_postconditions)
    
    # 6. Criar hierarquia
    parent_id, child_ids = create_hierarchy(test, all_tests)
    if parent_id:
        test.parent_test_id = parent_id
    if child_ids:
        test.child_test_ids.update(child_ids)
    
    return test


def main():
    """Função principal para melhorar testes Motorola."""
    print("=" * 80)
    print("MELHORANDO TESTES MOTOROLA BASEADO EM PADRÕES DIALER")
    print("=" * 80)
    print()
    
    # Carregar testes Dialer para análise de padrões
    print("[INFO] Analisando padroes dos testes Dialer...")
    dialer_tests = criar_testes_dialer()
    patterns = analyze_dialer_patterns(dialer_tests)
    print(f"   [OK] {len(dialer_tests)} testes Dialer analisados")
    print(f"   [OK] {len(patterns['verification_tests'])} testes de verificacao identificados")
    print()
    
    # Carregar testes Motorola
    print("[INFO] Carregando testes Motorola...")
    motorola_tests = criar_testes_motorola()
    print(f"   [OK] {len(motorola_tests)} testes Motorola carregados")
    print()
    
    # Melhorar cada teste
    print("[INFO] Aplicando melhorias...")
    improved_tests = []
    stats = {
        'validation_points_added': 0,
        'context_preserving_added': 0,
        'teardown_restores_added': 0,
        'hierarchies_created': 0,
        'preconditions_improved': 0,
        'postconditions_improved': 0
    }
    
    for test in motorola_tests:
        original_test = test
        
        # Aplicar melhorias
        improved_test = improve_test_case(test, motorola_tests, patterns)
        
        # Contar melhorias
        if improved_test.validation_point_action and not hasattr(original_test, 'validation_point_action'):
            stats['validation_points_added'] += 1
        if improved_test.context_preserving:
            stats['context_preserving_added'] += 1
        if improved_test.teardown_restores:
            stats['teardown_restores_added'] += 1
        if improved_test.parent_test_id or improved_test.child_test_ids:
            stats['hierarchies_created'] += 1
        
        improved_tests.append(improved_test)
    
    print(f"   [OK] {stats['validation_points_added']} validation_point_action adicionados")
    print(f"   [OK] {stats['context_preserving_added']} testes marcados como context_preserving")
    print(f"   [OK] {stats['teardown_restores_added']} testes marcados como teardown_restores")
    print(f"   [OK] {stats['hierarchies_created']} hierarquias criadas")
    print()
    
    # Salvar testes melhorados
    output_file = Path(__file__).parent / 'testes_motorola_melhorados.py'
    print(f"[INFO] Salvando testes melhorados em: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('"""\n')
        f.write('TESTES MOTOROLA MELHORADOS\n')
        f.write('Baseado em padrões dos testes Dialer\n')
        f.write('Gerado automaticamente por melhorar_testes_motorola.py\n')
        f.write('"""\n')
        f.write('import sys\n')
        f.write('from pathlib import Path\n')
        f.write('root_dir = Path(__file__).parent\n')
        f.write('sys.path.insert(0, str(root_dir))\n')
        f.write('\n')
        f.write('from src.models.test_case import TestCase, Action, ActionType, ActionImpact\n')
        f.write('\n\n')
        f.write('def criar_testes_motorola():\n')
        f.write('    """Cria suite completa de testes para smartphones Motorola (MELHORADA)"""\n')
        f.write('    \n')
        f.write('    testes = []\n')
        f.write('    \n')
        
        # Escrever cada teste
        for test in improved_tests:
            f.write(f'    # {test.name}\n')
            f.write(f'    testes.append(TestCase(\n')
            f.write(f'        id="{test.id}",\n')
            f.write(f'        name="{test.name}",\n')
            f.write(f'        description="""{test.description}""",\n')
            f.write(f'        priority={test.priority},\n')
            f.write(f'        module="{test.module}",\n')
            f.write(f'        tags={set(test.tags)},\n')
            if test.dependencies:
                f.write(f'        dependencies={set(test.dependencies)},\n')
            if test.validation_point_action:
                f.write(f'        validation_point_action="{test.validation_point_action}",\n')
            if test.context_preserving:
                f.write(f'        context_preserving=True,\n')
            if test.teardown_restores:
                f.write(f'        teardown_restores=True,\n')
            if test.parent_test_id:
                f.write(f'        parent_test_id="{test.parent_test_id}",\n')
            if test.child_test_ids:
                f.write(f'        child_test_ids={set(test.child_test_ids)},\n')
            f.write(f'        actions=[\n')
            for action in test.actions:
                f.write(f'            Action(\n')
                f.write(f'                id="{action.id}",\n')
                f.write(f'                description="{action.description}",\n')
                f.write(f'                action_type=ActionType.{action.action_type.name},\n')
                f.write(f'                impact=ActionImpact.{action.impact.name},\n')
                if action.preconditions:
                    f.write(f'                preconditions={set(action.preconditions)},\n')
                if action.postconditions:
                    f.write(f'                postconditions={set(action.postconditions)},\n')
                f.write(f'                estimated_time={action.estimated_time},\n')
                if action.priority:
                    f.write(f'                priority={action.priority},\n')
                if action.tags:
                    f.write(f'                tags={set(action.tags)},\n')
                f.write(f'            ),\n')
            f.write(f'        ]\n')
            f.write(f'    ))\n')
            f.write(f'    \n')
        
        f.write('    return testes\n')
    
    print(f"   [OK] Arquivo salvo com sucesso!")
    print()
    print("=" * 80)
    print("[SUCCESS] MELHORIAS APLICADAS COM SUCESSO!")
    print("=" * 80)
    print()
    print(f"[FILE] Arquivo gerado: {output_file}")
    print()
    print("Próximos passos:")
    print("1. Revisar o arquivo gerado")
    print("2. Substituir testes_motorola.py pelo arquivo melhorado (ou integrar)")
    print("3. Testar ordenação hierárquica com os novos dados")


if __name__ == '__main__':
    main()
