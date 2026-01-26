"""
Interface Web Visual para o Sistema de Recomendação de Testes Motorola
Flask + HTML/CSS/JavaScript para interface bonita e moderna
"""
import sys
from pathlib import Path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from flask import Flask, render_template, jsonify, request, session, redirect, url_for, send_file
from datetime import datetime
from typing import Dict, Any, List
import json
import hashlib
import secrets
import io
import os
from werkzeug.utils import secure_filename
from pathlib import Path

from src.models.test_case import ExecutionFeedback, TestCase, Action, ActionType, ActionImpact
from src.recommender.personalized_recommender import PersonalizedMLRecommender
from src.recommender.explainability import RecommendationExplainer
from src.recommender.anomaly_detector import AnomalyDetector
from src.utils.database import get_database
from src.utils.notification_manager import NotificationManager
from src.utils.report_generator import ReportGenerator
from testes_motorola import criar_testes_motorola

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Chave secreta para sessões

# Configurações de upload
UPLOAD_FOLDER = Path('static/uploads/profiles')
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Estado global
testes = criar_testes_motorola()
recommender = PersonalizedMLRecommender()  # NOVO: Recomendador personalizado
db = get_database("iartes.db")  # Banco de dados SQLite

# Sistemas avançados de IA
explainer = None  # Será inicializado quando modelo estiver treinado
anomaly_detector = AnomalyDetector(contamination=0.1)
notification_manager = NotificationManager(db)
report_generator = ReportGenerator(db)

# Configurar encoding UTF-8 para Windows
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Modelo global será carregado automaticamente pelo PersonalizedMLRecommender
print("✓ Sistema de recomendação personalizado inicializado")


# ==================== FUNÇÕES AUXILIARES ====================

def _generate_basic_explanation(test_cases: List[TestCase], recommended_order: List[str]):
    """Gera explicação básica baseada em heurísticas quando modelo não está treinado"""
    test_dict = {tc.id: tc for tc in test_cases}
    ordered_tests = [test_dict[tid] for tid in recommended_order if tid in test_dict]
    
    if not ordered_tests:
        return None
    
    factors = []
    reasoning = []
    
    # Fator 1: Agrupamento por módulo
    module_groups = 1
    for i in range(1, len(ordered_tests)):
        if ordered_tests[i].module != ordered_tests[i-1].module:
            module_groups += 1
    
    if module_groups < len(ordered_tests):
        factors.append({
            'name': 'Agrupamento por Módulo',
            'description': f'Testes agrupados em {module_groups} blocos por módulo',
            'impact': 'positive',
            'value': module_groups,
            'reason': 'Reduz mudança de contexto e melhora eficiência'
        })
        reasoning.append(f"Os testes foram organizados em {module_groups} grupos por módulo para reduzir mudanças de contexto.")
    
    # Fator 2: Priorização
    high_priority = [tc for tc in ordered_tests[:5] if tc.priority >= 4]
    if high_priority:
        factors.append({
            'name': 'Priorização',
            'description': f'{len(high_priority)} testes de alta prioridade executados primeiro',
            'impact': 'positive',
            'value': len(high_priority),
            'reason': 'Garante que testes críticos sejam executados cedo'
        })
        reasoning.append(f"{len(high_priority)} testes de alta prioridade foram posicionados no início da sequência.")
    
    # Fator 3: Ações destrutivas
    destructive_tests = [tc for tc in ordered_tests if tc.has_destructive_actions()]
    if destructive_tests:
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
            reasoning.append(f"Os {len(destructive_tests)} testes destrutivos foram posicionados no final para minimizar resets.")
    
    # Fator 4: Tempo total
    total_time = sum(tc.get_total_estimated_time() for tc in ordered_tests)
    factors.append({
        'name': 'Tempo Total Estimado',
        'description': f'{total_time:.0f} segundos estimados',
        'impact': 'neutral',
        'value': total_time,
        'reason': 'Tempo total de execução da suíte'
    })
    
    if not reasoning:
        reasoning.append("A ordem foi organizada para otimizar a execução dos testes.")
    
    return {
        'recommended_order': recommended_order,
        'factors': factors,
        'feature_importance': {},  # Vazio quando modelo não está treinado
        'test_scores': {},
        'comparison_with_alternatives': None,
        'reasoning': reasoning
    }

def hash_password(password: str) -> str:
    """Gera hash SHA-256 da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """Verifica se a senha corresponde ao hash"""
    return hash_password(password) == password_hash

def login_required(f):
    """Decorator para proteger rotas que requerem login"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Login necessário', 'redirect': '/login'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROTAS DE AUTENTICAÇÃO ====================

@app.route('/')
def index():
    """Página principal - redireciona para login se não autenticado"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('index.html')

@app.route('/login')
def login_page():
    """Página de login"""
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register')
def register_page():
    """Página de registro"""
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/api/login', methods=['POST'])
def login():
    """Endpoint de login"""
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'error': 'Username e senha são obrigatórios'}), 400
    
    user = db.get_user_by_username(username)
    if not user or not verify_password(password, user['password_hash']):
        return jsonify({'error': 'Usuário ou senha incorretos'}), 401
    
    # Criar sessão
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['full_name'] = user.get('full_name') or user['username']
    session['role'] = user.get('role', 'tester')
    
    # Atualizar último login
    db.update_last_login(user['id'])
    
    return jsonify({
        'status': 'success',
        'message': 'Login realizado com sucesso',
        'user': {
            'id': user['id'],
            'username': user['username'],
            'full_name': session['full_name'],
            'role': session['role']
        }
    })

@app.route('/api/register', methods=['POST'])
def register():
    """Endpoint de registro"""
    data = request.json or {}
    username = str(data.get('username', '') or '').strip()
    password = str(data.get('password', '') or '')
    email = str(data.get('email', '') or '').strip() or None
    full_name = str(data.get('full_name', '') or '').strip() or None
    experience_level = str(data.get('experience_level', 'beginner') or '').strip()
    
    if not username or not password:
        return jsonify({'error': 'Username e senha são obrigatórios'}), 400
    
    if len(password) < 4:
        return jsonify({'error': 'Senha deve ter pelo menos 4 caracteres'}), 400
    
    # Validar nível de experiência
    valid_levels = ['beginner', 'intermediate', 'advanced', 'expert']
    if experience_level not in valid_levels:
        experience_level = 'beginner'
    
    try:
        password_hash = hash_password(password)
        user_id = db.create_user(username, password_hash, email, full_name, 
                                experience_level=experience_level)
        
        # Login automático após registro
        session['user_id'] = user_id
        session['username'] = username
        session['full_name'] = full_name or username
        session['role'] = 'tester'
        session['experience_level'] = experience_level
        
        return jsonify({
            'status': 'success',
            'message': 'Usuário criado com sucesso',
            'user': {
                'id': user_id,
                'username': username,
                'full_name': session['full_name'],
                'experience_level': experience_level
            }
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/logout', methods=['POST'])
def logout():
    """Endpoint de logout"""
    session.clear()
    return jsonify({'status': 'success', 'message': 'Logout realizado com sucesso'})

@app.route('/api/user/current')
def get_current_user():
    """Retorna informações do usuário atual"""
    if 'user_id' not in session:
        return jsonify({'authenticated': False}), 401
    
    user = db.get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return jsonify({'authenticated': False}), 401
    
    return jsonify({
        'authenticated': True,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'full_name': session.get('full_name', user['username']),
            'role': session.get('role', 'tester'),
            'experience_level': user.get('experience_level', 'beginner')
        }
    })


@app.route('/api/testes')
@login_required
def get_testes():
    """
    Retorna lista de testes com suporte a filtros e busca avançada
    Inclui testes padrão e testes personalizados do usuário
    
    Query parameters:
    - search: Busca por ID, nome ou descrição
    - module: Filtrar por módulo
    - priority: Filtrar por prioridade (min)
    - impact_level: Filtrar por nível de impacto (destructive, partially_destructive, non_destructive)
    - min_time: Tempo mínimo estimado
    - max_time: Tempo máximo estimado
    - tags: Filtrar por tags (separadas por vírgula)
    - sort_by: Ordenar por (id, name, module, priority, estimated_time)
    - sort_order: Ordem (asc, desc)
    """
    user_id = session.get('user_id')
    
    # Obter parâmetros de busca e filtro
    search = request.args.get('search', '').strip().lower()
    module_filter = request.args.get('module', '').strip()
    priority_filter = request.args.get('priority', type=int)
    impact_filter = request.args.get('impact_level', '').strip()
    min_time = request.args.get('min_time', type=float)
    max_time = request.args.get('max_time', type=float)
    tags_filter = request.args.get('tags', '').strip()
    sort_by = request.args.get('sort_by', 'id').strip()
    sort_order = request.args.get('sort_order', 'asc').strip().lower()
    
    # Obter todos os testes disponíveis (padrão + personalizados)
    user_id = session.get('user_id')
    all_available_tests = get_all_test_cases(user_id)
    
    # Converter lista de testes para dicionários
    # get_all_test_cases() já inclui testes personalizados, então não precisamos adicionar novamente
    testes_data = []
    user_test_ids = set()  # Para identificar quais são personalizados
    
    # Obter IDs dos testes personalizados para marcar
    if user_id:
        user_tests = db.get_user_test_cases(user_id)
        user_test_ids = {ut['test_id'] for ut in user_tests}
    
    for tc in all_available_tests:
        composition = tc.get_impact_composition()
        test_data = {
            'id': tc.id,
            'name': tc.name,
            'description': tc.description,
            'module': tc.module,
            'priority': tc.priority,
            'num_actions': len(tc.actions),
            'estimated_time': tc.get_total_estimated_time(),
            'is_destructive': tc.has_destructive_actions(),
            'impact_level': tc.get_impact_level(),
            'impact_composition': composition,
            'tags': list(tc.tags),
            'is_custom': tc.id in user_test_ids  # Marca como teste personalizado
        }
        testes_data.append(test_data)
    
    # Aplicar filtros
    filtered_tests = []
    for test in testes_data:
        # Busca por texto
        if search:
            search_match = (
                search in test['id'].lower() or
                search in test['name'].lower() or
                search in test['description'].lower() or
                search in test['module'].lower()
            )
            if not search_match:
                continue
        
        # Filtro por módulo
        if module_filter and test['module'] != module_filter:
            continue
        
        # Filtro por prioridade
        if priority_filter is not None and test['priority'] < priority_filter:
            continue
        
        # Filtro por impacto
        if impact_filter and test['impact_level'] != impact_filter:
            continue
        
        # Filtro por tempo
        if min_time is not None and test['estimated_time'] < min_time:
            continue
        if max_time is not None and test['estimated_time'] > max_time:
            continue
        
        # Filtro por tags
        if tags_filter:
            required_tags = [t.strip().lower() for t in tags_filter.split(',')]
            test_tags = [t.lower() for t in test['tags']]
            if not all(tag in test_tags for tag in required_tags):
                continue
        
        filtered_tests.append(test)
    
    # Ordenação
    valid_sort_fields = ['id', 'name', 'module', 'priority', 'estimated_time']
    if sort_by not in valid_sort_fields:
        sort_by = 'id'
    
    reverse_order = sort_order == 'desc'
    
    if sort_by == 'id':
        filtered_tests.sort(key=lambda x: x['id'], reverse=reverse_order)
    elif sort_by == 'name':
        filtered_tests.sort(key=lambda x: x['name'].lower(), reverse=reverse_order)
    elif sort_by == 'module':
        filtered_tests.sort(key=lambda x: (x['module'], x['id']), reverse=reverse_order)
    elif sort_by == 'priority':
        filtered_tests.sort(key=lambda x: (x['priority'], x['id']), reverse=reverse_order)
    elif sort_by == 'estimated_time':
        filtered_tests.sort(key=lambda x: x['estimated_time'], reverse=reverse_order)
    
    return jsonify({
        'tests': filtered_tests,
        'total': len(filtered_tests),
        'filters_applied': {
            'search': search,
            'module': module_filter,
            'priority': priority_filter,
            'impact_level': impact_filter,
            'min_time': min_time,
            'max_time': max_time,
            'tags': tags_filter,
            'sort_by': sort_by,
            'sort_order': sort_order
        }
    })

@app.route('/api/testes/search')
@login_required
def search_testes():
    """
    Endpoint específico para busca avançada de testes
    Suporta busca por múltiplos critérios simultaneamente
    """
    data = request.json or {}
    
    search = data.get('search', '').strip().lower()
    modules = data.get('modules', [])  # Lista de módulos
    priority_min = data.get('priority_min', None)
    priority_max = data.get('priority_max', None)
    impact_levels = data.get('impact_levels', [])  # Lista de níveis
    time_range = data.get('time_range', {})  # {min, max}
    tags = data.get('tags', [])  # Lista de tags
    sort_by = data.get('sort_by', 'id')
    sort_order = data.get('sort_order', 'asc')
    
    # Obter todos os testes disponíveis (padrão + personalizados)
    user_id = session.get('user_id')
    all_available_tests = get_all_test_cases(user_id)
    
    # Converter lista de testes para dicionários
    testes_data = []
    for tc in all_available_tests:
        composition = tc.get_impact_composition()
        test_data = {
            'id': tc.id,
            'name': tc.name,
            'description': tc.description,
            'module': tc.module,
            'priority': tc.priority,
            'num_actions': len(tc.actions),
            'estimated_time': tc.get_total_estimated_time(),
            'is_destructive': tc.has_destructive_actions(),
            'impact_level': tc.get_impact_level(),
            'impact_composition': composition,
            'tags': list(tc.tags)
        }
        testes_data.append(test_data)
    
    # Aplicar filtros
    filtered_tests = []
    for test in testes_data:
        # Busca por texto
        if search:
            search_match = (
                search in test['id'].lower() or
                search in test['name'].lower() or
                search in test['description'].lower() or
                search in test['module'].lower()
            )
            if not search_match:
                continue
        
        # Filtro por módulos (múltiplos)
        if modules and test['module'] not in modules:
            continue
        
        # Filtro por prioridade (range)
        if priority_min is not None and test['priority'] < priority_min:
            continue
        if priority_max is not None and test['priority'] > priority_max:
            continue
        
        # Filtro por níveis de impacto (múltiplos)
        if impact_levels and test['impact_level'] not in impact_levels:
            continue
        
        # Filtro por tempo (range)
        if time_range.get('min') is not None and test['estimated_time'] < time_range['min']:
            continue
        if time_range.get('max') is not None and test['estimated_time'] > time_range['max']:
            continue
        
        # Filtro por tags (múltiplas)
        if tags:
            test_tags = [t.lower() for t in test['tags']]
            if not any(tag.lower() in test_tags for tag in tags):
                continue
        
        filtered_tests.append(test)
    
    # Ordenação
    valid_sort_fields = ['id', 'name', 'module', 'priority', 'estimated_time']
    if sort_by not in valid_sort_fields:
        sort_by = 'id'
    
    reverse_order = sort_order == 'desc'
    
    if sort_by == 'id':
        filtered_tests.sort(key=lambda x: x['id'], reverse=reverse_order)
    elif sort_by == 'name':
        filtered_tests.sort(key=lambda x: x['name'].lower(), reverse=reverse_order)
    elif sort_by == 'module':
        filtered_tests.sort(key=lambda x: (x['module'], x['id']), reverse=reverse_order)
    elif sort_by == 'priority':
        filtered_tests.sort(key=lambda x: (x['priority'], x['id']), reverse=reverse_order)
    elif sort_by == 'estimated_time':
        filtered_tests.sort(key=lambda x: x['estimated_time'], reverse=reverse_order)
    
    return jsonify({
        'tests': filtered_tests,
        'total': len(filtered_tests),
        'filters': data
    })

@app.route('/api/testes/filters/options')
@login_required
def get_filter_options():
    """Retorna opções disponíveis para filtros"""
    user_id = session.get('user_id')
    all_tests = get_all_test_cases(user_id)
    
    modules = sorted(set(tc.module for tc in all_tests))
    priorities = sorted(set(tc.priority for tc in all_tests))
    impact_levels = ['destructive', 'partially_destructive', 'non_destructive']
    
    # Coletar todas as tags
    all_tags = set()
    for tc in all_tests:
        all_tags.update(tc.tags)
    tags = sorted(list(all_tags))
    
    # Estatísticas de tempo
    times = [tc.get_total_estimated_time() for tc in all_tests]
    min_time = min(times) if times else 0
    max_time = max(times) if times else 0
    
    return jsonify({
        'modules': modules,
        'priorities': priorities,
        'impact_levels': impact_levels,
        'tags': tags,
        'time_range': {
            'min': min_time,
            'max': max_time
        }
    })


@app.route('/api/recomendacao', methods=['GET', 'POST'])
@login_required
def get_recomendacao():
    """Gera recomendação de ordenação (para testes selecionados ou todos)"""
    
    # Obter ID do usuário logado
    user_id = session.get('user_id')
    
    # Obter todos os testes disponíveis (padrão + personalizados)
    all_available_tests = get_all_test_cases(user_id)
    
    # Se for POST, pegar apenas os testes selecionados
    if request.method == 'POST':
        data = request.json
        test_ids = data.get('test_ids', [])
        testes_selecionados = [t for t in all_available_tests if t.id in test_ids]
    else:
        # GET: todos os testes
        testes_selecionados = all_available_tests
    
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
    
    # Obter nível de experiência do usuário
    cursor = db.conn.cursor()
    cursor.execute("SELECT experience_level FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    experience_level = row['experience_level'] if row else 'beginner'
    
    # O peso será calculado automaticamente baseado no nível de experiência
    recomendacao = recommender.recommend_order(
        user_id=user_id,
        test_cases=testes_selecionados,
        db=db,
        experience_level=experience_level
    )
    
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
    
    # Gerar explicação da recomendação
    explanation = None
    global explainer
    
    try:
        if recommender.global_recommender.is_trained:
            # Modelo treinado: usar explicação completa
            if explainer is None or not hasattr(explainer, 'model'):
                explainer = RecommendationExplainer(
                    recommender.global_recommender.model,
                    recommender.global_recommender.feature_extractor
                )
            
            explanation = explainer.explain_recommendation(
                testes_selecionados,
                recomendacao.recommended_order
            )
        else:
            # Modelo não treinado: gerar explicação básica baseada em heurísticas
            explanation = _generate_basic_explanation(
                testes_selecionados,
                recomendacao.recommended_order
            )
    except Exception as e:
        print(f"Erro ao gerar explicação: {e}")
        import traceback
        traceback.print_exc()
        # Mesmo com erro, tentar explicação básica
        try:
            explanation = _generate_basic_explanation(
                testes_selecionados,
                recomendacao.recommended_order
            )
        except:
            pass
    
    return jsonify({
        'order': recomendacao.recommended_order,
        'details': ordem_detalhada,
        'total_time': recomendacao.estimated_total_time,
        'estimated_resets': recomendacao.estimated_resets,
        'confidence': recomendacao.confidence_score,
        'method': recomendacao.reasoning.get('method', 'N/A'),
        'training_samples': recomendacao.reasoning.get('training_samples', 0),
        'explanation': explanation  # NOVO: Explicação da IA
    })


@app.route('/api/estatisticas')
@login_required
def get_estatisticas():
    """Retorna estatísticas do modelo (do banco de dados)"""
    # Estatísticas do banco de dados
    db_stats = db.get_statistics()
    
    # Informações do modelo ML global
    user_id = session.get('user_id')
    user_stats = None
    personal_training_samples = 0
    
    if user_id:
        # Buscar estatísticas do usuário
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT * FROM user_learning_stats WHERE user_id = ?
        """, (user_id,))
        row = cursor.fetchone()
        if row:
            user_stats = dict(row)
        
        # Buscar modelo personalizado
        cursor.execute("""
            SELECT training_samples FROM user_models WHERE user_id = ?
        """, (user_id,))
        row = cursor.fetchone()
        if row:
            personal_training_samples = row['training_samples'] or 0
    
    stats = {
        'total_feedbacks': db_stats['total_feedbacks'],
        'is_trained': recommender.global_recommender.is_trained,
        'training_samples': len(recommender.global_recommender.training_data.get('y', [])),
        'success_rate': db_stats['success_rate'],
        'avg_rating': db_stats['avg_rating'],
        'resets_count': db_stats['resets_count'],
        'followed_recommendation': db_stats['followed_recommendation_count'],
        'user_stats': user_stats,
        'personal_training_samples': personal_training_samples
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
@login_required
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
        
        # Obter ordem de execução (aceita pelo usuário)
        # Incluir testes padrão e personalizados
        user_id = session.get('user_id')
        all_available_tests = get_all_test_cases(user_id)
        accepted_order_ids = data.get('accepted_order', [])
        accepted_order = [t for t in all_available_tests if t.id in accepted_order_ids]
        
        # Adicionar feedback ao recommender (ML global + personalizado)
        # user_id já foi obtido acima
        recommender.add_feedback(
            user_id=user_id,
            feedback=feedback,
            test_order=accepted_order,
            db=db
        )
        
        # Atualizar estatísticas de aprendizado do usuário
        if user_id:
            recommender.update_user_learning_stats(user_id, db)
        
        # Salvar feedback no banco de dados SQLite (com tester_id)
        feedback_dict = {
            'tester_id': session.get('user_id'),  # NOVO: ID do testador
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
        
        # Obter estatísticas do usuário
        user_id = session.get('user_id')
        user_stats = None
        if user_id:
            cursor = db.conn.cursor()
            cursor.execute("""
                SELECT * FROM user_learning_stats WHERE user_id = ?
            """, (user_id,))
            row = cursor.fetchone()
            if row:
                user_stats = dict(row)
            
            # Verificar e criar notificações automáticas
            try:
                notification_manager.check_all_user_alerts(user_id)
            except Exception as e:
                print(f"Erro ao verificar alertas: {e}")
        
        return jsonify({
            'status': 'success',
            'message': 'Feedback registrado com sucesso!',
            'total_feedbacks': len(recommender.global_recommender.feedback_history),
            'is_trained': recommender.global_recommender.is_trained,
            'user_stats': user_stats
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


@app.route('/api/modulos')
@login_required
def get_modulos():
    """Retorna estatísticas por módulo"""
    user_id = session.get('user_id')
    all_tests = get_all_test_cases(user_id)
    
    modulos = {}
    for tc in all_tests:
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

@app.route('/api/user/stats')
@login_required
def get_user_stats():
    """Retorna estatísticas de aprendizado do usuário atual"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    cursor = db.conn.cursor()
    
    # Buscar estatísticas do usuário
    cursor.execute("""
        SELECT * FROM user_learning_stats WHERE user_id = ?
    """, (user_id,))
    row = cursor.fetchone()
    
    if row:
        stats = dict(row)
    else:
        stats = {
            'total_feedbacks': 0,
            'avg_rating': 0.0,
            'success_rate': 0.0,
            'avg_execution_time': 0.0,
            'preferred_modules': None
        }
    
    # Buscar informações do modelo personalizado
    cursor.execute("""
        SELECT training_samples, last_trained FROM user_models WHERE user_id = ?
    """, (user_id,))
    model_row = cursor.fetchone()
    
    if model_row:
        stats['personal_model'] = {
            'training_samples': model_row['training_samples'] or 0,
            'last_trained': model_row['last_trained']
        }
    else:
        stats['personal_model'] = {
            'training_samples': 0,
            'last_trained': None
        }
    
    return jsonify(stats)

@app.route('/api/user/feedbacks')
@login_required
def get_user_feedbacks():
    """Retorna histórico de feedbacks do usuário atual"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    cursor = db.conn.cursor()
    
    # Buscar feedbacks do usuário (últimos 50)
    cursor.execute("""
        SELECT 
            test_case_id,
            executed_at,
            actual_execution_time,
            success,
            tester_rating,
            required_reset,
            notes
        FROM feedbacks
        WHERE tester_id = ?
        ORDER BY executed_at DESC
        LIMIT 50
    """, (user_id,))
    
    feedbacks = []
    for row in cursor.fetchall():
        feedbacks.append({
            'test_case_id': row['test_case_id'],
            'executed_at': row['executed_at'],
            'actual_execution_time': row['actual_execution_time'],
            'success': bool(row['success']),
            'tester_rating': row['tester_rating'],
            'required_reset': bool(row['required_reset']),
            'notes': row['notes']
        })
    
    return jsonify(feedbacks)

@app.route('/api/explain/<test_ids>')
@login_required
def explain_recommendation(test_ids):
    """Explica uma recomendação específica"""
    user_id = session.get('user_id')
    all_available_tests = get_all_test_cases(user_id)
    
    test_id_list = test_ids.split(',')
    testes_selecionados = [t for t in all_available_tests if t.id in test_id_list]
    
    if not testes_selecionados:
        return jsonify({'error': 'Testes não encontrados'}), 404
    
    # Obter recomendação
    user_id = session.get('user_id')
    cursor = db.conn.cursor()
    cursor.execute("SELECT experience_level FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    experience_level = row['experience_level'] if row else 'beginner'
    
    recomendacao = recommender.recommend_order(
        user_id=user_id,
        test_cases=testes_selecionados,
        db=db,
        experience_level=experience_level
    )
    
    # Gerar explicação
    global explainer
    if recommender.global_recommender.is_trained:
        if explainer is None or not hasattr(explainer, 'model'):
            explainer = RecommendationExplainer(
                recommender.global_recommender.model,
                recommender.global_recommender.feature_extractor
            )
        
        try:
            explanation = explainer.explain_recommendation(
                testes_selecionados,
                recomendacao.recommended_order
            )
            return jsonify(explanation)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Modelo não treinado ainda'}), 400

@app.route('/api/anomalies')
@login_required
def get_anomalies():
    """Detecta anomalias nos feedbacks do usuário"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    cursor = db.conn.cursor()
    
    # Buscar feedbacks do usuário
    cursor.execute("""
        SELECT 
            test_case_id,
            executed_at,
            actual_execution_time,
            success,
            tester_rating,
            required_reset,
            followed_recommendation
        FROM feedbacks
        WHERE tester_id = ?
        ORDER BY executed_at DESC
        LIMIT 100
    """, (user_id,))
    
    rows = cursor.fetchall()
    
    # Converter para ExecutionFeedback
    feedbacks = []
    test_dict = {tc.id: tc for tc in testes}
    
    for row in rows:
        feedback = ExecutionFeedback(
            test_case_id=row['test_case_id'],
            executed_at=datetime.fromisoformat(row['executed_at']),
            actual_execution_time=row['actual_execution_time'],
            success=bool(row['success']),
            tester_rating=row['tester_rating'],
            required_reset=bool(row['required_reset']),
            followed_recommendation=bool(row['followed_recommendation'])
        )
        feedbacks.append(feedback)
    
    # Detectar anomalias
    anomalies_result = anomaly_detector.detect_anomalies(feedbacks, test_dict)
    
    return jsonify(anomalies_result)

@app.route('/api/feature-importance')
@login_required
def get_feature_importance():
    """Retorna importância das features do modelo"""
    global explainer
    
    if not recommender.global_recommender.is_trained:
        return jsonify({'error': 'Modelo não treinado'}), 400
    
    if explainer is None or not hasattr(explainer, 'model'):
        explainer = RecommendationExplainer(
            recommender.global_recommender.model,
            recommender.global_recommender.feature_extractor
        )
    
    try:
        importance = explainer._get_feature_importance()
        return jsonify(importance)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== NOTIFICAÇÕES ====================

@app.route('/api/notifications')
@login_required
def get_notifications():
    """Retorna notificações do usuário"""
    user_id = session.get('user_id')
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    limit = request.args.get('limit', type=int)
    
    notifications = db.get_user_notifications(
        user_id=user_id,
        unread_only=unread_only,
        limit=limit
    )
    
    return jsonify(notifications)

@app.route('/api/notifications/unread-count')
@login_required
def get_unread_count():
    """Retorna contagem de notificações não lidas"""
    user_id = session.get('user_id')
    count = db.get_unread_count(user_id)
    return jsonify({'count': count})

@app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Marca uma notificação como lida"""
    user_id = session.get('user_id')
    db.mark_notification_read(notification_id, user_id)
    return jsonify({'status': 'success'})

@app.route('/api/notifications/read-all', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Marca todas as notificações como lidas"""
    user_id = session.get('user_id')
    db.mark_all_notifications_read(user_id)
    return jsonify({'status': 'success'})

# ==================== ANOTAÇÕES (POST-ITS) ====================

@app.route('/api/notes', methods=['GET'])
@login_required
def get_notes():
    """Retorna todas as anotações do usuário"""
    user_id = session.get('user_id')
    notes = db.get_user_notes(user_id)
    return jsonify({'notes': notes})

@app.route('/api/notes', methods=['POST'])
@login_required
def create_note():
    """Cria uma nova anotação"""
    user_id = session.get('user_id')
    data = request.json or {}
    
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Título é obrigatório'}), 400
    
    content = data.get('content', '').strip()
    column_name = data.get('column_name', 'todo')
    color = data.get('color', 'yellow')
    
    note_id = db.create_note(user_id, title, content, column_name, color)
    return jsonify({
        'status': 'success',
        'note_id': note_id
    })

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
@login_required
def update_note(note_id):
    """Atualiza uma anotação"""
    user_id = session.get('user_id')
    data = request.json or {}
    
    success = db.update_note(
        note_id=note_id,
        user_id=user_id,
        title=data.get('title'),
        content=data.get('content'),
        column_name=data.get('column_name'),
        color=data.get('color'),
        position=data.get('position')
    )
    
    if not success:
        return jsonify({'error': 'Anotação não encontrada'}), 404
    
    return jsonify({'status': 'success'})

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    """Deleta uma anotação"""
    user_id = session.get('user_id')
    success = db.delete_note(note_id, user_id)
    
    if not success:
        return jsonify({'error': 'Anotação não encontrada'}), 404
    
    return jsonify({'status': 'success'})

@app.route('/api/notes/positions', methods=['PUT'])
@login_required
def update_note_positions():
    """Atualiza posições de múltiplas anotações (drag and drop)"""
    user_id = session.get('user_id')
    data = request.json or {}
    
    column_name = data.get('column_name')
    note_positions = data.get('positions', [])  # Lista de [(note_id, position), ...]
    
    if not column_name or not note_positions:
        return jsonify({'error': 'Dados inválidos'}), 400
    
    success = db.update_note_positions(user_id, column_name, note_positions)
    
    if not success:
        return jsonify({'error': 'Erro ao atualizar posições'}), 500
    
    return jsonify({'status': 'success'})

# ==================== TESTES PERSONALIZADOS ====================

def convert_user_test_to_testcase(user_test: Dict) -> TestCase:
    """Converte um teste personalizado do banco em objeto TestCase"""
    actions = []
    actions_data = user_test.get('actions', [])
    
    # Se não há ações, criar uma ação padrão
    if not actions_data:
        actions_data = [{
            'id': 'action-0',
            'description': user_test.get('description', user_test.get('name', 'Executar teste')),
            'action_type': 'verification',
            'impact': user_test.get('impact_level', 'non_destructive'),
            'estimated_time': user_test.get('estimated_time', 5.0),
            'preconditions': [],
            'postconditions': [],
            'priority': 1,
            'tags': []
        }]
    
    for idx, action_data in enumerate(actions_data):
        # Garantir que action_data seja um dicionário
        if isinstance(action_data, str):
            try:
                import json
                action_data = json.loads(action_data)
            except:
                action_data = {'description': action_data}
        
        action = Action(
            id=action_data.get('id', f'action-{idx}'),
            description=action_data.get('description', ''),
            action_type=ActionType(action_data.get('action_type', 'verification')),
            impact=ActionImpact(action_data.get('impact', 'non_destructive')),
            preconditions=set(action_data.get('preconditions', [])),
            postconditions=set(action_data.get('postconditions', [])),
            estimated_time=float(action_data.get('estimated_time', 5.0)),
            priority=int(action_data.get('priority', 1)),
            tags=set(action_data.get('tags', []))
        )
        actions.append(action)
    
    test_case = TestCase(
        id=user_test['test_id'],
        name=user_test['name'],
        description=user_test.get('description', ''),
        actions=actions,
        priority=int(user_test.get('priority', 3)),
        module=user_test.get('module', 'Personalizado'),
        tags=set(user_test.get('tags', []))
    )
    return test_case

def get_all_test_cases(user_id: int = None) -> List[TestCase]:
    """
    Retorna todos os testes disponíveis (padrão + personalizados do usuário)
    Evita duplicação: se um teste personalizado tiver o mesmo ID de um teste padrão,
    o teste personalizado tem prioridade.
    
    Args:
        user_id: ID do usuário (opcional, se None retorna apenas testes padrão)
    
    Returns:
        Lista de objetos TestCase sem duplicações
    """
    # Criar dicionário para evitar duplicações (test_id -> TestCase)
    tests_dict = {}
    
    # Primeiro, adicionar todos os testes padrão
    for test in testes:
        tests_dict[test.id] = test
    
    # Depois, adicionar/sobrescrever com testes personalizados do usuário
    if user_id:
        user_tests = db.get_user_test_cases(user_id)
        for user_test in user_tests:
            try:
                test_case = convert_user_test_to_testcase(user_test)
                # Sobrescrever se já existir (teste personalizado tem prioridade)
                tests_dict[test_case.id] = test_case
            except Exception as e:
                print(f"Erro ao converter teste personalizado {user_test.get('test_id')}: {e}")
                import traceback
                traceback.print_exc()
                continue
    
    # Retornar lista sem duplicações
    return list(tests_dict.values())

@app.route('/api/user/test-cases', methods=['GET'])
@login_required
def get_user_test_cases():
    """Retorna todos os testes personalizados do usuário"""
    user_id = session.get('user_id')
    user_tests = db.get_user_test_cases(user_id)
    return jsonify({'test_cases': user_tests})

@app.route('/api/user/test-cases', methods=['POST'])
@login_required
def create_user_test_case():
    """Cria um novo teste personalizado"""
    user_id = session.get('user_id')
    data = request.json or {}
    
    # Validações
    test_id = data.get('test_id', '').strip()
    name = data.get('name', '').strip()
    
    if not test_id:
        return jsonify({'error': 'ID do teste é obrigatório'}), 400
    if not name:
        return jsonify({'error': 'Nome do teste é obrigatório'}), 400
    
    # Verificar se já existe
    existing = db.get_user_test_case(user_id, test_id)
    if existing:
        return jsonify({'error': 'Já existe um teste com este ID'}), 400
    
    # Preparar dados
    test_data = {
        'test_id': test_id,
        'name': name,
        'description': data.get('description', '').strip(),
        'module': data.get('module', '').strip(),
        'priority': int(data.get('priority', 3)),
        'tags': data.get('tags', []),
        'actions': data.get('actions', []),
        'estimated_time': float(data.get('estimated_time', 0.0)),
        'impact_level': data.get('impact_level', 'non_destructive')
    }
    
    # Calcular tempo estimado se não fornecido
    if test_data['estimated_time'] == 0.0 and test_data['actions']:
        test_data['estimated_time'] = sum(
            action.get('estimated_time', 5.0) 
            for action in test_data['actions']
        )
    
    # Criar teste
    db.create_user_test_case(user_id, test_data)
    
    return jsonify({'status': 'success', 'message': 'Teste criado com sucesso'})

@app.route('/api/user/test-cases/<test_id>', methods=['GET'])
@login_required
def get_user_test_case(test_id):
    """Retorna um teste personalizado específico"""
    user_id = session.get('user_id')
    test = db.get_user_test_case(user_id, test_id)
    
    if not test:
        return jsonify({'error': 'Teste não encontrado'}), 404
    
    return jsonify({'test_case': test})

@app.route('/api/user/test-cases/<test_id>', methods=['PUT'])
@login_required
def update_user_test_case(test_id):
    """Atualiza um teste personalizado"""
    user_id = session.get('user_id')
    data = request.json or {}
    
    # Preparar dados de atualização
    update_data = {}
    if 'name' in data:
        update_data['name'] = data['name'].strip()
    if 'description' in data:
        update_data['description'] = data['description'].strip()
    if 'module' in data:
        update_data['module'] = data['module'].strip()
    if 'priority' in data:
        update_data['priority'] = int(data['priority'])
    if 'tags' in data:
        update_data['tags'] = data['tags']
    if 'actions' in data:
        update_data['actions'] = data['actions']
        # Recalcular tempo estimado
        if data['actions']:
            update_data['estimated_time'] = sum(
                action.get('estimated_time', 5.0) 
                for action in data['actions']
            )
    if 'impact_level' in data:
        update_data['impact_level'] = data['impact_level']
    
    success = db.update_user_test_case(user_id, test_id, update_data)
    
    if not success:
        return jsonify({'error': 'Teste não encontrado'}), 404
    
    return jsonify({'status': 'success', 'message': 'Teste atualizado com sucesso'})

@app.route('/api/user/test-cases/<test_id>', methods=['DELETE'])
@login_required
def delete_user_test_case(test_id):
    """Deleta um teste personalizado"""
    user_id = session.get('user_id')
    success = db.delete_user_test_case(user_id, test_id)
    
    if not success:
        return jsonify({'error': 'Teste não encontrado'}), 404
    
    return jsonify({'status': 'success', 'message': 'Teste deletado com sucesso'})

# ==================== PREFERÊNCIAS DE USUÁRIO ====================

@app.route('/api/user/preferences')
@login_required
def get_user_preferences():
    """Retorna preferências do usuário"""
    user_id = session.get('user_id')
    preferences = db.get_user_preferences(user_id)
    return jsonify(preferences)

@app.route('/api/user/preferences', methods=['PUT'])
@login_required
def update_user_preferences():
    """Atualiza preferências do usuário"""
    user_id = session.get('user_id')
    data = request.json
    
    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400
    
    db.update_user_preferences(user_id, data)
    
    # Se tema foi alterado, atualizar na sessão
    if 'theme' in data:
        session['theme'] = data['theme']
    
    return jsonify({'status': 'success', 'message': 'Preferências atualizadas'})

# ==================== PERFIL DE USUÁRIO ====================

@app.route('/api/user/profile', methods=['GET'])
@login_required
def get_user_profile():
    """Retorna perfil completo do usuário"""
    user_id = session.get('user_id')
    user = db.get_user_by_id(user_id)
    
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    preferences = db.get_user_preferences(user_id)
    
    return jsonify({
        'id': user['id'],
        'username': user['username'],
        'email': user.get('email'),
        'full_name': user.get('full_name'),
        'experience_level': user.get('experience_level', 'beginner'),
        'profile_picture': user.get('profile_picture'),
        'created_at': user.get('created_at'),
        'last_login': user.get('last_login'),
        'preferences': preferences
    })

@app.route('/api/user/profile', methods=['PUT'])
@login_required
def update_user_profile():
    """Atualiza perfil do usuário"""
    user_id = session.get('user_id')
    data = request.json
    
    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400
    
    try:
        # Atualizar perfil
        db.update_user_profile(
            user_id=user_id,
            full_name=data.get('full_name'),
            email=data.get('email'),
            experience_level=data.get('experience_level')
        )
        
        # Se nível de experiência mudou, atualizar sessão
        if 'experience_level' in data:
            session['experience_level'] = data['experience_level']
            # Nota: Re-treinamento do modelo pode ser feito em background
        
        # Atualizar nome na sessão se mudou
        if 'full_name' in data:
            session['full_name'] = data['full_name']
        
        return jsonify({
            'status': 'success',
            'message': 'Perfil atualizado com sucesso'
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Erro ao atualizar perfil: {str(e)}'}), 500

@app.route('/api/user/profile/password', methods=['PUT'])
@login_required
def update_user_password():
    """Atualiza senha do usuário"""
    user_id = session.get('user_id')
    data = request.json
    
    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Senha atual e nova senha são obrigatórias'}), 400
    
    if len(new_password) < 4:
        return jsonify({'error': 'Nova senha deve ter pelo menos 4 caracteres'}), 400
    
    # Verificar senha atual
    user = db.get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    if not verify_password(current_password, user['password_hash']):
        return jsonify({'error': 'Senha atual incorreta'}), 401
    
    # Atualizar senha
    new_password_hash = hash_password(new_password)
    db.update_user_password(user_id, new_password_hash)
    
    return jsonify({
        'status': 'success',
        'message': 'Senha atualizada com sucesso'
    })

@app.route('/api/user/profile/picture', methods=['POST'])
@login_required
def upload_profile_picture():
    """Upload de foto de perfil"""
    user_id = session.get('user_id')
    
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Tipo de arquivo não permitido. Use: PNG, JPG, JPEG, GIF ou WEBP'}), 400
    
    # Verificar tamanho do arquivo
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return jsonify({'error': 'Arquivo muito grande. Tamanho máximo: 5MB'}), 400
    
    try:
        # Gerar nome único para o arquivo
        filename = secure_filename(file.filename)
        extension = filename.rsplit('.', 1)[1].lower()
        new_filename = f"user_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
        filepath = UPLOAD_FOLDER / new_filename
        
        # Salvar arquivo
        file.save(str(filepath))
        
        # Caminho relativo para salvar no banco
        relative_path = f"/static/uploads/profiles/{new_filename}"
        
        # Atualizar no banco de dados
        db.update_user_profile(user_id=user_id, profile_picture=relative_path)
        
        return jsonify({
            'status': 'success',
            'message': 'Foto de perfil atualizada com sucesso',
            'profile_picture': relative_path
        })
    except Exception as e:
        return jsonify({'error': f'Erro ao fazer upload: {str(e)}'}), 500

# ==================== EXPORTAÇÃO E RELATÓRIOS ====================

@app.route('/api/export/personal-stats/pdf')
@login_required
def export_personal_stats_pdf():
    """Exporta estatísticas pessoais em PDF"""
    user_id = session.get('user_id')
    
    try:
        pdf_data = report_generator.generate_personal_stats_pdf(user_id)
        filename = f"estatisticas_pessoais_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            io.BytesIO(pdf_data),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except ImportError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar PDF: {str(e)}'}), 500

@app.route('/api/export/personal-stats/excel')
@login_required
def export_personal_stats_excel():
    """Exporta estatísticas pessoais em Excel"""
    user_id = session.get('user_id')
    
    try:
        excel_data = report_generator.generate_personal_stats_excel(user_id)
        filename = f"estatisticas_pessoais_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(
            io.BytesIO(excel_data),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except ImportError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar Excel: {str(e)}'}), 500

@app.route('/api/export/comparative-report/excel')
@login_required
def export_comparative_report_excel():
    """Exporta relatório comparativo entre usuários em Excel"""
    user_ids = request.args.getlist('user_ids', type=int)
    
    if not user_ids:
        # Se não especificado, incluir usuário atual
        user_ids = [session.get('user_id')]
    
    try:
        excel_data = report_generator.generate_comparative_report_excel(user_ids)
        filename = f"relatorio_comparativo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(
            io.BytesIO(excel_data),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except ImportError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar relatório: {str(e)}'}), 500

@app.route('/api/model-evolution')
@login_required
def get_model_evolution():
    """Retorna dados de evolução do modelo ao longo do tempo"""
    user_id = request.args.get('user_id', type=int)
    # Se user_id não especificado, retorna evolução do modelo global
    
    try:
        evolution_data = report_generator.get_model_evolution_data(user_id)
        return jsonify(evolution_data)
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar dados: {str(e)}'}), 500

@app.route('/api/dashboard/executive')
@login_required
def get_executive_dashboard():
    """Retorna métricas agregadas para dashboard executivo"""
    cursor = db.conn.cursor()
    
    # Total de usuários
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_active = 1")
    total_users = cursor.fetchone()['count']
    
    # Total de feedbacks
    cursor.execute("SELECT COUNT(*) as count FROM feedbacks")
    total_feedbacks = cursor.fetchone()['count']
    
    # Taxa de sucesso global
    cursor.execute("""
        SELECT 
            AVG(CASE WHEN success = 1 THEN 1.0 ELSE 0.0 END) as success_rate,
            AVG(tester_rating) as avg_rating,
            AVG(actual_execution_time) as avg_time
        FROM feedbacks
    """)
    stats_row = cursor.fetchone()
    
    # Usuários mais ativos
    cursor.execute("""
        SELECT 
            u.id,
            u.full_name,
            u.username,
            COUNT(f.id) as feedback_count
        FROM users u
        LEFT JOIN feedbacks f ON f.tester_id = u.id
        WHERE u.is_active = 1
        GROUP BY u.id
        ORDER BY feedback_count DESC
        LIMIT 10
    """)
    top_users = [dict(row) for row in cursor.fetchall()]
    
    # Módulos mais testados
    cursor.execute("""
        SELECT 
            test_case_id,
            COUNT(*) as count
        FROM feedbacks
        GROUP BY test_case_id
        ORDER BY count DESC
        LIMIT 10
    """)
    top_tests = [dict(row) for row in cursor.fetchall()]
    
    return jsonify({
        'total_users': total_users,
        'total_feedbacks': total_feedbacks,
        'success_rate': stats_row['success_rate'] or 0.0,
        'avg_rating': stats_row['avg_rating'] or 0.0,
        'avg_execution_time': stats_row['avg_time'] or 0.0,
        'top_users': top_users,
        'top_tests': top_tests
    })

if __name__ == '__main__':
    print("=" * 80)
    print("🚀 INICIANDO INTERFACE WEB - SISTEMA DE RECOMENDAÇÃO MOTOROLA")
    print("=" * 80)
    print()
    print(f"📱 {len(testes)} testes carregados")
    print(f"🤖 Modelo Global: {'Treinado' if recommender.global_recommender.is_trained else 'Não treinado'}")
    print(f"📊 Feedbacks Globais: {len(recommender.global_recommender.feedback_history)}")
    print()
    print("🌐 Acesse: http://localhost:5000")
    print()
    print("Pressione Ctrl+C para parar")
    print("=" * 80)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
