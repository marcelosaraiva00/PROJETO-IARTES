"""
Módulo de execução automática de casos de teste.

Objetivo:
- Executar TestCase/Action (via simulador ou automação real)
- Coletar métricas (tempo, sucesso, reset, etc.)
- Gerar ExecutionFeedback automaticamente para o ML aprender
"""

from src.execution.hierarchical_executor import HierarchicalExecutor, HierarchicalExecutionResult

