"""
Módulo de gerenciamento do banco de dados SQLite para o sistema IARTES.

Armazena feedbacks, recomendações e histórico de execuções.
O modelo ML continua sendo salvo em pickle (.pkl).
"""
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
import json


class IARTESDatabase:
    """Gerenciador do banco de dados SQLite do IARTES"""
    
    def __init__(self, db_path: str = "iartes.db"):
        """
        Inicializa conexão com o banco de dados.
        
        Args:
            db_path: Caminho para o arquivo do banco de dados
        """
        self.db_path = Path(db_path)
        self.conn = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Estabelece conexão com o banco de dados"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
    
    def _create_tables(self):
        """Cria as tabelas do banco de dados se não existirem"""
        cursor = self.conn.cursor()
        
        # Tabela de usuários/testadores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                role TEXT DEFAULT 'tester',
                experience_level TEXT DEFAULT 'beginner',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Migração: Adicionar coluna experience_level se não existir
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='users'
        """)
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'experience_level' not in columns:
                try:
                    cursor.execute("ALTER TABLE users ADD COLUMN experience_level TEXT DEFAULT 'beginner'")
                    print("✓ Coluna experience_level adicionada à tabela users")
                except sqlite3.OperationalError as e:
                    print(f"⚠ Aviso ao adicionar coluna experience_level: {e}")
        
        # Tabela de feedbacks de execução (atualizada com tester_id)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedbacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tester_id INTEGER,
                test_case_id TEXT NOT NULL,
                executed_at TIMESTAMP NOT NULL,
                actual_execution_time REAL NOT NULL,
                success BOOLEAN NOT NULL,
                followed_recommendation BOOLEAN NOT NULL,
                tester_rating INTEGER CHECK(tester_rating >= 1 AND tester_rating <= 5),
                required_reset BOOLEAN NOT NULL DEFAULT 0,
                notes TEXT,
                initial_state TEXT,
                final_state TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tester_id) REFERENCES users(id)
            )
        """)
        
        # Tabela de recomendações geradas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                test_ids TEXT NOT NULL,
                recommended_order TEXT NOT NULL,
                method TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                estimated_total_time REAL,
                estimated_resets INTEGER,
                was_accepted BOOLEAN,
                user_modifications TEXT
            )
        """)
        
        # Tabela de execuções (relaciona recommendation com feedbacks)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recommendation_id INTEGER,
                started_at TIMESTAMP NOT NULL,
                finished_at TIMESTAMP,
                total_tests INTEGER,
                successful_tests INTEGER,
                failed_tests INTEGER,
                total_time REAL,
                actual_resets INTEGER,
                FOREIGN KEY (recommendation_id) REFERENCES recommendations(id)
            )
        """)
        
        # Migração: Adicionar coluna tester_id se não existir (para bancos antigos)
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='feedbacks'
        """)
        if cursor.fetchone():
            # Tabela existe, verificar se coluna tester_id existe
            cursor.execute("PRAGMA table_info(feedbacks)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'tester_id' not in columns:
                try:
                    cursor.execute("ALTER TABLE feedbacks ADD COLUMN tester_id INTEGER")
                    print("✓ Coluna tester_id adicionada à tabela feedbacks")
                except sqlite3.OperationalError as e:
                    print(f"⚠ Aviso ao adicionar coluna tester_id: {e}")
        
        # Índices para melhorar performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedbacks_test_id 
            ON feedbacks(test_case_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedbacks_executed_at 
            ON feedbacks(executed_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedbacks_success 
            ON feedbacks(success)
        """)
        # Criar índice para tester_id (após garantir que coluna existe)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedbacks_tester_id 
            ON feedbacks(tester_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_username 
            ON users(username)
        """)
        
        # Tabela para modelos personalizados por usuário
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                model_data BLOB,
                training_samples INTEGER DEFAULT 0,
                last_trained TIMESTAMP,
                accuracy_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id)
            )
        """)
        
        # Tabela para estatísticas de aprendizado por usuário
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_learning_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                total_feedbacks INTEGER DEFAULT 0,
                avg_rating REAL DEFAULT 0.0,
                success_rate REAL DEFAULT 0.0,
                preferred_modules TEXT,
                avg_execution_time REAL DEFAULT 0.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_models_user_id 
            ON user_models(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_learning_stats_user_id 
            ON user_learning_stats(user_id)
        """)
        
        # Tabela de notificações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                severity TEXT DEFAULT 'info',
                is_read BOOLEAN DEFAULT 0,
                action_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notifications_user_id 
            ON notifications(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notifications_is_read 
            ON notifications(is_read)
        """)
        
        # Tabela para preferências de usuário
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                theme TEXT DEFAULT 'light',
                notifications_enabled BOOLEAN DEFAULT 1,
                email_notifications BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id)
            )
        """)
        
        # Tabela de anotações (Post-its do Kanban)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                column_name TEXT NOT NULL DEFAULT 'todo',
                color TEXT DEFAULT 'yellow',
                position INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Índice para melhorar performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notes_user_id 
            ON notes(user_id)
        """)
        
        # Tabela de testes personalizados do usuário
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_test_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                test_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                module TEXT,
                priority INTEGER DEFAULT 3,
                tags TEXT,
                actions TEXT,
                estimated_time REAL DEFAULT 0.0,
                impact_level TEXT DEFAULT 'non_destructive',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, test_id)
            )
        """)
        
        # Índices
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_test_cases_user_id 
            ON user_test_cases(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_test_cases_test_id 
            ON user_test_cases(test_id)
        """)
        
        # Adicionar colunas opcionais na tabela users se não existirem
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN profile_picture TEXT")
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        
        self.conn.commit()
    
    def add_feedback(self, feedback: Dict[str, Any]) -> int:
        """
        Adiciona um feedback ao banco de dados.
        
        Args:
            feedback: Dicionário com dados do feedback
        
        Returns:
            ID do feedback inserido
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO feedbacks (
                tester_id, test_case_id, executed_at, actual_execution_time,
                success, followed_recommendation, tester_rating,
                required_reset, notes, initial_state, final_state
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            feedback.get('tester_id'),
            feedback['test_case_id'],
            feedback['executed_at'],
            feedback['actual_execution_time'],
            feedback['success'],
            feedback['followed_recommendation'],
            feedback.get('tester_rating'),
            feedback.get('required_reset', False),
            feedback.get('notes'),
            json.dumps(list(feedback.get('initial_state', set()))),
            json.dumps(list(feedback.get('final_state', set())))
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_all_feedbacks(self) -> List[Dict[str, Any]]:
        """
        Retorna todos os feedbacks do banco de dados.
        
        Returns:
            Lista de dicionários com os feedbacks
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM feedbacks ORDER BY executed_at DESC
        """)
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_feedbacks_by_test(self, test_case_id: str) -> List[Dict[str, Any]]:
        """
        Retorna feedbacks de um teste específico.
        
        Args:
            test_case_id: ID do caso de teste
        
        Returns:
            Lista de feedbacks
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM feedbacks 
            WHERE test_case_id = ? 
            ORDER BY executed_at DESC
        """, (test_case_id,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas gerais dos feedbacks.
        
        Returns:
            Dicionário com estatísticas
        """
        cursor = self.conn.cursor()
        
        # Total de feedbacks
        cursor.execute("SELECT COUNT(*) as total FROM feedbacks")
        total = cursor.fetchone()['total']
        
        if total == 0:
            return {
                'total_feedbacks': 0,
                'success_rate': 0.0,
                'avg_rating': 0.0,
                'resets_count': 0,
                'followed_recommendation_count': 0,
                'avg_execution_time': 0.0
            }
        
        # Taxa de sucesso
        cursor.execute("SELECT COUNT(*) as success FROM feedbacks WHERE success = 1")
        success = cursor.fetchone()['success']
        
        # Avaliação média
        cursor.execute("SELECT AVG(tester_rating) as avg_rating FROM feedbacks WHERE tester_rating IS NOT NULL")
        avg_rating = cursor.fetchone()['avg_rating'] or 0.0
        
        # Resets
        cursor.execute("SELECT COUNT(*) as resets FROM feedbacks WHERE required_reset = 1")
        resets = cursor.fetchone()['resets']
        
        # Seguiu recomendação
        cursor.execute("SELECT COUNT(*) as followed FROM feedbacks WHERE followed_recommendation = 1")
        followed = cursor.fetchone()['followed']
        
        # Tempo médio de execução
        cursor.execute("SELECT AVG(actual_execution_time) as avg_time FROM feedbacks")
        avg_time = cursor.fetchone()['avg_time'] or 0.0
        
        return {
            'total_feedbacks': total,
            'success_rate': (success / total) * 100,
            'avg_rating': avg_rating,
            'resets_count': resets,
            'followed_recommendation_count': followed,
            'avg_execution_time': avg_time
        }
    
    def get_test_statistics(self) -> List[Dict[str, Any]]:
        """
        Retorna estatísticas agrupadas por teste.
        
        Returns:
            Lista de dicionários com estatísticas por teste
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                test_case_id,
                COUNT(*) as executions,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes,
                AVG(actual_execution_time) as avg_time,
                AVG(tester_rating) as avg_rating,
                SUM(CASE WHEN required_reset = 1 THEN 1 ELSE 0 END) as resets,
                MAX(executed_at) as last_executed
            FROM feedbacks
            GROUP BY test_case_id
            ORDER BY executions DESC
        """)
        
        rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append({
                'test_case_id': row['test_case_id'],
                'executions': row['executions'],
                'success_rate': (row['successes'] / row['executions']) * 100,
                'avg_time': row['avg_time'],
                'avg_rating': row['avg_rating'] or 0.0,
                'resets': row['resets'],
                'last_executed': row['last_executed']
            })
        
        return results
    
    def add_recommendation(self, recommendation: Dict[str, Any]) -> int:
        """
        Adiciona uma recomendação ao banco de dados.
        
        Args:
            recommendation: Dicionário com dados da recomendação
        
        Returns:
            ID da recomendação inserida
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO recommendations (
                test_ids, recommended_order, method,
                confidence_score, estimated_total_time, estimated_resets,
                was_accepted, user_modifications
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            json.dumps(recommendation['test_ids']),
            json.dumps(recommendation['recommended_order']),
            recommendation['method'],
            recommendation['confidence_score'],
            recommendation.get('estimated_total_time'),
            recommendation.get('estimated_resets'),
            recommendation.get('was_accepted'),
            json.dumps(recommendation.get('user_modifications', []))
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_user_feedbacks(self, user_id: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retorna feedbacks de um usuário específico.
        
        Args:
            user_id: ID do usuário
            limit: Limite de resultados (opcional)
        
        Returns:
            Lista de feedbacks
        """
        cursor = self.conn.cursor()
        query = """
            SELECT * FROM feedbacks 
            WHERE tester_id = ? 
            ORDER BY executed_at DESC
        """
        params = [user_id]
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_recent_feedbacks(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Retorna os feedbacks mais recentes.
        
        Args:
            limit: Número máximo de feedbacks
        
        Returns:
            Lista de feedbacks
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM feedbacks 
            ORDER BY executed_at DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_feedbacks_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Retorna feedbacks em um intervalo de datas.
        
        Args:
            start_date: Data inicial
            end_date: Data final
        
        Returns:
            Lista de feedbacks
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM feedbacks 
            WHERE executed_at BETWEEN ? AND ?
            ORDER BY executed_at DESC
        """, (start_date, end_date))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def delete_all_feedbacks(self):
        """CUIDADO: Apaga todos os feedbacks do banco"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM feedbacks")
        self.conn.commit()
    
    def close(self):
        """Fecha a conexão com o banco de dados"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Suporte para context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Fecha conexão ao sair do context manager"""
        self.close()
    
    # ==================== FUNÇÕES DE AUTENTICAÇÃO ====================
    
    def create_user(self, username: str, password_hash: str, email: str = None, 
                    full_name: str = None, role: str = 'tester', 
                    experience_level: str = 'beginner') -> int:
        """
        Cria um novo usuário no banco de dados.
        
        Args:
            username: Nome de usuário único
            password_hash: Hash da senha (já deve estar hasheado)
            email: Email do usuário (opcional)
            full_name: Nome completo (opcional)
            role: Papel do usuário (padrão: 'tester')
            experience_level: Nível de experiência ('beginner', 'intermediate', 'advanced', 'expert')
        
        Returns:
            ID do usuário criado
        
        Raises:
            ValueError: Se username ou email já existirem
        """
        cursor = self.conn.cursor()
        
        # Validar nível de experiência
        valid_levels = ['beginner', 'intermediate', 'advanced', 'expert']
        if experience_level not in valid_levels:
            experience_level = 'beginner'
        
        try:
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, full_name, role, experience_level)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, email, password_hash, full_name, role, experience_level))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed: users.username' in str(e):
                raise ValueError(f"Usuário '{username}' já existe")
            elif 'UNIQUE constraint failed: users.email' in str(e):
                raise ValueError(f"Email '{email}' já está em uso")
            raise
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Busca usuário por nome de usuário.
        
        Args:
            username: Nome de usuário
        
        Returns:
            Dicionário com dados do usuário ou None se não encontrado
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM users WHERE username = ? AND is_active = 1
        """, (username,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca usuário por ID.
        
        Args:
            user_id: ID do usuário
        
        Returns:
            Dicionário com dados do usuário ou None se não encontrado
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM users WHERE id = ? AND is_active = 1
        """, (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def update_user_profile(
        self,
        user_id: int,
        full_name: Optional[str] = None,
        email: Optional[str] = None,
        experience_level: Optional[str] = None,
        profile_picture: Optional[str] = None
    ):
        """
        Atualiza informações do perfil do usuário.
        
        Args:
            user_id: ID do usuário
            full_name: Nome completo (opcional)
            email: Email (opcional)
            experience_level: Nível de experiência (opcional)
            profile_picture: Caminho da foto de perfil (opcional)
        """
        cursor = self.conn.cursor()
        
        updates = []
        params = []
        
        if full_name is not None:
            updates.append("full_name = ?")
            params.append(full_name)
        
        if email is not None:
            # Verificar se email já está em uso por outro usuário
            cursor.execute("SELECT id FROM users WHERE email = ? AND id != ?", (email, user_id))
            if cursor.fetchone():
                raise ValueError("Email já está em uso por outro usuário")
            updates.append("email = ?")
            params.append(email)
        
        if experience_level is not None:
            valid_levels = ['beginner', 'intermediate', 'advanced', 'expert']
            if experience_level not in valid_levels:
                raise ValueError(f"Nível de experiência inválido. Deve ser um de: {', '.join(valid_levels)}")
            updates.append("experience_level = ?")
            params.append(experience_level)
        
        if profile_picture is not None:
            updates.append("profile_picture = ?")
            params.append(profile_picture)
        
        if updates:
            params.append(user_id)
            cursor.execute(f"""
                UPDATE users 
                SET {', '.join(updates)}
                WHERE id = ?
            """, params)
            self.conn.commit()
    
    def update_user_password(self, user_id: int, new_password_hash: str):
        """
        Atualiza senha do usuário.
        
        Args:
            user_id: ID do usuário
            new_password_hash: Hash da nova senha
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET password_hash = ?
            WHERE id = ?
        """, (new_password_hash, user_id))
        self.conn.commit()
    
    def update_last_login(self, user_id: int):
        """Atualiza timestamp do último login do usuário"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
        """, (user_id,))
        self.conn.commit()
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Retorna todos os usuários ativos.
        
        Returns:
            Lista de usuários
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, username, email, full_name, role, created_at, last_login
            FROM users WHERE is_active = 1
            ORDER BY username
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def create_notification(
        self,
        user_id: Optional[int],
        notification_type: str,
        title: str,
        message: str,
        severity: str = 'info',
        action_url: Optional[str] = None
    ) -> int:
        """
        Cria uma nova notificação.
        
        Args:
            user_id: ID do usuário (None para notificação global)
            notification_type: Tipo da notificação (model_trained, success_rate_drop, etc.)
            title: Título da notificação
            message: Mensagem da notificação
            severity: Severidade (info, warning, error, success)
            action_url: URL de ação opcional
        
        Returns:
            ID da notificação criada
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO notifications 
            (user_id, type, title, message, severity, action_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, notification_type, title, message, severity, action_url))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca notificações do usuário.
        
        Args:
            user_id: ID do usuário
            unread_only: Se True, retorna apenas não lidas
            limit: Limite de resultados
        
        Returns:
            Lista de notificações
        """
        cursor = self.conn.cursor()
        query = """
            SELECT * FROM notifications 
            WHERE (user_id = ? OR user_id IS NULL)
        """
        params = [user_id]
        
        if unread_only:
            query += " AND is_read = 0"
        
        query += " ORDER BY created_at DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def mark_notification_read(self, notification_id: int, user_id: int):
        """
        Marca uma notificação como lida.
        
        Args:
            notification_id: ID da notificação
            user_id: ID do usuário (para validação)
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE notifications 
            SET is_read = 1 
            WHERE id = ? AND (user_id = ? OR user_id IS NULL)
        """, (notification_id, user_id))
        self.conn.commit()
    
    def mark_all_notifications_read(self, user_id: int):
        """
        Marca todas as notificações do usuário como lidas.
        
        Args:
            user_id: ID do usuário
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE notifications 
            SET is_read = 1 
            WHERE (user_id = ? OR user_id IS NULL) AND is_read = 0
        """, (user_id,))
        self.conn.commit()
    
    def get_unread_count(self, user_id: int) -> int:
        """
        Retorna contagem de notificações não lidas.
        
        Args:
            user_id: ID do usuário
        
        Returns:
            Número de notificações não lidas
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as count FROM notifications 
            WHERE (user_id = ? OR user_id IS NULL) AND is_read = 0
        """, (user_id,))
        row = cursor.fetchone()
        return row['count'] if row else 0
    
    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """
        Busca preferências do usuário.
        
        Args:
            user_id: ID do usuário
        
        Returns:
            Dicionário com preferências ou valores padrão
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM user_preferences WHERE user_id = ?
        """, (user_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        else:
            # Criar preferências padrão
            cursor.execute("""
                INSERT INTO user_preferences 
                (user_id, theme, notifications_enabled, email_notifications)
                VALUES (?, 'light', 1, 0)
            """, (user_id,))
            self.conn.commit()
            return {
                'user_id': user_id,
                'theme': 'light',
                'notifications_enabled': True,
                'email_notifications': False
            }
    
    def update_user_preferences(self, user_id: int, preferences: Dict[str, Any]):
        """
        Atualiza preferências do usuário.
        
        Args:
            user_id: ID do usuário
            preferences: Dicionário com preferências a atualizar
        """
        cursor = self.conn.cursor()
        
        # Verificar se existe
        cursor.execute("SELECT id FROM user_preferences WHERE user_id = ?", (user_id,))
        exists = cursor.fetchone()
        
        if exists:
            # Atualizar
            updates = []
            params = []
            for key, value in preferences.items():
                if key != 'user_id':
                    updates.append(f"{key} = ?")
                    params.append(value)
            
            if updates:
                params.append(user_id)
                cursor.execute(f"""
                    UPDATE user_preferences 
                    SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, params)
        else:
            # Criar
            cursor.execute("""
                INSERT INTO user_preferences 
                (user_id, theme, notifications_enabled, email_notifications)
                VALUES (?, ?, ?, ?)
            """, (
                user_id,
                preferences.get('theme', 'light'),
                preferences.get('notifications_enabled', True),
                preferences.get('email_notifications', False)
            ))
        
        self.conn.commit()
    
    # ==================== ANOTAÇÕES (POST-ITS) ====================
    
    def create_note(self, user_id: int, title: str, content: str = "", 
                    column_name: str = "todo", color: str = "yellow") -> int:
        """Cria uma nova anotação"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO notes (user_id, title, content, column_name, color, position)
            VALUES (?, ?, ?, ?, ?, 
                (SELECT COALESCE(MAX(position), -1) + 1 FROM notes WHERE user_id = ? AND column_name = ?))
        """, (user_id, title, content, column_name, color, user_id, column_name))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_user_notes(self, user_id: int) -> List[Dict[str, Any]]:
        """Retorna todas as anotações do usuário"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, title, content, column_name, color, position, 
                   created_at, updated_at
            FROM notes
            WHERE user_id = ?
            ORDER BY column_name, position
        """, (user_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def update_note(self, note_id: int, user_id: int, title: str = None, 
                    content: str = None, column_name: str = None, 
                    color: str = None, position: int = None) -> bool:
        """Atualiza uma anotação"""
        cursor = self.conn.cursor()
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if content is not None:
            updates.append("content = ?")
            params.append(content)
        if column_name is not None:
            updates.append("column_name = ?")
            params.append(column_name)
        if color is not None:
            updates.append("color = ?")
            params.append(color)
        if position is not None:
            updates.append("position = ?")
            params.append(position)
        
        if not updates:
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.extend([note_id, user_id])
        
        cursor.execute(f"""
            UPDATE notes 
            SET {', '.join(updates)}
            WHERE id = ? AND user_id = ?
        """, params)
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_note(self, note_id: int, user_id: int) -> bool:
        """Deleta uma anotação"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", 
                      (note_id, user_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def update_note_positions(self, user_id: int, column_name: str, 
                              note_positions: List[tuple]) -> bool:
        """Atualiza posições de múltiplas anotações (para drag and drop)"""
        cursor = self.conn.cursor()
        try:
            for note_id, position in note_positions:
                cursor.execute("""
                    UPDATE notes 
                    SET position = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND user_id = ? AND column_name = ?
                """, (position, note_id, user_id, column_name))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Erro ao atualizar posições: {e}")
            return False
    
    # ==================== TESTES PERSONALIZADOS ====================
    
    def create_user_test_case(self, user_id: int, test_data: Dict[str, Any]) -> int:
        """Cria um novo teste personalizado do usuário"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO user_test_cases 
            (user_id, test_id, name, description, module, priority, tags, actions, 
             estimated_time, impact_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            test_data['test_id'],
            test_data['name'],
            test_data.get('description', ''),
            test_data.get('module', ''),
            test_data.get('priority', 3),
            json.dumps(list(test_data.get('tags', []))),
            json.dumps(test_data.get('actions', [])),
            test_data.get('estimated_time', 0.0),
            test_data.get('impact_level', 'non_destructive')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_user_test_cases(self, user_id: int) -> List[Dict[str, Any]]:
        """Retorna todos os testes personalizados do usuário"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, test_id, name, description, module, priority, tags, actions,
                   estimated_time, impact_level, created_at, updated_at
            FROM user_test_cases
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        rows = cursor.fetchall()
        result = []
        for row in rows:
            test = dict(row)
            test['tags'] = json.loads(test.get('tags', '[]'))
            test['actions'] = json.loads(test.get('actions', '[]'))
            result.append(test)
        return result
    
    def get_user_test_case(self, user_id: int, test_id: str) -> Optional[Dict[str, Any]]:
        """Retorna um teste personalizado específico"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, test_id, name, description, module, priority, tags, actions,
                   estimated_time, impact_level, created_at, updated_at
            FROM user_test_cases
            WHERE user_id = ? AND test_id = ?
        """, (user_id, test_id))
        row = cursor.fetchone()
        if row:
            test = dict(row)
            test['tags'] = json.loads(test.get('tags', '[]'))
            test['actions'] = json.loads(test.get('actions', '[]'))
            return test
        return None
    
    def update_user_test_case(self, user_id: int, test_id: str, 
                              test_data: Dict[str, Any]) -> bool:
        """Atualiza um teste personalizado"""
        cursor = self.conn.cursor()
        updates = []
        params = []
        
        if 'name' in test_data:
            updates.append("name = ?")
            params.append(test_data['name'])
        if 'description' in test_data:
            updates.append("description = ?")
            params.append(test_data['description'])
        if 'module' in test_data:
            updates.append("module = ?")
            params.append(test_data['module'])
        if 'priority' in test_data:
            updates.append("priority = ?")
            params.append(test_data['priority'])
        if 'tags' in test_data:
            updates.append("tags = ?")
            params.append(json.dumps(list(test_data['tags'])))
        if 'actions' in test_data:
            updates.append("actions = ?")
            params.append(json.dumps(test_data['actions']))
        if 'estimated_time' in test_data:
            updates.append("estimated_time = ?")
            params.append(test_data['estimated_time'])
        if 'impact_level' in test_data:
            updates.append("impact_level = ?")
            params.append(test_data['impact_level'])
        
        if not updates:
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.extend([user_id, test_id])
        
        cursor.execute(f"""
            UPDATE user_test_cases 
            SET {', '.join(updates)}
            WHERE user_id = ? AND test_id = ?
        """, params)
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_user_test_case(self, user_id: int, test_id: str) -> bool:
        """Deleta um teste personalizado"""
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM user_test_cases 
            WHERE user_id = ? AND test_id = ?
        """, (user_id, test_id))
        self.conn.commit()
        return cursor.rowcount > 0


# Instância global (singleton)
_db_instance: Optional[IARTESDatabase] = None

def get_database(db_path: str = "iartes.db") -> IARTESDatabase:
    """
    Retorna instância do banco de dados (singleton).
    
    Args:
        db_path: Caminho para o arquivo do banco
    
    Returns:
        Instância do banco de dados
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = IARTESDatabase(db_path)
    return _db_instance
