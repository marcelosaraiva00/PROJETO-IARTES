"""
Executor Hierárquico: Suporta execução incremental, propagação de falhas e teardown.

Este executor implementa:
1. Execução incremental (múltiplos testes validados em uma sequência)
2. Propagação de falhas (se pai falha, filhos também falham)
3. Reinício da raiz quando necessário
4. Teardown automático para testes com teardown_restores=True
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict

from src.models.test_case import TestCase
from src.execution.executor_base import ExecutionResult, State, TestExecutor
from src.utils.hierarchy_utils import (
    get_tree_level, get_ancestors, get_descendants,
    find_shared_path, order_by_hierarchy
)


@dataclass
class HierarchicalExecutionResult:
    """Resultado de execução hierárquica com múltiplos testes validados"""
    executed_tests: List[str]  # IDs dos testes executados
    validated_tests: List[str]  # IDs dos testes validados (pode ser subset de executed)
    failed_tests: Set[str]  # IDs dos testes que falharam
    propagated_failures: Set[str]  # IDs de testes marcados como falhados por propagação
    results: Dict[str, ExecutionResult]  # Resultado de cada teste executado
    total_time: float
    total_resets: int
    sequence_started_at: datetime
    sequence_finished_at: datetime
    notes: List[str] = field(default_factory=list)


class HierarchicalExecutor:
    """
    Executor que suporta estrutura hierárquica de testes.
    
    Funcionalidades:
    - Execução incremental: valida múltiplos testes em uma sequência
    - Propagação de falhas: se pai falha, filhos também falham
    - Reinício da raiz: quando há falha hierárquica, reinicia da próxima raiz
    - Teardown automático: executa teardown para testes com teardown_restores=True
    """
    
    def __init__(self, base_executor: TestExecutor):
        """
        Args:
            base_executor: Executor base (SimulatorExecutor ou AndroidAppiumExecutor)
        """
        self.base_executor = base_executor
        self.test_by_id: Dict[str, TestCase] = {}
    
    def execute_hierarchical_sequence(
        self,
        test_order: List[TestCase],
        initial_state: Optional[State] = None
    ) -> HierarchicalExecutionResult:
        """
        Executa uma sequência hierárquica de testes.
        
        Args:
            test_order: Ordem de testes a executar
            initial_state: Estado inicial (None = reset)
        
        Returns:
            Resultado hierárquico com informações de execução e validação
        """
        if not test_order:
            return HierarchicalExecutionResult(
                executed_tests=[],
                validated_tests=[],
                failed_tests=set(),
                propagated_failures=set(),
                results={},
                total_time=0.0,
                total_resets=0,
                sequence_started_at=datetime.now(),
                sequence_finished_at=datetime.now()
            )
        
        # Mapear testes por ID
        self.test_by_id = {tc.id: tc for tc in test_order}
        
        # Estado inicial
        if initial_state is None:
            state = self.base_executor.reset()
            resets = 1
        else:
            state = set(initial_state)
            resets = 0
        
        sequence_started_at = datetime.now()
        executed_tests: List[str] = []
        validated_tests: List[str] = []
        failed_tests: Set[str] = set()
        propagated_failures: Set[str] = set()
        results: Dict[str, ExecutionResult] = {}
        notes: List[str] = []
        total_time = 0.0
        
        # Executar testes em ordem
        i = 0
        while i < len(test_order):
            test = test_order[i]
            
            # Verificar se algum ancestral falhou (propagação de falha)
            if self._has_failed_ancestor(test, failed_tests):
                # Marcar como falhado por propagação
                propagated_failures.add(test.id)
                failed_tests.add(test.id)
                
                # Criar resultado de falha propagada
                result = ExecutionResult(
                    test_case_id=test.id,
                    started_at=datetime.now(),
                    finished_at=datetime.now(),
                    actual_execution_time=0.0,
                    success=False,
                    required_reset=False,
                    notes=f"Falha propagada: teste ancestral falhou",
                    initial_state=set(),
                    final_state=set(),
                    failed_action_id=None
                )
                results[test.id] = result
                notes.append(f"TEST-{test.id}: Falha propagada (ancestral falhou)")
                
                # Pular para próximo teste
                i += 1
                continue
            
            # Executar teste
            try:
                result, new_state = self.base_executor.execute_test_case(test, state)
                results[test.id] = result
                executed_tests.append(test.id)
                total_time += result.actual_execution_time
                
                # Se teste tem validation_point_action, foi validado
                if test.validation_point_action:
                    validated_tests.append(test.id)
                    notes.append(f"TEST-{test.id}: Validado em {test.validation_point_action}")
                
                # Verificar se falhou
                if not result.success:
                    failed_tests.add(test.id)
                    notes.append(f"TEST-{test.id}: FALHOU - {result.notes}")
                    
                    # Propagação: marcar todos os filhos como falhados
                    descendants = get_descendants(test, self.test_by_id)
                    for child_id in descendants:
                        if child_id not in failed_tests:
                            propagated_failures.add(child_id)
                            failed_tests.add(child_id)
                            notes.append(f"TEST-{child_id}: Falha propagada (pai {test.id} falhou)")
                    
                    # Reiniciar da raiz: encontrar próxima raiz não executada
                    next_root = self._find_next_root(test_order, i + 1, executed_tests, failed_tests)
                    if next_root is not None:
                        notes.append(f"Reiniciando da raiz: TEST-{next_root.id}")
                        # Resetar estado e continuar da raiz
                        state = self.base_executor.reset()
                        resets += 1
                        # Encontrar índice do próximo root
                        for idx, tc in enumerate(test_order):
                            if tc.id == next_root.id:
                                i = idx
                                break
                        else:
                            i += 1
                        continue
                    else:
                        # Não há mais raízes, terminar
                        break
                
                # Teste passou: atualizar estado
                # Se tem teardown_restores, estado não muda (volta no teardown)
                if test.teardown_restores:
                    # Executar teardown (voltar tela anterior)
                    self._execute_teardown(test)
                    # Estado permanece o mesmo
                    notes.append(f"TEST-{test.id}: Teardown executado (estado restaurado)")
                elif not test.context_preserving:
                    # Atualizar estado normalmente
                    state = new_state
                
                # Se destrutivo, considerar reset do estado
                if test.has_destructive_actions():
                    state = set()
                
                # Verificar se precisa de reset
                if result.required_reset:
                    state = self.base_executor.reset()
                    resets += 1
                    notes.append(f"Reset necessário após TEST-{test.id}")
                
            except Exception as e:
                # Erro na execução
                failed_tests.add(test.id)
                notes.append(f"TEST-{test.id}: ERRO - {str(e)}")
                
                # Propagação
                descendants = get_descendants(test, self.test_by_id)
                for child_id in descendants:
                    if child_id not in failed_tests:
                        propagated_failures.add(child_id)
                        failed_tests.add(child_id)
                
                # Reiniciar da raiz
                next_root = self._find_next_root(test_order, i + 1, executed_tests, failed_tests)
                if next_root is not None:
                    state = self.base_executor.reset()
                    resets += 1
                    for idx, tc in enumerate(test_order):
                        if tc.id == next_root.id:
                            i = idx
                            break
                    else:
                        i += 1
                    continue
                else:
                    break
            
            i += 1
        
        sequence_finished_at = datetime.now()
        
        return HierarchicalExecutionResult(
            executed_tests=executed_tests,
            validated_tests=validated_tests,
            failed_tests=failed_tests,
            propagated_failures=propagated_failures,
            results=results,
            total_time=total_time,
            total_resets=resets,
            sequence_started_at=sequence_started_at,
            sequence_finished_at=sequence_finished_at,
            notes=notes
        )
    
    def _has_failed_ancestor(self, test: TestCase, failed_tests: Set[str]) -> bool:
        """Verifica se algum ancestral do teste falhou."""
        ancestors = get_ancestors(test, self.test_by_id)
        return any(anc_id in failed_tests for anc_id in ancestors)
    
    def _find_next_root(
        self,
        test_order: List[TestCase],
        start_index: int,
        executed_tests: List[str],
        failed_tests: Set[str]
    ) -> Optional[TestCase]:
        """
        Encontra a próxima raiz (teste sem pai) não executada e não falhada.
        
        Args:
            test_order: Ordem completa de testes
            start_index: Índice para começar a procurar
            executed_tests: IDs de testes já executados
            failed_tests: IDs de testes que falharam
        
        Returns:
            Próximo teste raiz ou None se não houver
        """
        for i in range(start_index, len(test_order)):
            test = test_order[i]
            # Raiz = sem pai OU pai já foi executado
            is_root = (
                not test.parent_test_id or
                test.parent_test_id in executed_tests
            )
            
            # Não deve ter falhado nem ter ancestral falhado
            if (is_root and 
                test.id not in failed_tests and
                not self._has_failed_ancestor(test, failed_tests)):
                return test
        
        return None
    
    def _execute_teardown(self, test: TestCase):
        """
        Executa ações de teardown para um teste.
        Por padrão, volta para a tela anterior (back).
        
        Args:
            test: Teste com teardown_restores=True
        """
        if not test.teardown_restores:
            return
        
        # Implementação básica: voltar uma tela (back)
        # Em implementação real, isso dependeria do executor base
        try:
            # Se for AppiumExecutor, usar back()
            if hasattr(self.base_executor, '_back'):
                self.base_executor._back(times=1)
            elif hasattr(self.base_executor, '_driver'):
                # Tentar usar driver.back() se disponível
                try:
                    self.base_executor._driver.back()
                except:
                    pass
        except Exception as e:
            # Se teardown falhar, apenas logar (não quebrar execução)
            print(f"Aviso: Teardown falhou para TEST-{test.id}: {e}")
