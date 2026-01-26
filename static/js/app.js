// Estado global
let allTests = [];
let selectedTests = [];
let currentRecommendation = null;
let originalRecommendedOrder = [];  // NOVO: ordem original da IA
let acceptedOrder = [];              // Ordem final aceita (pode ser modificada)
let currentStats = null;
let charts = {};

// Função auxiliar para escape HTML
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Função auxiliar para renderizar badge de impacto (simples)
function renderImpactBadge(test) {
    const level = test.impact_level;
    
    if (level === 'destructive') {
        return '<span class="test-badge" style="background:#fee2e2;color:#991b1b;">🔴 Destrutivo</span>';
    } else if (level === 'partially_destructive') {
        return '<span class="test-badge" style="background:#fef3c7;color:#92400e;">🟡 Parcialmente destrutivo</span>';
    } else {
        return '<span class="test-badge" style="background:#d1fae5;color:#065f46;">🟢 Não-destrutivo</span>';
    }
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    checkAuthentication();
    setupTabs();
    setupRating();
    setupForm();
    loadInitialData();
    loadSavedTheme();
});

// ==================== AUTENTICAÇÃO ====================

async function checkAuthentication() {
    try {
        const response = await fetch('/api/user/current');
        if (response.ok) {
            const data = await response.json();
            if (data.authenticated) {
                displayUserInfo(data.user);
            } else {
                redirectToLogin();
            }
        } else {
            redirectToLogin();
        }
    } catch (error) {
        console.error('Erro ao verificar autenticação:', error);
        redirectToLogin();
    }
}

function displayUserInfo(user) {
    const userInfo = document.getElementById('userInfo');
    const userName = document.getElementById('userName');
    const menuUserName = document.getElementById('menuUserName');
    const menuUserEmail = document.getElementById('menuUserEmail');
    
    if (userInfo && userName) {
        userName.textContent = user.full_name || user.username;
        userInfo.style.display = 'flex';
    }
    
    if (menuUserName) {
        menuUserName.textContent = user.full_name || user.username;
    }
    
    if (menuUserEmail && user.email) {
        menuUserEmail.textContent = user.email;
    }
    
    // Carregar perfil completo para obter foto
    loadUserProfileForHeader();
    
    // Carregar notificações quando usuário logar
    loadNotifications();
    loadUnreadCount();
    // Atualizar contagem a cada 30 segundos
    setInterval(loadUnreadCount, 30000);
}

function redirectToLogin() {
    window.location.href = '/login';
}

async function logout() {
    try {
        const response = await fetch('/api/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Erro ao fazer logout:', error);
        // Mesmo assim, redirecionar
        window.location.href = '/login';
    }
}

// Interceptar requisições para tratar erros 401
const originalFetch = window.fetch;
window.fetch = async function(...args) {
    const response = await originalFetch(...args);
    if (response.status === 401) {
        const data = await response.json();
        if (data.redirect) {
            window.location.href = data.redirect;
        } else {
            redirectToLogin();
        }
    }
    return response;
};

// ==================== ESTATÍSTICAS PESSOAIS ====================

// Carregar estatísticas pessoais
async function loadPersonalStatistics() {
    try {
        const [personalStats, globalStats, personalFeedbacks] = await Promise.all([
            fetch('/api/user/stats').then(r => r.json()),
            fetch('/api/estatisticas').then(r => r.json()),
            fetch('/api/user/feedbacks').then(r => r.json())
        ]);
        
        // Atualizar cards de estatísticas pessoais
        document.getElementById('personalTotalFeedbacks').textContent = personalStats.total_feedbacks || 0;
        document.getElementById('personalAvgRating').textContent = (personalStats.avg_rating || 0).toFixed(1);
        document.getElementById('personalSuccessRate').textContent = `${(personalStats.success_rate || 0).toFixed(1)}%`;
        document.getElementById('personalAvgTime').textContent = `${Math.round(personalStats.avg_execution_time || 0)}s`;
        document.getElementById('personalModelSamples').textContent = personalStats.personal_model?.training_samples || 0;
        
        // Calcular peso de personalização baseado no nível de experiência
        const userResponse = await fetch('/api/user/current');
        const userData = await userResponse.json();
        if (userData.authenticated && userData.user.experience_level) {
            const weights = {
                'beginner': '20%',
                'intermediate': '50%',
                'advanced': '70%',
                'expert': '85%'
            };
            document.getElementById('personalWeight').textContent = weights[userData.user.experience_level] || '-';
        }
        
        // Atualizar comparações
        updateComparisonBars(personalStats, globalStats);
        
        // Criar gráficos pessoais
        createPersonalRatingChart(personalFeedbacks);
        createPersonalModulesChart(personalStats.preferred_modules);
        
        // Atualizar status do modelo personalizado
        updatePersonalAIStatus(personalStats);
        
        // Exibir histórico de feedbacks
        displayPersonalFeedbackHistory(personalFeedbacks);
        
    } catch (error) {
        console.error('Erro ao carregar estatísticas pessoais:', error);
        showToast('Erro ao carregar estatísticas pessoais', 'error');
    }
}

// Atualizar barras de comparação
function updateComparisonBars(personalStats, globalStats) {
    // Avaliação média
    const personalRating = personalStats.avg_rating || 0;
    const globalRating = globalStats.avg_rating || 0;
    const maxRating = 5;
    
    document.getElementById('personalRatingBar').style.width = `${(personalRating / maxRating) * 100}%`;
    document.getElementById('personalRatingValue').textContent = personalRating.toFixed(1);
    document.getElementById('globalRatingBar').style.width = `${(globalRating / maxRating) * 100}%`;
    document.getElementById('globalRatingValue').textContent = globalRating.toFixed(1);
    
    // Taxa de sucesso
    const personalSuccess = personalStats.success_rate || 0;
    const globalSuccess = globalStats.success_rate || 0;
    
    document.getElementById('personalSuccessBar').style.width = `${personalSuccess}%`;
    document.getElementById('personalSuccessValue').textContent = `${personalSuccess.toFixed(1)}%`;
    document.getElementById('globalSuccessBar').style.width = `${globalSuccess}%`;
    document.getElementById('globalSuccessValue').textContent = `${globalSuccess.toFixed(1)}%`;
}

// Criar gráfico de evolução pessoal de ratings
function createPersonalRatingChart(feedbacks) {
    const ctx = document.getElementById('personalRatingChart');
    const container = ctx.parentElement;
    
    if (charts.personalRating) {
        charts.personalRating.destroy();
        charts.personalRating = null;
    }
    
    if (!feedbacks || feedbacks.length === 0) {
        ctx.style.display = 'none';
        const existingMsg = container.querySelector('.no-data-message');
        if (!existingMsg) {
            const msg = document.createElement('p');
            msg.className = 'no-data-message';
            msg.style.cssText = 'text-align:center;padding:40px;color:#64748b;';
            msg.textContent = 'Você ainda não registrou feedbacks. Comece a usar o sistema!';
            container.appendChild(msg);
        }
        return;
    }
    
    ctx.style.display = 'block';
    const msg = container.querySelector('.no-data-message');
    if (msg) msg.remove();
    
    // Ordenar por data (mais antigo primeiro)
    const sortedFeedbacks = [...feedbacks].reverse();
    
    charts.personalRating = new Chart(ctx, {
        type: 'line',
        data: {
            labels: sortedFeedbacks.map((f, i) => `#${i + 1}`),
            datasets: [{
                label: 'Minha Avaliação',
                data: sortedFeedbacks.map(f => f.tester_rating || 0),
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 5,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Criar gráfico de módulos preferidos
function createPersonalModulesChart(preferredModules) {
    const ctx = document.getElementById('personalModulesChart');
    const container = ctx.parentElement;
    
    if (charts.personalModules) {
        charts.personalModules.destroy();
        charts.personalModules = null;
    }
    
    if (!preferredModules) {
        ctx.style.display = 'none';
        const existingMsg = container.querySelector('.no-data-message');
        if (!existingMsg) {
            const msg = document.createElement('p');
            msg.className = 'no-data-message';
            msg.style.cssText = 'text-align:center;padding:40px;color:#64748b;';
            msg.textContent = 'Módulos preferidos serão exibidos após alguns feedbacks.';
            container.appendChild(msg);
        }
        return;
    }
    
    const modules = preferredModules.split(',').filter(m => m.trim());
    
    if (modules.length === 0) {
        ctx.style.display = 'none';
        const existingMsg = container.querySelector('.no-data-message');
        if (!existingMsg) {
            const msg = document.createElement('p');
            msg.className = 'no-data-message';
            msg.style.cssText = 'text-align:center;padding:40px;color:#64748b;';
            msg.textContent = 'Módulos preferidos serão exibidos após alguns feedbacks.';
            container.appendChild(msg);
        }
        return;
    }
    
    ctx.style.display = 'block';
    const msg = container.querySelector('.no-data-message');
    if (msg) msg.remove();
    
    // Contar frequência de módulos
    const moduleCounts = {};
    modules.forEach(m => {
        moduleCounts[m] = (moduleCounts[m] || 0) + 1;
    });
    
    charts.personalModules = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(moduleCounts),
            datasets: [{
                data: Object.values(moduleCounts),
                backgroundColor: [
                    '#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
                    '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Atualizar status do modelo personalizado
function updatePersonalAIStatus(stats) {
    const container = document.getElementById('personalAIProgress');
    if (!container) return;
    
    const samples = stats.personal_model?.training_samples || 0;
    const phase = samples < 5 ? 1 : samples < 20 ? 2 : 3;
    const progress = samples < 5 ? (samples / 5) * 100 : samples < 20 ? 50 + ((samples - 5) / 15) * 50 : 100;
    
    container.innerHTML = `
        <div class="ai-phase-header">
            <span>Fase ${phase} de 3</span>
            <span>${Math.round(progress)}%</span>
        </div>
        <div class="ai-progress-bar">
            <div class="ai-progress-fill" style="width: ${progress}%"></div>
        </div>
        <div class="ai-phases">
            <div class="ai-phase ${phase === 1 ? 'active' : samples >= 5 ? 'completed' : ''}">
                <strong>🌱 Fase 1: Inicial (0-5 feedbacks)</strong>
                <p>${phase === 1 ? '✅ Fase Atual' : samples >= 5 ? '✅ Concluída' : '⏳ Aguardando'} - ${samples} feedbacks registrados</p>
            </div>
            <div class="ai-phase ${phase === 2 ? 'active' : samples >= 20 ? 'completed' : ''}">
                <strong>📚 Fase 2: Desenvolvimento (5-20 feedbacks)</strong>
                <p>${phase === 2 ? '✅ Fase Atual' : samples >= 20 ? '✅ Concluída' : '⏳ Aguardando'} - ${samples >= 5 ? samples : 0} feedbacks registrados</p>
            </div>
            <div class="ai-phase ${phase === 3 ? 'active' : ''}">
                <strong>🚀 Fase 3: Avançado (20+ feedbacks)</strong>
                <p>${phase === 3 ? '✅ Fase Atual' : '⏳ Aguardando'} - ${samples >= 20 ? samples : 0} feedbacks registrados</p>
            </div>
        </div>
        <p style="margin-top: 16px; color: var(--text-secondary); font-size: 14px;">
            💡 <strong>Dica:</strong> Quanto mais feedbacks você der, mais personalizado o modelo fica!
        </p>
    `;
}

// Exibir histórico de feedbacks pessoais
function displayPersonalFeedbackHistory(feedbacks) {
    const container = document.getElementById('personalFeedbackHistory');
    if (!container) return;
    
    if (!feedbacks || feedbacks.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 40px;">Nenhum feedback registrado ainda.</p>';
        return;
    }
    
    container.innerHTML = feedbacks.slice(0, 10).map(f => {
        const date = new Date(f.executed_at);
        const dateStr = date.toLocaleDateString('pt-BR') + ' ' + date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
        const stars = '★'.repeat(f.tester_rating || 0) + '☆'.repeat(5 - (f.tester_rating || 0));
        
        return `
            <div class="feedback-history-item">
                <div class="feedback-item-header">
                    <span class="feedback-test-id">${f.test_case_id}</span>
                    <span class="feedback-date">${dateStr}</span>
                </div>
                <div class="feedback-item-details">
                    <span class="feedback-rating">${stars}</span>
                    <span class="feedback-status ${f.success ? 'success' : 'failed'}">${f.success ? '✅ Sucesso' : '❌ Falhou'}</span>
                    <span class="feedback-time">⏱️ ${Math.round(f.actual_execution_time)}s</span>
                    ${f.required_reset ? '<span class="feedback-reset">🔄 Reset necessário</span>' : ''}
                </div>
                ${f.notes ? `<div class="feedback-notes">${f.notes}</div>` : ''}
            </div>
        `;
    }).join('');
}

// ==================== EXPLICABILIDADE DA IA ====================

// Exibir explicação da recomendação
function displayExplanation(explanation) {
    console.log('displayExplanation chamado com:', explanation);
    const container = document.getElementById('aiExplanation');
    const content = document.getElementById('explanationContent');
    
    if (!container) {
        console.error('Container aiExplanation não encontrado!');
        return;
    }
    
    if (!content) {
        console.error('Content explanationContent não encontrado!');
        return;
    }
    
    if (!explanation) {
        console.warn('Explicação vazia, ocultando card');
        container.style.display = 'none';
        return;
    }
    
    console.log('Exibindo card de explicação');
    container.style.display = 'block';
    
    let html = '';
    
    // Fatores que influenciaram
    if (explanation.factors && explanation.factors.length > 0) {
        html += '<div class="explanation-section">';
        html += '<h4>📊 Fatores que Influenciaram a Ordem:</h4>';
        html += '<div class="factors-list">';
        
        explanation.factors.forEach(factor => {
            const impactClass = factor.impact === 'positive' ? 'positive' : 
                               factor.impact === 'negative' ? 'negative' : 'neutral';
            html += `
                <div class="factor-item ${impactClass}">
                    <div class="factor-header">
                        <strong>${factor.name}</strong>
                        <span class="factor-value">${typeof factor.value === 'number' ? factor.value.toFixed(1) : factor.value}</span>
                    </div>
                    <div class="factor-description">${factor.description}</div>
                    <div class="factor-reason">💡 ${factor.reason}</div>
                </div>
            `;
        });
        
        html += '</div></div>';
    }
    
    // Importância de features
    if (explanation.feature_importance) {
        html += '<div class="explanation-section">';
        html += '<h4>🎯 Importância das Features:</h4>';
        html += '<div class="feature-importance-list">';
        
        const sortedFeatures = Object.entries(explanation.feature_importance)
            .sort((a, b) => b[1] - a[1]);
        
        sortedFeatures.forEach(([name, importance]) => {
            html += `
                <div class="feature-item">
                    <div class="feature-name">${name.replace(/_/g, ' ')}</div>
                    <div class="feature-bar-container">
                        <div class="feature-bar" style="width: ${importance}%"></div>
                        <span class="feature-value">${importance.toFixed(1)}%</span>
                    </div>
                </div>
            `;
        });
        
        html += '</div></div>';
    }
    
    // Explicação textual
    if (explanation.reasoning && explanation.reasoning.length > 0) {
        html += '<div class="explanation-section">';
        html += '<h4>📝 Explicação Detalhada:</h4>';
        html += '<div class="reasoning-text">';
        explanation.reasoning.forEach(reason => {
            html += `<p>${reason}</p>`;
        });
        html += '</div></div>';
    }
    
    // Se não houver conteúdo, mostrar mensagem padrão
    if (!html || html.trim() === '') {
        html = '<p style="color: var(--text-secondary);">A IA ainda está aprendendo. A ordem foi gerada usando heurísticas baseadas em prioridade, agrupamento por módulo e minimização de resets.</p>';
    }
    
    content.innerHTML = html;
}

// Toggle explicação
function toggleExplanation() {
    const content = document.getElementById('explanationContent');
    const btn = document.getElementById('toggleExplanationBtn');
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        btn.textContent = '▲';
    } else {
        content.style.display = 'none';
        btn.textContent = '▼';
    }
}

// ==================== DETECÇÃO DE ANOMALIAS ====================

// Carregar e exibir anomalias
async function loadAnomalies() {
    try {
        const response = await fetch('/api/anomalies');
        const data = await response.json();
        
        const container = document.getElementById('anomaliesResults');
        container.style.display = 'block';
        
        let html = '';
        
        // Resumo
        html += `<div class="anomalies-summary">
            <div class="summary-item">
                <strong>Total de Feedbacks Analisados:</strong> ${data.summary.total}
            </div>
            <div class="summary-item">
                <strong>Anomalias Detectadas:</strong> <span class="anomaly-count">${data.summary.anomalies_count}</span>
            </div>
            <div class="summary-item">
                <strong>Taxa de Anomalias:</strong> ${data.summary.anomaly_rate.toFixed(1)}%
            </div>
        </div>`;
        
        // Alertas
        if (data.alerts && data.alerts.length > 0) {
            html += '<div class="alerts-section">';
            html += '<h4>⚠️ Alertas:</h4>';
            
            data.alerts.forEach(alert => {
                const severityClass = alert.severity === 'high' ? 'alert-high' : 'alert-medium';
                html += `
                    <div class="alert-item ${severityClass}">
                        <div class="alert-header">
                            <strong>${alert.type.replace(/_/g, ' ')}</strong>
                            <span class="alert-severity">${alert.severity}</span>
                        </div>
                        <div class="alert-message">${alert.message}</div>
                        ${alert.action ? `<div class="alert-action">💡 ${alert.action}</div>` : ''}
                    </div>
                `;
            });
            
            html += '</div>';
        }
        
        // Padrões detectados
        if (data.patterns && data.patterns.length > 0) {
            html += '<div class="patterns-section">';
            html += '<h4>🔍 Padrões Detectados:</h4>';
            
            data.patterns.forEach(pattern => {
                html += `
                    <div class="pattern-item">
                        <div class="pattern-header">
                            <strong>${pattern.type.replace(/_/g, ' ')}</strong>
                        </div>
                        <div class="pattern-message">${pattern.message}</div>
                        ${pattern.test_id ? `<div class="pattern-test">Teste: ${pattern.test_id}</div>` : ''}
                    </div>
                `;
            });
            
            html += '</div>';
        }
        
        // Anomalias individuais
        if (data.anomalies && data.anomalies.length > 0) {
            html += '<div class="anomalies-list">';
            html += '<h4>🚨 Anomalias Individuais:</h4>';
            
            data.anomalies.slice(0, 10).forEach(anomaly => {
                const feedback = anomaly.feedback;
                html += `
                    <div class="anomaly-item">
                        <div class="anomaly-header">
                            <span class="anomaly-test">${feedback.test_case_id}</span>
                            <span class="anomaly-score">Score: ${anomaly.anomaly_score.toFixed(2)}</span>
                        </div>
                        <div class="anomaly-details">
                            <span>Tempo: ${Math.round(feedback.actual_execution_time)}s</span>
                            <span>Rating: ${feedback.tester_rating || 'N/A'}/5</span>
                            <span class="${feedback.success ? 'success' : 'failed'}">${feedback.success ? '✅ Sucesso' : '❌ Falhou'}</span>
                        </div>
                        <div class="anomaly-reasons">
                            <strong>Razões:</strong>
                            <ul>
                                ${anomaly.reasons.map(r => `<li>${r}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
        } else {
            html += '<div class="no-anomalies">✅ Nenhuma anomalia detectada nos seus feedbacks recentes!</div>';
        }
        
        container.innerHTML = html;
        
    } catch (error) {
        console.error('Erro ao carregar anomalias:', error);
        showToast('Erro ao carregar anomalias', 'error');
    }
}

// ==================== IMPORTÂNCIA DE FEATURES ====================

// Carregar e exibir importância de features
async function loadFeatureImportance() {
    try {
        const response = await fetch('/api/feature-importance');
        const data = await response.json();
        
        if (response.status !== 200) {
            showToast(data.error || 'Erro ao carregar importância de features', 'error');
            return;
        }
        
        const container = document.getElementById('featureImportanceChart');
        
        // Criar gráfico de barras
        const canvas = document.createElement('canvas');
        canvas.id = 'featureImportanceCanvas';
        container.innerHTML = '';
        container.appendChild(canvas);
        
        const sortedFeatures = Object.entries(data)
            .sort((a, b) => b[1] - a[1]);
        
        const labels = sortedFeatures.map(([name]) => name.replace(/_/g, ' '));
        const values = sortedFeatures.map(([, value]) => value);
        
        if (charts.featureImportance) {
            charts.featureImportance.destroy();
        }
        
        charts.featureImportance = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Importância (%)',
                    data: values,
                    backgroundColor: '#2563eb',
                    borderColor: '#1e40af',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Importância: ${context.parsed.x.toFixed(1)}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
        
    } catch (error) {
        console.error('Erro ao carregar importância de features:', error);
        showToast('Erro ao carregar importância de features', 'error');
    }
}

// Setup de Tabs
function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Atualizar botões
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Atualizar conteúdo
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`tab-${tabName}`).classList.add('active');
    
    // Carregar dados específicos da tab
    if (tabName === 'estatisticas') {
        loadStatistics();
    } else if (tabName === 'pessoais') {
        loadPersonalStatistics();
    } else if (tabName === 'testes') {
        loadAllTests();
    } else if (tabName === 'anotacoes') {
        loadNotes();
    } else if (tabName === 'recomendacao') {
        // Resetar para etapa 1 ao voltar
        showStep(1);
    }
}

// Controle de etapas
function showStep(step) {
    document.getElementById('step1-selection').style.display = step === 1 ? 'block' : 'none';
    document.getElementById('step2-recommendation').style.display = step === 2 ? 'block' : 'none';
    document.getElementById('step3-execution').style.display = step === 3 ? 'block' : 'none';
}

// Setup de Rating
function setupRating() {
    const stars = document.querySelectorAll('.star');
    const ratingInput = document.getElementById('rating');
    
    stars.forEach(star => {
        star.addEventListener('click', () => {
            const value = parseInt(star.dataset.value);
            ratingInput.value = value;
            
            stars.forEach(s => {
                const starValue = parseInt(s.dataset.value);
                if (starValue <= value) {
                    s.classList.add('active');
                    s.textContent = '★';
                } else {
                    s.classList.remove('active');
                    s.textContent = '☆';
                }
            });
        });
    });
    
    // Inicializar com 5 estrelas
    stars.forEach(s => {
        s.classList.add('active');
        s.textContent = '★';
    });
}

// Setup de Form
function setupForm() {
    const form = document.getElementById('feedbackForm');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await submitFeedback();
    });
}

// Carregar dados iniciais
async function loadInitialData() {
    try {
        await Promise.all([
            loadTests(),
            loadHeaderStats()
        ]);
        
        // Carregar testes para seleção
        await loadTestSelection();
    } catch (error) {
        showToast('Erro ao carregar dados iniciais', 'error');
        console.error(error);
    }
}

// Carregar testes
async function loadTests() {
    try {
        const response = await fetch('/api/testes');
        const data = await response.json();
        
        // O endpoint agora retorna {tests: [...], total: ..., filters_applied: {...}}
        // Se for um array direto (compatibilidade), usar diretamente
        if (Array.isArray(data)) {
            allTests = data;
        } else if (data.tests && Array.isArray(data.tests)) {
            allTests = data.tests;
        } else {
            console.error('Formato de resposta inesperado:', data);
            allTests = [];
        }
        
        // Popular select de feedback
        const select = document.getElementById('testSelect');
        if (select) {
            select.innerHTML = '<option value="">Selecione um teste...</option>';
            allTests.forEach(test => {
                const option = document.createElement('option');
                option.value = test.id;
                option.textContent = `${test.id} - ${test.name}`;
                option.dataset.time = test.estimated_time;
                select.appendChild(option);
            });
            
            // Auto-preencher tempo ao selecionar teste
            select.addEventListener('change', (e) => {
                const selectedOption = e.target.selectedOptions[0];
                if (selectedOption && selectedOption.dataset.time) {
                    const actualTimeInput = document.getElementById('actualTime');
                    if (actualTimeInput) {
                        actualTimeInput.value = selectedOption.dataset.time;
                    }
                }
            });
        }
        
        return allTests;
    } catch (error) {
        console.error('Erro ao carregar testes:', error);
        allTests = []; // Garantir que allTests seja sempre um array
        throw error;
    }
}

// Carregar testes para seleção (Etapa 1)
async function loadTestSelection() {
    const container = document.getElementById('testSelectionGrid');
    const moduleFilter = document.getElementById('filterModuleSelect');
    const searchInput = document.getElementById('searchTestsSelect');
    
    // Garantir que allTests é um array
    if (!Array.isArray(allTests) || allTests.length === 0) {
        if (container) {
            container.innerHTML = '<div class="loading">Carregando testes...</div>';
        }
        return;
    }
    
    // Popular filtro de módulos
    const modules = [...new Set(allTests.map(t => t.module))];
    if (moduleFilter) {
        moduleFilter.innerHTML = '<option value="">Todos os Módulos</option>';
    }
    modules.forEach(module => {
        const option = document.createElement('option');
        option.value = module;
        option.textContent = module;
        moduleFilter.appendChild(option);
    });
    
    // Função de filtro
    const filterTests = () => {
        const searchTerm = searchInput.value.toLowerCase();
        const moduleValue = moduleFilter.value;
        
        const filtered = allTests.filter(test => {
            const matchesSearch = !searchTerm || 
                test.name.toLowerCase().includes(searchTerm) ||
                test.id.toLowerCase().includes(searchTerm);
            const matchesModule = !moduleValue || test.module === moduleValue;
            return matchesSearch && matchesModule;
        });
        
        renderTestSelection(filtered);
    };
    
    // Event listeners
    searchInput.addEventListener('input', filterTests);
    moduleFilter.addEventListener('change', filterTests);
    
    // Renderizar inicial
    renderTestSelection(allTests);
}

function renderTestSelection(tests) {
    const container = document.getElementById('testSelectionGrid');
    container.innerHTML = '';
    
    tests.forEach(test => {
        const isSelected = selectedTests.includes(test.id);
        const card = document.createElement('div');
        card.className = `test-select-card ${isSelected ? 'selected' : ''}`;
        card.onclick = () => toggleTestSelection(test.id);
        card.innerHTML = `
            <div class="test-select-checkbox">${isSelected ? '✅' : '⬜'}</div>
            <div class="test-card-header">
                <div class="test-card-id">${test.id}</div>
                <div class="test-card-title">${test.name}</div>
            </div>
            <div class="test-card-footer">
                <span class="test-badge badge-module">📦 ${test.module}</span>
                <span class="test-badge badge-priority">🎯 P${test.priority}</span>
                <span class="test-badge badge-time">⏱️ ${test.estimated_time.toFixed(0)}s</span>
            </div>
        `;
        container.appendChild(card);
    });
    
    updateSelectionSummary();
}

function toggleTestSelection(testId) {
    const index = selectedTests.indexOf(testId);
    if (index > -1) {
        selectedTests.splice(index, 1);
    } else {
        selectedTests.push(testId);
    }
    
    // Re-renderizar para atualizar visual
    const searchInput = document.getElementById('searchTestsSelect');
    const moduleFilter = document.getElementById('filterModuleSelect');
    const searchTerm = searchInput.value.toLowerCase();
    const moduleValue = moduleFilter.value;
    
    const filtered = allTests.filter(test => {
        const matchesSearch = !searchTerm || 
            test.name.toLowerCase().includes(searchTerm) ||
            test.id.toLowerCase().includes(searchTerm);
        const matchesModule = !moduleValue || test.module === moduleValue;
        return matchesSearch && matchesModule;
    });
    
    renderTestSelection(filtered);
}

function updateSelectionSummary() {
    const summary = document.getElementById('selectionSummary');
    const count = document.getElementById('selectedCount');
    const time = document.getElementById('selectedTime');
    const btn = document.getElementById('btnSolicitar');
    
    if (selectedTests.length === 0) {
        summary.style.display = 'none';
        btn.disabled = true;
        btn.textContent = '🤖 Selecione ao menos 1 teste';
    } else {
        summary.style.display = 'block';
        btn.disabled = false;
        btn.textContent = '🤖 Solicitar Recomendação de Ordem';
        
        count.textContent = selectedTests.length;
        
        const totalTime = selectedTests.reduce((sum, testId) => {
            const test = allTests.find(t => t.id === testId);
            return sum + (test ? test.estimated_time : 0);
        }, 0);
        
        time.textContent = (totalTime / 60).toFixed(1);
    }
}

function selecionarTodos() {
    const searchInput = document.getElementById('searchTestsSelect');
    const moduleFilter = document.getElementById('filterModuleSelect');
    const searchTerm = searchInput.value.toLowerCase();
    const moduleValue = moduleFilter.value;
    
    const filtered = allTests.filter(test => {
        const matchesSearch = !searchTerm || 
            test.name.toLowerCase().includes(searchTerm) ||
            test.id.toLowerCase().includes(searchTerm);
        const matchesModule = !moduleValue || test.module === moduleValue;
        return matchesSearch && matchesModule;
    });
    
    filtered.forEach(test => {
        if (!selectedTests.includes(test.id)) {
            selectedTests.push(test.id);
        }
    });
    
    renderTestSelection(filtered);
}

function limparSelecao() {
    selectedTests = [];
    const searchInput = document.getElementById('searchTestsSelect');
    const moduleFilter = document.getElementById('filterModuleSelect');
    const searchTerm = searchInput.value.toLowerCase();
    const moduleValue = moduleFilter.value;
    
    const filtered = allTests.filter(test => {
        const matchesSearch = !searchTerm || 
            test.name.toLowerCase().includes(searchTerm) ||
            test.id.toLowerCase().includes(searchTerm);
        const matchesModule = !moduleValue || test.module === moduleValue;
        return matchesSearch && matchesModule;
    });
    
    renderTestSelection(filtered);
}

// Solicitar recomendação (Etapa 1 → 2)
async function solicitarRecomendacao() {
    if (selectedTests.length === 0) {
        showToast('Selecione ao menos 1 teste!', 'error');
        return;
    }
    
    showStep(2);
    
    try {
        const response = await fetch('/api/recomendacao', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({test_ids: selectedTests})
        });
        currentRecommendation = await response.json();
        displayRecommendation(currentRecommendation);
        await loadHeaderStats();
    } catch (error) {
        showToast('Erro ao gerar recomendação', 'error');
        console.error(error);
    }
}

// Exibir recomendação
function displayRecommendation(rec) {
    // Salvar ordem original da IA (NOVO!)
    originalRecommendedOrder = rec.details.map(test => test.id);
    
    // Atualizar info
    document.getElementById('recMethod').textContent = 
        rec.method === 'heuristic' ? '🧠 Heurísticas' : '🤖 Machine Learning';
    document.getElementById('recConfidence').textContent = 
        `${(rec.confidence * 100).toFixed(0)}%`;
    document.getElementById('recTime').textContent = 
        `${(rec.total_time / 60).toFixed(1)} min`;
    document.getElementById('recResets').textContent = rec.estimated_resets;
    
    // Exibir explicação se disponível
    console.log('Explicação recebida:', rec.explanation);
    if (rec.explanation && (rec.explanation.factors || rec.explanation.reasoning)) {
        displayExplanation(rec.explanation);
    } else {
        // Mesmo sem explicação completa, mostrar card com mensagem informativa
        const explanationCard = document.getElementById('aiExplanation');
        if (explanationCard) {
            const content = document.getElementById('explanationContent');
            if (content) {
                content.innerHTML = '<p style="color: var(--text-secondary);">A IA ainda está aprendendo. A ordem foi gerada usando heurísticas baseadas em prioridade, agrupamento por módulo e minimização de resets.</p>';
            }
            explanationCard.style.display = 'block';
        }
    }
    
    // Exibir lista de testes (drag-and-drop)
    const listContainer = document.getElementById('recommendedOrder');
    listContainer.innerHTML = '';
    
    rec.details.forEach((test, index) => {
        const testItem = document.createElement('div');
        testItem.className = `test-item ${test.is_destructive ? 'destructive' : 'non-destructive'}`;
        testItem.draggable = true;
        testItem.dataset.testId = test.id;
        testItem.ondragstart = handleDragStart;
        testItem.ondragover = handleDragOver;
        testItem.ondrop = handleDrop;
        testItem.ondragend = handleDragEnd;
        
        testItem.innerHTML = `
            <div class="test-number">${index + 1}</div>
            <div class="test-info">
                <div class="test-id">${test.id}</div>
                <div class="test-name">${test.name}</div>
                <div class="test-meta">
                    <span class="test-badge badge-module">📦 ${test.module}</span>
                    <span class="test-badge badge-priority">🎯 Prioridade ${test.priority}</span>
                    <span class="test-badge badge-time">⏱️ ${test.estimated_time.toFixed(0)}s</span>
                    ${renderImpactBadge(test)}
                </div>
            </div>
            <div class="drag-handle">⋮⋮</div>
        `;
        listContainer.appendChild(testItem);
    });
}

// Drag and Drop
let draggedElement = null;

function handleDragStart(e) {
    draggedElement = this;
    this.style.opacity = '0.4';
}

function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    return false;
}

function handleDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    
    if (draggedElement !== this) {
        const container = this.parentNode;
        const allItems = [...container.querySelectorAll('.test-item')];
        const draggedIndex = allItems.indexOf(draggedElement);
        const targetIndex = allItems.indexOf(this);
        
        if (draggedIndex < targetIndex) {
            this.parentNode.insertBefore(draggedElement, this.nextSibling);
        } else {
            this.parentNode.insertBefore(draggedElement, this);
        }
        
        // Atualizar números
        updateTestNumbers();
    }
    
    return false;
}

function handleDragEnd(e) {
    this.style.opacity = '1';
}

function updateTestNumbers() {
    const items = document.querySelectorAll('#recommendedOrder .test-item');
    items.forEach((item, index) => {
        item.querySelector('.test-number').textContent = index + 1;
    });
}

// Aceitar ordem (Etapa 2 → 3)
function aceitarOrdem() {
    // Capturar ordem atual (pode ter sido modificada)
    const items = document.querySelectorAll('#recommendedOrder .test-item');
    acceptedOrder = Array.from(items).map(item => ({
        id: item.dataset.testId,
        name: item.querySelector('.test-name').textContent,
        module: item.querySelector('.badge-module').textContent.replace('📦 ', '')
    }));
    
    showStep(3);
    displayExecutionOrder();
}

function displayExecutionOrder() {
    const container = document.getElementById('executionOrder');
    container.innerHTML = '';
    
    acceptedOrder.forEach((test, index) => {
        const testItem = document.createElement('div');
        testItem.className = 'test-item';
        testItem.innerHTML = `
            <div class="test-number">${index + 1}</div>
            <div class="test-info">
                <div class="test-id">${test.id}</div>
                <div class="test-name">${test.name}</div>
                <div class="test-meta">
                    <span class="test-badge badge-module">📦 ${test.module}</span>
                </div>
            </div>
        `;
        container.appendChild(testItem);
    });
}

function voltarSelecao() {
    selectedTests = [];
    currentRecommendation = null;
    acceptedOrder = [];
    showStep(1);
    loadTestSelection();
}

function novaRecomendacao() {
    solicitarRecomendacao();
}

function irParaFeedback() {
    switchTab('feedback');
}

// Carregar estatísticas do header
async function loadHeaderStats() {
    try {
        const [testsData, statsData] = await Promise.all([
            fetch('/api/testes').then(r => r.json()).then(data => {
                // Extrair array de testes se necessário
                return Array.isArray(data) ? data : (data.tests || []);
            }),
            fetch('/api/estatisticas').then(r => r.json())
        ]);
        
        const totalTests = Array.isArray(testsData) ? testsData.length : (testsData.total || 0);
        document.getElementById('totalTests').textContent = totalTests;
        document.getElementById('totalFeedbacks').textContent = statsData.total_feedbacks;
        
        if (currentRecommendation) {
            document.getElementById('confidence').textContent = 
                `${(currentRecommendation.confidence * 100).toFixed(0)}%`;
        } else {
            document.getElementById('confidence').textContent = '-';
        }
        
        const aiStatus = document.getElementById('aiStatus');
        if (statsData.is_trained) {
            aiStatus.textContent = '🚀 Treinado';
            aiStatus.style.background = '#10b981';
            aiStatus.style.color = 'white';
        } else {
            aiStatus.textContent = '🌱 Aprendendo';
            aiStatus.style.background = '#f59e0b';
            aiStatus.style.color = 'white';
        }
    } catch (error) {
        console.error('Erro ao carregar stats do header:', error);
    }
}

// Verificar se a ordem foi modificada
function checkIfOrderWasModified() {
    if (originalRecommendedOrder.length === 0 || acceptedOrder.length === 0) {
        return false;
    }
    
    const acceptedIds = acceptedOrder.map(t => t.id);
    
    // Comparar arrays
    if (originalRecommendedOrder.length !== acceptedIds.length) {
        return true;
    }
    
    for (let i = 0; i < originalRecommendedOrder.length; i++) {
        if (originalRecommendedOrder[i] !== acceptedIds[i]) {
            return true;
        }
    }
    
    return false;
}

// Submeter feedback
async function submitFeedback() {
    // Verificar se ordem foi modificada
    const wasModified = checkIfOrderWasModified();
    
    const formData = {
        test_id: document.getElementById('testSelect').value,
        actual_time: parseFloat(document.getElementById('actualTime').value),
        success: document.getElementById('testSuccess').value === 'true',
        rating: parseInt(document.getElementById('rating').value),
        required_reset: document.getElementById('requiredReset').value === 'true',
        followed_recommendation: document.getElementById('followedRecommendation').value === 'true',
        notes: document.getElementById('notes').value || null,
        order_was_modified: wasModified,  // NOVO!
        original_order: originalRecommendedOrder,  // NOVO!
        accepted_order: acceptedOrder.map(t => t.id)  // NOVO!
    };
    
    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            // Mostrar sucesso
            document.getElementById('feedbackForm').style.display = 'none';
            document.getElementById('feedbackSuccess').style.display = 'block';
            
            // Atualizar header stats
            await loadHeaderStats();
            
            showToast('✅ Feedback registrado com sucesso!', 'success');
        } else {
            showToast('❌ ' + result.message, 'error');
        }
    } catch (error) {
        showToast('Erro ao enviar feedback', 'error');
        console.error(error);
    }
}

// Resetar form de feedback
function resetFeedbackForm() {
    document.getElementById('feedbackForm').reset();
    document.getElementById('feedbackForm').style.display = 'block';
    document.getElementById('feedbackSuccess').style.display = 'none';
    
    // Resetar rating para 5 estrelas
    document.querySelectorAll('.star').forEach(s => {
        s.classList.add('active');
        s.textContent = '★';
    });
    document.getElementById('rating').value = 5;
}

// Carregar estatísticas completas
async function loadStatistics() {
    try {
        const [stats, modules] = await Promise.all([
            fetch('/api/estatisticas').then(r => r.json()),
            fetch('/api/modulos').then(r => r.json())
        ]);
        
        currentStats = stats;
        
        // Atualizar cards de estatísticas
        document.getElementById('statTotalFeedbacks').textContent = stats.total_feedbacks;
        document.getElementById('statSuccessRate').textContent = `${stats.success_rate.toFixed(1)}%`;
        document.getElementById('statAvgRating').textContent = stats.avg_rating.toFixed(1);
        document.getElementById('statResets').textContent = stats.resets_count;
        
        // Criar gráfico de ratings
        createRatingChart(stats.feedback_history);
        
        // Criar gráfico de módulos
        createModuleChart(modules);
        
        // Atualizar status da IA
        updateAIStatus(stats);
        
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
        showToast('Erro ao carregar estatísticas', 'error');
    }
}

// Criar gráfico de ratings
function createRatingChart(feedbackHistory) {
    const ctx = document.getElementById('ratingChart');
    const container = ctx.parentElement;
    
    // Destruir gráfico anterior se existir
    if (charts.rating) {
        charts.rating.destroy();
        charts.rating = null;
    }
    
    if (!feedbackHistory || feedbackHistory.length === 0) {
        // Esconder canvas e mostrar mensagem
        ctx.style.display = 'none';
        const existingMsg = container.querySelector('.no-data-message');
        if (!existingMsg) {
            const msg = document.createElement('p');
            msg.className = 'no-data-message';
            msg.style.cssText = 'text-align:center;padding:40px;color:#64748b;';
            msg.textContent = 'Sem dados ainda. Adicione feedbacks para ver a evolução!';
            container.appendChild(msg);
        }
        return;
    }
    
    // Remover mensagem e mostrar canvas
    ctx.style.display = 'block';
    const msg = container.querySelector('.no-data-message');
    if (msg) msg.remove();
    
    charts.rating = new Chart(ctx, {
        type: 'line',
        data: {
            labels: feedbackHistory.map(f => f.index),
            datasets: [{
                label: 'Avaliação',
                data: feedbackHistory.map(f => f.rating),
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 5,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Criar gráfico de módulos
function createModuleChart(modules) {
    const ctx = document.getElementById('moduleChart');
    const container = ctx.parentElement;
    
    // Destruir gráfico anterior se existir
    if (charts.module) {
        charts.module.destroy();
        charts.module = null;
    }
    
    // Verificar se há dados
    if (!modules || modules.length === 0) {
        // Esconder canvas e mostrar mensagem
        ctx.style.display = 'none';
        const existingMsg = container.querySelector('.no-data-message');
        if (!existingMsg) {
            const msg = document.createElement('p');
            msg.className = 'no-data-message';
            msg.style.cssText = 'text-align:center;padding:40px;color:#64748b;';
            msg.textContent = 'Sem dados de módulos ainda.';
            container.appendChild(msg);
        }
        return;
    }
    
    // Remover mensagem e mostrar canvas
    ctx.style.display = 'block';
    const msg = container.querySelector('.no-data-message');
    if (msg) msg.remove();
    
    const colors = [
        '#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
        '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'
    ];
    
    charts.module = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: modules.map(m => m.name),
            datasets: [{
                data: modules.map(m => m.count),
                backgroundColor: colors.slice(0, modules.length),
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Atualizar status da IA
function updateAIStatus(stats) {
    const container = document.getElementById('aiProgress');
    
    // Verificar se container existe (CORREÇÃO!)
    if (!container) {
        console.error('Container aiProgress não encontrado');
        return;
    }
    
    const phase = stats.total_feedbacks < 5 ? 1 :
                  stats.total_feedbacks < 20 ? 2 : 3;
    
    const progress = stats.total_feedbacks < 5 ? 
        (stats.total_feedbacks / 5) * 100 :
        stats.total_feedbacks < 20 ?
        50 + ((stats.total_feedbacks - 5) / 15) * 50 :
        100;
    
    container.innerHTML = `
        <div style="margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="font-weight: 600;">Fase ${phase} de 3</span>
                <span>${Math.round(progress)}%</span>
            </div>
            <div style="background: rgba(255,255,255,0.3); height: 12px; border-radius: 6px; overflow: hidden;">
                <div style="background: white; height: 100%; width: ${progress}%; transition: width 0.3s;"></div>
            </div>
        </div>
        
        <div style="display: grid; gap: 16px;">
            <div style="padding: 16px; background: rgba(255,255,255,0.1); border-radius: 8px;">
                <strong>🌱 Fase 1: Heurísticas (0-5 feedbacks)</strong>
                <p style="margin: 8px 0 0 0; opacity: 0.9; font-size: 14px;">
                    ${stats.total_feedbacks < 5 ? '✅ Fase Atual' : '✔️ Concluída'} - Usando regras inteligentes
                </p>
            </div>
            
            <div style="padding: 16px; background: rgba(255,255,255,0.1); border-radius: 8px;">
                <strong>📚 Fase 2: ML Inicial (5-20 feedbacks)</strong>
                <p style="margin: 8px 0 0 0; opacity: 0.9; font-size: 14px;">
                    ${stats.total_feedbacks >= 5 && stats.total_feedbacks < 20 ? '✅ Fase Atual' :
                      stats.total_feedbacks >= 20 ? '✔️ Concluída' : '⏳ Aguardando'} - 
                    ${stats.total_feedbacks >= 5 ? 'Modelo começou a aprender!' : 'Precisa de mais feedbacks'}
                </p>
            </div>
            
            <div style="padding: 16px; background: rgba(255,255,255,0.1); border-radius: 8px;">
                <strong>🚀 Fase 3: ML Completo (20+ feedbacks)</strong>
                <p style="margin: 8px 0 0 0; opacity: 0.9; font-size: 14px;">
                    ${stats.total_feedbacks >= 20 ? '✅ Fase Atual - IA totalmente treinada!' : 
                      '⏳ Aguardando - Faltam ' + (20 - stats.total_feedbacks) + ' feedbacks'}
                </p>
            </div>
        </div>
        
        <div style="margin-top: 20px; padding: 16px; background: rgba(0,0,0,0.2); border-radius: 8px;">
            <p style="margin: 0; font-size: 14px; opacity: 0.9;">
                💡 <strong>Dica:</strong> Quanto mais feedbacks você der, mais inteligente o sistema fica!
            </p>
        </div>
    `;
}

// Carregar todos os testes
async function loadAllTests() {
    try {
        // Carregar opções de filtros primeiro
        await loadFilterOptions();
        
        // Carregar testes com filtros aplicados
        await applyFilters();
    } catch (error) {
        console.error('Erro ao carregar todos os testes:', error);
        const container = document.getElementById('allTests');
        if (container) {
            container.innerHTML = '<div class="error">Erro ao carregar testes. Tente novamente.</div>';
        }
    }
}

// Carregar opções de filtros
async function loadFilterOptions() {
    try {
        const response = await fetch('/api/testes/filters/options');
        const options = await response.json();
        
        // Popular módulos
        const moduleSelect = document.getElementById('filterModule');
        if (moduleSelect) {
            moduleSelect.innerHTML = '';
            options.modules.forEach(module => {
                const option = document.createElement('option');
                option.value = module;
                option.textContent = module;
                moduleSelect.appendChild(option);
            });
        }
        
        // Popular tags
        const tagsSelect = document.getElementById('filterTags');
        if (tagsSelect) {
            tagsSelect.innerHTML = '';
            options.tags.forEach(tag => {
                const option = document.createElement('option');
                option.value = tag;
                option.textContent = tag;
                tagsSelect.appendChild(option);
            });
        }
        
        // Atualizar placeholders de tempo
        const timeMin = document.getElementById('timeMin');
        const timeMax = document.getElementById('timeMax');
        if (timeMin) timeMin.placeholder = `Mín (${options.time_range.min.toFixed(0)}s)`;
        if (timeMax) timeMax.placeholder = `Máx (${options.time_range.max.toFixed(0)}s)`;
    } catch (error) {
        console.error('Erro ao carregar opções de filtros:', error);
    }
}

// Aplicar filtros e buscar testes
async function applyFilters() {
    const container = document.getElementById('allTests');
    if (!container) return;
    
    container.innerHTML = '<div class="loading">Buscando testes...</div>';
    
    try {
        // Coletar filtros
        const search = document.getElementById('searchTests')?.value || '';
        const sortBy = document.getElementById('sortBy')?.value || 'id';
        const sortOrder = document.getElementById('sortOrder')?.value || 'asc';
        
        // Filtros avançados
        const moduleSelect = document.getElementById('filterModule');
        const modules = moduleSelect ? Array.from(moduleSelect.selectedOptions).map(o => o.value) : [];
        
        const priorityMin = document.getElementById('priorityMin')?.value || null;
        const priorityMax = document.getElementById('priorityMax')?.value || null;
        
        const impactLevels = [];
        if (document.getElementById('filterImpactDestructive')?.checked) {
            impactLevels.push('destructive');
        }
        if (document.getElementById('filterImpactPartial')?.checked) {
            impactLevels.push('partially_destructive');
        }
        if (document.getElementById('filterImpactNon')?.checked) {
            impactLevels.push('non_destructive');
        }
        
        const timeMin = document.getElementById('timeMin')?.value || null;
        const timeMax = document.getElementById('timeMax')?.value || null;
        
        const tagsSelect = document.getElementById('filterTags');
        const tags = tagsSelect ? Array.from(tagsSelect.selectedOptions).map(o => o.value) : [];
        
        // Construir query string para busca simples
        const params = new URLSearchParams();
        if (search) params.append('search', search);
        if (modules.length === 1) params.append('module', modules[0]);
        if (priorityMin && !priorityMax) params.append('priority', priorityMin);
        if (impactLevels.length === 1) params.append('impact_level', impactLevels[0]);
        if (timeMin && !timeMax) params.append('min_time', timeMin);
        if (timeMax && !timeMin) params.append('max_time', timeMax);
        if (tags.length === 1) params.append('tags', tags[0]);
        params.append('sort_by', sortBy);
        params.append('sort_order', sortOrder);
        
        // Se há múltiplos filtros ou ranges, usar endpoint de busca avançada
        const useAdvanced = modules.length > 1 || impactLevels.length > 1 || tags.length > 1 || 
                           (priorityMin && priorityMax) || (timeMin && timeMax);
        
        let response;
        if (useAdvanced) {
            // Usar busca avançada
            response = await fetch('/api/testes/search', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    search: search,
                    modules: modules.length > 0 ? modules : undefined,
                    priority_min: priorityMin ? parseInt(priorityMin) : undefined,
                    priority_max: priorityMax ? parseInt(priorityMax) : undefined,
                    impact_levels: impactLevels.length > 0 ? impactLevels : undefined,
                    time_range: {
                        min: timeMin ? parseFloat(timeMin) : undefined,
                        max: timeMax ? parseFloat(timeMax) : undefined
                    },
                    tags: tags.length > 0 ? tags : undefined,
                    sort_by: sortBy,
                    sort_order: sortOrder
                })
            });
        } else {
            // Usar busca simples
            response = await fetch(`/api/testes?${params.toString()}`);
        }
        
        const data = await response.json();
        const tests = data.tests || [];
        
        // Atualizar contador
        const resultsInfo = document.getElementById('resultsInfo');
        const resultsCount = document.getElementById('resultsCount');
        if (resultsInfo && resultsCount) {
            resultsCount.textContent = tests.length;
            resultsInfo.style.display = 'block';
        }
        
        // Exibir testes
        displayAllTests(tests);
    } catch (error) {
        console.error('Erro ao aplicar filtros:', error);
        container.innerHTML = '<div class="error">Erro ao buscar testes. Tente novamente.</div>';
    }
}

// Toggle filtros avançados
function toggleAdvancedFilters() {
    const filters = document.getElementById('advancedFilters');
    const btn = document.getElementById('toggleFiltersBtn');
    
    if (filters && btn) {
        const isVisible = filters.style.display !== 'none';
        filters.style.display = isVisible ? 'none' : 'block';
        btn.textContent = isVisible ? '🔧 Filtros Avançados' : '🔧 Ocultar Filtros';
    }
}

// Limpar todos os filtros
function clearAllFilters() {
    // Limpar busca
    const searchInput = document.getElementById('searchTests');
    if (searchInput) searchInput.value = '';
    
    // Limpar ordenação
    const sortBy = document.getElementById('sortBy');
    const sortOrder = document.getElementById('sortOrder');
    if (sortBy) sortBy.value = 'id';
    if (sortOrder) sortOrder.value = 'asc';
    
    // Limpar filtros avançados
    const moduleSelect = document.getElementById('filterModule');
    if (moduleSelect) {
        Array.from(moduleSelect.options).forEach(opt => opt.selected = false);
    }
    
    document.getElementById('priorityMin').value = '';
    document.getElementById('priorityMax').value = '';
    document.getElementById('filterImpactDestructive').checked = false;
    document.getElementById('filterImpactPartial').checked = false;
    document.getElementById('filterImpactNon').checked = false;
    document.getElementById('timeMin').value = '';
    document.getElementById('timeMax').value = '';
    
    const tagsSelect = document.getElementById('filterTags');
    if (tagsSelect) {
        Array.from(tagsSelect.options).forEach(opt => opt.selected = false);
    }
    
    // Reaplicar filtros (vai buscar todos)
    applyFilters();
}

// Exibir todos os testes
function displayAllTests(tests) {
    // Apenas renderizar os testes - os filtros já estão configurados no HTML
    // com onchange/oninput que chamam applyFilters()
    renderTestCards(tests);
}

function renderTestCards(tests) {
    const container = document.getElementById('allTests');
    
    if (tests.length === 0) {
        container.innerHTML = '<div class="loading">Nenhum teste encontrado</div>';
        return;
    }
    
    container.innerHTML = '';
    tests.forEach(test => {
        const card = document.createElement('div');
        card.className = 'test-card';
        
        const isCustom = test.is_custom || false;
        const customBadge = isCustom ? '<span class="test-badge" style="background:#e0e7ff;color:#4338ca;">⭐ Personalizado</span>' : '';
        
        // Escapar valores para segurança
        const escapedId = escapeHtml(test.id);
        const escapedName = escapeHtml(test.name);
        const escapedDesc = escapeHtml(test.description || '');
        const escapedModule = escapeHtml(test.module);
        
        // Para onclick, usar escape de aspas simples
        const safeId = test.id.replace(/'/g, "\\'").replace(/"/g, '&quot;');
        const customActions = isCustom ? `
            <div class="test-card-actions">
                <button class="btn-icon" onclick="editUserTest('${safeId}')" title="Editar">✏️</button>
                <button class="btn-icon" onclick="deleteUserTest('${safeId}')" title="Excluir">🗑️</button>
            </div>
        ` : '';
        
        card.innerHTML = `
            <div class="test-card-header">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div class="test-card-id">${escapedId}</div>
                    ${customActions}
                </div>
                <div class="test-card-title">${escapedName}</div>
                <div class="test-card-description">${escapedDesc}</div>
            </div>
            <div class="test-card-footer">
                <span class="test-badge badge-module">📦 ${escapedModule}</span>
                <span class="test-badge badge-priority">🎯 P${test.priority}</span>
                <span class="test-badge badge-time">⏱️ ${test.estimated_time.toFixed(0)}s</span>
                ${customBadge}
                ${renderImpactBadge(test)}
            </div>
        `;
        container.appendChild(card);
    });
}

// Mostrar toast
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// ==================== NOTIFICAÇÕES ====================

let notificationsDropdownOpen = false;

async function loadNotifications() {
    try {
        const response = await fetch('/api/notifications?limit=20');
        const notifications = await response.json();
        renderNotifications(notifications);
    } catch (error) {
        console.error('Erro ao carregar notificações:', error);
    }
}

async function loadUnreadCount() {
    try {
        const response = await fetch('/api/notifications/unread-count');
        const data = await response.json();
        const badge = document.getElementById('notificationBadge');
        if (badge) {
            if (data.count > 0) {
                badge.textContent = data.count > 99 ? '99+' : data.count;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Erro ao carregar contagem de notificações:', error);
    }
}

function renderNotifications(notifications) {
    const container = document.getElementById('notificationsList');
    if (!container) return;
    
    if (notifications.length === 0) {
        container.innerHTML = '<div class="notification-empty">Nenhuma notificação</div>';
        return;
    }
    
    container.innerHTML = notifications.map(notif => {
        const timeAgo = getTimeAgo(notif.created_at);
        const severityClass = `notification-severity-${notif.severity || 'info'}`;
        const readClass = notif.is_read ? 'read' : 'unread';
        
        return `
            <div class="notification-item ${readClass} ${severityClass}" 
                 onclick="markNotificationRead(${notif.id}, this)">
                <div class="notification-icon">
                    ${getNotificationIcon(notif.type, notif.severity)}
                </div>
                <div class="notification-content">
                    <div class="notification-title">${notif.title}</div>
                    <div class="notification-message">${notif.message}</div>
                    <div class="notification-time">${timeAgo}</div>
                </div>
            </div>
        `;
    }).join('');
}

function getNotificationIcon(type, severity) {
    const icons = {
        'model_trained': '🎉',
        'success_rate_drop': '⚠️',
        'feedback_reminder': '💡',
        'recommendation_improvement': '📈'
    };
    
    if (icons[type]) {
        return icons[type];
    }
    
    // Fallback por severidade
    const severityIcons = {
        'success': '✅',
        'warning': '⚠️',
        'error': '❌',
        'info': 'ℹ️'
    };
    
    return severityIcons[severity] || '🔔';
}

function getTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Agora';
    if (diffMins < 60) return `${diffMins} min atrás`;
    if (diffHours < 24) return `${diffHours}h atrás`;
    if (diffDays < 7) return `${diffDays}d atrás`;
    
    return date.toLocaleDateString('pt-BR');
}

function toggleNotifications() {
    const dropdown = document.getElementById('notificationsDropdown');
    if (!dropdown) return;
    
    notificationsDropdownOpen = !notificationsDropdownOpen;
    dropdown.style.display = notificationsDropdownOpen ? 'flex' : 'none';
    
    if (notificationsDropdownOpen) {
        loadNotifications();
    }
}

async function markNotificationRead(notificationId, element) {
    try {
        const response = await fetch(`/api/notifications/${notificationId}/read`, {
            method: 'POST'
        });
        
        if (response.ok) {
            element.classList.remove('unread');
            element.classList.add('read');
            loadUnreadCount();
            
            // Se houver action_url, navegar para lá
            const notification = await response.json();
            if (notification.action_url) {
                // Não navegar automaticamente, apenas destacar
            }
        }
    } catch (error) {
        console.error('Erro ao marcar notificação como lida:', error);
    }
}

async function markAllNotificationsRead() {
    try {
        const response = await fetch('/api/notifications/read-all', {
            method: 'POST'
        });
        
        if (response.ok) {
            loadNotifications();
            loadUnreadCount();
            showToast('Todas as notificações foram marcadas como lidas', 'success');
        }
    } catch (error) {
        console.error('Erro ao marcar todas como lidas:', error);
    }
}

// Fechar dropdown ao clicar fora
document.addEventListener('click', (e) => {
    const container = document.querySelector('.notifications-container');
    const dropdown = document.getElementById('notificationsDropdown');
    
    if (container && dropdown && notificationsDropdownOpen) {
        if (!container.contains(e.target)) {
            notificationsDropdownOpen = false;
            dropdown.style.display = 'none';
        }
    }
});

// ==================== PERFIL DE USUÁRIO ====================

let userProfile = null;
let userMenuOpen = false;

// Carregar perfil do usuário para o header
async function loadUserProfileForHeader() {
    try {
        const response = await fetch('/api/user/profile');
        if (response.ok) {
            const profile = await response.json();
            updateHeaderProfilePicture(profile.profile_picture);
            // Atualizar email no menu se disponível
            const menuUserEmail = document.getElementById('menuUserEmail');
            if (menuUserEmail && profile.email) {
                menuUserEmail.textContent = profile.email;
            }
        }
    } catch (error) {
        console.error('Erro ao carregar perfil para header:', error);
    }
}

// Atualizar foto de perfil no header
function updateHeaderProfilePicture(profilePicture) {
    const headerPicture = document.getElementById('headerProfilePicture');
    const menuPicture = document.getElementById('menuProfilePicture');
    
    // Se não houver foto, usar placeholder SVG
    const defaultAvatar = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='32' height='32'%3E%3Ccircle cx='16' cy='16' r='16' fill='%23e2e8f0'/%3E%3Ctext x='16' y='20' font-size='18' text-anchor='middle' fill='%2364748b'%3E👤%3C/text%3E%3C/svg%3E";
    const defaultAvatarLarge = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='48' height='48'%3E%3Ccircle cx='24' cy='24' r='24' fill='%23e2e8f0'/%3E%3Ctext x='24' y='30' font-size='28' text-anchor='middle' fill='%2364748b'%3E👤%3C/text%3E%3C/svg%3E";
    
    if (headerPicture) {
        headerPicture.src = profilePicture || defaultAvatar;
    }
    if (menuPicture) {
        menuPicture.src = profilePicture || defaultAvatarLarge;
    }
}

// Toggle menu do usuário
function toggleUserMenu() {
    const dropdown = document.getElementById('userMenuDropdown');
    if (!dropdown) return;
    
    userMenuOpen = !userMenuOpen;
    dropdown.style.display = userMenuOpen ? 'block' : 'none';
}

// Fechar menu do usuário ao clicar fora
document.addEventListener('click', (e) => {
    const container = document.querySelector('.user-menu-container');
    const dropdown = document.getElementById('userMenuDropdown');
    
    if (container && dropdown && userMenuOpen) {
        if (!container.contains(e.target)) {
            userMenuOpen = false;
            dropdown.style.display = 'none';
        }
    }
});

// Carregar perfil do usuário (para modal)
async function loadUserProfile() {
    try {
        const response = await fetch('/api/user/profile');
        if (response.ok) {
            userProfile = await response.json();
            displayUserProfile(userProfile);
        }
    } catch (error) {
        console.error('Erro ao carregar perfil:', error);
    }
}

// Exibir perfil do usuário
function displayUserProfile(profile) {
    const profileUsername = document.getElementById('profileUsername');
    const profileFullName = document.getElementById('profileFullName');
    const profileEmail = document.getElementById('profileEmail');
    const profileExperienceLevel = document.getElementById('profileExperienceLevel');
    const profilePicture = document.getElementById('profilePicture');
    
    if (profileUsername) profileUsername.value = profile.username || '';
    if (profileFullName) profileFullName.value = profile.full_name || '';
    if (profileEmail) profileEmail.value = profile.email || '';
    if (profileExperienceLevel) profileExperienceLevel.value = profile.experience_level || 'beginner';
    
    // Foto de perfil
    if (profilePicture && profile.profile_picture) {
        profilePicture.src = profile.profile_picture;
    }
    // Atualizar também no header
    updateHeaderProfilePicture(profile.profile_picture);
}

// Abrir modal de perfil
function openProfileModal() {
    const modal = document.getElementById('profileModal');
    if (modal) {
        modal.style.display = 'flex';
        loadUserProfile();
        userMenuOpen = false;
        const dropdown = document.getElementById('userMenuDropdown');
        if (dropdown) dropdown.style.display = 'none';
    }
}

// Fechar modal de perfil
function closeProfileModal() {
    const modal = document.getElementById('profileModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Abrir modal de preferências
function openPreferencesModal() {
    const modal = document.getElementById('preferencesModal');
    if (modal) {
        modal.style.display = 'flex';
        loadUserProfile(); // Para carregar preferências
        userMenuOpen = false;
        const dropdown = document.getElementById('userMenuDropdown');
        if (dropdown) dropdown.style.display = 'none';
    }
}

// Fechar modal de preferências
function closePreferencesModal() {
    const modal = document.getElementById('preferencesModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Fechar modais ao clicar fora
document.addEventListener('click', (e) => {
    const profileModal = document.getElementById('profileModal');
    const preferencesModal = document.getElementById('preferencesModal');
    
    if (profileModal && e.target === profileModal) {
        closeProfileModal();
    }
    
    if (preferencesModal && e.target === preferencesModal) {
        closePreferencesModal();
    }
});

// Salvar perfil
async function saveProfile() {
    const fullName = document.getElementById('profileFullName').value.trim();
    const email = document.getElementById('profileEmail').value.trim();
    const experienceLevel = document.getElementById('profileExperienceLevel').value;
    
    try {
        const response = await fetch('/api/user/profile', {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                full_name: fullName || null,
                email: email || null,
                experience_level: experienceLevel
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Perfil atualizado com sucesso!', 'success');
            await loadUserProfile();
            // Atualizar nome no header e menu
            const menuUserName = document.getElementById('menuUserName');
            if (menuUserName && fullName) menuUserName.textContent = fullName;
            const userName = document.getElementById('userName');
            if (userName && fullName) userName.textContent = fullName;
        } else {
            showToast(data.error || 'Erro ao atualizar perfil', 'error');
        }
    } catch (error) {
        showToast('Erro ao salvar perfil', 'error');
        console.error(error);
    }
}

// Alterar senha
async function changePassword() {
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    if (!currentPassword || !newPassword || !confirmPassword) {
        showToast('Preencha todos os campos', 'error');
        return;
    }
    
    if (newPassword !== confirmPassword) {
        showToast('As senhas não coincidem', 'error');
        return;
    }
    
    if (newPassword.length < 4) {
        showToast('A senha deve ter pelo menos 4 caracteres', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/user/profile/password', {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Senha alterada com sucesso!', 'success');
            // Limpar campos
            document.getElementById('currentPassword').value = '';
            document.getElementById('newPassword').value = '';
            document.getElementById('confirmPassword').value = '';
        } else {
            showToast(data.error || 'Erro ao alterar senha', 'error');
        }
    } catch (error) {
        showToast('Erro ao alterar senha', 'error');
        console.error(error);
    }
}

// Upload de foto de perfil
async function uploadProfilePicture(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validar tipo
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        showToast('Tipo de arquivo não permitido. Use: PNG, JPG, GIF ou WEBP', 'error');
        return;
    }
    
    // Validar tamanho (5MB)
    if (file.size > 5 * 1024 * 1024) {
        showToast('Arquivo muito grande. Tamanho máximo: 5MB', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/user/profile/picture', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Foto de perfil atualizada!', 'success');
            const profilePicture = document.getElementById('profilePicture');
            if (profilePicture) profilePicture.src = data.profile_picture;
            // Atualizar também no header
            updateHeaderProfilePicture(data.profile_picture);
        } else {
            showToast(data.error || 'Erro ao fazer upload', 'error');
        }
    } catch (error) {
        showToast('Erro ao fazer upload', 'error');
        console.error(error);
    }
}

// Alterar tema
async function changeTheme(theme) {
    applyTheme(theme);
    
    // Sincronizar ambos os selects de tema
    const themeSelect = document.getElementById('themeSelect');
    const themeSelectModal = document.getElementById('themeSelectModal');
    if (themeSelect) themeSelect.value = theme;
    if (themeSelectModal) themeSelectModal.value = theme;
    
    // Salvar preferência
    try {
        await fetch('/api/user/preferences', {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({theme: theme})
        });
    } catch (error) {
        console.error('Erro ao salvar tema:', error);
    }
}

// Aplicar tema
function applyTheme(theme) {
    if (theme === 'auto') {
        // Detectar preferência do sistema
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        theme = prefersDark ? 'dark' : 'light';
    }
    
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
}

// Atualizar preferência de notificações
async function updateNotificationPreference() {
    // Verificar qual checkbox foi alterado (modal ou perfil)
    const notificationsEnabled = document.getElementById('notificationsEnabled')?.checked ?? 
                                 document.getElementById('notificationsEnabledModal')?.checked ?? true;
    const emailNotifications = document.getElementById('emailNotifications')?.checked ?? 
                              document.getElementById('emailNotificationsModal')?.checked ?? false;
    
    try {
        await fetch('/api/user/preferences', {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                notifications_enabled: notificationsEnabled,
                email_notifications: emailNotifications
            })
        });
        
        // Sincronizar ambos os checkboxes
        const notificationsEnabledEl = document.getElementById('notificationsEnabled');
        const notificationsEnabledModalEl = document.getElementById('notificationsEnabledModal');
        const emailNotificationsEl = document.getElementById('emailNotifications');
        const emailNotificationsModalEl = document.getElementById('emailNotificationsModal');
        
        if (notificationsEnabledEl) notificationsEnabledEl.checked = notificationsEnabled;
        if (notificationsEnabledModalEl) notificationsEnabledModalEl.checked = notificationsEnabled;
        if (emailNotificationsEl) emailNotificationsEl.checked = emailNotifications;
        if (emailNotificationsModalEl) emailNotificationsModalEl.checked = emailNotifications;
    } catch (error) {
        console.error('Erro ao atualizar preferências:', error);
    }
}

// Carregar tema salvo ao iniciar
function loadSavedTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        applyTheme(savedTheme);
    }
}

// Inicializar tema ao carregar página
document.addEventListener('DOMContentLoaded', () => {
    loadSavedTheme();
});

// ==================== ANOTAÇÕES (KANBAN) ====================

let currentEditingNoteId = null;
let notes = [];

// Carregar anotações
async function loadNotes() {
    try {
        const response = await fetch('/api/notes');
        const data = await response.json();
        notes = data.notes || [];
        renderKanban();
    } catch (error) {
        console.error('Erro ao carregar anotações:', error);
        showToast('Erro ao carregar anotações', 'error');
    }
}

// Renderizar quadro Kanban
function renderKanban() {
    const columns = ['todo', 'doing', 'done'];
    
    columns.forEach(column => {
        const columnElement = document.getElementById(`column-${column}`);
        const countElement = document.getElementById(`count-${column}`);
        
        if (!columnElement) return;
        
        // Limpar coluna
        columnElement.innerHTML = '';
        
        // Filtrar anotações da coluna
        const columnNotes = notes
            .filter(note => note.column_name === column)
            .sort((a, b) => a.position - b.position);
        
        // Atualizar contador
        if (countElement) {
            countElement.textContent = columnNotes.length;
        }
        
        // Renderizar Post-its
        columnNotes.forEach(note => {
            const noteElement = createNoteElement(note);
            columnElement.appendChild(noteElement);
        });
    });
}

// Criar elemento de Post-it
function createNoteElement(note) {
    const div = document.createElement('div');
    div.className = `note-card note-${note.color}`;
    div.draggable = true;
    div.dataset.noteId = note.id;
    div.dataset.column = note.column_name;
    
    div.innerHTML = `
        <div class="note-header">
            <h4 class="note-title">${escapeHtml(note.title)}</h4>
            <div class="note-actions">
                <button class="note-btn-edit" onclick="editNote(${note.id})" title="Editar">✏️</button>
                <button class="note-btn-delete" onclick="deleteNote(${note.id})" title="Excluir">🗑️</button>
            </div>
        </div>
        ${note.content ? `<div class="note-content">${escapeHtml(note.content)}</div>` : ''}
        <div class="note-footer">
            <small class="note-date">${formatDate(note.updated_at)}</small>
        </div>
    `;
    
    // Event listeners para drag and drop
    div.addEventListener('dragstart', handleNoteDragStart);
    div.addEventListener('dragend', handleNoteDragEnd);
    
    return div;
}

// Funções de drag and drop para anotações
let draggedNoteElement = null;

function handleNoteDragStart(e) {
    draggedNoteElement = this;
    this.style.opacity = '0.5';
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.innerHTML);
}

function handleNoteDragEnd(e) {
    this.style.opacity = '1';
}

function allowNoteDrop(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
}

function handleNoteDrop(e) {
    e.preventDefault();
    
    if (!draggedNoteElement) return;
    
    const targetColumn = e.currentTarget;
    const newColumn = targetColumn.closest('.kanban-column').dataset.column;
    const noteId = parseInt(draggedNoteElement.dataset.noteId);
    const oldColumn = draggedNoteElement.dataset.column;
    
    // Se mudou de coluna, mover elemento
    if (oldColumn !== newColumn) {
        targetColumn.appendChild(draggedNoteElement);
        draggedNoteElement.dataset.column = newColumn;
    }
    
    // Atualizar posição no backend
    updateNotePosition(noteId, newColumn, targetColumn);
    
    draggedNoteElement = null;
}

// Atualizar posição da anotação
async function updateNotePosition(noteId, columnName, columnElement) {
    try {
        // Calcular nova posição baseada na ordem atual
        const notesInColumn = Array.from(columnElement.children)
            .filter(el => el.classList.contains('note-card'))
            .map((el, index) => [parseInt(el.dataset.noteId), index]);
        
        // Atualizar todas as notas da coluna no backend
        if (notesInColumn.length > 0) {
            await fetch('/api/notes/positions', {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    column_name: columnName,
                    positions: notesInColumn
                })
            });
        }
        
        // Atualizar nota específica (mudança de coluna)
        const note = notes.find(n => n.id === noteId);
        if (note) {
            await fetch(`/api/notes/${noteId}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    column_name: columnName
                })
            });
        }
        
        // Recarregar anotações para sincronizar
        await loadNotes();
    } catch (error) {
        console.error('Erro ao atualizar posição:', error);
        showToast('Erro ao mover anotação', 'error');
        // Recarregar anotações em caso de erro
        await loadNotes();
    }
}

// Abrir modal para nova anotação
function openNewNoteModal() {
    currentEditingNoteId = null;
    document.getElementById('noteModalTitle').textContent = '➕ Nova Anotação';
    document.getElementById('noteTitle').value = '';
    document.getElementById('noteContent').value = '';
    document.getElementById('noteColor').value = 'yellow';
    document.getElementById('noteColumn').value = 'todo';
    document.getElementById('noteModal').style.display = 'flex';
}

// Editar anotação
function editNote(noteId) {
    const note = notes.find(n => n.id === noteId);
    if (!note) return;
    
    currentEditingNoteId = noteId;
    document.getElementById('noteModalTitle').textContent = '✏️ Editar Anotação';
    document.getElementById('noteTitle').value = note.title;
    document.getElementById('noteContent').value = note.content || '';
    document.getElementById('noteColor').value = note.color || 'yellow';
    document.getElementById('noteColumn').value = note.column_name || 'todo';
    document.getElementById('noteModal').style.display = 'flex';
}

// Fechar modal
function closeNoteModal() {
    document.getElementById('noteModal').style.display = 'none';
    currentEditingNoteId = null;
}

// Salvar anotação
async function saveNote() {
    const title = document.getElementById('noteTitle').value.trim();
    if (!title) {
        showToast('Título é obrigatório', 'error');
        return;
    }
    
    const content = document.getElementById('noteContent').value.trim();
    const color = document.getElementById('noteColor').value;
    const column = document.getElementById('noteColumn').value;
    
    try {
        if (currentEditingNoteId) {
            // Atualizar anotação existente
            await fetch(`/api/notes/${currentEditingNoteId}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    title,
                    content,
                    color,
                    column_name: column
                })
            });
            showToast('Anotação atualizada com sucesso', 'success');
        } else {
            // Criar nova anotação
            await fetch('/api/notes', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    title,
                    content,
                    color,
                    column_name: column
                })
            });
            showToast('Anotação criada com sucesso', 'success');
        }
        
        closeNoteModal();
        await loadNotes();
    } catch (error) {
        console.error('Erro ao salvar anotação:', error);
        showToast('Erro ao salvar anotação', 'error');
    }
}

// Deletar anotação
async function deleteNote(noteId) {
    if (!confirm('Tem certeza que deseja excluir esta anotação?')) {
        return;
    }
    
    try {
        await fetch(`/api/notes/${noteId}`, {
            method: 'DELETE'
        });
        showToast('Anotação excluída com sucesso', 'success');
        await loadNotes();
    } catch (error) {
        console.error('Erro ao deletar anotação:', error);
        showToast('Erro ao excluir anotação', 'error');
    }
}

// Funções auxiliares
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

// ==================== TESTES PERSONALIZADOS ====================

let currentEditingTestId = null;
let testActions = [];

// Abrir modal para criar teste
function openCreateTestModal() {
    currentEditingTestId = null;
    testActions = [];
    document.getElementById('createTestModalTitle').textContent = '➕ Criar Teste Personalizado';
    document.getElementById('testId').value = '';
    document.getElementById('testId').disabled = false;
    document.getElementById('testName').value = '';
    document.getElementById('testDescription').value = '';
    document.getElementById('testModule').value = '';
    document.getElementById('testPriority').value = '3';
    document.getElementById('testImpact').value = 'non_destructive';
    document.getElementById('testTags').value = '';
    document.getElementById('testActionsContainer').innerHTML = '';
    document.getElementById('createTestModal').style.display = 'flex';
}

// Fechar modal
function closeCreateTestModal() {
    document.getElementById('createTestModal').style.display = 'none';
    currentEditingTestId = null;
    testActions = [];
}

// Adicionar ação ao teste
function addTestAction(actionData = null) {
    const container = document.getElementById('testActionsContainer');
    const actionIndex = testActions.length;
    
    const actionDiv = document.createElement('div');
    actionDiv.className = 'test-action-item';
    actionDiv.dataset.index = actionIndex;
    
    // Escapar valores para segurança
    const safeDesc = actionData?.description ? escapeHtml(actionData.description) : '';
    
    actionDiv.innerHTML = `
        <div class="action-header">
            <h4>Ação ${actionIndex + 1}</h4>
            <button type="button" class="btn-icon" onclick="removeTestAction(${actionIndex})" title="Remover">🗑️</button>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Descrição *</label>
                <input type="text" class="action-description" placeholder="Ex: Clicar no botão de login" value="${safeDesc}">
            </div>
            <div class="form-group">
                <label>Tipo</label>
                <select class="action-type">
                    <option value="navigation" ${actionData?.action_type === 'navigation' ? 'selected' : ''}>🧭 Navegação</option>
                    <option value="creation" ${actionData?.action_type === 'creation' ? 'selected' : ''}>➕ Criação</option>
                    <option value="verification" ${actionData?.action_type === 'verification' || !actionData ? 'selected' : ''}>✓ Verificação</option>
                    <option value="modification" ${actionData?.action_type === 'modification' ? 'selected' : ''}>✏️ Modificação</option>
                    <option value="deletion" ${actionData?.action_type === 'deletion' ? 'selected' : ''}>🗑️ Deleção</option>
                </select>
            </div>
            <div class="form-group">
                <label>Impacto</label>
                <select class="action-impact">
                    <option value="non_destructive" ${actionData?.impact === 'non_destructive' || !actionData ? 'selected' : ''}>🟢 Não-Destrutivo</option>
                    <option value="partially_destructive" ${actionData?.impact === 'partially_destructive' ? 'selected' : ''}>🟡 Parcialmente Destrutivo</option>
                    <option value="destructive" ${actionData?.impact === 'destructive' ? 'selected' : ''}>🔴 Destrutivo</option>
                </select>
            </div>
            <div class="form-group">
                <label>Tempo Estimado (s)</label>
                <input type="number" class="action-time" min="0" step="0.1" value="${actionData?.estimated_time || 5.0}">
            </div>
        </div>
    `;
    
    container.appendChild(actionDiv);
    
    // Adicionar ao array apenas se não for uma re-renderização (quando actionData é null, é uma nova ação)
    if (!actionData) {
        testActions.push({
            id: `action-${actionIndex}`,
            description: '',
            action_type: 'verification',
            impact: 'non_destructive',
            estimated_time: 5.0,
            preconditions: [],
            postconditions: [],
            priority: 1,
            tags: []
        });
    }
    // Se actionData existe, já foi adicionado em renderTestActions, não adicionar novamente
}

// Remover ação
function removeTestAction(index) {
    testActions.splice(index, 1);
    renderTestActions();
}

// Re-renderizar ações
function renderTestActions() {
    const container = document.getElementById('testActionsContainer');
    container.innerHTML = '';
    const actionsCopy = [...testActions]; // Copiar array
    testActions = []; // Limpar array antes de re-renderizar
    actionsCopy.forEach((action) => {
        // Adicionar diretamente ao array sem duplicar
        testActions.push(action);
        const actionIndex = testActions.length - 1;
        
        const actionDiv = document.createElement('div');
        actionDiv.className = 'test-action-item';
        actionDiv.dataset.index = actionIndex;
        
        const safeDesc = action.description ? escapeHtml(action.description) : '';
        
        actionDiv.innerHTML = `
            <div class="action-header">
                <h4>Ação ${actionIndex + 1}</h4>
                <button type="button" class="btn-icon" onclick="removeTestAction(${actionIndex})" title="Remover">🗑️</button>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Descrição *</label>
                    <input type="text" class="action-description" placeholder="Ex: Clicar no botão de login" value="${safeDesc}">
                </div>
                <div class="form-group">
                    <label>Tipo</label>
                    <select class="action-type">
                        <option value="navigation" ${action.action_type === 'navigation' ? 'selected' : ''}>🧭 Navegação</option>
                        <option value="creation" ${action.action_type === 'creation' ? 'selected' : ''}>➕ Criação</option>
                        <option value="verification" ${action.action_type === 'verification' || !action.action_type ? 'selected' : ''}>✓ Verificação</option>
                        <option value="modification" ${action.action_type === 'modification' ? 'selected' : ''}>✏️ Modificação</option>
                        <option value="deletion" ${action.action_type === 'deletion' ? 'selected' : ''}>🗑️ Deleção</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Impacto</label>
                    <select class="action-impact">
                        <option value="non_destructive" ${action.impact === 'non_destructive' || !action.impact ? 'selected' : ''}>🟢 Não-Destrutivo</option>
                        <option value="partially_destructive" ${action.impact === 'partially_destructive' ? 'selected' : ''}>🟡 Parcialmente Destrutivo</option>
                        <option value="destructive" ${action.impact === 'destructive' ? 'selected' : ''}>🔴 Destrutivo</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Tempo Estimado (s)</label>
                    <input type="number" class="action-time" min="0" step="0.1" value="${action.estimated_time || 5.0}">
                </div>
            </div>
        `;
        
        container.appendChild(actionDiv);
    });
}

// Salvar teste personalizado
async function saveUserTest() {
    const testId = document.getElementById('testId').value.trim();
    const testName = document.getElementById('testName').value.trim();
    
    if (!testId) {
        showToast('ID do teste é obrigatório', 'error');
        return;
    }
    if (!testName) {
        showToast('Nome do teste é obrigatório', 'error');
        return;
    }
    
    // Coletar dados das ações
    const actionElements = document.querySelectorAll('.test-action-item');
    const actions = [];
    actionElements.forEach((element, index) => {
        const description = element.querySelector('.action-description').value.trim();
        if (!description) return; // Pular ações sem descrição
        
        actions.push({
            id: `action-${index}`,
            description: description,
            action_type: element.querySelector('.action-type').value,
            impact: element.querySelector('.action-impact').value,
            estimated_time: parseFloat(element.querySelector('.action-time').value) || 5.0,
            preconditions: [],
            postconditions: [],
            priority: 1,
            tags: []
        });
    });
    
    // Preparar dados do teste
    const tags = document.getElementById('testTags').value
        .split(',')
        .map(t => t.trim())
        .filter(t => t);
    
    const testData = {
        test_id: testId,
        name: testName,
        description: document.getElementById('testDescription').value.trim(),
        module: document.getElementById('testModule').value.trim() || 'Personalizado',
        priority: parseInt(document.getElementById('testPriority').value),
        impact_level: document.getElementById('testImpact').value,
        tags: tags,
        actions: actions,
        estimated_time: actions.reduce((sum, a) => sum + a.estimated_time, 0)
    };
    
    try {
        const url = currentEditingTestId 
            ? `/api/user/test-cases/${currentEditingTestId}`
            : '/api/user/test-cases';
        const method = currentEditingTestId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(testData)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Erro ao salvar teste');
        }
        
        showToast(currentEditingTestId ? 'Teste atualizado com sucesso' : 'Teste criado com sucesso', 'success');
        closeCreateTestModal();
        
        // Recarregar lista de testes
        if (document.getElementById('tab-testes').classList.contains('active')) {
            await loadAllTests();
        }
    } catch (error) {
        console.error('Erro ao salvar teste:', error);
        showToast(error.message || 'Erro ao salvar teste', 'error');
    }
}

// Editar teste personalizado
async function editUserTest(testId) {
    try {
        const response = await fetch(`/api/user/test-cases/${testId}`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Erro ao carregar teste');
        }
        
        const test = data.test_case;
        currentEditingTestId = testId;
        testActions = test.actions || [];
        
        document.getElementById('createTestModalTitle').textContent = '✏️ Editar Teste Personalizado';
        document.getElementById('testId').value = test.test_id;
        document.getElementById('testId').disabled = true; // Não permitir editar ID
        document.getElementById('testName').value = test.name;
        document.getElementById('testDescription').value = test.description || '';
        document.getElementById('testModule').value = test.module || '';
        document.getElementById('testPriority').value = test.priority || 3;
        document.getElementById('testImpact').value = test.impact_level || 'non_destructive';
        document.getElementById('testTags').value = (test.tags || []).join(', ');
        
        renderTestActions();
        document.getElementById('createTestModal').style.display = 'flex';
    } catch (error) {
        console.error('Erro ao carregar teste:', error);
        showToast('Erro ao carregar teste', 'error');
    }
}

// Deletar teste personalizado
async function deleteUserTest(testId) {
    if (!confirm('Tem certeza que deseja excluir este teste personalizado?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/user/test-cases/${testId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Erro ao deletar teste');
        }
        
        showToast('Teste excluído com sucesso', 'success');
        
        // Remover teste da lista de selecionados se estiver selecionado
        const index = selectedTests.indexOf(testId);
        if (index > -1) {
            selectedTests.splice(index, 1);
            // Atualizar display de testes selecionados
            const summary = document.getElementById('selectedSummary');
            const count = document.getElementById('selectedCount');
            const time = document.getElementById('selectedTime');
            const btn = document.getElementById('btnSolicitar');
            
            if (selectedTests.length === 0) {
                if (summary) summary.style.display = 'none';
                if (btn) {
                    btn.disabled = true;
                    btn.textContent = '🤖 Selecione ao menos 1 teste';
                }
            } else {
                if (summary) summary.style.display = 'block';
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = '🤖 Solicitar Recomendação de Ordem';
                }
                if (count) count.textContent = selectedTests.length;
                
                const totalTime = selectedTests.reduce((sum, testId) => {
                    const test = allTests.find(t => t.id === testId);
                    return sum + (test ? test.estimated_time : 0);
                }, 0);
                if (time) time.textContent = `${(totalTime / 60).toFixed(1)} min`;
            }
        }
        
        // Recarregar todas as listas de testes
        await loadTests();
        await loadTestSelection();
        
        // Recarregar lista de testes na aba "Todos os Testes"
        if (document.getElementById('tab-testes').classList.contains('active')) {
            await loadAllTests();
        }
    } catch (error) {
        console.error('Erro ao deletar teste:', error);
        showToast('Erro ao excluir teste', 'error');
    }
}
