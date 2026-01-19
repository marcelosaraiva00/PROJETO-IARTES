# 🗄️ BANCO DE DADOS SQLITE

## 📋 Visão Geral

O sistema IARTES agora utiliza **SQLite** para armazenar todos os feedbacks de execução de testes e histórico de recomendações.

### ✅ O que é armazenado

- **Feedbacks**: Todos os feedbacks de execução de testes (tempo, sucesso, avaliação, etc.)
- **Recomendações**: Histórico de recomendações geradas pela IA
- **Execuções**: Tracking de sessões de execução

### 💾 Onde está o banco

```
IARTES/
├── iartes.db          ← Banco de dados SQLite
└── models/
    └── motorola_modelo.pkl  ← Modelo ML (continua em pickle)
```

**Importante:** O modelo de Machine Learning continua sendo salvo em arquivo `.pkl` (é o padrão). O banco de dados armazena os **dados** (feedbacks, histórico).

---

## 📊 ESTRUTURA DO BANCO

### Tabela: `feedbacks`

Armazena todos os feedbacks de execução.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | INTEGER | ID único (auto increment) |
| `test_case_id` | TEXT | ID do teste executado |
| `executed_at` | TIMESTAMP | Data/hora da execução |
| `actual_execution_time` | REAL | Tempo real de execução (segundos) |
| `success` | BOOLEAN | Se o teste passou (1) ou falhou (0) |
| `followed_recommendation` | BOOLEAN | Se seguiu a ordem recomendada |
| `tester_rating` | INTEGER | Avaliação (1-5 estrelas) |
| `required_reset` | BOOLEAN | Se precisou reiniciar dispositivo |
| `notes` | TEXT | Observações do testador |
| `initial_state` | TEXT | Estado inicial (JSON) |
| `final_state` | TEXT | Estado final (JSON) |
| `created_at` | TIMESTAMP | Quando foi inserido no BD |

**Índices:**
- `idx_feedbacks_test_id` (test_case_id)
- `idx_feedbacks_executed_at` (executed_at)
- `idx_feedbacks_success` (success)

### Tabela: `recommendations`

Armazena histórico de recomendações geradas.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | INTEGER | ID único |
| `created_at` | TIMESTAMP | Quando foi gerada |
| `test_ids` | TEXT | IDs dos testes selecionados (JSON) |
| `recommended_order` | TEXT | Ordem recomendada (JSON) |
| `method` | TEXT | Método usado (heuristic/ml) |
| `confidence_score` | REAL | Nível de confiança (0-1) |
| `estimated_total_time` | REAL | Tempo total estimado |
| `estimated_resets` | INTEGER | Resets estimados |
| `was_accepted` | BOOLEAN | Se foi aceita pelo usuário |
| `user_modifications` | TEXT | Modificações feitas (JSON) |

### Tabela: `executions`

Tracking de sessões de execução.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | INTEGER | ID único |
| `recommendation_id` | INTEGER | FK para recommendations |
| `started_at` | TIMESTAMP | Início da sessão |
| `finished_at` | TIMESTAMP | Fim da sessão |
| `total_tests` | INTEGER | Total de testes |
| `successful_tests` | INTEGER | Testes que passaram |
| `failed_tests` | INTEGER | Testes que falharam |
| `total_time` | REAL | Tempo total real |
| `actual_resets` | INTEGER | Resets reais |

---

## 🛠️ FERRAMENTAS DISPONÍVEIS

### 1️⃣ Visualizar Dados

```bash
python ver_banco_dados.py
```

Mostra:
- Estatísticas gerais
- Top 10 testes mais executados
- Últimos 10 feedbacks

### 2️⃣ Gerar Relatórios

```bash
python gerar_relatorio.py
```

Gera 3 arquivos:
- `relatorio_feedbacks_YYYYMMDD_HHMMSS.csv` - Todos os feedbacks
- `relatorio_testes_YYYYMMDD_HHMMSS.csv` - Estatísticas por teste
- `relatorio_resumo_YYYYMMDD_HHMMSS.txt` - Resumo geral

💡 Abra os `.csv` no Excel ou LibreOffice!

### 3️⃣ Ver Dados Salvos no Pickle (legado)

```bash
python ver_dados_salvos.py
```

Mostra o que está salvo no modelo pickle (para comparação).

---

## 🔍 COMO CONSULTAR MANUALMENTE

### Opção 1: DB Browser for SQLite (Recomendado)

1. Baixe: [https://sqlitebrowser.org/](https://sqlitebrowser.org/)
2. Abra: `File → Open Database → iartes.db`
3. Navegue pelas tabelas, faça consultas SQL, exporte dados

### Opção 2: Python

```python
import sqlite3

conn = sqlite3.connect('iartes.db')
cursor = conn.cursor()

# Exemplo: todos os feedbacks de um teste
cursor.execute("""
    SELECT * FROM feedbacks 
    WHERE test_case_id = 'MOTO_CAM_001'
""")

for row in cursor.fetchall():
    print(row)

conn.close()
```

### Opção 3: CLI do SQLite

```bash
sqlite3 iartes.db

# Dentro do CLI:
.tables                    # Listar tabelas
.schema feedbacks          # Ver estrutura
SELECT * FROM feedbacks LIMIT 10;
.quit                      # Sair
```

---

## 📈 CONSULTAS SQL ÚTEIS

### 1. Testes com menor taxa de sucesso

```sql
SELECT 
    test_case_id,
    COUNT(*) as total,
    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as sucessos,
    ROUND(AVG(CASE WHEN success = 1 THEN 100.0 ELSE 0.0 END), 1) as taxa_sucesso
FROM feedbacks
GROUP BY test_case_id
HAVING total >= 3
ORDER BY taxa_sucesso ASC
LIMIT 10;
```

### 2. Feedbacks da última semana

```sql
SELECT 
    test_case_id,
    executed_at,
    success,
    actual_execution_time,
    tester_rating
FROM feedbacks
WHERE executed_at >= datetime('now', '-7 days')
ORDER BY executed_at DESC;
```

### 3. Testes que mais precisam de reset

```sql
SELECT 
    test_case_id,
    COUNT(*) as total_execucoes,
    SUM(required_reset) as total_resets,
    ROUND(AVG(required_reset) * 100, 1) as taxa_reset
FROM feedbacks
GROUP BY test_case_id
HAVING total_resets > 0
ORDER BY taxa_reset DESC;
```

### 4. Evolução das avaliações ao longo do tempo

```sql
SELECT 
    DATE(executed_at) as data,
    AVG(tester_rating) as rating_medio,
    COUNT(*) as total_feedbacks
FROM feedbacks
WHERE tester_rating IS NOT NULL
GROUP BY DATE(executed_at)
ORDER BY data DESC
LIMIT 30;
```

### 5. Comparação: seguiu vs não seguiu recomendação

```sql
SELECT 
    followed_recommendation,
    COUNT(*) as total,
    AVG(actual_execution_time) as tempo_medio,
    AVG(tester_rating) as rating_medio,
    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as sucessos
FROM feedbacks
GROUP BY followed_recommendation;
```

---

## 🔄 FLUXO DE DADOS

```
1. Testador dá feedback na interface web
                ↓
2. app_web.py recebe feedback
                ↓
3. Feedback vai para 2 lugares:
   ├─→ recommender.add_feedback()  → modelo ML treina
   │   └─→ recommender.save_model("motorola_modelo.pkl")
   └─→ db.add_feedback()           → banco de dados
                ↓
4. Dados disponíveis para:
   - Interface web (estatísticas)
   - Relatórios (CSV/Excel)
   - Consultas SQL customizadas
```

---

## 🔒 BACKUP

### Backup Simples

```bash
# Copiar arquivo do banco
copy iartes.db iartes_backup_YYYYMMDD.db
```

### Backup Automatizado (PowerShell)

```powershell
# backup_db.ps1
$data = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item iartes.db -Destination "backups\iartes_$data.db"
Write-Host "Backup criado: backups\iartes_$data.db"
```

### Restaurar Backup

```bash
# Substituir banco atual pelo backup
copy iartes_backup_20260115.db iartes.db
```

---

## 📊 ESTATÍSTICAS ATUAIS

Após migração:
- ✅ **172 feedbacks** migrados do pickle
- ✅ **34 testes** Motorola com dados
- ✅ Taxa de sucesso geral: **39%**
- ✅ Avaliação média: **2.6/5**
- ✅ Tempo médio de execução: **10.2s**

---

## 🆘 SOLUÇÃO DE PROBLEMAS

### Banco corrompido

```python
# Recriar banco do zero
import os
os.remove('iartes.db')

# Depois re-migrar
python migrar_pickle_para_sqlite.py
```

### Dados duplicados

```sql
-- Verificar duplicatas
SELECT test_case_id, executed_at, COUNT(*) 
FROM feedbacks 
GROUP BY test_case_id, executed_at 
HAVING COUNT(*) > 1;

-- Remover duplicatas (CUIDADO!)
DELETE FROM feedbacks
WHERE id NOT IN (
    SELECT MIN(id)
    FROM feedbacks
    GROUP BY test_case_id, executed_at
);
```

### Performance lenta

```sql
-- Recriar índices
DROP INDEX idx_feedbacks_test_id;
DROP INDEX idx_feedbacks_executed_at;
DROP INDEX idx_feedbacks_success;

CREATE INDEX idx_feedbacks_test_id ON feedbacks(test_case_id);
CREATE INDEX idx_feedbacks_executed_at ON feedbacks(executed_at);
CREATE INDEX idx_feedbacks_success ON feedbacks(success);

-- Otimizar banco
VACUUM;
ANALYZE;
```

---

## 💡 PRÓXIMOS PASSOS

### Funcionalidades Futuras

1. **Dashboard Web**: Gráficos interativos do banco
2. **Exportar para Excel**: Botão na interface web
3. **Filtros Avançados**: Consultar por período, módulo, sucesso
4. **Comparações**: "Setembro vs Outubro"
5. **Alertas**: "Teste X falhou 3x seguidas"

### Migração para PostgreSQL (opcional)

Se precisar de mais robustez (múltiplos usuários, produção):

```python
# Em vez de SQLite:
db = get_database("iartes.db")

# PostgreSQL:
db = get_database("postgresql://user:pass@localhost/iartes")
```

O código já está preparado para isso (usa SQL padrão).

---

## 📚 RECURSOS

- **DB Browser**: [https://sqlitebrowser.org/](https://sqlitebrowser.org/)
- **SQLite Docs**: [https://www.sqlite.org/docs.html](https://www.sqlite.org/docs.html)
- **SQL Tutorial**: [https://www.w3schools.com/sql/](https://www.w3schools.com/sql/)

---

**Última atualização**: 2026-01-15
