"""
Sistema de Gerenciamento de Notificações e Alertas
Gera notificações automáticas baseadas em eventos do sistema
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from src.utils.database import IARTESDatabase


class NotificationManager:
    """Gerencia criação e verificação de notificações"""
    
    def __init__(self, db: IARTESDatabase):
        self.db = db
    
    def check_model_training_phases(self, user_id: int, training_samples: int):
        """
        Verifica se o modelo personalizado atingiu uma nova fase de treinamento.
        Fases: 5, 10, 25, 50, 100, 250, 500 amostras
        
        Args:
            user_id: ID do usuário
            training_samples: Número atual de amostras de treinamento
        """
        phases = [5, 10, 25, 50, 100, 250, 500]
        
        # Verificar se atingiu alguma fase
        for phase in phases:
            if training_samples == phase:
                self.db.create_notification(
                    user_id=user_id,
                    notification_type='model_trained',
                    title=f'🎉 Modelo Personalizado Treinado!',
                    message=f'Seu modelo personalizado atingiu {phase} amostras de treinamento. As recomendações estão ficando mais precisas!',
                    severity='success',
                    action_url='/minhas-estatisticas'
                )
                break
    
    def check_success_rate_drop(
        self,
        user_id: int,
        current_success_rate: float,
        threshold: float = 0.7
    ):
        """
        Verifica se a taxa de sucesso caiu abaixo do threshold.
        
        Args:
            user_id: ID do usuário
            current_success_rate: Taxa de sucesso atual
            threshold: Threshold mínimo (padrão 70%)
        """
        if current_success_rate < threshold:
            # Verificar se já existe notificação recente sobre isso
            notifications = self.db.get_user_notifications(
                user_id=user_id,
                unread_only=True,
                limit=10
            )
            
            # Verificar se já há notificação de success_rate_drop nas últimas 24h
            recent_notification = any(
                n['type'] == 'success_rate_drop' and
                datetime.fromisoformat(n['created_at']) > datetime.now() - timedelta(hours=24)
                for n in notifications
            )
            
            if not recent_notification:
                self.db.create_notification(
                    user_id=user_id,
                    notification_type='success_rate_drop',
                    title='⚠️ Taxa de Sucesso Abaixo do Esperado',
                    message=f'Sua taxa de sucesso atual é {current_success_rate:.1%}, abaixo do threshold de {threshold:.1%}. Considere revisar os testes que estão falhando.',
                    severity='warning',
                    action_url='/minhas-estatisticas'
                )
    
    def check_feedback_reminder(
        self,
        user_id: int,
        last_feedback_time: Optional[datetime]
    ):
        """
        Envia lembrete para dar feedback após execução.
        
        Args:
            user_id: ID do usuário
            last_feedback_time: Data/hora do último feedback
        """
        if last_feedback_time is None:
            return
        
        # Se passou mais de 1 hora desde o último feedback e não há feedback recente
        time_since_feedback = datetime.now() - last_feedback_time
        
        if time_since_feedback > timedelta(hours=1):
            # Verificar se já existe notificação de lembrete recente
            notifications = self.db.get_user_notifications(
                user_id=user_id,
                unread_only=True,
                limit=10
            )
            
            recent_reminder = any(
                n['type'] == 'feedback_reminder' and
                datetime.fromisoformat(n['created_at']) > datetime.now() - timedelta(hours=2)
                for n in notifications
            )
            
            if not recent_reminder:
                self.db.create_notification(
                    user_id=user_id,
                    notification_type='feedback_reminder',
                    title='💡 Lembrete: Dê seu Feedback!',
                    message='Você executou testes recentemente. Forneça feedback para ajudar a IA a aprender e melhorar as recomendações.',
                    severity='info',
                    action_url='/feedback'
                )
    
    def notify_recommendation_improvement(
        self,
        user_id: int,
        improvement_percentage: float
    ):
        """
        Notifica quando há melhoria significativa nas recomendações.
        
        Args:
            user_id: ID do usuário
            improvement_percentage: Percentual de melhoria (ex: 15.5 para 15.5%)
        """
        if improvement_percentage >= 10:  # Apenas notificar melhorias >= 10%
            self.db.create_notification(
                user_id=user_id,
                notification_type='recommendation_improvement',
                title='📈 Melhoria nas Recomendações!',
                message=f'As recomendações da IA melhoraram {improvement_percentage:.1f}% desde o último treinamento. Continue fornecendo feedback!',
                severity='success',
                action_url='/recomendacao'
            )
    
    def check_all_user_alerts(self, user_id: int):
        """
        Verifica todos os alertas para um usuário e cria notificações se necessário.
        
        Args:
            user_id: ID do usuário
        """
        cursor = self.db.conn.cursor()
        
        # Buscar estatísticas do usuário
        cursor.execute("""
            SELECT * FROM user_learning_stats WHERE user_id = ?
        """, (user_id,))
        stats_row = cursor.fetchone()
        
        # Buscar modelo personalizado
        cursor.execute("""
            SELECT training_samples FROM user_models WHERE user_id = ?
        """, (user_id,))
        model_row = cursor.fetchone()
        
        if stats_row:
            stats = dict(stats_row)
            success_rate = stats.get('success_rate', 0.0) or 0.0
            
            # Verificar taxa de sucesso
            self.check_success_rate_drop(user_id, success_rate)
        
        if model_row:
            training_samples = model_row['training_samples'] or 0
            # Verificar fases de treinamento
            self.check_model_training_phases(user_id, training_samples)
        
        # Buscar último feedback
        cursor.execute("""
            SELECT executed_at FROM feedbacks 
            WHERE tester_id = ? 
            ORDER BY executed_at DESC 
            LIMIT 1
        """, (user_id,))
        last_feedback_row = cursor.fetchone()
        
        if last_feedback_row:
            last_feedback_time = datetime.fromisoformat(last_feedback_row['executed_at'])
            self.check_feedback_reminder(user_id, last_feedback_time)
