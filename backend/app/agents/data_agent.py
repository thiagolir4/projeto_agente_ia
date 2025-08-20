from agno.agent import Agent
from agno.tools import Function
import duckdb
import pandas as pd
from typing import Dict, Any, Optional
from app.db import get_duckdb, close_duckdb
from app.vectors import search
import json
import os

# Memória simples por sessão (armazenamento local)
session_memory = {}

def format_table_markdown(df: pd.DataFrame) -> str:
    """
    Formata DataFrame como tabela Markdown
    
    Args:
        df: DataFrame pandas
        
    Returns:
        String formatada em Markdown
    """
    if df.empty:
        return "**Nenhum dado encontrado**"
    
    # Criar cabeçalho
    markdown = "| " + " | ".join(str(col) for col in df.columns) + " |\n"
    markdown += "| " + " | ".join("---" for _ in df.columns) + " |\n"
    
    # Adicionar linhas
    for _, row in df.iterrows():
        markdown += "| " + " | ".join(str(val) if pd.notna(val) else "N/D" for val in row) + " |\n"
    
    return markdown

def execute_duckdb_query(query: str, session_id: str) -> str:
    """
    Executa query SELECT no DuckDB para tabela ds_{session_id}_clean
    
    Args:
        query: Query SQL (apenas SELECT)
        session_id: ID da sessão
        
    Returns:
        Resultado formatado em Markdown
    """
    if not query.strip().upper().startswith("SELECT"):
        return "**Erro: Apenas queries SELECT são permitidas**"
    
    # Substituir referências genéricas pela tabela específica da sessão
    table_name = f"ds_{session_id}_clean"
    query = query.replace("ds_clean", table_name)
    
    try:
        conn = get_duckdb()
        
        # Verificar se a tabela existe
        tables = conn.execute("SHOW TABLES").fetchall()
        table_exists = any(table_name in str(table) for table in tables)
        
        if not table_exists:
            close_duckdb(conn)
            return f"**Tabela {table_name} não encontrada para esta sessão**"
        
        # Executar query
        result = conn.execute(query)
        df = result.df()
        close_duckdb(conn)
        
        if df.empty:
            return "**Nenhum resultado encontrado**"
        
        return format_table_markdown(df)
        
    except Exception as e:
        return f"**Erro na execução da query: {str(e)}**"

def search_vectors_tool(query: str, session_id: str, top_k: int = 8) -> str:
    """
    Busca por similaridade usando vectors.search
    
    Args:
        query: Texto da consulta
        session_id: ID da sessão
        top_k: Número máximo de resultados
        
    Returns:
        Resultado formatado em Markdown
    """
    try:
        results = search(session_id, query, top_k)
        
        if not results['results']:
            return "**Nenhum resultado encontrado na busca por similaridade**"
        
        # Criar DataFrame dos resultados
        data = []
        for result in results['results']:
            data.append({
                'Texto': result['text'][:100] + "..." if len(result['text']) > 100 else result['text'],
                'Score': f"{result['similarity_score']:.3f}",
                'Rank': result['rank'],
                'Metadados': json.dumps(result['metadata'], ensure_ascii=False)
            })
        
        df = pd.DataFrame(data)
        return format_table_markdown(df)
        
    except Exception as e:
        return f"**Erro na busca por similaridade: {str(e)}**"

def get_session_info(session_id: str) -> str:
    """
    Obtém informações da sessão atual
    
    Args:
        session_id: ID da sessão
        
    Returns:
        Informações da sessão
    """
    try:
        conn = get_duckdb()
        
        # Verificar tabelas disponíveis
        tables = conn.execute("SHOW TABLES").fetchall()
        session_tables = [str(table[0]) for table in tables if f"ds_{session_id}_" in str(table[0])]
        
        # Contar registros em cada tabela
        table_info = []
        for table in session_tables:
            try:
                count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                table_info.append(f"- {table}: {count} registros")
            except:
                table_info.append(f"- {table}: erro ao contar")
        
        close_duckdb(conn)
        
        if not table_info:
            return f"**Sessão {session_id}: Nenhuma tabela encontrada**"
        
        return f"**Sessão {session_id}**\n" + "\n".join(table_info)
        
    except Exception as e:
        return f"**Erro ao obter informações da sessão: {str(e)}**"

# Criar agentes com memória por sessão
def get_data_agent(session_id: str) -> Agent:
    """
    Cria ou retorna DataAgent para uma sessão específica
    
    Args:
        session_id: ID da sessão
        
    Returns:
        DataAgent configurado
    """
    if session_id in session_memory:
        return session_memory[session_id]
    
    # Criar novo agente
    agent = Agent(
        name="DataAgent",
        model="gpt-4o",
        instructions="""Você é um agente especializado em análise de dados. Suas responsabilidades são:

1. **SEMPRE responda em tabelas Markdown** usando as ferramentas disponíveis
2. **Seja neutro e técnico** em todas as respostas
3. **NUNCA invente dados**: se não houver dados, marque como 'N/D'
4. Use as ferramentas para:
   - Executar queries SQL no DuckDB (apenas SELECT)
   - Buscar por similaridade nos vetores
   - Formatar resultados em tabelas Markdown

5. **Formato de resposta obrigatório**: Use sempre tabelas Markdown
6. **Se não houver dados**: Responda com "N/D" ou "Nenhum dado encontrado"
7. **Mantenha-se objetivo**: Sem opiniões pessoais ou interpretações subjetivas

Exemplo de resposta:
```markdown
| Coluna | Valor |
|--------|-------|
| Dado1  | Valor1|
| Dado2  | N/D   |
```""",
        tools=[
            Function(
                name="execute_duckdb_query",
                function=execute_duckdb_query,
                description="Executa query SELECT no DuckDB para a sessão atual. Use apenas queries SELECT."
            ),
            Function(
                name="search_vectors",
                function=search_vectors_tool,
                description="Busca por similaridade nos vetores da sessão atual."
            ),
            Function(
                name="format_table_markdown",
                function=format_table_markdown,
                description="Formata DataFrame como tabela Markdown."
            ),
            Function(
                name="get_session_info",
                function=get_session_info,
                description="Obtém informações sobre as tabelas disponíveis na sessão atual."
            )
        ]
    )
    
    # Armazenar na memória
    session_memory[session_id] = agent
    
    return agent

def clear_session_memory(session_id: str):
    """Limpa a memória de uma sessão específica"""
    if session_id in session_memory:
        del session_memory[session_id]

def clear_all_memory():
    """Limpa toda a memória de sessões"""
    session_memory.clear()
