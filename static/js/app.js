// Estado global
let allTests = [];
let selectedTests = [];
let currentRecommendation = null;
let originalRecommendedOrder = [];  // NOVO: ordem original da IA
let acceptedOrder = [];              // Ordem final aceita (pode ser modificada)
let currentStats = null;
let charts = {};

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
    setupTabs();
    setupRating();
    setupForm();
    loadInitialData();
});

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
    } else if (tabName === 'testes') {
        loadAllTests();
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
        allTests = await response.json();
        
        // Popular select de feedback
        const select = document.getElementById('testSelect');
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
            if (selectedOption.dataset.time) {
                document.getElementById('actualTime').value = selectedOption.dataset.time;
            }
        });
        
        return allTests;
    } catch (error) {
        console.error('Erro ao carregar testes:', error);
        throw error;
    }
}

// Carregar testes para seleção (Etapa 1)
async function loadTestSelection() {
    const container = document.getElementById('testSelectionGrid');
    const moduleFilter = document.getElementById('filterModuleSelect');
    const searchInput = document.getElementById('searchTestsSelect');
    
    // Popular filtro de módulos
    const modules = [...new Set(allTests.map(t => t.module))];
    moduleFilter.innerHTML = '<option value="">Todos os Módulos</option>';
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
            fetch('/api/testes').then(r => r.json()),
            fetch('/api/estatisticas').then(r => r.json())
        ]);
        
        document.getElementById('totalTests').textContent = testsData.length;
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
        if (allTests.length === 0) {
            await loadTests();
        }
        
        displayAllTests(allTests);
    } catch (error) {
        console.error('Erro ao carregar todos os testes:', error);
    }
}

// Exibir todos os testes
function displayAllTests(tests) {
    const container = document.getElementById('allTests');
    const moduleFilter = document.getElementById('filterModule');
    const priorityFilter = document.getElementById('filterPriority');
    const searchInput = document.getElementById('searchTests');
    
    // Popular filtro de módulos
    const modules = [...new Set(tests.map(t => t.module))];
    moduleFilter.innerHTML = '<option value="">Todos os Módulos</option>';
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
        const priorityValue = priorityFilter.value;
        
        const filtered = tests.filter(test => {
            const matchesSearch = !searchTerm || 
                test.name.toLowerCase().includes(searchTerm) ||
                test.id.toLowerCase().includes(searchTerm) ||
                test.description.toLowerCase().includes(searchTerm);
            
            const matchesModule = !moduleValue || test.module === moduleValue;
            const matchesPriority = !priorityValue || test.priority === parseInt(priorityValue);
            
            return matchesSearch && matchesModule && matchesPriority;
        });
        
        renderTestCards(filtered);
    };
    
    // Event listeners para filtros
    searchInput.addEventListener('input', filterTests);
    moduleFilter.addEventListener('change', filterTests);
    priorityFilter.addEventListener('change', filterTests);
    
    // Renderizar inicial
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
        card.innerHTML = `
            <div class="test-card-header">
                <div class="test-card-id">${test.id}</div>
                <div class="test-card-title">${test.name}</div>
                <div class="test-card-description">${test.description}</div>
            </div>
            <div class="test-card-footer">
                <span class="test-badge badge-module">📦 ${test.module}</span>
                <span class="test-badge badge-priority">🎯 P${test.priority}</span>
                <span class="test-badge badge-time">⏱️ ${test.estimated_time.toFixed(0)}s</span>
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
