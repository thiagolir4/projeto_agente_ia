import uuid
import json
import pandas as pd
import polars as pl
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import io
import csv
import gzip
import zipfile
from collections import Counter
from app.db import get_duckdb, close_duckdb

router = APIRouter(prefix="/datasets", tags=["datasets"])

def detect_encoding(file_content: bytes) -> str:
    """Detecta a codificação do arquivo"""
    # Para arquivos brasileiros, tentar utf-8 primeiro, depois latin1
    try:
        # Tentar decodificar uma amostra com utf-8
        sample_size = min(1024, len(file_content))
        sample = file_content[:sample_size].decode('utf-8')
        return 'utf-8'
    except UnicodeDecodeError:
        # Se utf-8 falhar, usar latin1 (comum em arquivos brasileiros)
        return 'latin1'

def safe_decode(file_content: bytes, encoding: str) -> str:
    """Decodifica o conteúdo do arquivo de forma segura"""
    try:
        return file_content.decode(encoding)
    except UnicodeDecodeError:
        # Se falhar, tentar com latin1 e ignorar erros
        return file_content.decode('latin1', errors='ignore')

def detect_delimiter_and_compression(file_content: bytes) -> tuple[str, str, str]:
    """Detecta delimitador, compressão e codificação do arquivo"""
    # Verificar compressão
    compression = "none"
    if file_content.startswith(b'\x1f\x8b'):
        compression = "gzip"
    elif file_content.startswith(b'PK'):
        compression = "zip"
    
    # Detectar codificação
    encoding = detect_encoding(file_content)
    
    # Para arquivos CSV simples, usar vírgula como delimitador padrão
    # (mais comum em arquivos brasileiros)
    delimiter = ','
    
    return delimiter, compression, encoding

def infer_schema_with_pandas(file_content: bytes, delimiter: str, compression: str, encoding: str = 'utf-8') -> Dict[str, Any]:
    """Infere schema usando pandas"""
    try:
        if compression == "gzip":
            df = pd.read_csv(io.BytesIO(file_content), delimiter=delimiter, compression='gzip', nrows=1000, on_bad_lines='skip', encoding=encoding)
        elif compression == "zip":
            with zipfile.ZipFile(io.BytesIO(file_content)) as z:
                csv_file = z.namelist()[0]
                with z.open(csv_file) as f:
                    df = pd.read_csv(f, delimiter=delimiter, nrows=1000, on_bad_lines='skip', encoding=encoding)
        else:
            df = pd.read_csv(io.BytesIO(file_content), delimiter=delimiter, nrows=1000, on_bad_lines='skip', encoding=encoding)
        
        schema = {}
        for col in df.columns:
            dtype = str(df[col].dtype)
            if 'int' in dtype:
                schema[col] = "INTEGER"
            elif 'float' in dtype:
                schema[col] = "DOUBLE"
            elif 'datetime' in dtype:
                schema[col] = "TIMESTAMP"
            else:
                schema[col] = "VARCHAR"
        
        return {
            "columns": schema,
            "row_count": len(df),
            "sample_data": []
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao inferir schema com pandas: {str(e)}")

def infer_schema_with_polars(file_content: bytes, delimiter: str, compression: str, encoding: str = 'utf-8') -> Dict[str, Any]:
    """Infere schema usando polars (fallback)"""
    try:
        if compression == "gzip":
            df = pl.read_csv(io.BytesIO(file_content), separator=delimiter, n_rows=1000, truncate_ragged_lines=True, encoding=encoding)
        elif compression == "zip":
            with zipfile.ZipFile(io.BytesIO(file_content)) as z:
                csv_file = z.namelist()[0]
                with z.open(csv_file) as f:
                    df = pl.read_csv(f, separator=delimiter, n_rows=1000, truncate_ragged_lines=True, encoding=encoding)
        else:
            df = pl.read_csv(io.BytesIO(file_content), separator=delimiter, n_rows=1000, truncate_ragged_lines=True, encoding=encoding)
        
        schema = {}
        for col in df.columns:
            dtype = str(df[col].dtype)
            if 'Int' in dtype:
                schema[col] = "INTEGER"
            elif 'Float' in dtype:
                schema[col] = "DOUBLE"
            elif 'Datetime' in dtype:
                schema[col] = "TIMESTAMP"
            else:
                schema[col] = "VARCHAR"
        
        return {
            "columns": schema,
            "row_count": len(df),
            "sample_data": []
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao inferir schema com polars: {str(e)}")

@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """Upload de um arquivo CSV para criar um novo dataset"""
    
    # Validar arquivo
    if not file.filename or not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser um CSV")
    
    try:
        # Ler conteúdo do arquivo
        file_content = await file.read()
        
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="Arquivo está vazio")
        
        # Detectar delimitador, compressão e codificação
        delimiter, compression, encoding = detect_delimiter_and_compression(file_content)
        
        # Tentar inferir schema com pandas primeiro
        try:
            schema_info = infer_schema_with_pandas(file_content, delimiter, compression, encoding)
        except Exception as e:
            # Fallback para polars
            try:
                schema_info = infer_schema_with_polars(file_content, delimiter, compression, encoding)
            except Exception as e2:
                # Último fallback: tentar com latin1 forçado
                try:
                    schema_info = infer_schema_with_pandas(file_content, delimiter, compression, 'latin1')
                except Exception as e3:
                    raise HTTPException(status_code=400, detail=f"Erro ao inferir schema: pandas={e}, polars={e2}, latin1={e3}")
        
        # Gerar ID único para o dataset
        dataset_id = f"ds_{str(uuid.uuid4())[:8]}"
        
        # Conectar ao DuckDB
        conn = get_duckdb()
        
        try:
            # Criar tabela para o dataset
            columns_def = []
            for col_name, col_type in schema_info["columns"].items():
                # Escapar nomes de coluna que podem ser reservados
                safe_col_name = f'"{col_name}"'
                columns_def.append(f"{safe_col_name} {col_type}")
            
            create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {dataset_id} (
                    {', '.join(columns_def)}
                )
            """
            conn.execute(create_table_sql)
            
            # Inserir dados na tabela
            try:
                if compression == "gzip":
                    df = pd.read_csv(io.BytesIO(file_content), delimiter=delimiter, compression='gzip', on_bad_lines='skip', encoding=encoding)
                elif compression == "zip":
                    with zipfile.ZipFile(io.BytesIO(file_content)) as z:
                        csv_file = z.namelist()[0]
                        with z.open(csv_file) as f:
                            df = pd.read_csv(f, delimiter=delimiter, on_bad_lines='skip', encoding=encoding)
                else:
                    df = pd.read_csv(io.BytesIO(file_content), delimiter=delimiter, on_bad_lines='skip', encoding=encoding)
            except Exception as e:
                # Fallback para latin1 se a codificação detectada falhar
                if compression == "gzip":
                    df = pd.read_csv(io.BytesIO(file_content), delimiter=delimiter, compression='gzip', on_bad_lines='skip', encoding='latin1')
                elif compression == "zip":
                    with zipfile.ZipFile(io.BytesIO(file_content)) as z:
                        csv_file = z.namelist()[0]
                        with z.open(csv_file) as f:
                            df = pd.read_csv(f, delimiter=delimiter, on_bad_lines='skip', encoding='latin1')
                else:
                    df = pd.read_csv(io.BytesIO(file_content), delimiter=delimiter, on_bad_lines='skip', encoding='latin1')
            
            # Inserir no DuckDB
            conn.execute(f"DELETE FROM {dataset_id}")
            for _, row in df.iterrows():
                placeholders = ', '.join(['?' for _ in row])
                conn.execute(f"INSERT INTO {dataset_id} VALUES ({placeholders})", list(row))
            
            # Obter contagem real de linhas
            real_row_count = conn.execute(f"SELECT COUNT(*) FROM {dataset_id}").fetchone()[0]
            
            # Inserir metadados na tabela datasets
            conn.execute("""
                INSERT INTO datasets (id, name, row_count, schema_json)
                VALUES (?, ?, ?, ?)
            """, (
                dataset_id,
                file.filename,
                real_row_count,
                json.dumps(schema_info)
            ))
            
            return {
                "success": True,
                "message": f"Dataset {dataset_id} criado com sucesso",
                "data": {
                    "dataset_id": dataset_id,
                    "row_count": real_row_count,
                    "columns": list(schema_info["columns"].keys())
                }
            }
            
        finally:
            close_duckdb(conn)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar arquivo: {str(e)}")

@router.get("/")
async def list_datasets():
    """Lista todos os datasets disponíveis"""
    conn = get_duckdb()
    
    try:
        result = conn.execute("""
            SELECT id, name, uploaded_at, row_count, schema_json
            FROM datasets
            ORDER BY uploaded_at DESC
        """).fetchall()
        
        datasets = []
        for row in result:
            try:
                schema_data = json.loads(row[4]) if row[4] else {"columns": {}}
                datasets.append({
                    "id": row[0],
                    "name": row[1],
                    "uploaded_at": row[2],
                    "row_count": row[3],
                    "schema": schema_data.get("columns", {})
                })
            except (json.JSONDecodeError, KeyError):
                # Fallback se houver problema com o schema
                datasets.append({
                    "id": row[0],
                    "name": row[1],
                    "uploaded_at": row[2],
                    "row_count": row[3],
                    "schema": {}
                })
        
        return {"datasets": datasets}
        
    finally:
        close_duckdb(conn)

@router.get("/{dataset_id}/preview")
async def preview_dataset(dataset_id: str):
    """Retorna as primeiras 50 linhas de um dataset"""
    conn = get_duckdb()
    
    try:
        # Verificar se o dataset existe
        dataset_info = conn.execute("""
            SELECT name, schema_json FROM datasets WHERE id = ?
        """, [dataset_id]).fetchone()
        
        if not dataset_info:
            raise HTTPException(status_code=404, detail="Dataset não encontrado")
        
        # Buscar primeiras 50 linhas
        result = conn.execute(f"SELECT * FROM {dataset_id} LIMIT 50").fetchall()
        
        # Obter nomes das colunas
        columns = [desc[0] for desc in conn.execute(f"SELECT * FROM {dataset_id} LIMIT 0").description]
        
        # Converter para lista de dicionários
        rows = []
        for row in result:
            row_dict = {}
            for i, col in enumerate(columns):
                # Garantir que os valores sejam serializáveis
                value = row[i]
                if value is None:
                    row_dict[col] = None
                elif isinstance(value, (int, float, str, bool)):
                    row_dict[col] = value
                else:
                    row_dict[col] = str(value)
            rows.append(row_dict)
        
        return {
            "success": True,
            "message": f"Preview do dataset {dataset_id} obtido com sucesso",
            "data": {
                "preview": rows,
                "columns": columns,
                "total_rows": len(rows)
            }
        }
        
    finally:
        close_duckdb(conn)
