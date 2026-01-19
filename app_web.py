"""
Interface Web Visual para o Sistema de Recomendação de Testes Motorola
Flask + HTML/CSS/JavaScript para interface bonita e moderna
"""
import sys
from pathlib import Path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from flask import Flask, render_template, jsonify, request
from datetime import datetime
import json

from src.models.test_case import ExecutionFeedback
from src.recommender.ml_recommender import MLTestRecommender
from src.utils.database import get_database
from testes_motorola import criar_testes_motorola

app = Flask(__name__)

# Estado global
testes = criar_testes_motorola()
recommender = MLTestRecommender()
db = get_database("iartes.db")  # Banco de dados SQLite

# Configurar encoding UTF-8 para Windows
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Tentar carregar modelo existente
try:
    recommender.load_model("models/motorola_modelo.pkl")
    print("✓ Modelo carregado")
except:
    print("✓ Novo modelo criado")


@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')


@app.route('/api/testes')
def get_testes():
    """Retorna lista de testes"""
    testes_data = []
    for tc in testes:
        composition = tc.get_impact_composition()
        testes_data.append({
            'id': tc.id,
            'name': tc.name,
            'description': tc.description,
            'module': tc.module,
            'priority': tc.priority,
            'num_actions': len(tc.actions),
            'estimated_time': tc.get_total_estimated_time(),
            'is_destructive': tc.has_destructive_actions(),
            'impact_level': tc.get_impact_level(),
            'impact_composition': composition,  # NOVO: composição detalhada
            'tags': list(tc.tags)
        })
    return jsonify(testes_data)


@app.route('/api/recomendacao', methods=['GET', 'POST'])
def get_recomendacao():
    """Gera recomendação de ordenação (para testes selecionados ou todos)"""
    
    # Se for POST, pegar apenas os testes selecionados
    if request.method == 'POST':
        data = request.json
        test_ids = data.get('test_ids', [])
        testes_selecionados = [t for t in testes if t.id in test_ids]
    else:
        # GET: todos os testes
        testes_selecionados = testes
    
    if len(testes_selecionados) == 0:
        return jsonify({
            'error': 'Nenhum teste selecionado',
            'order': [],
            'details': [],
            'total_time': 0,
            'estimated_resets': 0,
            'confidence': 0,
            'method': 'N/A'
        }), 400
    
    recomendacao = recommender.recommend_order(testes_selecionados)
    
    # Detalhes de cada teste na ordem recomendada
    ordem_detalhada = []
    for test_id in recomendacao.recommended_order:
        tc = next((t for t in testes_selecionados if t.id == test_id), None)
        if tc:
            composition = tc.get_impact_composition()
            ordem_detalhada.append({
                'id': tc.id,
                'name': tc.name,
                'module': tc.module,
                'priority': tc.priority,
                'estimated_time': tc.get_total_estimated_time(),
                'is_destructive': tc.has_destructive_actions(),
                'impact_level': tc.get_impact_level(),
                'impact_composition': composition  # NOVO
            })
    
    return jsonify({
        'order': recomendacao.recommended_order,
        'details': ordem_detalhada,
        'total_time': recomendacao.estimated_total_time,
        'estimated_resets': recomendacao.estimated_resets,
        'confidence': recomendacao.confidence_score,
        'method': recomendacao.reasoning.get('method', 'N/A'),
        'training_samples': recomendacao.reasoning.get('training_samples', 0)
    })


@app.route('/api/estatisticas')
def get_estatisticas():
    """Retorna estatísticas do modelo (do banco de dados)"""
    # Estatísticas do banco de dados
    db_stats = db.get_statistics()
    
    # Informações do modelo ML
    stats = {
        'total_feedbacks': db_stats['total_feedbacks'],
        'is_trained': recommender.is_trained,
        'training_samples': len(recommender.training_data.get('y', [])),
        'success_rate': db_stats['success_rate'],
        'avg_rating': db_stats['avg_rating'],
        'resets_count': db_stats['resets_count'],
        'followed_recommendation': db_stats['followed_recommendation_count'],
    }
    
    # Histórico de feedbacks para gráficos (últimos 20)
    recent_feedbacks = db.get_recent_feedbacks(20)
    feedback_history = []
    for i, f in enumerate(recent_feedbacks[::-1], 1):  # Inverter para ordem crescente
        feedback_history.append({
            'index': i,
            'test_id': f['test_case_id'],
            'rating': f['tester_rating'] or 3,
            'time': f['actual_execution_time'],
            'success': bool(f['success'])
        })
    stats['feedback_history'] = feedback_history
    
    return jsonify(stats)


@app.route('/api/feedback', methods=['POST'])
def add_feedback():
    """Adiciona feedback de execução"""
    data = request.json
    
    try:
        # Capturar informações sobre modificação de ordem
        order_modified = data.get('order_was_modified', False)
        original_order = data.get('original_order', [])
        accepted_order = data.get('accepted_order', [])
        
        # Adicionar informação nas notas se ordem foi modificada
        notes = data.get('notes', '')
        if order_modified and original_order and accepted_order:
            modification_note = f"\n[ORDEM MODIFICADA] Original: {' → '.join(original_order[:3])}... | Aceita: {' → '.join(accepted_order[:3])}..."
            notes = (notes or '') + modification_note
        
        feedback = ExecutionFeedback(
            test_case_id=data['test_id'],
            executed_at=datetime.now(),
            actual_execution_time=float(data['actual_time']),
            success=bool(data['success']),
            followed_recommendation=bool(data.get('followed_recommendation', True)),
            tester_rating=int(data['rating']),
            required_reset=bool(data.get('required_reset', False)),
            notes=notes
        )
        
        # Adicionar feedback ao recommender (ML)
        recommender.add_feedback(feedback, testes)
        recommender.save_model("models/motorola_modelo.pkl")
        
        # Salvar feedback no banco de dados SQLite
        feedback_dict = {
            'test_case_id': feedback.test_case_id,
            'executed_at': feedback.executed_at.isoformat(),
            'actual_execution_time': feedback.actual_execution_time,
            'success': feedback.success,
            'followed_recommendation': feedback.followed_recommendation,
            'tester_rating': feedback.tester_rating,
            'required_reset': feedback.required_reset,
            'notes': feedback.notes,
            'initial_state': feedback.initial_state,
            'final_state': feedback.final_state
        }
        db.add_feedback(feedback_dict)
        
        return jsonify({
            'status': 'success',
            'message': 'Feedback registrado com sucesso!',
            'total_feedbacks': len(recommender.feedback_history),
            'is_trained': recommender.is_trained
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


@app.route('/api/modulos')
def get_modulos():
    """Retorna estatísticas por módulo"""
    modulos = {}
    for tc in testes:
        if tc.module not in modulos:
            modulos[tc.module] = {
                'name': tc.module,
                'count': 0,
                'total_time': 0,
                'avg_priority': 0,
                'priorities': []
            }
        modulos[tc.module]['count'] += 1
        modulos[tc.module]['total_time'] += tc.get_total_estimated_time()
        modulos[tc.module]['priorities'].append(tc.priority)
    
    # Calcular média de prioridade
    for mod in modulos.values():
        mod['avg_priority'] = sum(mod['priorities']) / len(mod['priorities'])
        del mod['priorities']
    
    return jsonify(list(modulos.values()))


if __name__ == '__main__':
    print("=" * 80)
    print("🚀 INICIANDO INTERFACE WEB - SISTEMA DE RECOMENDAÇÃO MOTOROLA")
    print("=" * 80)
    print()
    print(f"📱 {len(testes)} testes carregados")
    print(f"🤖 Modelo: {'Treinado' if recommender.is_trained else 'Não treinado'}")
    print(f"📊 Feedbacks: {len(recommender.feedback_history)}")
    print()
    print("🌐 Acesse: http://localhost:5000")
    print()
    print("Pressione Ctrl+C para parar")
    print("=" * 80)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
