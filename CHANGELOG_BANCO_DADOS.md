# 📝 CHANGELOG: MIGRAÇÃO PARA SQLITE

## 🎯 Resumo da Mudança

O sistema IARTES agora utiliza **banco de dados SQLite** para armazenar feedbacks e histórico, em vez de depender apenas de arquivos pickle.

---

## ✨ O QUE FOI IMPLEMENTADO

### 1. **Módulo de Banco de Dados** (`src/utils/database.py`)

Novo módulo completo com:
- ✅ Classe `IARTESDatabase` para gerenciar SQLite
- ✅ 3 tabelas: `feedbacks`, `recommendations`, `executions`
- ✅ Índices para performance
- ✅ Métodos para CRUD e consultas
- ✅ Estatísticas agregadas
- ✅ Suporte a context manager

### 2. **Scripts de Utilitários**

#### **`migrar_pickle_para_sqlite.py`**
- Migra feedbacks existentes do `.pkl` para `.db`
- Validação e relatório de progresso
- **Resultado**: 172 feedbacks migrados com sucesso ✅

#### **`ver_banco_dados.py`**
- Visualiza dados do banco de forma amigável
- Estatísticas gerais e por teste
- Últimos feedbacks

#### **`gerar_relatorio.py`**
- Gera relatórios em CSV e TXT
- Exporta dados para Excel/LibreOffice
- 3 tipos de relatório:
  - Todos os feedbacks
  - Estatísticas por teste
  - Resumo geral

#### **`ver_dados_salvos.py`** (mantido para compatibilidade)
- Visualiza dados do pickle (legado)

### 3. **Integração com Interface Web** (`app_web.py`)

- ✅ Importa módulo de banco de dados
- ✅ Cria instância global `db`
- ✅ **Rota `/api/feedback`**: salva no BD + pickle
- ✅ **Rota `/api/estatisticas`**: busca do BD
- ✅ Estatísticas em tempo real do banco

### 4. **Documentação Completa**

- ✅ **`BANCO_DE_DADOS.md`**: guia completo
  - Estrutura das tabelas
  - Consultas SQL úteis
  - Como visualizar dados
  - Backup e restore
  - Solução de problemas
- ✅ **README.md** atualizado
- ✅ Este changelog

---

## 🔄 ANTES vs DEPOIS

### ❌ ANTES (Apenas Pickle)

```
📦 models/motorola_modelo.pkl
   ├─ Modelo ML
   ├─ Feedbacks (172)
   ├─ Dados de treinamento
   └─ Histórico

Problemas:
- Formato binário (difícil visualizar)
- Sem consultas SQL
- Difícil gerar relatórios
- Um único arquivo
```

### ✅ DEPOIS (Pickle + SQLite)

```
📦 models/motorola_modelo.pkl
   ├─ Modelo ML
   └─ Dados de treinamento

🗄️ iartes.db (NOVO!)
   ├─ feedbacks (172 registros)
   ├─ recommendations
   └─ executions

Benefícios:
- Consultas SQL poderosas
- Fácil visualizar (DB Browser)
- Relatórios automáticos
- Exportar para Excel
- Backup separado
```

---

## 📊 ESTRUTURA DO BANCO

### Tabela `feedbacks`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | INTEGER PK | ID único |
| test_case_id | TEXT | Teste executado |
| executed_at | TIMESTAMP | Data/hora |
| actual_execution_time | REAL | Tempo real (s) |
| success | BOOLEAN | Passou/falhou |
| followed_recommendation | BOOLEAN | Seguiu ordem? |
| tester_rating | INTEGER | Avaliação 1-5 |
| required_reset | BOOLEAN | Precisou reset? |
| notes | TEXT | Observações |
| initial_state | TEXT | Estado inicial (JSON) |
| final_state | TEXT | Estado final (JSON) |
| created_at | TIMESTAMP | Inserido no BD |

**Índices**: test_case_id, executed_at, success

### Tabela `recommendations`

Histórico de recomendações geradas pela IA.

### Tabela `executions`

Tracking de sessões de execução de testes.

---

## 🛠️ NOVOS COMANDOS

### Visualizar Dados

```bash
python ver_banco_dados.py
```

**Output:**
```
📊 ESTATÍSTICAS GERAIS
Total de feedbacks: 172
Taxa de sucesso: 39.0%
Avaliação média: 2.6/5
...
```

### Gerar Relatórios

```bash
python gerar_relatorio.py
```

**Output:**
```
📁 Arquivos criados:
- relatorio_feedbacks_20260115_120000.csv
- relatorio_testes_20260115_120000.csv  
- relatorio_resumo_20260115_120000.txt
```

### Consultas SQL Customizadas

```bash
sqlite3 iartes.db

# Exemplo: testes com menor taxa de sucesso
SELECT test_case_id, 
       COUNT(*) as total,
       AVG(success) * 100 as taxa_sucesso
FROM feedbacks
GROUP BY test_case_id
ORDER BY taxa_sucesso ASC
LIMIT 5;
```

---

## 🔍 DADOS MIGRADOS

```
✅ Migração bem-sucedida!

Origem: models/motorola_modelo.pkl
Destino: iartes.db

📊 Resultados:
- Total no pickle: 172 feedbacks
- Migrados: 172 (100%)
- Erros: 0
- Taxa de sucesso geral: 39.0%
- Avaliação média: 2.6/5
- Tempo médio: 10.2s
```

---

## 📈 CONSULTAS ÚTEIS

### 1. Top 5 testes mais executados

```sql
SELECT test_case_id, COUNT(*) as total
FROM feedbacks
GROUP BY test_case_id
ORDER BY total DESC
LIMIT 5;
```

### 2. Feedbacks da última semana

```sql
SELECT *
FROM feedbacks
WHERE executed_at >= datetime('now', '-7 days')
ORDER BY executed_at DESC;
```

### 3. Taxa de sucesso por módulo

```sql
SELECT 
    SUBSTR(test_case_id, 1, INSTR(test_case_id, '_')) as modulo,
    AVG(success) * 100 as taxa_sucesso
FROM feedbacks
GROUP BY modulo
ORDER BY taxa_sucesso DESC;
```

---

## 🎯 IMPACTO

### Para o Testador

- ✅ Visualiza dados facilmente (DB Browser)
- ✅ Gera relatórios para gerência (Excel)
- ✅ Histórico completo consultável
- ✅ Backup independente do modelo

### Para a IA

- ✅ Modelo ML continua funcionando igual
- ✅ Dados em formato aberto (SQL)
- ✅ Facilita análises futuras
- ✅ Base para dashboards web

### Para o Sistema

- ✅ Mais robusto (dados separados)
- ✅ Mais flexível (SQL queries)
- ✅ Mais escalável (pode migrar para PostgreSQL)
- ✅ Mais transparente (dados abertos)

---

## 🔄 COMPATIBILIDADE

### ✅ Mantido (Funciona Como Antes)

- Interface web (`python app_web.py`)
- Recomendações da IA
- Treinamento do modelo ML
- Arquivo pickle (continua sendo usado)
- Todos os scripts examples/

### 🆕 Novo (Funcionalidades Extras)

- Consultas SQL diretas
- Relatórios CSV/Excel
- Visualização amigável dos dados
- Estatísticas agregadas
- Backup/restore facilitado

---

## 📚 DOCUMENTAÇÃO ATUALIZADA

- ✅ **`BANCO_DE_DADOS.md`** ← **Leia para detalhes técnicos**
- ✅ `README.md` (seção de banco adicionada)
- ✅ `CHANGELOG_BANCO_DADOS.md` (este arquivo)
- ✅ Comentários nos scripts novos

---

## 🚀 PRÓXIMOS PASSOS

### Imediato

1. ✅ Sistema funcionando com SQLite
2. ✅ 172 feedbacks migrados
3. ✅ Scripts de consulta prontos
4. ✅ Documentação completa

### Futuro (Opcional)

1. **Dashboard Web**: visualizar dados na interface
2. **Exportar Excel**: botão na interface web
3. **Filtros Avançados**: consultar por período
4. **Alertas**: notificar testes problemáticos
5. **PostgreSQL**: se precisar multi-usuário

---

## 🆘 PRECISA DE AJUDA?

### Ver dados do banco

```bash
python ver_banco_dados.py
```

### Gerar relatório para gerência

```bash
python gerar_relatorio.py
```

### Consulta SQL customizada

```bash
sqlite3 iartes.db
.help
```

### Problemas?

Veja **BANCO_DE_DADOS.md** seção "Solução de Problemas"

---

**Data**: 2026-01-15  
**Status**: ✅ **IMPLEMENTAÇÃO COMPLETA E TESTADA**  
**Migração**: ✅ **172 feedbacks migrados com sucesso**
