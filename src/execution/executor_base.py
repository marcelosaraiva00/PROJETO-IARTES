from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Set, Protocol

from src.models.test_case import TestCase


State = Set[str]


@dataclass
class ExecutionResult:
    """Resultado bruto da execução (antes de virar ExecutionFeedback)."""
    test_case_id: str
    started_at: datetime
    finished_at: datetime
    actual_execution_time: float
    success: bool
    required_reset: bool = False
    notes: str = ""
    initial_state: State = field(default_factory=set)
    final_state: State = field(default_factory=set)
    failed_action_id: Optional[str] = None


class TestExecutor(Protocol):
    """
    Interface de execução.

    Implementações:
    - SimulatorExecutor: executa em um ambiente simulado (treino offline)
    - AndroidAppiumExecutor: executa no Android real (Appium/UIAutomator2)
    """

    def reset(self) -> State:
        """Reseta o ambiente/dispositivo para um estado conhecido."""
        ...

    def execute_test_case(self, test_case: TestCase, current_state: State) -> tuple[ExecutionResult, State]:
        """Executa um TestCase e retorna (resultado, novo_estado)."""
        ...

