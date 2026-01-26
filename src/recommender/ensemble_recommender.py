"""
Sistema de Ensemble de Múltiplos Modelos
Combina diferentes algoritmos para melhorar recomendações
"""
import numpy as np
from typing import List, Dict, Optional
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
import pickle

from src.models.test_case import TestCase, RecommendationResult, ExecutionFeedback
from src.features.feature_extractor import FeatureExtractor
from src.recommender.ml_recommender import MLTestRecommender


class EnsembleRecommender:
    """
    Recomendador que combina múltiplos modelos usando ensemble
    """
    
    def __init__(self, use_deep_learning: bool = False):
        """
        Inicializa o ensemble de modelos
        
        Args:
            use_deep_learning: Se True, inclui modelo de Deep Learning
        """
        self.feature_extractor = FeatureExtractor()
        self.scaler = StandardScaler()
        self.use_deep_learning = use_deep_learning
        
        # Modelos individuais
        self.random_forest = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        self.gradient_boosting = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        
        # Deep Learning (MLP) se habilitado
        if use_deep_learning:
            self.neural_network = MLPRegressor(
                hidden_layer_sizes=(100, 50),
                activation='relu',
                solver='adam',
                alpha=0.001,
                learning_rate='adaptive',
                max_iter=500,
                random_state=42
            )
        else:
            self.neural_network = None
        
        # Ensemble usando Voting Regressor
        estimators = [
            ('rf', self.random_forest),
            ('gb', self.gradient_boosting)
        ]
        
        if self.neural_network:
            estimators.append(('nn', self.neural_network))
        
        self.ensemble = VotingRegressor(
            estimators=estimators,
            weights=[0.4, 0.4, 0.2] if self.neural_network else [0.5, 0.5]
        )
        
        self.is_trained = False
        self.feedback_history: List[ExecutionFeedback] = []
        self.training_data = {'X': [], 'y': []}
        self.model_weights = {
            'random_forest': 0.4,
            'gradient_boosting': 0.4,
            'neural_network': 0.2 if use_deep_learning else 0.0
        }
    
    def _calculate_order_score(
        self,
        test_order: List[TestCase],
        feedback: Optional[ExecutionFeedback] = None
    ) -> float:
        """Calcula score de qualidade de uma ordenação (mesmo método do MLRecommender)"""
        if not test_order:
            return 0.0
        
        score = 100.0
        
        # Penalizar quebras de dependências
        for i, test in enumerate(test_order):
            for dep_id in test.dependencies:
                executed_ids = {t.id for t in test_order[:i]}
                if dep_id not in executed_ids:
                    score -= 20
        
        # Bonificar transições compatíveis
        for i in range(len(test_order) - 1):
            current = test_order[i]
            next_test = test_order[i + 1]
            
            post_current = current.get_postconditions()
            pre_next = next_test.get_preconditions()
            
            if pre_next:
                compatibility = len(post_current.intersection(pre_next)) / len(pre_next)
                score += compatibility * 10
        
        # Incorporar feedback
        if feedback:
            if feedback.success:
                score += 10
            else:
                score -= 10
            
            if feedback.required_reset:
                score -= 15
            
            if feedback.tester_rating:
                score += (feedback.tester_rating - 3) * 5
        
        return max(score, 0.0)
    
    def _generate_training_sample(
        self,
        test_order: List[TestCase],
        score: float
    ) -> tuple:
        """Gera amostra de treinamento"""
        features = []
        
        total_time = sum(tc.get_total_estimated_time() for tc in test_order)
        avg_priority = np.mean([tc.priority for tc in test_order])
        num_destructive = sum(1 for tc in test_order if tc.has_destructive_actions())
        
        features.extend([
            len(test_order),
            total_time,
            avg_priority,
            num_destructive,
        ])
        
        compatible_transitions = 0
        same_module_transitions = 0
        
        for i in range(len(test_order) - 1):
            current = test_order[i]
            next_test = test_order[i + 1]
            
            post = current.get_postconditions()
            pre = next_test.get_preconditions()
            if pre and post.intersection(pre):
                compatible_transitions += 1
            
            if current.module == next_test.module:
                same_module_transitions += 1
        
        features.extend([
            compatible_transitions,
            same_module_transitions,
        ])
        
        return np.array(features, dtype=np.float32), score
    
    def add_feedback(self, feedback: ExecutionFeedback, test_order: List[TestCase]):
        """Adiciona feedback para aprendizado"""
        self.feedback_history.append(feedback)
        
        score = self._calculate_order_score(test_order, feedback)
        X, y = self._generate_training_sample(test_order, score)
        
        self.training_data['X'].append(X)
        self.training_data['y'].append(y)
        
        # Re-treinar periodicamente
        if len(self.training_data['y']) % 10 == 0 and len(self.training_data['y']) > 0:
            self.train()
    
    def train(self):
        """Treina todos os modelos do ensemble"""
        if len(self.training_data['y']) < 5:
            return
        
        X = np.array(self.training_data['X'])
        y = np.array(self.training_data['y'])
        
        X_scaled = self.scaler.fit_transform(X)
        
        # Treinar cada modelo individualmente primeiro
        self.random_forest.fit(X_scaled, y)
        self.gradient_boosting.fit(X_scaled, y)
        
        if self.neural_network:
            self.neural_network.fit(X_scaled, y)
        
        # Treinar ensemble
        self.ensemble.fit(X_scaled, y)
        self.is_trained = True
        
        # Calcular pesos dinâmicos baseados em performance
        self._update_model_weights(X_scaled, y)
    
    def _update_model_weights(self, X_scaled: np.ndarray, y: np.ndarray):
        """Atualiza pesos dos modelos baseado em performance"""
        if len(y) < 10:
            return
        
        # Usar validação cruzada simples
        split = len(y) // 2
        X_train, X_val = X_scaled[:split], X_scaled[split:]
        y_train, y_val = y[:split], y[split:]
        
        # Treinar modelos temporários
        rf_temp = RandomForestRegressor(n_estimators=50, random_state=42)
        gb_temp = GradientBoostingRegressor(n_estimators=50, random_state=42)
        
        rf_temp.fit(X_train, y_train)
        gb_temp.fit(X_train, y_train)
        
        # Avaliar performance
        rf_score = -np.mean((rf_temp.predict(X_val) - y_val) ** 2)
        gb_score = -np.mean((gb_temp.predict(X_val) - y_val) ** 2)
        
        # Normalizar pesos
        total = abs(rf_score) + abs(gb_score)
        if total > 0:
            self.model_weights['random_forest'] = abs(rf_score) / total
            self.model_weights['gradient_boosting'] = abs(gb_score) / total
        
        if self.neural_network:
            nn_temp = MLPRegressor(hidden_layer_sizes=(50, 25), random_state=42, max_iter=200)
            nn_temp.fit(X_train, y_train)
            nn_score = -np.mean((nn_temp.predict(X_val) - y_val) ** 2)
            
            total = abs(rf_score) + abs(gb_score) + abs(nn_score)
            if total > 0:
                self.model_weights['random_forest'] = abs(rf_score) / total
                self.model_weights['gradient_boosting'] = abs(gb_score) / total
                self.model_weights['neural_network'] = abs(nn_score) / total
    
    def recommend_order(
        self,
        test_cases: List[TestCase],
        use_heuristics: bool = True
    ) -> RecommendationResult:
        """Recomenda ordenação usando ensemble"""
        if not test_cases:
            return RecommendationResult(
                recommended_order=[],
                estimated_total_time=0.0,
                estimated_resets=0,
                confidence_score=0.0
            )
        
        if not self.is_trained or use_heuristics:
            # Usar heurísticas básicas
            ordered = self._heuristic_ordering(test_cases)
            confidence = 0.6 if not self.is_trained else 0.8
        else:
            # Usar ensemble
            ordered = self._ensemble_ordering(test_cases)
            confidence = 0.95  # Ensemble tem maior confiança
        
        total_time = sum(tc.get_total_estimated_time() for tc in ordered)
        estimated_resets = self._estimate_resets(ordered)
        
        return RecommendationResult(
            recommended_order=[tc.id for tc in ordered],
            estimated_total_time=total_time,
            estimated_resets=estimated_resets,
            confidence_score=confidence,
            reasoning={
                'method': 'ensemble',
                'models_used': list(self.model_weights.keys()),
                'model_weights': self.model_weights,
                'training_samples': len(self.training_data['y'])
            }
        )
    
    def _heuristic_ordering(self, test_cases: List[TestCase]) -> List[TestCase]:
        """Ordenação heurística (mesmo do MLRecommender)"""
        remaining = set(test_cases)
        ordered = []
        
        while remaining:
            executable = []
            for tc in remaining:
                deps_satisfied = all(
                    dep_id in {t.id for t in ordered}
                    for dep_id in tc.dependencies
                )
                if deps_satisfied:
                    executable.append(tc)
            
            if not executable:
                executable = list(remaining)
            
            executable.sort(key=lambda tc: (
                -tc.priority,
                tc.module,
                tc.has_destructive_actions(),
                tc.get_total_estimated_time()
            ))
            
            next_test = executable[0]
            ordered.append(next_test)
            remaining.remove(next_test)
        
        return ordered
    
    def _ensemble_ordering(self, test_cases: List[TestCase]) -> List[TestCase]:
        """Ordenação usando ensemble de modelos"""
        # Usar heurística como base
        base_order = self._heuristic_ordering(test_cases)
        
        # Avaliar com ensemble e melhorar
        best_order = base_order.copy()
        best_score = self._predict_order_score(best_order)
        
        # Tentar melhorias locais
        for i in range(len(best_order) - 1):
            temp_order = best_order.copy()
            temp_order[i], temp_order[i + 1] = temp_order[i + 1], temp_order[i]
            
            score = self._predict_order_score(temp_order)
            if score > best_score:
                best_score = score
                best_order = temp_order
        
        return best_order
    
    def _predict_order_score(self, test_order: List[TestCase]) -> float:
        """Prediz score usando ensemble"""
        if not self.is_trained:
            return self._calculate_order_score(test_order)
        
        X, _ = self._generate_training_sample(test_order, 0)
        X_scaled = self.scaler.transform(X.reshape(1, -1))
        return self.ensemble.predict(X_scaled)[0]
    
    def _estimate_resets(self, test_order: List[TestCase]) -> int:
        """Estima número de reinicializações"""
        resets = 0
        current_state = set()
        
        for test in test_order:
            required = test.get_preconditions()
            
            if required and not required.issubset(current_state):
                resets += 1
                current_state = set()
            
            current_state.update(test.get_postconditions())
        
        return resets
    
    def get_model_performance(self) -> Dict:
        """Retorna performance de cada modelo no ensemble"""
        if not self.is_trained:
            return {}
        
        return {
            'random_forest': {
                'weight': self.model_weights['random_forest'],
                'feature_importance': self.random_forest.feature_importances_.tolist() if hasattr(self.random_forest, 'feature_importances_') else []
            },
            'gradient_boosting': {
                'weight': self.model_weights['gradient_boosting'],
                'feature_importance': self.gradient_boosting.feature_importances_.tolist() if hasattr(self.gradient_boosting, 'feature_importances_') else []
            },
            'neural_network': {
                'weight': self.model_weights.get('neural_network', 0.0),
                'enabled': self.neural_network is not None
            } if self.neural_network else None
        }
    
    def save_model(self, filepath: str):
        """Salva o ensemble"""
        model_data = {
            'random_forest': self.random_forest,
            'gradient_boosting': self.gradient_boosting,
            'neural_network': self.neural_network,
            'ensemble': self.ensemble,
            'scaler': self.scaler,
            'is_trained': self.is_trained,
            'training_data': self.training_data,
            'model_weights': self.model_weights,
            'use_deep_learning': self.use_deep_learning
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, filepath: str):
        """Carrega o ensemble"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.random_forest = model_data['random_forest']
        self.gradient_boosting = model_data['gradient_boosting']
        self.neural_network = model_data.get('neural_network')
        self.ensemble = model_data['ensemble']
        self.scaler = model_data['scaler']
        self.is_trained = model_data['is_trained']
        self.training_data = model_data.get('training_data', {'X': [], 'y': []})
        self.model_weights = model_data.get('model_weights', self.model_weights)
        self.use_deep_learning = model_data.get('use_deep_learning', False)
