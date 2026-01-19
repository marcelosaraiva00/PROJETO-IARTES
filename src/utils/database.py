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
        
        # Tabela de feedbacks de execução
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedbacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                test_case_id, executed_at, actual_execution_time,
                success, followed_recommendation, tester_rating,
                required_reset, notes, initial_state, final_state
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
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
