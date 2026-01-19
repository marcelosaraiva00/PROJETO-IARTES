"""
Extração de features dos casos de teste para o modelo de ML
"""
import numpy as np
from typing import List, Dict, Tuple, Set
from collections import defaultdict
from src.models.test_case import TestCase, Action, ActionImpact, ActionType


class FeatureExtractor:
    """Extrai features relevantes dos casos de teste para o modelo de ML"""
    
    def __init__(self):
        self.feature_names = []
        self._build_feature_names()
    
    def _build_feature_names(self):
        """Constrói lista de nomes de features"""
        self.feature_names = [
            # Features básicas do teste
            'priority',
            'num_actions',
            'estimated_time',
            'success_rate',
            'times_executed',
            
            # Features de ações
            'num_destructive_actions',
            'num_non_destructive_actions',
            'num_creation_actions',
            'num_verification_actions',
            'num_modification_actions',
            'num_deletion_actions',
            'num_navigation_actions',
            
            # Features de estado
            'num_preconditions',
            'num_postconditions',
            'state_change_ratio',
            
            # Features de dependências
            'num_dependencies',
            'has_destructive_actions',
            
            # Features temporais
            'avg_action_time',
            'time_since_last_execution',
        ]
    
    def extract_features(self, test_case: TestCase) -> np.ndarray:
        """
        Extrai features de um caso de teste individual
        
        Args:
            test_case: Caso de teste para extrair features
            
        Returns:
            Array numpy com as features
        """
        features = []
        
        # Features básicas
        features.append(test_case.priority)
        features.append(len(test_case.actions))
        features.append(test_case.get_total_estimated_time())
        features.append(test_case.success_rate)
        features.append(test_case.times_executed)
        
        # Contar tipos de ações por impacto
        destructive_count = sum(
            1 for a in test_case.actions 
            if a.impact in [ActionImpact.DESTRUCTIVE, ActionImpact.PARTIALLY_DESTRUCTIVE]
        )
        non_destructive_count = sum(
            1 for a in test_case.actions 
            if a.impact == ActionImpact.NON_DESTRUCTIVE
        )
        features.append(destructive_count)
        features.append(non_destructive_count)
        
        # Contar tipos de ações
        action_type_counts = defaultdict(int)
        for action in test_case.actions:
            action_type_counts[action.action_type] += 1
        
        features.append(action_type_counts[ActionType.CREATION])
        features.append(action_type_counts[ActionType.VERIFICATION])
        features.append(action_type_counts[ActionType.MODIFICATION])
        features.append(action_type_counts[ActionType.DELETION])
        features.append(action_type_counts[ActionType.NAVIGATION])
        
        # Features de estado
        preconditions = test_case.get_preconditions()
        postconditions = test_case.get_postconditions()
        features.append(len(preconditions))
        features.append(len(postconditions))
        
        # Razão de mudança de estado
        if len(preconditions) > 0:
            state_change_ratio = len(postconditions) / len(preconditions)
        else:
            state_change_ratio = len(postconditions)
        features.append(state_change_ratio)
        
        # Features de dependências
        features.append(len(test_case.dependencies))
        features.append(1 if test_case.has_destructive_actions() else 0)
        
        # Features temporais
        avg_action_time = (
            test_case.get_total_estimated_time() / len(test_case.actions)
            if test_case.actions else 0
        )
        features.append(avg_action_time)
        
        # Tempo desde última execução (em dias)
        if test_case.last_executed:
            from datetime import datetime
            days_since = (datetime.now() - test_case.last_executed).days
        else:
            days_since = 999  # Valor alto para testes nunca executados
        features.append(days_since)
        
        return np.array(features, dtype=np.float32)
    
    def extract_pairwise_features(
        self, 
        test1: TestCase, 
        test2: TestCase
    ) -> np.ndarray:
        """
        Extrai features de relação entre dois testes (para ordenação)
        
        Args:
            test1: Primeiro caso de teste
            test2: Segundo caso de teste
            
        Returns:
            Array com features de relação entre os testes
        """
        features = []
        
        # Compatibilidade de estado (pós-condições de test1 atendem pré-condições de test2)
        post1 = test1.get_postconditions()
        pre2 = test2.get_preconditions()
        
        if pre2:
            state_compatibility = len(post1.intersection(pre2)) / len(pre2)
        else:
            state_compatibility = 1.0
        features.append(state_compatibility)
        
        # Diferença de prioridade
        features.append(abs(test1.priority - test2.priority))
        
        # Se são do mesmo módulo
        features.append(1 if test1.module == test2.module else 0)
        
        # Sobreposição de tags
        if test1.tags or test2.tags:
            tag_overlap = len(test1.tags.intersection(test2.tags)) / max(
                len(test1.tags.union(test2.tags)), 1
            )
        else:
            tag_overlap = 0
        features.append(tag_overlap)
        
        # Impacto combinado (test1 destrutivo antes de test2 não-destrutivo é ruim)
        test1_destructive = test1.has_destructive_actions()
        test2_non_destructive = not test2.has_destructive_actions()
        bad_order_penalty = 1 if (test1_destructive and test2_non_destructive) else 0
        features.append(bad_order_penalty)
        
        # Diferença de tempo de execução
        time_diff = abs(test1.get_total_estimated_time() - test2.get_total_estimated_time())
        features.append(time_diff)
        
        # Se test2 depende de test1
        features.append(1 if test1.id in test2.dependencies else 0)
        
        return np.array(features, dtype=np.float32)
    
    def extract_suite_features(self, test_cases: List[TestCase]) -> Dict[str, np.ndarray]:
        """
        Extrai features de toda a suíte de testes
        
        Args:
            test_cases: Lista de casos de teste
            
        Returns:
            Dicionário com features individuais e features de pares
        """
        # Features individuais
        individual_features = np.array([
            self.extract_features(tc) for tc in test_cases
        ])
        
        # Matriz de features pareadas
        n_tests = len(test_cases)
        pairwise_features = np.zeros((n_tests, n_tests, 7))  # 7 features pareadas
        
        for i in range(n_tests):
            for j in range(n_tests):
                if i != j:
                    pairwise_features[i, j] = self.extract_pairwise_features(
                        test_cases[i], test_cases[j]
                    )
        
        return {
            'individual': individual_features,
            'pairwise': pairwise_features,
            'test_ids': [tc.id for tc in test_cases]
        }
    
    def get_feature_importance_names(self) -> List[str]:
        """Retorna nomes das features para interpretabilidade"""
        return self.feature_names
