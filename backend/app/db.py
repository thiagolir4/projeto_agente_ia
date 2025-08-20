import duckdb
import os
from app.config import settings

def get_duckdb():
    """Abre/garante o arquivo de banco DuckDB e cria tabelas necessarias"""
    # Garantir que o diretorio existe
    os.makedirs(os.path.dirname(settings.DUCKDB_PATH), exist_ok=True)
    
    # Conectar ao DuckDB
    conn = duckdb.connect(settings.DUCKDB_PATH)
    
    # Criar tabela datasets se nao existir
    conn.execute("""
        CREATE TABLE IF NOT EXISTS datasets (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            row_count INT NOT NULL,
            schema_json TEXT NOT NULL
        )
    """)
    
    return conn

def close_duckdb(conn):
    """Fecha a conexao com o DuckDB"""
    if conn:
        conn.close()

