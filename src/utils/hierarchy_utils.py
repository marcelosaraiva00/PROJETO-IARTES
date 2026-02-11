"""
Utilitários para trabalhar com estrutura hierárquica de testes.
Suporta ordenação hierárquica, agrupamento por caminho compartilhado e propagação de falhas.
"""
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
from src.models.test_case import TestCase


def get_tree_level(test: TestCase, test_by_id: Dict[str, TestCase]) -> int:
    """
    Calcula o nível do teste na árvore hierárquica.
    Raiz = 0, filhos = 1, netos = 2, etc.
    """
    if not test.parent_test_id or test.parent_test_id not in test_by_id:
        return 0
    
    parent = test_by_id[test.parent_test_id]
    return 1 + get_tree_level(parent, test_by_id)


def get_ancestors(test: TestCase, test_by_id: Dict[str, TestCase]) -> List[str]:
    """Retorna lista de IDs de ancestrais (do mais próximo ao mais distante)."""
    ancestors = []
    current = test
    
    while current.parent_test_id and current.parent_test_id in test_by_id:
        ancestors.append(current.parent_test_id)
        current = test_by_id[current.parent_test_id]
    
    return ancestors


def get_descendants(test: TestCase, test_by_id: Dict[str, TestCase]) -> Set[str]:
    """Retorna conjunto de IDs de todos os descendentes (filhos, netos, etc.)."""
    descendants = set(test.child_test_ids)
    
    for child_id in test.child_test_ids:
        if child_id in test_by_id:
            child = test_by_id[child_id]
            descendants.update(get_descendants(child, test_by_id))
    
    return descendants


def find_shared_path(test1: TestCase, test2: TestCase, test_by_id: Dict[str, TestCase]) -> List[str]:
    """
    Encontra o caminho compartilhado entre dois testes.
    Retorna lista de IDs de testes no caminho comum (da raiz até o último ancestral comum).
    """
    ancestors1 = set(get_ancestors(test1, test_by_id))
    ancestors2 = set(get_ancestors(test2, test_by_id))
    
    # Adicionar os próprios testes se um é ancestral do outro
    if test1.id in ancestors2:
        ancestors1.add(test1.id)
    if test2.id in ancestors1:
        ancestors2.add(test2.id)
    
    common = ancestors1.intersection(ancestors2)
    
    # Ordenar por nível (raiz primeiro)
    common_list = []
    for tid in common:
        if tid in test_by_id:
            common_list.append((get_tree_level(test_by_id[tid], test_by_id), tid))
    
    common_list.sort()
    return [tid for _, tid in common_list]


def get_shared_path_length(test1: TestCase, test2: TestCase, test_by_id: Dict[str, TestCase]) -> int:
    """Retorna o comprimento do caminho compartilhado entre dois testes."""
    return len(find_shared_path(test1, test2, test_by_id))


def group_tests_by_shared_path(test_cases: List[TestCase], test_by_id: Dict[str, TestCase] = None) -> List[List[TestCase]]:
    """
    Agrupa testes que compartilham um caminho comum significativo.
    Retorna lista de grupos, onde cada grupo contém testes que podem ser executados juntos.
    """
    if test_by_id is None:
        test_by_id = {tc.id: tc for tc in test_cases}
    
    groups = []
    used = set()
    
    for tc1 in test_cases:
        if tc1.id in used:
            continue
        
        # Criar grupo começando com tc1
        group = [tc1]
        used.add(tc1.id)
        
        # Procurar outros testes que compartilham caminho significativo
        for tc2 in test_cases:
            if tc2.id in used or tc2.id == tc1.id:
                continue
            
            # Se compartilham pelo menos 2 ancestrais ou um é ancestral do outro
            shared = find_shared_path(tc1, tc2, test_by_id)
            ancestors1 = set(get_ancestors(tc1, test_by_id))
            ancestors2 = set(get_ancestors(tc2, test_by_id))
            
            # Critério: compartilham caminho significativo OU um é ancestral do outro
            if (len(shared) >= 2 or 
                tc1.id in ancestors2 or 
                tc2.id in ancestors1 or
                (tc1.parent_test_id and tc1.parent_test_id == tc2.parent_test_id)):
                group.append(tc2)
                used.add(tc2.id)
        
        if group:
            groups.append(group)
    
    return groups


def can_group_tests(test1: TestCase, test2: TestCase, test_by_id: Dict[str, TestCase]) -> bool:
    """
    Verifica se dois testes podem ser agrupados para execução sequencial.
    Considera hierarquia, contexto preservado e teardown.
    """
    # Se um é ancestral do outro, podem ser agrupados
    ancestors1 = set(get_ancestors(test1, test_by_id))
    ancestors2 = set(get_ancestors(test2, test_by_id))
    
    if test1.id in ancestors2 or test2.id in ancestors1:
        return True
    
    # Se compartilham caminho significativo
    shared = find_shared_path(test1, test2, test_by_id)
    if len(shared) >= 2:
        return True
    
    # Se ambos preservam contexto, podem ser agrupados
    if test1.context_preserving and test2.context_preserving:
        return True
    
    # Se um tem teardown_restores, pode vir antes do outro sem problema
    if test1.teardown_restores:
        return True
    
    return False


def order_by_hierarchy(test_cases: List[TestCase]) -> List[TestCase]:
    """
    Ordena testes respeitando a hierarquia (raiz primeiro, depois filhos).
    Retorna lista ordenada por nível na árvore.
    """
    test_by_id = {tc.id: tc for tc in test_cases}
    
    # Agrupar por nível
    by_level = defaultdict(list)
    for tc in test_cases:
        level = get_tree_level(tc, test_by_id)
        by_level[level].append(tc)
    
    # Ordenar por nível (raiz primeiro)
    ordered = []
    for level in sorted(by_level.keys()):
        # Dentro do mesmo nível, manter ordem original ou ordenar por ID
        level_tests = sorted(by_level[level], key=lambda tc: tc.id)
        ordered.extend(level_tests)
    
    return ordered


def estimate_resets_with_hierarchy(test_order: List[TestCase]) -> int:
    """
    Estima número de resets considerando hierarquia e teardown.
    Testes com teardown_restores não causam reset porque voltam ao estado anterior.
    """
    resets = 0
    current_state = set()
    
    for test in test_order:
        # Se teste tem teardown_restores, não altera estado final
        if test.teardown_restores:
            # Ainda precisa verificar pré-condições, mas não altera estado final
            required = test.get_preconditions()
            if required and not required.issubset(current_state):
                resets += 1
                current_state = set()
            # Estado não é atualizado (volta no teardown)
            continue
        
        # Teste normal: verificar pré-condições
        required = test.get_preconditions()
        if required and not required.issubset(current_state):
            resets += 1
            current_state = set()
        
        # Atualizar estado (a menos que seja context_preserving sem alteração real)
        if not test.context_preserving:
            current_state.update(test.get_postconditions())
        
        # Se destrutivo, limpar estado
        if test.has_destructive_actions():
            current_state = set()
    
    return resets


def calculate_hierarchy_score(test_order: List[TestCase], test_by_id: Dict[str, TestCase]) -> float:
    """
    Calcula score de qualidade baseado em hierarquia.
    Bônus por:
    - Respeitar ordem hierárquica (raiz antes de filhos)
    - Agrupar testes com caminho compartilhado
    - Agrupar testes context_preserving
    - Reduzir resets (considerando teardown)
    """
    score = 100.0
    
    # Penalizar violações de hierarquia
    violations = 0
    executed = set()
    for test in test_order:
        if test.parent_test_id and test.parent_test_id not in executed:
            violations += 1
        executed.add(test.id)
    
    score -= violations * 25
    
    # Bônus por agrupamento de testes com caminho compartilhado
    groups = group_tests_by_shared_path(test_order)
    score += len(groups) * 15
    
    # Bônus por agrupar testes context_preserving
    context_preserving_groups = 0
    i = 0
    while i < len(test_order):
        if test_order[i].context_preserving:
            group_start = i
            while i < len(test_order) and test_order[i].context_preserving:
                i += 1
            if i - group_start > 1:
                context_preserving_groups += 1
        else:
            i += 1
    
    score += context_preserving_groups * 10
    
    # Bônus por reduzir resets (considerando teardown)
    resets = estimate_resets_with_hierarchy(test_order)
    max_possible_resets = len(test_order)
    reset_reduction = max_possible_resets - resets
    score += reset_reduction * 5
    
    return max(score, 0.0)
