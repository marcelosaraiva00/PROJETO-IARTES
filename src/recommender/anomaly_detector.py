"""
Sistema de Detecção de Anomalias
Identifica padrões anômalos em execuções de testes
"""
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from src.models.test_case import ExecutionFeedback


class AnomalyDetector:
    """
    Detecta anomalias em execuções de testes
    """
    
    def __init__(self, contamination: float = 0.1):
        """
        Inicializa o detector de anomalias
        
        Args:
            contamination: Proporção esperada de anomalias (0-1)
        """
        self.contamination = contamination
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
    
    def detect_anomalies(
        self,
        feedbacks: List[ExecutionFeedback],
        test_cases: Optional[Dict[str, any]] = None
    ) -> Dict:
        """
        Detecta anomalias em uma lista de feedbacks
        
        Args:
            feedbacks: Lista de feedbacks de execução
            test_cases: Dicionário de casos de teste (opcional)
        
        Returns:
            Dicionário com anomalias detectadas
        """
        if len(feedbacks) < 10:
            return {
                'anomalies': [],
                'patterns': [],
                'alerts': [],
                'summary': {
                    'total': len(feedbacks),
                    'anomalies_count': 0,
                    'anomaly_rate': 0.0
                }
            }
        
        # Extrair features dos feedbacks
        features = self._extract_features(feedbacks, test_cases)
        
        # Treinar modelo se necessário
        if not self.is_fitted or len(feedbacks) > 50:
            self._fit_model(features)
        
        # Detectar anomalias
        predictions = self.isolation_forest.predict(features)
        anomaly_scores = self.isolation_forest.score_samples(features)
        
        # Identificar anomalias
        anomalies = []
        for i, (feedback, is_anomaly, score) in enumerate(zip(feedbacks, predictions, anomaly_scores)):
            if is_anomaly == -1:  # -1 indica anomalia
                anomalies.append({
                    'feedback': feedback,
                    'index': i,
                    'anomaly_score': float(score),
                    'reasons': self._explain_anomaly(feedback, features[i], test_cases)
                })
        
        # Detectar padrões
        patterns = self._detect_patterns(feedbacks, anomalies)
        
        # Gerar alertas
        alerts = self._generate_alerts(feedbacks, anomalies, patterns)
        
        return {
            'anomalies': anomalies,
            'patterns': patterns,
            'alerts': alerts,
            'summary': {
                'total': len(feedbacks),
                'anomalies_count': len(anomalies),
                'anomaly_rate': len(anomalies) / len(feedbacks) * 100
            }
        }
    
    def _extract_features(
        self,
        feedbacks: List[ExecutionFeedback],
        test_cases: Optional[Dict] = None
    ) -> np.ndarray:
        """
        Extrai features dos feedbacks para detecção de anomalias
        
        Args:
            feedbacks: Lista de feedbacks
            test_cases: Dicionário de casos de teste
        
        Returns:
            Array numpy com features
        """
        features = []
        
        for feedback in feedbacks:
            feature_vector = [
                feedback.actual_execution_time,
                feedback.tester_rating if feedback.tester_rating else 3.0,
                1.0 if feedback.success else 0.0,
                1.0 if feedback.required_reset else 0.0,
                1.0 if feedback.followed_recommendation else 0.0,
            ]
            
            # Adicionar features do teste se disponível
            if test_cases and feedback.test_case_id in test_cases:
                test = test_cases[feedback.test_case_id]
                feature_vector.extend([
                    test.priority,
                    test.get_total_estimated_time(),
                    1.0 if test.has_destructive_actions() else 0.0,
                ])
            else:
                feature_vector.extend([3.0, 20.0, 0.0])  # Valores padrão
            
            features.append(feature_vector)
        
        return np.array(features)
    
    def _fit_model(self, features: np.ndarray):
        """Treina o modelo de detecção de anomalias"""
        features_scaled = self.scaler.fit_transform(features)
        self.isolation_forest.fit(features_scaled)
        self.is_fitted = True
    
    def _explain_anomaly(
        self,
        feedback: ExecutionFeedback,
        features: np.ndarray,
        test_cases: Optional[Dict] = None
    ) -> List[str]:
        """
        Explica por que um feedback é considerado anômalo
        
        Args:
            feedback: Feedback anômalo
            features: Features do feedback
            test_cases: Dicionário de casos de teste
        
        Returns:
            Lista de razões
        """
        reasons = []
        
        # Verificar tempo de execução
        if test_cases and feedback.test_case_id in test_cases:
            test = test_cases[feedback.test_case_id]
            estimated_time = test.get_total_estimated_time()
            
            if feedback.actual_execution_time > estimated_time * 2:
                reasons.append(
                    f"Tempo de execução muito alto: {feedback.actual_execution_time:.1f}s "
                    f"(esperado: ~{estimated_time:.1f}s)"
                )
            elif feedback.actual_execution_time < estimated_time * 0.3:
                reasons.append(
                    f"Tempo de execução muito baixo: {feedback.actual_execution_time:.1f}s "
                    f"(esperado: ~{estimated_time:.1f}s)"
                )
        
        # Verificar rating
        if feedback.tester_rating:
            if feedback.tester_rating <= 2:
                reasons.append(f"Avaliação muito baixa: {feedback.tester_rating}/5")
            elif feedback.tester_rating == 5 and not feedback.success:
                reasons.append("Avaliação alta mas teste falhou (inconsistente)")
        
        # Verificar sucesso
        if not feedback.success:
            reasons.append("Teste falhou")
        
        # Verificar reset
        if feedback.required_reset:
            reasons.append("Reinicialização necessária (pode indicar problema)")
        
        return reasons if reasons else ["Padrão incomum detectado"]
    
    def _detect_patterns(
        self,
        feedbacks: List[ExecutionFeedback],
        anomalies: List[Dict]
    ) -> List[Dict]:
        """
        Detecta padrões anômalos recorrentes
        
        Args:
            feedbacks: Todos os feedbacks
            anomalies: Anomalias detectadas
        
        Returns:
            Lista de padrões identificados
        """
        patterns = []
        
        # Padrão 1: Testes que falham frequentemente
        failure_counts = defaultdict(int)
        test_counts = defaultdict(int)
        
        for feedback in feedbacks:
            test_counts[feedback.test_case_id] += 1
            if not feedback.success:
                failure_counts[feedback.test_case_id] += 1
        
        for test_id, failures in failure_counts.items():
            failure_rate = (failures / test_counts[test_id]) * 100
            if failure_rate > 50 and test_counts[test_id] >= 3:
                patterns.append({
                    'type': 'high_failure_rate',
                    'test_id': test_id,
                    'failure_rate': failure_rate,
                    'total_executions': test_counts[test_id],
                    'failures': failures,
                    'severity': 'high' if failure_rate > 75 else 'medium',
                    'message': f"Teste {test_id} falha em {failure_rate:.1f}% das execuções"
                })
        
        # Padrão 2: Degradação de performance ao longo do tempo
        if len(feedbacks) >= 10:
            recent_feedbacks = feedbacks[-10:]
            older_feedbacks = feedbacks[-20:-10] if len(feedbacks) >= 20 else feedbacks[:-10]
            
            if older_feedbacks:
                recent_avg_time = np.mean([f.actual_execution_time for f in recent_feedbacks])
                older_avg_time = np.mean([f.actual_execution_time for f in older_feedbacks])
                
                if recent_avg_time > older_avg_time * 1.5:
                    patterns.append({
                        'type': 'performance_degradation',
                        'recent_avg': recent_avg_time,
                        'older_avg': older_avg_time,
                        'degradation': ((recent_avg_time - older_avg_time) / older_avg_time) * 100,
                        'severity': 'medium',
                        'message': f"Tempo de execução aumentou {((recent_avg_time - older_avg_time) / older_avg_time) * 100:.1f}% recentemente"
                    })
        
        # Padrão 3: Testes com tempo muito variável
        test_times = defaultdict(list)
        for feedback in feedbacks:
            test_times[feedback.test_case_id].append(feedback.actual_execution_time)
        
        for test_id, times in test_times.items():
            if len(times) >= 5:
                std_dev = np.std(times)
                mean_time = np.mean(times)
                cv = (std_dev / mean_time) * 100 if mean_time > 0 else 0
                
                if cv > 50:  # Coeficiente de variação > 50%
                    patterns.append({
                        'type': 'high_variability',
                        'test_id': test_id,
                        'mean_time': mean_time,
                        'std_dev': std_dev,
                        'coefficient_of_variation': cv,
                        'severity': 'medium',
                        'message': f"Teste {test_id} tem alta variabilidade de tempo (CV: {cv:.1f}%)"
                    })
        
        return patterns
    
    def _generate_alerts(
        self,
        feedbacks: List[ExecutionFeedback],
        anomalies: List[Dict],
        patterns: List[Dict]
    ) -> List[Dict]:
        """
        Gera alertas baseados em anomalias e padrões
        
        Args:
            feedbacks: Todos os feedbacks
            anomalies: Anomalias detectadas
            patterns: Padrões identificados
        
        Returns:
            Lista de alertas
        """
        alerts = []
        
        # Alerta 1: Taxa de anomalias alta
        if len(anomalies) / len(feedbacks) > 0.2:
            alerts.append({
                'type': 'high_anomaly_rate',
                'severity': 'high',
                'message': f"Taxa de anomalias alta: {len(anomalies)/len(feedbacks)*100:.1f}%",
                'action': 'Revisar execuções recentes e verificar problemas sistêmicos'
            })
        
        # Alerta 2: Testes com alta taxa de falha
        high_failure_patterns = [p for p in patterns if p['type'] == 'high_failure_rate' and p['severity'] == 'high']
        for pattern in high_failure_patterns:
            alerts.append({
                'type': 'test_failing_frequently',
                'severity': 'high',
                'test_id': pattern['test_id'],
                'message': pattern['message'],
                'action': f"Investigar por que {pattern['test_id']} falha frequentemente"
            })
        
        # Alerta 3: Degradação de performance
        perf_patterns = [p for p in patterns if p['type'] == 'performance_degradation']
        for pattern in perf_patterns:
            alerts.append({
                'type': 'performance_degradation',
                'severity': 'medium',
                'message': pattern['message'],
                'action': 'Verificar se há mudanças no ambiente ou no sistema testado'
            })
        
        # Alerta 4: Múltiplas anomalias recentes
        recent_anomalies = [a for a in anomalies if len(feedbacks) - a['index'] <= 5]
        if len(recent_anomalies) >= 3:
            alerts.append({
                'type': 'multiple_recent_anomalies',
                'severity': 'medium',
                'count': len(recent_anomalies),
                'message': f"{len(recent_anomalies)} anomalias detectadas nas últimas 5 execuções",
                'action': 'Revisar execuções recentes para identificar causa comum'
            })
        
        return alerts
