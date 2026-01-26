"""
Sistema de recomendação personalizado por usuário
Combina aprendizado global com aprendizado individual
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pickle
from datetime import datetime

from src.models.test_case import TestCase, RecommendationResult, ExecutionFeedback
from src.features.feature_extractor import FeatureExtractor
from src.recommender.ml_recommender import MLTestRecommender


class PersonalizedMLRecommender:
    """
    Recomendador que combina modelo global com modelos personalizados por usuário
    """
    
    def __init__(self, global_model_path: str = "models/motorola_modelo.pkl"):
        """
        Inicializa o recomendador personalizado
        
        Args:
            global_model_path: Caminho para o modelo global
        """
        self.global_recommender = MLTestRecommender()
        self.global_model_path = global_model_path
        
        # Tentar carregar modelo global
        try:
            self.global_recommender.load_model(global_model_path)
        except:
            pass  # Modelo global será criado quando necessário
        
        # Cache de modelos personalizados (em memória)
        self.user_models: Dict[int, MLTestRecommender] = {}
    
    def get_user_model(self, user_id: int, db) -> MLTestRecommender:
        """
        Obtém ou cria modelo personalizado para um usuário
        
        Args:
            user_id: ID do usuário
            db: Instância do banco de dados
            
        Returns:
            Modelo ML personalizado do usuário
        """
        # Verificar cache
        if user_id in self.user_models:
            return self.user_models[user_id]
        
        # Tentar carregar do banco
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT model_data, training_samples FROM user_models 
            WHERE user_id = ?
        """, (user_id,))
        row = cursor.fetchone()
        
        if row and row['model_data']:
            # Carregar modelo do banco
            user_model = MLTestRecommender()
            try:
                model_data = pickle.loads(row['model_data'])
                user_model.model = model_data['model']
                user_model.scaler = model_data['scaler']
                user_model.is_trained = model_data['is_trained']
                user_model.training_data = model_data.get('training_data', {'X': [], 'y': []})
                user_model.feedback_history = model_data.get('feedback_history', [])
            except Exception as e:
                print(f"Erro ao carregar modelo do usuário {user_id}: {e}")
                user_model = MLTestRecommender()  # Criar novo
        else:
            # Criar novo modelo personalizado
            user_model = MLTestRecommender()
        
        # Armazenar em cache
        self.user_models[user_id] = user_model
        return user_model
    
    def save_user_model(self, user_id: int, user_model: MLTestRecommender, db):
        """
        Salva modelo personalizado do usuário no banco
        
        Args:
            user_id: ID do usuário
            user_model: Modelo ML do usuário
            db: Instância do banco de dados
        """
        # Serializar modelo
        model_data = {
            'model': user_model.model,
            'scaler': user_model.scaler,
            'is_trained': user_model.is_trained,
            'training_data': user_model.training_data,
            'feedback_history': user_model.feedback_history
        }
        model_blob = pickle.dumps(model_data)
        
        # Salvar no banco
        cursor = db.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_models 
            (user_id, model_data, training_samples, last_trained)
            VALUES (?, ?, ?, ?)
        """, (
            user_id,
            model_blob,
            len(user_model.training_data.get('y', [])),
            datetime.now().isoformat()
        ))
        db.conn.commit()
    
    def add_feedback(
        self, 
        user_id: int, 
        feedback: ExecutionFeedback, 
        test_order: List[TestCase],
        db
    ):
        """
        Adiciona feedback e treina tanto modelo global quanto personalizado
        
        Args:
            user_id: ID do usuário
            feedback: Feedback da execução
            test_order: Ordem em que os testes foram executados
            db: Instância do banco de dados
        """
        # Adicionar ao modelo global
        self.global_recommender.add_feedback(feedback, test_order)
        
        # Adicionar ao modelo personalizado
        user_model = self.get_user_model(user_id, db)
        user_model.add_feedback(feedback, test_order)
        
        # Treinar modelo personalizado se tiver dados suficientes
        if len(user_model.training_data.get('y', [])) >= 5:
            user_model.train()
            self.save_user_model(user_id, user_model, db)
        
        # Salvar modelo global periodicamente
        if len(self.global_recommender.training_data.get('y', [])) % 20 == 0:
            self.global_recommender.save_model(self.global_model_path)
    
    def get_personalization_weight(self, experience_level: str) -> float:
        """
        Calcula peso de personalização baseado no nível de experiência
        
        Args:
            experience_level: Nível de experiência ('beginner', 'intermediate', 'advanced', 'expert')
        
        Returns:
            Peso de personalização (0-1)
            - beginner: 0.2 (20% personalizado, 80% global)
            - intermediate: 0.5 (50% personalizado, 50% global)
            - advanced: 0.7 (70% personalizado, 30% global)
            - expert: 0.85 (85% personalizado, 15% global)
        """
        weights = {
            'beginner': 0.2,      # Mais dependente da base global
            'intermediate': 0.5,   # Equilibrado
            'advanced': 0.7,       # Mais personalizado
            'expert': 0.85         # Muito personalizado
        }
        return weights.get(experience_level.lower(), 0.5)
    
    def recommend_order(
        self,
        user_id: Optional[int],
        test_cases: List[TestCase],
        db,
        personalization_weight: Optional[float] = None,
        experience_level: Optional[str] = None
    ) -> RecommendationResult:
        """
        Recomenda ordenação combinando modelo global e personalizado
        
        Args:
            user_id: ID do usuário (None para usar apenas global)
            test_cases: Lista de casos de teste
            db: Instância do banco de dados
            personalization_weight: Peso do modelo personalizado (0-1). Se None, calcula baseado em experience_level
            experience_level: Nível de experiência do usuário ('beginner', 'intermediate', 'advanced', 'expert')
        
        Returns:
            Resultado da recomendação
        """
        if not test_cases:
            return RecommendationResult(
                recommended_order=[],
                estimated_total_time=0.0,
                estimated_resets=0,
                confidence_score=0.0
            )
        
        # Se não há usuário ou modelo personalizado não treinado, usar apenas global
        if user_id is None:
            return self.global_recommender.recommend_order(test_cases)
        
        # Buscar nível de experiência do usuário se não fornecido
        if experience_level is None:
            cursor = db.conn.cursor()
            cursor.execute("SELECT experience_level FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            experience_level = row['experience_level'] if row else 'beginner'
        
        # Calcular peso de personalização baseado no nível de experiência
        if personalization_weight is None:
            personalization_weight = self.get_personalization_weight(experience_level)
        
        user_model = self.get_user_model(user_id, db)
        
        # Se modelo personalizado não está treinado, usar apenas global (mas com peso reduzido para iniciantes)
        if not user_model.is_trained or len(user_model.training_data.get('y', [])) < 5:
            result = self.global_recommender.recommend_order(test_cases)
            result.reasoning['method'] = 'global_only'
            result.reasoning['experience_level'] = experience_level
            result.reasoning['personalization_weight'] = personalization_weight
            return result
        
        # Obter recomendações de ambos modelos
        global_result = self.global_recommender.recommend_order(test_cases)
        personal_result = user_model.recommend_order(test_cases)
        
        # Combinar ordenações usando ensemble
        combined_order = self._ensemble_order(
            test_cases,
            global_result.recommended_order,
            personal_result.recommended_order,
            personalization_weight
        )
        
        # Calcular métricas da ordenação combinada
        ordered_tests = {tc.id: tc for tc in test_cases}
        ordered_list = [ordered_tests[tid] for tid in combined_order if tid in ordered_tests]
        
        total_time = sum(tc.get_total_estimated_time() for tc in ordered_list)
        estimated_resets = self._estimate_resets(ordered_list)
        
        # Confiança baseada na combinação
        confidence = (
            personalization_weight * personal_result.confidence_score +
            (1 - personalization_weight) * global_result.confidence_score
        )
        
        return RecommendationResult(
            recommended_order=combined_order,
            estimated_total_time=total_time,
            estimated_resets=estimated_resets,
            confidence_score=confidence,
            reasoning={
                'method': 'personalized_ensemble',
                'global_samples': len(self.global_recommender.training_data.get('y', [])),
                'personal_samples': len(user_model.training_data.get('y', [])),
                'personalization_weight': personalization_weight,
                'experience_level': experience_level
            }
        )
    
    def _ensemble_order(
        self,
        test_cases: List[TestCase],
        global_order: List[str],
        personal_order: List[str],
        weight: float
    ) -> List[str]:
        """
        Combina duas ordenações usando ensemble
        
        Args:
            test_cases: Lista completa de testes
            global_order: Ordem do modelo global
            personal_order: Ordem do modelo personalizado
            weight: Peso do modelo personalizado
            
        Returns:
            Ordem combinada
        """
        # Criar dicionário de posições
        global_positions = {test_id: i for i, test_id in enumerate(global_order)}
        personal_positions = {test_id: i for i, test_id in enumerate(personal_order)}
        
        # Calcular score combinado para cada teste
        test_scores = {}
        for tc in test_cases:
            test_id = tc.id
            
            # Posições normalizadas (0-1)
            global_pos = global_positions.get(test_id, len(test_cases))
            personal_pos = personal_positions.get(test_id, len(test_cases))
            
            global_score = 1.0 - (global_pos / len(test_cases))
            personal_score = 1.0 - (personal_pos / len(test_cases))
            
            # Score combinado
            combined_score = (
                weight * personal_score +
                (1 - weight) * global_score
            )
            
            test_scores[test_id] = combined_score
        
        # Ordenar por score combinado
        sorted_tests = sorted(
            test_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [test_id for test_id, _ in sorted_tests]
    
    def _estimate_resets(self, test_order: List[TestCase]) -> int:
        """Estima número de reinicializações necessárias"""
        resets = 0
        current_state = set()
        
        for test in test_order:
            required = test.get_preconditions()
            
            if required and not required.issubset(current_state):
                resets += 1
                current_state = set()
            
            current_state.update(test.get_postconditions())
        
        return resets
    
    def update_user_learning_stats(self, user_id: int, db):
        """
        Atualiza estatísticas de aprendizado do usuário
        
        Args:
            user_id: ID do usuário
            db: Instância do banco de dados
        """
        cursor = db.conn.cursor()
        
        # Buscar feedbacks do usuário
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                AVG(tester_rating) as avg_rating,
                AVG(CASE WHEN success = 1 THEN 1.0 ELSE 0.0 END) * 100 as success_rate,
                AVG(actual_execution_time) as avg_time
            FROM feedbacks
            WHERE tester_id = ?
        """, (user_id,))
        
        stats = cursor.fetchone()
        
        if stats and stats['total'] > 0:
            # Buscar módulos preferidos (dos testes executados pelo usuário)
            # Mapear IDs de teste para módulos
            test_to_module = {
                'MOTO_SETUP_001': 'Setup', 'MOTO_CAM_001': 'Camera', 'MOTO_CAM_002': 'Camera',
                'MOTO_CAM_003': 'Camera', 'MOTO_WIFI_001': 'Connectivity', 'MOTO_WIFI_002': 'Connectivity',
                'MOTO_BT_001': 'Connectivity', 'MOTO_BAT_001': 'Battery', 'MOTO_BAT_002': 'Battery',
                'MOTO_CALL_001': 'Telephony', 'MOTO_CALL_002': 'Telephony', 'MOTO_SMS_001': 'Messaging',
                'MOTO_SEC_001': 'Security', 'MOTO_SEC_002': 'Security', 'MOTO_GESTURE_001': 'MotoGestures',
                'MOTO_GESTURE_002': 'MotoGestures', 'MOTO_AUDIO_001': 'Multimedia', 'MOTO_PERF_001': 'Performance',
                'MOTO_PERF_002': 'Performance', 'MOTO_DISP_001': 'Display', 'MOTO_CELL_001': 'Connectivity',
                'MOTO_CELL_002': 'Connectivity', 'MOTO_CELL_003': 'Connectivity', 'MOTO_GPS_001': 'Location',
                'MOTO_NFC_001': 'NFC', 'MOTO_SYS_001': 'System', 'MOTO_SYS_002': 'System',
                'MOTO_NOTIF_001': 'Notifications', 'MOTO_ACC_001': 'Accessibility', 'MOTO_SENSOR_001': 'Sensors',
                'MOTO_AUDIO_002': 'Multimedia', 'MOTO_STORE_001': 'Storage', 'MOTO_SEC_003': 'Security',
                'MOTO_APP_001': 'Apps'
            }
            
            # Buscar testes mais executados pelo usuário
            cursor.execute("""
                SELECT test_case_id, COUNT(*) as count
                FROM feedbacks
                WHERE tester_id = ?
                GROUP BY test_case_id
                ORDER BY count DESC
                LIMIT 20
            """, (user_id,))
            
            module_counts = {}
            for row in cursor.fetchall():
                test_id = row['test_case_id']
                module = test_to_module.get(test_id, 'Other')
                module_counts[module] = module_counts.get(module, 0) + row['count']
            
            # Ordenar por frequência e pegar top 5
            modules = sorted(module_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            modules = [m[0] for m in modules]
            
            # Inserir ou atualizar estatísticas
            cursor.execute("""
                INSERT OR REPLACE INTO user_learning_stats
                (user_id, total_feedbacks, avg_rating, success_rate, 
                 avg_execution_time, preferred_modules, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                stats['total'],
                stats['avg_rating'] or 0.0,
                stats['success_rate'] or 0.0,
                stats['avg_time'] or 0.0,
                ','.join(modules) if modules else None,
                datetime.now().isoformat()
            ))
            db.conn.commit()
