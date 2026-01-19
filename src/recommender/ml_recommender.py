"""
Sistema de recomendação baseado em Machine Learning
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import pickle
from datetime import datetime

from src.models.test_case import TestCase, RecommendationResult, ExecutionFeedback
from src.features.feature_extractor import FeatureExtractor


class MLTestRecommender:
    """
    Recomendador de ordenação de testes usando Machine Learning
    Utiliza aprendizado por reforço simplificado com feedback humano
    """
    
    def __init__(self, model_type: str = 'random_forest'):
        """
        Inicializa o recomendador
        
        Args:
            model_type: Tipo de modelo ('random_forest' ou 'gradient_boosting')
        """
        self.feature_extractor = FeatureExtractor()
        self.scaler = StandardScaler()
        
        # Modelo para prever "qualidade" de uma ordenação
        if model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
        else:
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        
        self.is_trained = False
        self.feedback_history: List[ExecutionFeedback] = []
        self.training_data = {'X': [], 'y': []}
    
    def _calculate_order_score(
        self, 
        test_order: List[TestCase],
        feedback: Optional[ExecutionFeedback] = None
    ) -> float:
        """
        Calcula score de qualidade de uma ordenação
        
        Score baseado em:
        - Minimização de reinicializações
        - Tempo total de execução
        - Compatibilidade de estados
        - Feedback do testador
        
        Args:
            test_order: Lista ordenada de casos de teste
            feedback: Feedback opcional de execução
            
        Returns:
            Score de qualidade (maior é melhor)
        """
        if not test_order:
            return 0.0
        
        score = 100.0  # Score inicial
        
        # Penalizar quebras de dependências
        for i, test in enumerate(test_order):
            for dep_id in test.dependencies:
                # Verificar se dependência foi executada antes
                executed_ids = {t.id for t in test_order[:i]}
                if dep_id not in executed_ids:
                    score -= 20  # Grande penalidade
        
        # Bonificar transições de estado compatíveis
        for i in range(len(test_order) - 1):
            current = test_order[i]
            next_test = test_order[i + 1]
            
            post_current = current.get_postconditions()
            pre_next = next_test.get_preconditions()
            
            if pre_next:
                compatibility = len(post_current.intersection(pre_next)) / len(pre_next)
                score += compatibility * 10
        
        # Penalizar ações destrutivas seguidas de não-destrutivas do mesmo módulo
        for i in range(len(test_order) - 1):
            current = test_order[i]
            next_test = test_order[i + 1]
            
            if (current.module == next_test.module and 
                current.has_destructive_actions() and 
                not next_test.has_destructive_actions()):
                score -= 5
        
        # Bonificar agrupamento por módulo (reduz context switching)
        for i in range(len(test_order) - 1):
            if test_order[i].module == test_order[i + 1].module:
                score += 3
        
        # Incorporar feedback humano se disponível
        if feedback:
            if feedback.success:
                score += 10
            else:
                score -= 10
            
            if feedback.required_reset:
                score -= 15
            
            if feedback.followed_recommendation:
                score += 5
            
            if feedback.tester_rating:
                # Rating de 1-5
                score += (feedback.tester_rating - 3) * 5
        
        return max(score, 0.0)
    
    def _generate_training_sample(
        self,
        test_order: List[TestCase],
        score: float
    ) -> Tuple[np.ndarray, float]:
        """
        Gera amostra de treinamento a partir de uma ordenação
        
        Args:
            test_order: Ordenação de testes
            score: Score da ordenação
            
        Returns:
            Tupla (features, score)
        """
        # Extrair features da ordenação
        features = []
        
        # Features agregadas da ordenação
        total_time = sum(tc.get_total_estimated_time() for tc in test_order)
        avg_priority = np.mean([tc.priority for tc in test_order])
        num_destructive = sum(1 for tc in test_order if tc.has_destructive_actions())
        
        features.extend([
            len(test_order),
            total_time,
            avg_priority,
            num_destructive,
        ])
        
        # Features de transições
        compatible_transitions = 0
        same_module_transitions = 0
        
        for i in range(len(test_order) - 1):
            current = test_order[i]
            next_test = test_order[i + 1]
            
            # Compatibilidade de estado
            post = current.get_postconditions()
            pre = next_test.get_preconditions()
            if pre and post.intersection(pre):
                compatible_transitions += 1
            
            # Mesmo módulo
            if current.module == next_test.module:
                same_module_transitions += 1
        
        features.extend([
            compatible_transitions,
            same_module_transitions,
        ])
        
        return np.array(features, dtype=np.float32), score
    
    def add_feedback(self, feedback: ExecutionFeedback, test_order: List[TestCase]):
        """
        Adiciona feedback de execução para aprendizado
        
        Args:
            feedback: Feedback da execução
            test_order: Ordem em que os testes foram executados
        """
        self.feedback_history.append(feedback)
        
        # Calcular score da ordenação com feedback
        score = self._calculate_order_score(test_order, feedback)
        
        # Gerar amostra de treinamento
        X, y = self._generate_training_sample(test_order, score)
        
        self.training_data['X'].append(X)
        self.training_data['y'].append(y)
        
        # Re-treinar o modelo periodicamente (a cada 10 feedbacks)
        if len(self.training_data['y']) % 10 == 0 and len(self.training_data['y']) > 0:
            self.train()
    
    def train(self):
        """Treina o modelo com os dados de feedback acumulados"""
        if len(self.training_data['y']) < 5:
            print("Dados insuficientes para treinamento. Mínimo: 5 amostras")
            return
        
        X = np.array(self.training_data['X'])
        y = np.array(self.training_data['y'])
        
        # Normalizar features
        X_scaled = self.scaler.fit_transform(X)
        
        # Treinar modelo
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        print(f"Modelo treinado com {len(y)} amostras")
    
    def recommend_order(
        self, 
        test_cases: List[TestCase],
        use_heuristics: bool = True
    ) -> RecommendationResult:
        """
        Recomenda ordenação de casos de teste
        
        Args:
            test_cases: Lista de casos de teste a ordenar
            use_heuristics: Se True, usa heurísticas quando modelo não treinado
            
        Returns:
            Resultado da recomendação com ordenação sugerida
        """
        if not test_cases:
            return RecommendationResult(
                recommended_order=[],
                estimated_total_time=0.0,
                estimated_resets=0,
                confidence_score=0.0
            )
        
        # Se modelo não está treinado, usar heurísticas
        if not self.is_trained or use_heuristics:
            ordered = self._heuristic_ordering(test_cases)
            confidence = 0.6 if not self.is_trained else 0.8
        else:
            ordered = self._ml_ordering(test_cases)
            confidence = 0.9
        
        # Calcular métricas da ordenação
        total_time = sum(tc.get_total_estimated_time() for tc in ordered)
        estimated_resets = self._estimate_resets(ordered)
        
        return RecommendationResult(
            recommended_order=[tc.id for tc in ordered],
            estimated_total_time=total_time,
            estimated_resets=estimated_resets,
            confidence_score=confidence,
            reasoning={
                'method': 'heuristic' if not self.is_trained else 'ml',
                'num_tests': len(test_cases),
                'training_samples': len(self.training_data['y'])
            }
        )
    
    def _heuristic_ordering(self, test_cases: List[TestCase]) -> List[TestCase]:
        """
        Ordenação baseada em heurísticas (usado quando modelo não está treinado)
        
        Heurísticas aplicadas:
        1. Testes sem dependências primeiro
        2. Agrupar por módulo
        3. Ações não-destrutivas antes de destrutivas no mesmo módulo
        4. Ordenar por prioridade
        """
        # Criar grafo de dependências
        remaining = set(test_cases)
        ordered = []
        
        while remaining:
            # Encontrar testes cujas dependências já foram executadas
            executable = []
            for tc in remaining:
                deps_satisfied = all(
                    dep_id in {t.id for t in ordered}
                    for dep_id in tc.dependencies
                )
                if deps_satisfied:
                    executable.append(tc)
            
            if not executable:
                # Se nenhum executável (ciclo de dependências), pegar qualquer um
                executable = list(remaining)
            
            # Ordenar executáveis por heurísticas
            executable.sort(key=lambda tc: (
                -tc.priority,  # Prioridade alta primeiro
                tc.module,  # Agrupar por módulo
                tc.has_destructive_actions(),  # Não-destrutivos primeiro
                tc.get_total_estimated_time()  # Rápidos primeiro
            ))
            
            # Adicionar o melhor candidato
            next_test = executable[0]
            ordered.append(next_test)
            remaining.remove(next_test)
        
        return ordered
    
    def _ml_ordering(self, test_cases: List[TestCase]) -> List[TestCase]:
        """
        Ordenação baseada em ML (usa busca gulosa guiada pelo modelo)
        """
        # Implementação simplificada: avaliar permutações e escolher a melhor
        # Para escalar, seria necessário usar algoritmos mais sofisticados (beam search, etc)
        
        # Por enquanto, combinar heurística com ajustes do modelo
        base_order = self._heuristic_ordering(test_cases)
        
        # Tentar pequenas melhorias locais (swap de testes adjacentes)
        improved_order = base_order.copy()
        best_score = self._predict_order_score(improved_order)
        
        for i in range(len(improved_order) - 1):
            # Tentar trocar testes adjacentes
            temp_order = improved_order.copy()
            temp_order[i], temp_order[i + 1] = temp_order[i + 1], temp_order[i]
            
            score = self._predict_order_score(temp_order)
            if score > best_score:
                best_score = score
                improved_order = temp_order
        
        return improved_order
    
    def _predict_order_score(self, test_order: List[TestCase]) -> float:
        """Prediz score de uma ordenação usando o modelo treinado"""
        if not self.is_trained:
            return self._calculate_order_score(test_order)
        
        X, _ = self._generate_training_sample(test_order, 0)
        X_scaled = self.scaler.transform(X.reshape(1, -1))
        return self.model.predict(X_scaled)[0]
    
    def _estimate_resets(self, test_order: List[TestCase]) -> int:
        """Estima número de reinicializações necessárias"""
        resets = 0
        current_state = set()
        
        for test in test_order:
            required = test.get_preconditions()
            
            # Se estado atual não satisfaz as pré-condições, precisa reset
            if required and not required.issubset(current_state):
                resets += 1
                current_state = set()
            
            # Atualizar estado com pós-condições
            current_state.update(test.get_postconditions())
        
        return resets
    
    def save_model(self, filepath: str):
        """Salva o modelo treinado"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'is_trained': self.is_trained,
            'training_data': self.training_data,
            'feedback_history': self.feedback_history
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Modelo salvo em: {filepath}")
    
    def load_model(self, filepath: str):
        """Carrega um modelo treinado"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.is_trained = model_data['is_trained']
        self.training_data = model_data['training_data']
        self.feedback_history = model_data['feedback_history']
        
        print(f"Modelo carregado de: {filepath}")
