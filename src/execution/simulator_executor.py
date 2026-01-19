from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime
from typing import Set

from src.models.test_case import ActionImpact, TestCase
from src.execution.executor_base import ExecutionResult, State


@dataclass
class SimulatorConfig:
    """
    Config do simulador.
    - precondition_failure_prob: chance de falhar mesmo com pré-condições ok (flakiness)
    - destructive_corruption_prob: chance de uma ação destrutiva "corromper" o estado
    - time_noise_std: variação do tempo em torno do estimado
    """
    seed: int = 42
    baseline_state: Set[str] = None  # estado retornado após reset (ex: pós-setup)
    precondition_failure_prob: float = 0.03
    destructive_corruption_prob: float = 0.08
    time_noise_std: float = 0.15


class SimulatorExecutor:
    """
    Executor simulado (para treinar a IA sem precisar de device).

    Regras:
    - Se uma ação exigir preconditions não presentes no estado → falha
    - Ações destrutivas/partially destrutivas podem introduzir 'state_corrupted'
    - Tempo real = soma dos tempos estimados com ruído
    """

    def __init__(self, config: SimulatorConfig | None = None):
        self.config = config or SimulatorConfig()
        self._rng = random.Random(self.config.seed)
        # baseline padrão: simula um device já configurado (pós-setup)
        if self.config.baseline_state is None:
            self.config.baseline_state = {
                "device_on",
                "google_logged_in",
                "wifi_connected",
                "setup_complete",
            }

    def reset(self) -> State:
        # Reset deve voltar para um estado conhecido e utilizável.
        return set(self.config.baseline_state)

    def execute_test_case(self, test_case: TestCase, current_state: State) -> tuple[ExecutionResult, State]:
        started_at = datetime.now()
        initial_state = set(current_state)
        state: Set[str] = set(current_state)

        # Se estado já está corrompido, há maior chance de falha
        corrupted = "state_corrupted" in state

        total_time = 0.0
        required_reset = False
        failed_action_id = None
        notes = ""

        for action in test_case.actions:
            # Pré-condições
            missing = action.preconditions.difference(state)
            if missing:
                failed_action_id = action.id
                notes = f"Falha por precondições faltando: {sorted(missing)}"
                required_reset = action.impact in (ActionImpact.DESTRUCTIVE, ActionImpact.PARTIALLY_DESTRUCTIVE)
                finished_at = datetime.now()
                result = ExecutionResult(
                    test_case_id=test_case.id,
                    started_at=started_at,
                    finished_at=finished_at,
                    actual_execution_time=max(total_time, 0.1),
                    success=False,
                    required_reset=required_reset,
                    notes=notes,
                    initial_state=initial_state,
                    final_state=set(state),
                    failed_action_id=failed_action_id,
                )
                return result, state

            # Flakiness
            flake_prob = self.config.precondition_failure_prob * (2.0 if corrupted else 1.0)
            if self._rng.random() < flake_prob:
                failed_action_id = action.id
                notes = "Falha simulada (flaky) durante execução da ação"
                required_reset = True
                finished_at = datetime.now()
                result = ExecutionResult(
                    test_case_id=test_case.id,
                    started_at=started_at,
                    finished_at=finished_at,
                    actual_execution_time=max(total_time + 0.2, 0.2),
                    success=False,
                    required_reset=required_reset,
                    notes=notes,
                    initial_state=initial_state,
                    final_state=set(state),
                    failed_action_id=failed_action_id,
                )
                return result, state

            # Tempo (com ruído)
            base = max(action.estimated_time, 0.1)
            noise = self._rng.gauss(0.0, self.config.time_noise_std)
            total_time += max(0.05, base * (1.0 + noise))

            # Aplicar pós-condições
            state.update(action.postconditions)

            # Ações destrutivas podem corromper
            if action.impact in (ActionImpact.DESTRUCTIVE, ActionImpact.PARTIALLY_DESTRUCTIVE):
                if self._rng.random() < self.config.destructive_corruption_prob:
                    state.add("state_corrupted")
                    required_reset = True

        # Sucesso
        finished_at = datetime.now()
        result = ExecutionResult(
            test_case_id=test_case.id,
            started_at=started_at,
            finished_at=finished_at,
            actual_execution_time=max(total_time, 0.2),
            success=True,
            required_reset=required_reset,
            notes=notes or "OK",
            initial_state=initial_state,
            final_state=set(state),
            failed_action_id=None,
        )
        return result, state

