"""
Script para importar testes do arquivo Dialer Example.csv para o formato do IARTES.

Analisa o CSV e a estrutura hierárquica mostrada na imagem para criar TestCases
com Actions, preconditions, postconditions e dependências corretas.
"""
import csv
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from datetime import datetime

from src.models.test_case import TestCase, Action, ActionType, ActionImpact


def infer_action_type(step_text: str) -> ActionType:
    """Infere o tipo de ação baseado no texto do passo."""
    step_lower = step_text.lower()
    
    if any(word in step_lower for word in ['open', 'go to', 'navigate', 'start']):
        return ActionType.NAVIGATION
    elif any(word in step_lower for word in ['type', 'enter', 'input', 'set']):
        return ActionType.CREATION
    elif any(word in step_lower for word in ['check', 'verify', 'validate', 'confirm']):
        return ActionType.VERIFICATION
    elif any(word in step_lower for word in ['change', 'modify', 'update', 'upgrade', 'downgrade']):
        return ActionType.MODIFICATION
    elif any(word in step_lower for word in ['delete', 'remove', 'clear']):
        return ActionType.DELETION
    else:
        return ActionType.NAVIGATION  # Default


def infer_action_impact(action_type: ActionType, step_text: str) -> ActionImpact:
    """Infere o impacto da ação baseado no tipo e texto."""
    step_lower = step_text.lower()
    
    if action_type == ActionType.VERIFICATION:
        return ActionImpact.NON_DESTRUCTIVE
    elif action_type == ActionType.DELETION:
        return ActionImpact.DESTRUCTIVE
    elif action_type == ActionType.NAVIGATION:
        # Navegação geralmente não altera estado, mas pode alterar contexto
        if any(word in step_lower for word in ['open', 'start', 'go to']):
            return ActionImpact.PARTIALLY_DESTRUCTIVE  # Altera contexto/tela
        return ActionImpact.NON_DESTRUCTIVE
    elif action_type == ActionType.MODIFICATION:
        if any(word in step_lower for word in ['upgrade', 'downgrade', 'change network']):
            return ActionImpact.DESTRUCTIVE  # Altera configuração crítica
        return ActionImpact.PARTIALLY_DESTRUCTIVE
    elif action_type == ActionType.CREATION:
        if any(word in step_lower for word in ['type number', 'enter']):
            return ActionImpact.NON_DESTRUCTIVE  # Apenas entrada de dados
        return ActionImpact.PARTIALLY_DESTRUCTIVE
    
    return ActionImpact.PARTIALLY_DESTRUCTIVE


def extract_test_ids_from_text(text: str) -> List[str]:
    """Extrai IDs de teste mencionados no texto (ex: [TEST-0001])."""
    pattern = r'\[TEST-(\d+)\]'
    matches = re.findall(pattern, text)
    return [f'TEST-{match.zfill(4)}' for match in matches]


def estimate_time(action_type: ActionType, step_text: str) -> float:
    """Estima tempo de execução baseado no tipo e complexidade."""
    base_times = {
        ActionType.NAVIGATION: 3.0,
        ActionType.CREATION: 5.0,
        ActionType.VERIFICATION: 2.0,
        ActionType.MODIFICATION: 8.0,
        ActionType.DELETION: 5.0,
    }
    
    base = base_times.get(action_type, 5.0)
    step_lower = step_text.lower()
    
    # Ajustes por complexidade
    if any(word in step_lower for word in ['call', 'conference', 'video']):
        base += 10.0  # Chamadas são mais demoradas
    if any(word in step_lower for word in ['answer', 'wait']):
        base += 5.0
    
    return base


def parse_steps(step_text: str) -> List[Tuple[int, str]]:
    """Parse dos passos numerados do CSV."""
    if not step_text:
        return []
    
    steps = []
    # Padrão: "1- texto\n2- texto" ou "1- texto 2- texto"
    lines = step_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Procurar padrão "número- texto"
        match = re.match(r'^(\d+)[-\s]+(.+)$', line)
        if match:
            step_num = int(match.group(1))
            step_desc = match.group(2).strip()
            steps.append((step_num, step_desc))
        else:
            # Se não tem número, adicionar como passo único
            steps.append((len(steps) + 1, line))
    
    return steps


def extract_preconditions_from_setup(setup_text: str) -> Set[str]:
    """Extrai pré-condições do campo Setup."""
    if not setup_text:
        return set()
    
    preconditions = set()
    setup_lower = setup_text.lower()
    
    # Mapear requisitos comuns para estados
    if 'sim card' in setup_lower or 'sim' in setup_lower:
        preconditions.add('sim_card_inserted')
    if 'dut' in setup_lower and 'sup' in setup_lower:
        preconditions.add('dut_and_sup_available')
    if 'sup2' in setup_lower:
        preconditions.add('sup2_available')
    if 'valid' in setup_lower:
        preconditions.add('device_configured')
    
    return preconditions


def generate_postconditions(step_text: str, action_type: ActionType) -> Set[str]:
    """Gera pós-condições baseadas no passo e tipo de ação."""
    postconditions = set()
    step_lower = step_text.lower()
    
    # Estados específicos baseados em palavras-chave
    if 'dialer' in step_lower and 'open' in step_lower:
        postconditions.add('dialer_open')
    if 'keypad' in step_lower and 'open' in step_lower:
        postconditions.add('keypad_open')
    if 'hidden menu' in step_lower or 'phone info' in step_lower:
        postconditions.add('hidden_menu_displayed')
    if 'phone info menu' in step_lower:
        postconditions.add('phone_info_menu_displayed')
    if 'phone usage' in step_lower:
        postconditions.add('phone_usage_displayed')
    if 'number' in step_lower and 'type' in step_lower:
        postconditions.add('number_entered')
    if 'voice call' in step_lower and 'start' in step_lower:
        postconditions.add('voice_call_active')
    if 'video call' in step_lower and 'start' in step_lower:
        postconditions.add('video_call_active')
    if 'conference' in step_lower:
        postconditions.add('conference_active')
    if 'network' in step_lower and 'set' in step_lower:
        postconditions.add('network_preference_set')
    if 'answer' in step_lower:
        postconditions.add('call_answered')
    if 'upgrade' in step_lower and 'video' in step_lower:
        postconditions.add('call_upgraded_to_video')
    if 'downgrade' in step_lower:
        postconditions.add('call_downgraded_to_voice')
    
    return postconditions


def generate_preconditions_for_step(step_text: str, previous_postconditions: Set[str]) -> Set[str]:
    """Gera pré-condições para um passo baseado no texto e estados anteriores."""
    preconditions = set()
    step_lower = step_text.lower()
    
    # Pré-condições baseadas em palavras-chave
    if 'keypad' in step_lower:
        preconditions.add('dialer_open')
    if 'phone info' in step_lower or 'phone usage' in step_lower:
        preconditions.add('hidden_menu_displayed')
    if 'type' in step_lower and ('*#' in step_text or 'number' in step_lower):
        preconditions.add('keypad_open')
    if 'voice call' in step_lower or 'video call' in step_lower:
        if 'start' in step_lower:
            preconditions.add('keypad_open')
        elif 'answer' in step_lower:
            preconditions.add('incoming_call')
    if 'upgrade' in step_lower:
        preconditions.add('voice_call_active')
    if 'downgrade' in step_lower:
        preconditions.add('video_call_active')
    if 'conference' in step_lower:
        preconditions.add('call_active')  # Pode ser voice ou video
    
    # Herdar estados anteriores se fizer sentido
    if 'dialer' in step_lower or 'keypad' in step_lower:
        preconditions.update(previous_postconditions)
    
    return preconditions


def get_hierarchy_info(test_id: str) -> Dict:
    """
    Retorna informações de hierarquia baseadas na estrutura conhecida.
    Baseado na árvore hierárquica e na descrição fornecida.
    """
    hierarchy_map = {
        'TEST-0001': {
            'parent': None,  # Raiz
            'children': set(),
            'validation_point': 'open keypad',
            'context_preserving': False,
            'teardown_restores': False
        },
        'TEST-0002': {
            'parent': None,  # Filho de "open testing hidden menu" (não é um teste)
            'children': set(),
            'validation_point': 'check options',
            'context_preserving': True,  # (*)
            'teardown_restores': False
        },
        'TEST-0003': {
            'parent': None,
            'children': set(),
            'validation_point': 'open phone info',
            'context_preserving': True,  # (*)
            'teardown_restores': False
        },
        'TEST-0004': {
            'parent': None,
            'children': set(),
            'validation_point': 'open phone usage',
            'context_preserving': False,
            'teardown_restores': True  # (**)
        },
        'TEST-0005': {
            'parent': None,
            'children': set(),
            'validation_point': 'change preferred network',
            'context_preserving': False,
            'teardown_restores': False
        },
        'TEST-0006': {
            'parent': None,
            'children': set(),
            'validation_point': 'check options',
            'context_preserving': False,  # Tem * mas não é (*)
            'teardown_restores': False
        },
        'TEST-0007': {
            'parent': None,
            'children': set(),
            'validation_point': 'upgrade to video',
            'context_preserving': False,
            'teardown_restores': False
        },
        'TEST-0008': {
            'parent': None,
            'children': set(),
            'validation_point': 'start conference',
            'context_preserving': False,
            'teardown_restores': False
        },
        'TEST-0009': {
            'parent': None,
            'children': set(),
            'validation_point': 'downgrade to voice only',
            'context_preserving': False,
            'teardown_restores': False
        },
        'TEST-0010': {
            'parent': None,
            'children': set(),
            'validation_point': 'answer as voice only',
            'context_preserving': False,
            'teardown_restores': False
        },
        'TEST-0011': {
            'parent': None,
            'children': set(),
            'validation_point': 'answer as video',
            'context_preserving': False,
            'teardown_restores': False
        },
        'TEST-0012': {
            'parent': None,
            'children': set(),
            'validation_point': 'start conference',
            'context_preserving': False,
            'teardown_restores': False
        }
    }
    
    return hierarchy_map.get(test_id, {
        'parent': None,
        'children': set(),
        'validation_point': None,
        'context_preserving': False,
        'teardown_restores': False
    })


def find_validation_action(actions: List[Action], validation_point: str) -> Optional[str]:
    """Encontra a ação que corresponde ao ponto de validação."""
    if not validation_point:
        return None
    
    validation_lower = validation_point.lower()
    for action in actions:
        if validation_lower in action.description.lower():
            return action.id
    
    # Se não encontrou exato, retornar primeira ação como fallback
    return actions[0].id if actions else None


def import_dialer_tests(csv_path: Path) -> List[TestCase]:
    """Importa testes do CSV e retorna lista de TestCases."""
    test_cases = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            test_id = row.get('TestCase ID', '').strip()
            summary = row.get('Summary', '').strip()
            setup = row.get('Setup', '').strip()
            step_text = row.get('Step', '').strip()
            expected_result = row.get('Expected Result', '').strip()
            
            if not test_id or not summary:
                continue
            
            # Parse dos passos
            steps = parse_steps(step_text)
            if not steps:
                # Se não há passos explícitos, criar um passo baseado no summary
                steps = [(1, summary)]
            
            # Pré-condições do setup
            setup_preconditions = extract_preconditions_from_setup(setup)
            
            # Criar Actions a partir dos passos
            actions = []
            current_state = set(setup_preconditions)
            
            for idx, (step_num, step_desc) in enumerate(steps):
                action_type = infer_action_type(step_desc)
                impact = infer_action_impact(action_type, step_desc)
                estimated_time = estimate_time(action_type, step_desc)
                
                # Pré-condições: setup + estados anteriores + inferidas do passo
                preconditions = set(setup_preconditions)
                preconditions.update(generate_preconditions_for_step(step_desc, current_state))
                
                # Pós-condições: geradas do passo
                postconditions = generate_postconditions(step_desc, action_type)
                
                # Se não há pós-condições específicas, criar uma genérica baseada no tipo
                if not postconditions:
                    if action_type == ActionType.NAVIGATION:
                        postconditions.add(f'step_{step_num}_completed')
                    elif action_type == ActionType.VERIFICATION:
                        postconditions.add(f'step_{step_num}_verified')
                    else:
                        postconditions.add(f'step_{step_num}_executed')
                
                action = Action(
                    id=f'{test_id}_A{step_num:03d}',
                    description=step_desc,
                    action_type=action_type,
                    impact=impact,
                    preconditions=preconditions,
                    postconditions=postconditions,
                    estimated_time=estimated_time,
                    priority=1,
                    tags={'dialer', 'imported'}
                )
                
                actions.append(action)
                current_state.update(postconditions)
            
            # Descrição completa combinando summary e expected result
            description = summary
            if expected_result:
                description += f"\n\nResultado Esperado: {expected_result}"
            if setup:
                description += f"\n\nPré-requisitos: {setup}"
            
            # Determinar módulo baseado no conteúdo
            module = "Telephony"
            if 'video' in summary.lower() or 'video' in step_text.lower():
                module = "Video Calls"
            elif 'conference' in summary.lower():
                module = "Conference Calls"
            elif 'hidden menu' in summary.lower() or 'phone info' in summary.lower():
                module = "System Settings"
            
            # Prioridade baseada no tipo de teste
            priority = 3  # Default
            if 'critical' in summary.lower() or 'network' in summary.lower():
                priority = 5
            elif 'info' in summary.lower() or 'check' in summary.lower():
                priority = 2
            
            # Extrair dependências de outros testes mencionados
            dependencies = set()
            all_text = f"{summary} {step_text} {expected_result}"
            mentioned_tests = extract_test_ids_from_text(all_text)
            for mentioned_test in mentioned_tests:
                if mentioned_test != test_id:
                    dependencies.add(mentioned_test)
            
            # Obter informações de hierarquia
            hierarchy_info = get_hierarchy_info(test_id)
            validation_action_id = find_validation_action(actions, hierarchy_info['validation_point'])
            
            test_case = TestCase(
                id=test_id,
                name=summary,
                description=description,
                actions=actions,
                priority=priority,
                module=module,
                tags={'dialer', 'imported', 'csv'},
                dependencies=dependencies,
                validation_point_action=validation_action_id,
                context_preserving=hierarchy_info['context_preserving'],
                teardown_restores=hierarchy_info['teardown_restores'],
                parent_test_id=hierarchy_info['parent'],
                child_test_ids=hierarchy_info['children']
            )
            
            test_cases.append(test_case)
    
    # Pós-processamento: atualizar relações pai-filho
    test_by_id = {tc.id: tc for tc in test_cases}
    for tc in test_cases:
        if tc.parent_test_id and tc.parent_test_id in test_by_id:
            parent = test_by_id[tc.parent_test_id]
            parent.child_test_ids.add(tc.id)
    
    return test_cases
    
    return test_cases


def main():
    """Função principal para importar e salvar testes."""
    root = Path(__file__).parent
    csv_path = root / 'arquivos' / 'Dialer Example.csv'
    
    if not csv_path.exists():
        print(f"Arquivo não encontrado: {csv_path}")
        return
    
    print(f"Importando testes de: {csv_path}")
    test_cases = import_dialer_tests(csv_path)
    
    print(f"\n[OK] {len(test_cases)} testes importados:")
    for tc in test_cases:
        print(f"  - {tc.id}: {tc.name} ({len(tc.actions)} acoes)")
        if tc.dependencies:
            print(f"    Dependencias: {', '.join(tc.dependencies)}")
    
    # Salvar em arquivo Python para adicionar ao testes_motorola.py
    output_path = root / 'testes_dialer_importados.py'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('"""\n')
        f.write('Testes importados do Dialer Example.csv\n')
        f.write('Gerado automaticamente por importar_testes_dialer.py\n')
        f.write('"""\n\n')
        f.write('from src.models.test_case import TestCase, Action, ActionType, ActionImpact\n\n\n')
        f.write('def criar_testes_dialer():\n')
        f.write('    """Retorna lista de testes do módulo Dialer importados do CSV."""\n')
        f.write('    return [\n')
        
        for tc in test_cases:
            f.write(f'        TestCase(\n')
            f.write(f'            id="{tc.id}",\n')
            f.write(f'            name={repr(tc.name)},\n')
            f.write(f'            description={repr(tc.description)},\n')
            f.write(f'            priority={tc.priority},\n')
            f.write(f'            module={repr(tc.module)},\n')
            f.write(f'            tags={tc.tags},\n')
            f.write(f'            dependencies={tc.dependencies},\n')
            if tc.validation_point_action:
                f.write(f'            validation_point_action={repr(tc.validation_point_action)},\n')
            if tc.context_preserving:
                f.write(f'            context_preserving=True,\n')
            if tc.teardown_restores:
                f.write(f'            teardown_restores=True,\n')
            if tc.parent_test_id:
                f.write(f'            parent_test_id={repr(tc.parent_test_id)},\n')
            if tc.child_test_ids:
                f.write(f'            child_test_ids={tc.child_test_ids},\n')
            f.write(f'            actions=[\n')
            
            for action in tc.actions:
                f.write(f'                Action(\n')
                f.write(f'                    id={repr(action.id)},\n')
                f.write(f'                    description={repr(action.description)},\n')
                f.write(f'                    action_type=ActionType.{action.action_type.name},\n')
                f.write(f'                    impact=ActionImpact.{action.impact.name},\n')
                f.write(f'                    preconditions={action.preconditions},\n')
                f.write(f'                    postconditions={action.postconditions},\n')
                f.write(f'                    estimated_time={action.estimated_time},\n')
                f.write(f'                    priority={action.priority},\n')
                f.write(f'                    tags={action.tags}\n')
                f.write(f'                ),\n')
            
            f.write(f'            ]\n')
            f.write(f'        ),\n')
        
        f.write('    ]\n')
    
    print(f"\n[OK] Testes salvos em: {output_path}")
    print("\nPara usar no projeto:")
    print("1. Abra testes_motorola.py")
    print("2. Importe: from testes_dialer_importados import criar_testes_dialer")
    print("3. Adicione os testes na função criar_testes_motorola() ou crie uma função separada")


if __name__ == '__main__':
    main()
