"""
Sistema de Explicabilidade da IA
Explica por que testes foram recomendados e quais fatores influenciaram
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance

from src.models.test_case import TestCase, RecommendationResult
from src.features.feature_extractor import FeatureExtractor


class RecommendationExplainer:
    """
    Explica as recomendações da IA de forma transparente
    """
    
    def __init__(self, model: RandomForestRegressor, feature_extractor: FeatureExtractor):
        """
        Inicializa o explicador
        
        Args:
            model: Modelo ML treinado
            feature_extractor: Extrator de features usado
        """
        self.model = model
        self.feature_extractor = feature_extractor
        self.feature_names = [
            'num_tests',
            'total_time',
            'avg_priority',
            'num_destructive',
            'compatible_transitions',
            'same_module_transitions'
        ]
    
    def explain_recommendation(
        self,
        test_cases: List[TestCase],
        recommended_order: List[str],
        alternative_orders: Optional[List[List[str]]] = None
    ) -> Dict:
        """
        Explica por que uma ordem específica foi recomendada
        
        Args:
            test_cases: Lista completa de casos de teste
            recommended_order: Ordem recomendada
            alternative_orders: Ordens alternativas para comparação
        
        Returns:
            Dicionário com explicações detalhadas
        """
        explanation = {
            'recommended_order': recommended_order,
            'factors': [],
            'feature_importance': self._get_feature_importance(),
            'test_scores': {},
            'comparison_with_alternatives': None,
            'reasoning': []
        }
        
        # Calcular scores para cada teste na ordem recomendada
        test_dict = {tc.id: tc for tc in test_cases}
        ordered_tests = [test_dict[tid] for tid in recommended_order if tid in test_dict]
        
        # Analisar fatores que influenciaram
        factors = self._analyze_factors(ordered_tests)
        explanation['factors'] = factors
        
        # Calcular scores individuais
        for i, test_id in enumerate(recommended_order):
            if test_id in test_dict:
                test = test_dict[test_id]
                score = self._calculate_test_score(test, i, ordered_tests)
                explanation['test_scores'][test_id] = score
        
        # Comparar com alternativas se fornecidas
        if alternative_orders:
            explanation['comparison_with_alternatives'] = self._compare_orders(
                ordered_tests,
                alternative_orders,
                test_dict
            )
        
        # Gerar explicação textual
        explanation['reasoning'] = self._generate_textual_explanation(factors, ordered_tests)
        
        return explanation
    
    def _get_feature_importance(self) -> Dict[str, float]:
        """
        Obtém importância de cada feature do modelo
        
        Returns:
            Dicionário com importância de cada feature
        """
        if not hasattr(self.model, 'feature_importances_'):
            return {}
        
        importances = self.model.feature_importances_
        total = sum(importances)
        
        return {
            name: (imp / total * 100) if total > 0 else 0
            for name, imp in zip(self.feature_names, importances)
        }
    
    def _analyze_factors(self, ordered_tests: List[TestCase]) -> List[Dict]:
        """
        Analisa fatores que influenciaram a ordenação
        
        Args:
            ordered_tests: Testes na ordem recomendada
        
        Returns:
            Lista de fatores identificados
        """
        factors = []
        
        if not ordered_tests:
            return factors
        
        # Fator 1: Agrupamento por módulo
        module_groups = self._count_module_groups(ordered_tests)
        if module_groups > 0:
            factors.append({
                'name': 'Agrupamento por Módulo',
                'description': f'Testes agrupados em {module_groups} blocos por módulo',
                'impact': 'positive',
                'value': module_groups,
                'reason': 'Reduz mudança de contexto e melhora eficiência'
            })
        
        # Fator 2: Compatibilidade de estados
        compatible = self._count_compatible_transitions(ordered_tests)
        total_transitions = len(ordered_tests) - 1
        if total_transitions > 0:
            compatibility_rate = (compatible / total_transitions) * 100
            factors.append({
                'name': 'Compatibilidade de Estados',
                'description': f'{compatible}/{total_transitions} transições são compatíveis',
                'impact': 'positive',
                'value': compatibility_rate,
                'reason': 'Reduz necessidade de resets e preparação'
            })
        
        # Fator 3: Priorização
        high_priority_first = sum(1 for tc in ordered_tests[:3] if tc.priority >= 4)
        if high_priority_first > 0:
            factors.append({
                'name': 'Priorização',
                'description': f'{high_priority_first} testes de alta prioridade executados primeiro',
                'impact': 'positive',
                'value': high_priority_first,
                'reason': 'Garante que testes críticos sejam executados cedo'
            })
        
        # Fator 4: Minimização de ações destrutivas
        destructive_tests = [tc for tc in ordered_tests if tc.has_destructive_actions()]
        if len(destructive_tests) > 0:
            # Verificar se destrutivos estão agrupados no final
            last_destructive_idx = max(
                (i for i, tc in enumerate(ordered_tests) if tc.has_destructive_actions()),
                default=-1
            )
            if last_destructive_idx >= len(ordered_tests) * 0.7:
                factors.append({
                    'name': 'Minimização de Impacto Destrutivo',
                    'description': 'Testes destrutivos agrupados no final',
                    'impact': 'positive',
                    'value': len(destructive_tests),
                    'reason': 'Permite executar mais testes antes de resetar'
                })
        
        # Fator 5: Tempo total estimado
        total_time = sum(tc.get_total_estimated_time() for tc in ordered_tests)
        factors.append({
            'name': 'Tempo Total Estimado',
            'description': f'{total_time:.0f} segundos estimados',
            'impact': 'neutral',
            'value': total_time,
            'reason': 'Tempo total de execução da suíte'
        })
        
        return factors
    
    def _count_module_groups(self, tests: List[TestCase]) -> int:
        """Conta quantos grupos de módulos existem"""
        if len(tests) <= 1:
            return 0
        
        groups = 1
        for i in range(1, len(tests)):
            if tests[i].module != tests[i-1].module:
                groups += 1
        
        return groups
    
    def _count_compatible_transitions(self, tests: List[TestCase]) -> int:
        """Conta transições compatíveis entre testes"""
        compatible = 0
        
        for i in range(len(tests) - 1):
            current = tests[i]
            next_test = tests[i + 1]
            
            post_current = current.get_postconditions()
            pre_next = next_test.get_preconditions()
            
            if pre_next and post_current.intersection(pre_next):
                compatible += 1
        
        return compatible
    
    def _calculate_test_score(
        self,
        test: TestCase,
        position: int,
        all_tests: List[TestCase]
    ) -> Dict:
        """
        Calcula score explicativo para um teste específico
        
        Args:
            test: Caso de teste
            position: Posição na ordem
            all_tests: Todos os testes na ordem
        
        Returns:
            Dicionário com score e razões
        """
        score = 100.0
        reasons = []
        
        # Bonificar testes de alta prioridade no início
        if position < 3 and test.priority >= 4:
            score += 20
            reasons.append('Alta prioridade no início')
        
        # Bonificar agrupamento por módulo
        if position > 0 and all_tests[position - 1].module == test.module:
            score += 15
            reasons.append('Agrupado com mesmo módulo')
        
        # Bonificar compatibilidade de estado
        if position > 0:
            prev_test = all_tests[position - 1]
            post_prev = prev_test.get_postconditions()
            pre_current = test.get_preconditions()
            
            if pre_current and post_prev.intersection(pre_current):
                score += 25
                reasons.append('Estado compatível com teste anterior')
        
        # Penalizar testes destrutivos no início
        if position < len(all_tests) * 0.3 and test.has_destructive_actions():
            score -= 10
            reasons.append('Teste destrutivo muito cedo')
        
        return {
            'score': max(score, 0),
            'reasons': reasons,
            'position': position + 1
        }
    
    def _compare_orders(
        self,
        recommended: List[TestCase],
        alternatives: List[List[str]],
        test_dict: Dict[str, TestCase]
    ) -> Dict:
        """
        Compara ordem recomendada com alternativas
        
        Args:
            recommended: Testes na ordem recomendada
            alternatives: Lista de ordens alternativas
            test_dict: Dicionário de testes
        
        Returns:
            Comparação detalhada
        """
        rec_time = sum(tc.get_total_estimated_time() for tc in recommended)
        rec_resets = self._estimate_resets(recommended)
        
        comparisons = []
        for alt_order in alternatives:
            alt_tests = [test_dict[tid] for tid in alt_order if tid in test_dict]
            alt_time = sum(tc.get_total_estimated_time() for tc in alt_tests)
            alt_resets = self._estimate_resets(alt_tests)
            
            comparisons.append({
                'order': alt_order,
                'time': alt_time,
                'resets': alt_resets,
                'time_diff': alt_time - rec_time,
                'resets_diff': alt_resets - rec_resets,
                'better': alt_time < rec_time and alt_resets <= rec_resets
            })
        
        return {
            'recommended': {
                'time': rec_time,
                'resets': rec_resets
            },
            'alternatives': comparisons
        }
    
    def _estimate_resets(self, tests: List[TestCase]) -> int:
        """Estima número de resets necessários"""
        resets = 0
        current_state = set()
        
        for test in tests:
            required = test.get_preconditions()
            
            if required and not required.issubset(current_state):
                resets += 1
                current_state = set()
            
            current_state.update(test.get_postconditions())
        
        return resets
    
    def _generate_textual_explanation(
        self,
        factors: List[Dict],
        ordered_tests: List[TestCase]
    ) -> List[str]:
        """
        Gera explicação textual da recomendação
        
        Args:
            factors: Fatores identificados
            ordered_tests: Testes ordenados
        
        Returns:
            Lista de explicações em texto
        """
        explanations = []
        
        if not ordered_tests:
            return ["Nenhum teste para ordenar"]
        
        # Explicação geral
        explanations.append(
            f"A ordem foi otimizada para {len(ordered_tests)} testes, "
            f"considerando múltiplos fatores de eficiência."
        )
        
        # Explicar fatores principais
        positive_factors = [f for f in factors if f.get('impact') == 'positive']
        if positive_factors:
            explanations.append("\nFatores que melhoram a eficiência:")
            for factor in positive_factors[:3]:  # Top 3
                explanations.append(
                    f"  • {factor['name']}: {factor['description']} "
                    f"({factor['reason']})"
                )
        
        # Explicar estrutura da ordem
        modules = [tc.module for tc in ordered_tests]
        unique_modules = len(set(modules))
        explanations.append(
            f"\nA ordem agrupa testes de {unique_modules} módulos diferentes, "
            f"minimizando mudanças de contexto."
        )
        
        # Explicar tempo estimado
        total_time = sum(tc.get_total_estimated_time() for tc in ordered_tests)
        explanations.append(
            f"Tempo total estimado: {total_time:.0f} segundos "
            f"({total_time/60:.1f} minutos)."
        )
        
        return explanations
