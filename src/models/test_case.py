"""
Modelos de dados para casos de teste e ações
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum
from datetime import datetime


class ActionType(Enum):
    """Tipos de ações em um teste"""
    CREATION = "creation"  # Criação de dados/estado
    VERIFICATION = "verification"  # Verificação/checagem
    MODIFICATION = "modification"  # Modificação de estado
    DELETION = "deletion"  # Deleção de dados
    NAVIGATION = "navigation"  # Navegação na interface


class ActionImpact(Enum):
    """Impacto da ação no estado do sistema"""
    NON_DESTRUCTIVE = "non_destructive"  # Não altera estado (ex: verificações)
    PARTIALLY_DESTRUCTIVE = "partially_destructive"  # Altera parcialmente
    DESTRUCTIVE = "destructive"  # Altera completamente o estado


@dataclass
class Action:
    """Representa uma ação individual dentro de um caso de teste"""
    id: str
    description: str
    action_type: ActionType
    impact: ActionImpact
    preconditions: Set[str] = field(default_factory=set)  # Estados necessários
    postconditions: Set[str] = field(default_factory=set)  # Estados resultantes
    estimated_time: float = 0.0  # Tempo estimado em segundos
    priority: int = 1  # Prioridade da ação (1-5)
    tags: Set[str] = field(default_factory=set)  # Tags para categorização
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if isinstance(other, Action):
            return self.id == other.id
        return False


@dataclass
class TestCase:
    """Representa um caso de teste completo"""
    id: str
    name: str
    description: str
    actions: List[Action] = field(default_factory=list)
    priority: int = 1  # Prioridade do teste (1-5)
    module: str = ""  # Módulo/funcionalidade testada
    tags: Set[str] = field(default_factory=set)
    dependencies: Set[str] = field(default_factory=set)  # IDs de outros testes
    
    # Metadados de execução
    average_execution_time: float = 0.0
    success_rate: float = 1.0
    last_executed: Optional[datetime] = None
    times_executed: int = 0
    
    def get_total_estimated_time(self) -> float:
        """Calcula tempo total estimado do teste"""
        return sum(action.estimated_time for action in self.actions)
    
    def get_preconditions(self) -> Set[str]:
        """Retorna todas as pré-condições necessárias"""
        preconditions = set()
        for action in self.actions:
            preconditions.update(action.preconditions)
        return preconditions
    
    def get_postconditions(self) -> Set[str]:
        """Retorna todas as pós-condições geradas"""
        postconditions = set()
        for action in self.actions:
            postconditions.update(action.postconditions)
        return postconditions
    
    def has_destructive_actions(self) -> bool:
        """Verifica se o teste contém ações REALMENTE destrutivas (não parciais)"""
        return any(
            action.impact == ActionImpact.DESTRUCTIVE
            for action in self.actions
        )
    
    def has_state_changing_actions(self) -> bool:
        """Verifica se o teste altera estado (destrutivo OU parcialmente destrutivo)"""
        return any(
            action.impact in [ActionImpact.DESTRUCTIVE, ActionImpact.PARTIALLY_DESTRUCTIVE]
            for action in self.actions
        )
    
    def get_impact_level(self) -> str:
        """
        Retorna o nível de impacto MÁXIMO do teste (pior caso).
        
        Returns:
            'destructive' - tem ações que destroem dados
            'partially_destructive' - tem ações que alteram estado parcialmente
            'non_destructive' - apenas lê/verifica
        """
        if any(action.impact == ActionImpact.DESTRUCTIVE for action in self.actions):
            return 'destructive'
        elif any(action.impact == ActionImpact.PARTIALLY_DESTRUCTIVE for action in self.actions):
            return 'partially_destructive'
        else:
            return 'non_destructive'
    
    def get_impact_composition(self) -> dict:
        """
        Retorna a composição detalhada de impactos no teste.
        
        Returns:
            Dict com contagens e percentuais de cada tipo de ação
        """
        total = len(self.actions)
        if total == 0:
            return {'non_destructive': 0, 'partially_destructive': 0, 'destructive': 0}
        
        non = sum(1 for a in self.actions if a.impact == ActionImpact.NON_DESTRUCTIVE)
        partial = sum(1 for a in self.actions if a.impact == ActionImpact.PARTIALLY_DESTRUCTIVE)
        destruct = sum(1 for a in self.actions if a.impact == ActionImpact.DESTRUCTIVE)
        
        return {
            'non_destructive': {'count': non, 'percent': round((non / total) * 100)},
            'partially_destructive': {'count': partial, 'percent': round((partial / total) * 100)},
            'destructive': {'count': destruct, 'percent': round((destruct / total) * 100)},
            'total': total
        }
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if isinstance(other, TestCase):
            return self.id == other.id
        return False


@dataclass
class TestSuite:
    """Representa uma suíte de testes"""
    id: str
    name: str
    description: str
    test_cases: List[TestCase] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_total_tests(self) -> int:
        """Retorna o número total de testes"""
        return len(self.test_cases)
    
    def get_total_estimated_time(self) -> float:
        """Calcula tempo total estimado da suíte"""
        return sum(tc.get_total_estimated_time() for tc in self.test_cases)
    
    def get_all_modules(self) -> Set[str]:
        """Retorna todos os módulos cobertos pela suíte"""
        return {tc.module for tc in self.test_cases if tc.module}


@dataclass
class ExecutionFeedback:
    """Feedback de execução de um teste"""
    test_case_id: str
    executed_at: datetime
    actual_execution_time: float
    success: bool
    followed_recommendation: bool  # Se seguiu a ordem recomendada
    tester_rating: Optional[int] = None  # Avaliação do testador (1-5)
    required_reset: bool = False  # Se precisou reinicializar o sistema
    notes: str = ""
    
    # Estado do sistema antes/depois
    initial_state: Set[str] = field(default_factory=set)
    final_state: Set[str] = field(default_factory=set)


@dataclass
class RecommendationResult:
    """Resultado de uma recomendação de ordenação"""
    recommended_order: List[str]  # Lista de IDs de TestCase
    estimated_total_time: float
    estimated_resets: int
    confidence_score: float  # Confiança na recomendação (0-1)
    reasoning: Dict[str, any] = field(default_factory=dict)  # Justificativa
    generated_at: datetime = field(default_factory=datetime.now)
