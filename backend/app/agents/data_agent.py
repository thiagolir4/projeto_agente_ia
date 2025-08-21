import duckdb
import pandas as pd
from typing import Dict, Any, Optional
from app.db import get_duckdb, close_duckdb
from app.vectors import search
import json
import os
import re

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

class SimpleDataAgent:
    """
    Implementação simplificada do DataAgent sem dependência da biblioteca agno
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.name = "DataAgent"
        
    async def run(self, prompt: str) -> str:
        """
        Processa o prompt e retorna resposta baseada no contexto
        
        Args:
            prompt: Pergunta do usuário
            
        Returns:
            Resposta formatada em Markdown
        """
        prompt_lower = prompt.lower()
        
        # Detectar tipo de consulta
        if any(word in prompt_lower for word in ['query', 'sql', 'select', 'consulta']):
            # Extrair query SQL se fornecida
            sql_match = re.search(r'SELECT\s+.+?(?:FROM|$)', prompt, re.IGNORECASE)
            if sql_match:
                query = sql_match.group(0)
                return execute_duckdb_query(query, self.session_id)
            else:
                return "**Por favor, forneça uma query SQL válida (apenas SELECT)**"
        
        elif any(word in prompt_lower for word in ['busca', 'similar', 'vector', 'search']):
            # Busca por similaridade
            return search_vectors_tool(prompt, self.session_id)
        
        elif any(word in prompt_lower for word in ['info', 'informação', 'sessão', 'tabela']):
            # Informações da sessão
            return get_session_info(self.session_id)
        
        elif any(word in prompt_lower for word in ['dados', 'registros', 'linhas', 'colunas']):
            # Consulta básica de dados
            try:
                conn = get_duckdb()
                table_name = f"ds_{self.session_id}_clean"
                
                # Verificar se a tabela existe
                tables = conn.execute("SHOW TABLES").fetchall()
                table_exists = any(table_name in str(table) for table in tables)
                
                if not table_exists:
                    close_duckdb(conn)
                    return f"**Tabela {table_name} não encontrada para esta sessão**"
                
                # Executar query básica
                result = conn.execute(f"SELECT * FROM {table_name} LIMIT 10")
                df = result.df()
                close_duckdb(conn)
                
                if df.empty:
                    return "**Nenhum dado encontrado**"
                
                return format_table_markdown(df)
                
            except Exception as e:
                return f"**Erro ao consultar dados: {str(e)}**"
        
        else:
            # Resposta padrão com instruções
            return """**Olá! Sou o DataAgent e posso ajudá-lo com:**

• **Consultas SQL**: Execute queries SELECT nos seus dados
• **Busca por similaridade**: Encontre dados relacionados
• **Informações da sessão**: Veja tabelas e registros disponíveis
• **Visualização de dados**: Veja os primeiros registros

**Exemplos de perguntas:**
- "Mostre os primeiros 5 registros"
- "Quantos registros existem?"
- "Quais colunas estão disponíveis?"
- "Execute: SELECT * FROM dados LIMIT 10"

Por favor, seja mais específico sobre o que você gostaria de analisar."""

# Função para obter DataAgent (mantém compatibilidade com o código existente)
def get_data_agent(session_id: str) -> SimpleDataAgent:
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
    agent = SimpleDataAgent(session_id)
    
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
