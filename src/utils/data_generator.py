"""
Gerador de dados sintéticos para testes e experimentação
"""
import random
from typing import List, Set
from datetime import datetime, timedelta

from src.models.test_case import (
    TestCase, Action, TestSuite,
    ActionType, ActionImpact
)


class SyntheticDataGenerator:
    """Gera dados sintéticos de casos de teste para treinamento e experimentação"""
    
    def __init__(self, seed: int = 42):
        """
        Inicializa o gerador
        
        Args:
            seed: Semente para geração aleatória reproduzível
        """
        random.seed(seed)
        self.action_counter = 0
        self.test_counter = 0
        
        # Templates de descrições
        self.modules = [
            "Authentication", "Products", "Orders", "Users", 
            "Reports", "Settings", "Dashboard", "Notifications"
        ]
        
        self.action_templates = {
            ActionType.NAVIGATION: [
                "Navegar para página de {module}",
                "Acessar seção de {module}",
                "Abrir tela de {module}",
            ],
            ActionType.CREATION: [
                "Criar novo {entity}",
                "Adicionar {entity}",
                "Inserir dados de {entity}",
            ],
            ActionType.VERIFICATION: [
                "Verificar {entity} exibido",
                "Validar dados de {entity}",
                "Confirmar {entity} correto",
            ],
            ActionType.MODIFICATION: [
                "Editar {entity}",
                "Atualizar dados de {entity}",
                "Modificar {entity}",
            ],
            ActionType.DELETION: [
                "Deletar {entity}",
                "Remover {entity}",
                "Excluir {entity}",
            ]
        }
    
    def _generate_action_id(self) -> str:
        """Gera ID único para ação"""
        self.action_counter += 1
        return f"A{self.action_counter:04d}"
    
    def _generate_test_id(self) -> str:
        """Gera ID único para teste"""
        self.test_counter += 1
        return f"TC{self.test_counter:04d}"
    
    def generate_action(
        self,
        action_type: ActionType,
        module: str,
        preconditions: Set[str] = None,
        force_impact: ActionImpact = None
    ) -> Action:
        """
        Gera uma ação sintética
        
        Args:
            action_type: Tipo da ação
            module: Módulo relacionado
            preconditions: Pré-condições (opcional)
            force_impact: Forçar impacto específico (opcional)
            
        Returns:
            Ação gerada
        """
        action_id = self._generate_action_id()
        
        # Gerar descrição
        template = random.choice(self.action_templates[action_type])
        entity = module.lower().rstrip('s')
        description = template.format(module=module, entity=entity)
        
        # Determinar impacto baseado no tipo (se não forçado)
        if force_impact:
            impact = force_impact
        else:
            impact_map = {
                ActionType.NAVIGATION: ActionImpact.NON_DESTRUCTIVE,
                ActionType.VERIFICATION: ActionImpact.NON_DESTRUCTIVE,
                ActionType.CREATION: ActionImpact.DESTRUCTIVE,
                ActionType.MODIFICATION: ActionImpact.PARTIALLY_DESTRUCTIVE,
                ActionType.DELETION: ActionImpact.DESTRUCTIVE,
            }
            impact = impact_map.get(action_type, ActionImpact.PARTIALLY_DESTRUCTIVE)
        
        # Gerar pós-condições baseadas no tipo de ação
        postconditions = set()
        if action_type == ActionType.NAVIGATION:
            postconditions.add(f"on_{module.lower()}_page")
        elif action_type == ActionType.CREATION:
            postconditions.add(f"{entity}_created")
        elif action_type == ActionType.VERIFICATION:
            postconditions.add(f"{entity}_verified")
        elif action_type == ActionType.MODIFICATION:
            postconditions.add(f"{entity}_updated")
        elif action_type == ActionType.DELETION:
            postconditions.add(f"{entity}_deleted")
        
        # Tempo estimado aleatório baseado no tipo
        time_ranges = {
            ActionType.NAVIGATION: (1.0, 3.0),
            ActionType.VERIFICATION: (2.0, 5.0),
            ActionType.CREATION: (3.0, 8.0),
            ActionType.MODIFICATION: (2.0, 6.0),
            ActionType.DELETION: (1.0, 3.0),
        }
        time_range = time_ranges[action_type]
        estimated_time = random.uniform(*time_range)
        
        # Prioridade aleatória
        priority = random.randint(1, 5)
        
        return Action(
            id=action_id,
            description=description,
            action_type=action_type,
            impact=impact,
            preconditions=preconditions or set(),
            postconditions=postconditions,
            estimated_time=estimated_time,
            priority=priority,
            tags={module.lower(), action_type.value}
        )
    
    def generate_test_case(
        self,
        module: str,
        num_actions: int = None,
        priority: int = None,
        include_dependencies: bool = True
    ) -> TestCase:
        """
        Gera um caso de teste sintético
        
        Args:
            module: Módulo do teste
            num_actions: Número de ações (aleatório se None)
            priority: Prioridade (aleatória se None)
            include_dependencies: Se deve incluir dependências
            
        Returns:
            Caso de teste gerado
        """
        test_id = self._generate_test_id()
        
        # Número de ações
        if num_actions is None:
            num_actions = random.randint(3, 8)
        
        # Prioridade
        if priority is None:
            priority = random.randint(1, 5)
        
        # Gerar sequência lógica de ações
        actions = []
        current_preconditions = set()
        
        # Sempre começar com navegação
        nav_action = self.generate_action(
            ActionType.NAVIGATION,
            module,
            current_preconditions
        )
        actions.append(nav_action)
        current_preconditions.update(nav_action.postconditions)
        
        # Gerar ações restantes
        action_types = [
            ActionType.CREATION,
            ActionType.VERIFICATION,
            ActionType.MODIFICATION,
            ActionType.VERIFICATION,
        ]
        
        for i in range(min(num_actions - 1, len(action_types))):
            action_type = action_types[i]
            action = self.generate_action(
                action_type,
                module,
                current_preconditions.copy()
            )
            actions.append(action)
            current_preconditions.update(action.postconditions)
        
        # Metadados de execução simulados
        success_rate = random.uniform(0.85, 0.99)
        times_executed = random.randint(0, 50)
        
        last_executed = None
        if times_executed > 0:
            days_ago = random.randint(1, 30)
            last_executed = datetime.now() - timedelta(days=days_ago)
        
        avg_time = sum(a.estimated_time for a in actions) * random.uniform(0.9, 1.2)
        
        # Dependências (se aplicável)
        dependencies = set()
        if include_dependencies and self.test_counter > 1 and random.random() < 0.3:
            # 30% de chance de ter dependência
            num_deps = random.randint(1, min(2, self.test_counter - 1))
            for _ in range(num_deps):
                dep_id = f"TC{random.randint(1, self.test_counter - 1):04d}"
                dependencies.add(dep_id)
        
        # Nome e descrição
        action_verb = random.choice([
            "Test", "Verify", "Validate", "Check"
        ])
        
        entity = module.lower().rstrip('s')
        operation = random.choice([
            "Creation", "Update", "Deletion", "Listing", "Search"
        ])
        
        name = f"{action_verb} {module} {operation}"
        description = f"Testa funcionalidade de {operation.lower()} do módulo {module}"
        
        return TestCase(
            id=test_id,
            name=name,
            description=description,
            actions=actions,
            priority=priority,
            module=module,
            tags={module.lower(), operation.lower()},
            dependencies=dependencies,
            average_execution_time=avg_time,
            success_rate=success_rate,
            last_executed=last_executed,
            times_executed=times_executed
        )
    
    def generate_test_suite(
        self,
        num_tests: int = 20,
        modules: List[str] = None
    ) -> TestSuite:
        """
        Gera uma suíte de testes sintética
        
        Args:
            num_tests: Número de testes a gerar
            modules: Lista de módulos (usa padrão se None)
            
        Returns:
            Suíte de testes gerada
        """
        if modules is None:
            modules = self.modules
        
        test_cases = []
        
        # Distribuir testes entre módulos
        for i in range(num_tests):
            module = random.choice(modules)
            test_case = self.generate_test_case(
                module=module,
                include_dependencies=(i > 3)  # Primeiros testes sem dependências
            )
            test_cases.append(test_case)
        
        suite = TestSuite(
            id="TS_SYNTHETIC",
            name="Synthetic Test Suite",
            description=f"Suíte sintética com {num_tests} casos de teste",
            test_cases=test_cases
        )
        
        return suite
    
    def generate_multiple_suites(
        self,
        num_suites: int = 5,
        tests_per_suite: int = 15
    ) -> List[TestSuite]:
        """
        Gera múltiplas suítes de teste
        
        Args:
            num_suites: Número de suítes
            tests_per_suite: Testes por suíte
            
        Returns:
            Lista de suítes geradas
        """
        suites = []
        for i in range(num_suites):
            # Reset dos contadores para cada suíte
            self.test_counter = 0
            self.action_counter = 0
            
            suite = self.generate_test_suite(num_tests=tests_per_suite)
            suite.id = f"TS{i+1:03d}"
            suite.name = f"Test Suite {i+1}"
            suites.append(suite)
        
        return suites
