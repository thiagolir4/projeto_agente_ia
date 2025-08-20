# API dos Agentes - Documentação

## Visão Geral

Esta API implementa dois agentes especializados usando Agno:

1. **DataAgent**: Analisa dados e retorna tabelas Markdown
2. **InsightAgent**: Gera insights executivos baseados na saída do DataAgent

## Endpoints

### 1. Análise de Dados (`POST /chat/data`)

**Descrição**: Executa análise de dados usando o DataAgent

**Request Body**:

```json
{
  "session_id": "string",
  "prompt": "string"
}
```

**Response**:

```json
{
  "success": true,
  "message": "Análise de dados concluída com sucesso",
  "data": {
    "session_id": "string",
    "prompt": "string",
    "response": "string (tabelas Markdown)",
    "response_type": "markdown_table"
  }
}
```

**Exemplo de uso**:

```bash
curl -X POST "http://localhost:8000/chat/data" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sessao_001",
    "prompt": "Mostre os primeiros 10 registros da tabela"
  }'
```

### 2. Geração de Insights (`POST /chat/insight`)

**Descrição**: Gera insights executivos baseados na saída do DataAgent

**Request Body**:

```json
{
  "session_id": "string",
  "context": "string (saída do DataAgent em Markdown)"
}
```

**Response**:

```json
{
  "success": true,
  "message": "Insights gerados com sucesso",
  "data": {
    "session_id": "string",
    "insights": "string (resumo executivo em bullet points)",
    "response_type": "executive_summary"
  }
}
```

**Exemplo de uso**:

```bash
curl -X POST "http://localhost:8000/chat/insight" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sessao_001",
    "context": "| Coluna | Valor |\n|--------|-------|\n| Dado1  | 100   |"
  }'
```

### 3. Informações da Sessão (`GET /chat/sessions/{session_id}/info`)

**Descrição**: Obtém informações sobre uma sessão específica

**Response**:

```json
{
  "success": true,
  "message": "Informações da sessão obtidas com sucesso",
  "data": {
    "session_id": "string",
    "session_info": "string"
  }
}
```

### 4. Limpar Sessão (`DELETE /chat/sessions/{session_id}`)

**Descrição**: Limpa a memória de uma sessão específica

**Response**:

```json
{
  "success": true,
  "message": "Memória da sessão {session_id} limpa com sucesso",
  "data": {
    "session_id": "string",
    "cleared": true
  }
}
```

## Características dos Agentes

### DataAgent

- **Modelo**: GPT-4o
- **Ferramentas**:

  - `execute_duckdb_query`: Executa queries SELECT no DuckDB
  - `search_vectors`: Busca por similaridade nos vetores
  - `format_table_markdown`: Formata DataFrames como tabelas Markdown
  - `get_session_info`: Obtém informações da sessão

- **Instruções**:
  - SEMPRE responde em tabelas Markdown
  - Neutro e técnico
  - NUNCA inventa dados (usa 'N/D' para valores ausentes)

### InsightAgent

- **Modelo**: GPT-4o
- **Funcionalidades**:

  - Extrai métricas-chave dos dados
  - Gera resumo executivo em bullet points
  - Fornece recomendações baseadas nos dados
  - Identifica padrões nos dados

- **Formato de resposta**:

  ```
  ## Resumo Executivo
  • Volume de dados: X registros
  • Estrutura: Y colunas

  ## Recomendações
  • Recomendação 1
  • Recomendação 2

  ## Padrões Identificados
  • Padrão 1
  • Padrão 2
  ```

## Fluxo de Uso

1. **Upload de dados** → Cria tabela `ds_{session_id}_clean`
2. **Análise** → `POST /chat/data` com prompt específico
3. **Insights** → `POST /chat/insight` com saída do DataAgent
4. **Limpeza** → `DELETE /chat/sessions/{session_id}` quando necessário

## Exemplos de Prompts

### Para DataAgent:

- "Mostre os primeiros 10 registros"
- "Conte quantos registros existem"
- "Quais são as colunas disponíveis?"
- "Mostre estatísticas descritivas das colunas numéricas"
- "Filtre registros onde a coluna X > 100"

### Respostas Esperadas:

- Tabelas Markdown formatadas
- Valores 'N/D' para dados ausentes
- Sem opiniões ou interpretações subjetivas

## Gerenciamento de Sessões

- Cada `session_id` mantém um DataAgent separado
- Memória persistente durante a sessão
- Limpeza automática de memória ao deletar sessão
- Suporte a múltiplas sessões simultâneas

## Tratamento de Erros

- Validação de `session_id` e `prompt`
- Verificação de formato de tabelas Markdown
- Tratamento de erros de banco de dados
- Logs detalhados para debugging

## Testes

Execute o arquivo de teste para verificar o funcionamento:

```bash
cd backend
python test_agents.py
```

## Dependências

- Agno 0.1.0+
- FastAPI
- DuckDB
- Pandas
- ChromaDB (para busca por vetores)

