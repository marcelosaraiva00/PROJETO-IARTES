"""
Script para expandir testes existentes com ações detalhadas e estabelecer hierarquias
Baseado no padrão dos testes Dialer - cada ação detalhada em múltiplas ações específicas
"""

import sys
from pathlib import Path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from src.models.test_case import TestCase, Action, ActionType, ActionImpact
from testes_motorola_melhorados import criar_testes_motorola


def expand_action(action: Action, context: dict) -> list[Action]:
    """
    Expande uma ação em múltiplas ações detalhadas quando apropriado.
    Retorna lista de ações expandidas ou a ação original se não precisar expansão.
    """
    desc_lower = action.description.lower()
    
    # Ações que devem ser expandidas
    expanded = []
    
    # "Abrir aplicativo X" -> expandir em múltiplas ações
    if "abrir aplicativo" in desc_lower or "abrir app" in desc_lower:
        if "câmera" in desc_lower or "camera" in desc_lower:
            expanded.append(Action(
                id=f"{action.id}_STEP1",
                description="Desbloquear dispositivo se necessário",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions=action.preconditions.copy(),
                postconditions={"device_unlocked"},
                estimated_time=2.0,
                priority=1,
                tags=action.tags.copy() if action.tags else set()
            ))
            expanded.append(Action(
                id=f"{action.id}_STEP2",
                description="Localizar ícone do aplicativo Câmera na tela inicial",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"device_unlocked"},
                postconditions={"camera_icon_visible"},
                estimated_time=2.0,
                priority=1,
                tags=action.tags.copy() if action.tags else set()
            ))
            expanded.append(Action(
                id=action.id,
                description="Tocar no ícone para abrir aplicativo Câmera",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"camera_icon_visible"},
                postconditions=action.postconditions.copy(),
                estimated_time=2.0,
                priority=1,
                tags=action.tags.copy() if action.tags else set()
            ))
            return expanded
    
    # "Abrir Configurações" -> expandir
    if "abrir configurações" in desc_lower or "abrir settings" in desc_lower:
        expanded.append(Action(
            id=f"{action.id}_STEP1",
            description="Desbloquear dispositivo se necessário",
            action_type=ActionType.NAVIGATION,
            impact=ActionImpact.NON_DESTRUCTIVE,
            preconditions=action.preconditions.copy(),
            postconditions={"device_unlocked"},
            estimated_time=2.0,
            priority=1,
            tags=action.tags.copy() if action.tags else set()
        ))
        expanded.append(Action(
            id=f"{action.id}_STEP2",
            description="Abrir menu de aplicativos ou drawer",
            action_type=ActionType.NAVIGATION,
            impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
            preconditions={"device_unlocked"},
            postconditions={"app_drawer_open"},
            estimated_time=2.0,
            priority=1,
            tags=action.tags.copy() if action.tags else set()
        ))
        expanded.append(Action(
            id=action.id,
            description="Localizar e tocar no ícone Configurações",
            action_type=ActionType.NAVIGATION,
            impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
            preconditions={"app_drawer_open"},
            postconditions=action.postconditions.copy(),
            estimated_time=2.0,
            priority=1,
            tags=action.tags.copy() if action.tags else set()
        ))
        return expanded
    
    # "Navegar para X" -> expandir
    if "navegar para" in desc_lower or "navegar" in desc_lower:
        if "wifi" in desc_lower:
            expanded.append(Action(
                id=f"{action.id}_STEP1",
                description="Verificar seção WiFi está visível na lista",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions=action.preconditions.copy(),
                postconditions={"wifi_section_visible"},
                estimated_time=1.0,
                priority=1,
                tags=action.tags.copy() if action.tags else set()
            ))
            expanded.append(Action(
                id=action.id,
                description="Tocar na seção WiFi para abrir configurações",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"wifi_section_visible"},
                postconditions=action.postconditions.copy(),
                estimated_time=2.0,
                priority=1,
                tags=action.tags.copy() if action.tags else set()
            ))
            return expanded
        elif "bluetooth" in desc_lower:
            expanded.append(Action(
                id=f"{action.id}_STEP1",
                description="Verificar seção Bluetooth está visível na lista",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions=action.preconditions.copy(),
                postconditions={"bluetooth_section_visible"},
                estimated_time=1.0,
                priority=1,
                tags=action.tags.copy() if action.tags else set()
            ))
            expanded.append(Action(
                id=action.id,
                description="Tocar na seção Bluetooth para abrir configurações",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"bluetooth_section_visible"},
                postconditions=action.postconditions.copy(),
                estimated_time=2.0,
                priority=1,
                tags=action.tags.copy() if action.tags else set()
            ))
            return expanded
    
    # "Selecionar rede WiFi" -> expandir
    if "selecionar rede" in desc_lower or "selecionar" in desc_lower and "wifi" in desc_lower:
        expanded.append(Action(
            id=f"{action.id}_STEP1",
            description="Verificar lista de redes WiFi disponíveis é exibida",
            action_type=ActionType.VERIFICATION,
            impact=ActionImpact.NON_DESTRUCTIVE,
            preconditions=action.preconditions.copy(),
            postconditions={"wifi_networks_list_visible"},
            estimated_time=3.0,
            priority=1,
            tags=action.tags.copy() if action.tags else set()
        ))
        expanded.append(Action(
            id=action.id,
            description="Tocar na rede WiFi desejada da lista",
            action_type=ActionType.CREATION,
            impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
            preconditions={"wifi_networks_list_visible"},
            postconditions=action.postconditions.copy(),
            estimated_time=2.0,
            priority=1,
            tags=action.tags.copy() if action.tags else set()
        ))
        return expanded
    
    # "Inserir senha" -> expandir
    if "inserir senha" in desc_lower or "digitar senha" in desc_lower:
        expanded.append(Action(
            id=f"{action.id}_STEP1",
            description="Verificar campo de senha está visível e focado",
            action_type=ActionType.VERIFICATION,
            impact=ActionImpact.NON_DESTRUCTIVE,
            preconditions=action.preconditions.copy(),
            postconditions={"password_field_ready"},
            estimated_time=1.0,
            priority=1,
            tags=action.tags.copy() if action.tags else set()
        ))
        expanded.append(Action(
            id=f"{action.id}_STEP2",
            description="Digitar senha WiFi no campo de texto",
            action_type=ActionType.CREATION,
            impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
            preconditions={"password_field_ready"},
            postconditions={"password_entered"},
            estimated_time=4.0,
            priority=1,
            tags=action.tags.copy() if action.tags else set()
        ))
        expanded.append(Action(
            id=action.id,
            description="Confirmar senha e iniciar conexão",
            action_type=ActionType.CREATION,
            impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
            preconditions={"password_entered"},
            postconditions=action.postconditions.copy(),
            estimated_time=2.0,
            priority=1,
            tags=action.tags.copy() if action.tags else set()
        ))
        return expanded
    
    # "Tirar foto" -> expandir
    if "tirar foto" in desc_lower or "capturar foto" in desc_lower:
        expanded.append(Action(
            id=f"{action.id}_STEP1",
            description="Verificar visualização da câmera está estável",
            action_type=ActionType.VERIFICATION,
            impact=ActionImpact.NON_DESTRUCTIVE,
            preconditions=action.preconditions.copy(),
            postconditions={"camera_view_stable"},
            estimated_time=2.0,
            priority=1,
            tags=action.tags.copy() if action.tags else set()
        ))
        expanded.append(Action(
            id=action.id,
            description="Pressionar botão de captura para tirar foto",
            action_type=ActionType.CREATION,
            impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
            preconditions={"camera_view_stable"},
            postconditions=action.postconditions.copy(),
            estimated_time=1.0,
            priority=1,
            tags=action.tags.copy() if action.tags else set()
        ))
        return expanded
    
    # "Iniciar gravação" -> expandir
    if "iniciar gravação" in desc_lower or "iniciar gravar" in desc_lower:
        expanded.append(Action(
            id=f"{action.id}_STEP1",
            description="Verificar modo vídeo está ativo e visualização estável",
            action_type=ActionType.VERIFICATION,
            impact=ActionImpact.NON_DESTRUCTIVE,
            preconditions=action.preconditions.copy(),
            postconditions={"video_view_ready"},
            estimated_time=2.0,
            priority=1,
            tags=action.tags.copy() if action.tags else set()
        ))
        expanded.append(Action(
            id=action.id,
            description="Tocar no botão de gravação para iniciar",
            action_type=ActionType.CREATION,
            impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
            preconditions={"video_view_ready"},
            postconditions=action.postconditions.copy(),
            estimated_time=1.0,
            priority=1,
            tags=action.tags.copy() if action.tags else set()
        ))
        return expanded
    
    # Se não precisa expansão, retorna ação original
    return [action]


def find_shared_actions(test_cases: list[TestCase]) -> dict:
    """
    Identifica ações compartilhadas entre testes para estabelecer hierarquias.
    Retorna dicionário mapeando ação comum -> lista de testes que a compartilham.
    """
    shared = {}
    
    for test in test_cases:
        # Primeira ação geralmente é a "abertura" comum
        if test.actions:
            first_action = test.actions[0]
            key = first_action.description.lower()
            
            if key not in shared:
                shared[key] = []
            shared[key].append(test.id)
    
    return shared


def establish_hierarchy(test_cases: list[TestCase]) -> list[TestCase]:
    """
    Estabelece hierarquias pai-filho baseadas em ações compartilhadas.
    Testes que compartilham ações iniciais comuns têm relação pai-filho.
    """
    test_by_id = {tc.id: tc for tc in test_cases}
    shared_actions = find_shared_actions(test_cases)
    
    # Identificar testes "pai" - testes que têm ações iniciais compartilhadas
    parent_tests = {}
    
    for action_desc, test_ids in shared_actions.items():
        if len(test_ids) > 1:
            # O primeiro teste da lista é considerado "pai"
            parent_id = test_ids[0]
            children = set(test_ids[1:])
            
            if parent_id not in parent_tests:
                parent_tests[parent_id] = set()
            parent_tests[parent_id].update(children)
    
    # Atualizar hierarquias
    for test in test_cases:
        # Se este teste é pai de outros
        if test.id in parent_tests:
            test.child_test_ids.update(parent_tests[test.id])
        
        # Se este teste compartilha ações com outro teste pai
        for parent_id, children in parent_tests.items():
            if test.id in children:
                # Verificar se o teste pai existe e compartilha ações iniciais
                if parent_id in test_by_id:
                    parent_test = test_by_id[parent_id]
                    if parent_test.actions and test.actions:
                        # Se primeira ação é similar, estabelecer relação
                        parent_first = parent_test.actions[0].description.lower()
                        test_first = test.actions[0].description.lower()
                        
                        # Se compartilham ação inicial (ex: "abrir câmera")
                        if parent_first == test_first or (
                            "abrir" in parent_first and "abrir" in test_first and
                            any(word in parent_first and word in test_first 
                                for word in ["câmera", "camera", "configurações", "settings", "wifi", "bluetooth"])
                        ):
                            test.parent_test_id = parent_id
    
    return test_cases


def expand_test_case(test: TestCase) -> TestCase:
    """
    Expande um caso de teste adicionando mais ações detalhadas.
    """
    expanded_actions = []
    
    for action in test.actions:
        expanded = expand_action(action, {})
        expanded_actions.extend(expanded)
    
    # Criar novo teste com ações expandidas
    return TestCase(
        id=test.id,
        name=test.name,
        description=test.description,
        actions=expanded_actions,
        priority=test.priority,
        module=test.module,
        tags=test.tags.copy(),
        dependencies=test.dependencies.copy(),
        validation_point_action=test.validation_point_action,
        context_preserving=test.context_preserving,
        teardown_restores=test.teardown_restores,
        parent_test_id=test.parent_test_id,
        child_test_ids=test.child_test_ids.copy()
    )


def expand_all_tests():
    """
    Expande todos os testes existentes e estabelece hierarquias.
    """
    # Carregar testes existentes
    original_tests = criar_testes_motorola()
    
    # Expandir cada teste
    expanded_tests = []
    for test in original_tests:
        expanded_test = expand_test_case(test)
        expanded_tests.append(expanded_test)
    
    # Estabelecer hierarquias baseadas em ações compartilhadas
    expanded_tests = establish_hierarchy(expanded_tests)
    
    return expanded_tests


def criar_testes_motorola_expandidos():
    """
    Retorna testes Motorola expandidos com ações detalhadas e hierarquias estabelecidas.
    """
    return expand_all_tests()


if __name__ == "__main__":
    # Testar expansão
    expanded = expand_all_tests()
    print(f"Total de testes expandidos: {len(expanded)}")
    
    # Mostrar exemplo
    cam_test = next((t for t in expanded if t.id == "MOTO_CAM_001"), None)
    if cam_test:
        print(f"\nExemplo - {cam_test.id}: {cam_test.name}")
        print(f"Total de ações: {len(cam_test.actions)}")
        print(f"Filhos: {cam_test.child_test_ids}")
        for i, action in enumerate(cam_test.actions[:5], 1):
            print(f"  {i}. {action.description}")
