import pandas as pd
import polars as pl
import re
import unicodedata
import logging
from typing import Dict, Any, Tuple, Union
from app.db import get_duckdb, close_duckdb

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def normalize_columns(df: Union[pd.DataFrame, pl.DataFrame]) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Normaliza nomes das colunas: snake_case, trim, sem acentos
    Função pura e idempotente
    """
    logger.info("Normalizando nomes das colunas...")
    
    if isinstance(df, pd.DataFrame):
        # Pandas
        new_columns = {}
        for col in df.columns:
            # Remover acentos
            normalized = unicodedata.normalize('NFD', str(col))
            normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
            
            # Converter para snake_case
            normalized = re.sub(r'[^a-zA-Z0-9\s]', ' ', normalized)
            normalized = re.sub(r'\s+', '_', normalized.strip().lower())
            
            # Remover underscores duplicados
            normalized = re.sub(r'_+', '_', normalized)
            normalized = normalized.strip('_')
            
            new_columns[col] = normalized
        
        df_clean = df.rename(columns=new_columns)
        logger.info(f"Colunas normalizadas: {list(new_columns.values())}")
        
    else:
        # Polars
        new_columns = {}
        for col in df.columns:
            # Remover acentos
            normalized = unicodedata.normalize('NFD', str(col))
            normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
            
            # Converter para snake_case
            normalized = re.sub(r'[^a-zA-Z0-9\s]', ' ', normalized)
            normalized = re.sub(r'\s+', '_', normalized.strip().lower())
            
            # Remover underscores duplicados
            normalized = re.sub(r'_+', '_', normalized)
            normalized = normalized.strip('_')
            
            new_columns[col] = normalized
        
        df_clean = df.rename(new_columns)
        logger.info(f"Colunas normalizadas: {list(new_columns.values())}")
    
    return df_clean

def coerce_types(df: Union[pd.DataFrame, pl.DataFrame]) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Detecta e converte tipos de dados automaticamente
    Função pura e idempotente
    """
    logger.info("Coercionando tipos de dados...")
    
    if isinstance(df, pd.DataFrame):
        # Pandas
        df_clean = df.copy()
        
        for col in df_clean.columns:
            # Tentar converter para datetime (YYYY-MM-DD)
            try:
                pd.to_datetime(df_clean[col], format='%Y-%m-%d', errors='raise')
                df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
                logger.info(f"Coluna '{col}' convertida para datetime")
                continue
            except:
                pass
            
            # Tentar converter para numérico
            try:
                # Remover caracteres não numéricos (exceto . e ,)
                temp_col = df_clean[col].astype(str).str.replace(r'[^\d.,-]', '', regex=True)
                # Substituir vírgula por ponto para decimal
                temp_col = temp_col.str.replace(',', '.')
                
                # Tentar converter
                numeric_col = pd.to_numeric(temp_col, errors='coerce')
                if not numeric_col.isna().all():
                    df_clean[col] = numeric_col
                    logger.info(f"Coluna '{col}' convertida para numérico")
                    continue
            except:
                pass
            
            # Verificar se é categoria (poucos valores únicos)
            if df_clean[col].nunique() < min(50, len(df_clean) * 0.1):
                df_clean[col] = df_clean[col].astype('category')
                logger.info(f"Coluna '{col}' convertida para categoria")
    
    else:
        # Polars
        df_clean = df.clone()
        
        for col in df_clean.columns:
            # Tentar converter para datetime
            try:
                datetime_col = pl.Series(df_clean[col]).str.strptime(pl.Datetime, fmt='%Y-%m-%d')
                if not datetime_col.is_null().all():
                    df_clean = df_clean.with_columns(pl.col(col).str.strptime(pl.Datetime, fmt='%Y-%m-%d'))
                    logger.info(f"Coluna '{col}' convertida para datetime")
                    continue
            except:
                pass
            
            # Tentar converter para numérico
            try:
                # Remover caracteres não numéricos
                temp_col = df_clean[col].cast(pl.Utf8).str.replace_all(r'[^\d.,-]', '')
                # Substituir vírgula por ponto
                temp_col = temp_col.str.replace_all(',', '.')
                
                # Tentar converter
                numeric_col = temp_col.cast(pl.Float64, strict=False)
                if not numeric_col.is_null().all():
                    df_clean = df_clean.with_columns(pl.col(col).cast(pl.Utf8).str.replace_all(r'[^\d.,-]', '').str.replace_all(',', '.').cast(pl.Float64, strict=False))
                    logger.info(f"Coluna '{col}' convertida para numérico")
                    continue
            except:
                pass
            
            # Verificar se é categoria
            if df_clean[col].n_unique() < min(50, len(df_clean) * 0.1):
                df_clean = df_clean.with_columns(pl.col(col).cast(pl.Categorical))
                logger.info(f"Coluna '{col}' convertida para categoria")
    
    return df_clean

def standardize_values(df: Union[pd.DataFrame, pl.DataFrame], 
                      currency_default: str = "BRL",
                      decimal_places: int = 2) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Padroniza valores: moeda, casas decimais
    Função pura e idempotente
    """
    logger.info(f"Padronizando valores (moeda: {currency_default}, decimais: {decimal_places})...")
    
    if isinstance(df, pd.DataFrame):
        # Pandas
        df_clean = df.copy()
        
        for col in df_clean.columns:
            col_str = str(col).lower()
            
            # Padronizar moeda
            if any(word in col_str for word in ['valor', 'preco', 'custo', 'salario', 'moeda', 'dinheiro']):
                # Remover símbolos de moeda e converter para float
                df_clean[col] = df_clean[col].astype(str).str.replace(r'[R$\s]', '', regex=True)
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
                
                # Arredondar para casas decimais especificadas
                df_clean[col] = df_clean[col].round(decimal_places)
                logger.info(f"Coluna '{col}' padronizada como moeda ({currency_default})")
            
            # Padronizar números decimais
            elif df_clean[col].dtype in ['float64', 'float32']:
                df_clean[col] = df_clean[col].round(decimal_places)
                logger.info(f"Coluna '{col}' arredondada para {decimal_places} casas decimais")
    
    else:
        # Polars
        df_clean = df.clone()
        
        for col in df_clean.columns:
            col_str = str(col).lower()
            
            # Padronizar moeda
            if any(word in col_str for word in ['valor', 'preco', 'custo', 'salario', 'moeda', 'dinheiro']):
                # Remover símbolos de moeda
                df_clean = df_clean.with_columns(
                    pl.col(col).cast(pl.Utf8).str.replace_all(r'[R$\s]', '').cast(pl.Float64, strict=False)
                )
                
                # Arredondar
                df_clean = df_clean.with_columns(
                    pl.col(col).round(decimal_places)
                )
                logger.info(f"Coluna '{col}' padronizada como moeda ({currency_default})")
            
            # Padronizar números decimais
            elif df_clean[col].dtype in [pl.Float64, pl.Float32]:
                df_clean = df_clean.with_columns(
                    pl.col(col).round(decimal_places)
                )
                logger.info(f"Coluna '{col}' arredondada para {decimal_places} casas decimais")
    
    return df_clean

def drop_dupes_and_nas(df: Union[pd.DataFrame, pl.DataFrame], 
                       how: str = "smart") -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Remove duplicatas e valores nulos de forma inteligente
    Função pura e idempotente
    
    Args:
        how: "smart" (remove duplicatas primeiro, depois NAs), "strict" (remove tudo), "conservative" (só duplicatas)
    """
    logger.info(f"Removendo duplicatas e NAs (estratégia: {how})...")
    
    initial_rows = len(df)
    
    if isinstance(df, pd.DataFrame):
        # Pandas
        df_clean = df.copy()
        
        if how in ["smart", "strict"]:
            # Remover duplicatas primeiro
            df_clean = df_clean.drop_duplicates()
            logger.info(f"Duplicatas removidas: {initial_rows - len(df_clean)} linhas")
            
            if how == "strict":
                # Remover todas as linhas com NAs
                df_clean = df_clean.dropna()
                logger.info(f"NAs removidos: {len(df_clean)} linhas restantes")
            else:  # smart
                # Remover apenas linhas onde todas as colunas são NA
                df_clean = df_clean.dropna(how='all')
                logger.info(f"Linhas completamente vazias removidas: {len(df_clean)} linhas restantes")
        
        elif how == "conservative":
            # Só remover duplicatas
            df_clean = df_clean.drop_duplicates()
            logger.info(f"Duplicatas removidas: {initial_rows - len(df_clean)} linhas")
    
    else:
        # Polars
        df_clean = df.clone()
        
        if how in ["smart", "strict"]:
            # Remover duplicatas primeiro
            df_clean = df_clean.unique()
            logger.info(f"Duplicatas removidas: {initial_rows - len(df_clean)} linhas")
            
            if how == "strict":
                # Remover todas as linhas com NAs
                df_clean = df_clean.drop_nulls()
                logger.info(f"NAs removidos: {len(df_clean)} linhas restantes")
            else:  # smart
                # Remover apenas linhas onde todas as colunas são NA
                df_clean = df_clean.filter(~pl.all_horizontal(pl.all().is_null()))
                logger.info(f"Linhas completamente vazias removidas: {len(df_clean)} linhas restantes")
        
        elif how == "conservative":
            # Só remover duplicatas
            df_clean = df_clean.unique()
            logger.info(f"Duplicatas removidas: {initial_rows - len(df_clean)} linhas")
    
    final_rows = len(df_clean)
    logger.info(f"Limpeza concluída: {initial_rows} -> {final_rows} linhas ({final_rows/initial_rows*100:.1f}% mantidas)")
    
    return df_clean

def clean_dataset(dataset_id: str) -> Dict[str, Any]:
    """
    Executa pipeline completo de limpeza em um dataset
    
    Args:
        dataset_id: ID do dataset a ser limpo
        
    Returns:
        Dicionário com métricas de limpeza e preview dos dados
    """
    logger.info(f"Iniciando limpeza do dataset: {dataset_id}")
    
    try:
        # Conectar ao DuckDB
        conn = get_duckdb()
        
        # Verificar se o dataset existe
        dataset_info = conn.execute("""
            SELECT name, row_count, schema_json FROM datasets WHERE id = ?
        """, [dataset_id]).fetchone()
        
        if not dataset_info:
            raise ValueError(f"Dataset {dataset_id} não encontrado")
        
        dataset_name = dataset_info[0]
        initial_rows = dataset_info[1]
        schema_info = dataset_info[2]
        
        logger.info(f"Dataset: {dataset_name}, Linhas iniciais: {initial_rows}")
        
        # Carregar dados do DuckDB para pandas
        df = conn.execute(f"SELECT * FROM {dataset_id}").df()
        
        logger.info(f"Dados carregados: {len(df)} linhas, {len(df.columns)} colunas")
        
        # Aplicar pipeline de limpeza
        df_clean = df.copy()
        
        # 1. Normalizar colunas
        df_clean = normalize_columns(df_clean)
        
        # 2. Coercionar tipos
        df_clean = coerce_types(df_clean)
        
        # 3. Padronizar valores
        df_clean = standardize_values(df_clean)
        
        # 4. Remover duplicatas e NAs
        df_clean = drop_dupes_and_nas(df_clean, how="smart")
        
        # Métricas finais
        final_rows = len(df_clean)
        final_cols = len(df_clean.columns)
        
        # Calcular percentual de valores nulos por coluna
        null_percentages = {}
        for col in df_clean.columns:
            if isinstance(df_clean, pd.DataFrame):
                null_count = df_clean[col].isna().sum()
            else:  # Polars
                null_count = df_clean[col].is_null().sum()
            null_percentages[col] = (null_count / final_rows) * 100 if final_rows > 0 else 0
        
        # Criar tabela limpa no DuckDB
        clean_table_name = f"{dataset_id}_clean"
        
        # Criar tabela com schema baseado nos dados limpos
        conn.execute(f"DROP TABLE IF EXISTS {clean_table_name}")
        
        # Criar tabela com schema apropriado
        columns_def = []
        for col in df_clean.columns:
            col_type = df_clean[col].dtype
            # Escapar nome da coluna para DuckDB
            safe_col_name = f'"{col}"'
            
            if 'datetime' in str(col_type):
                columns_def.append(f'{safe_col_name} TIMESTAMP')
            elif 'float' in str(col_type) or 'int' in str(col_type):
                columns_def.append(f'{safe_col_name} DOUBLE')
            elif 'category' in str(col_type):
                columns_def.append(f'{safe_col_name} VARCHAR')
            else:
                columns_def.append(f'{safe_col_name} VARCHAR')
        
        create_table_sql = f"""
            CREATE TABLE {clean_table_name} (
                {', '.join(columns_def)}
            )
        """
        conn.execute(create_table_sql)
        
        # Inserir dados limpos usando pandas to_sql para melhor compatibilidade
        if isinstance(df_clean, pd.DataFrame):
            # Usar pandas to_sql para DuckDB
            df_clean.to_sql(clean_table_name, conn, if_exists='replace', index=False)
        else:
            # Para Polars, converter para pandas primeiro
            df_pandas = df_clean.to_pandas()
            df_pandas.to_sql(clean_table_name, conn, if_exists='replace', index=False)
        
        # Criar tabela datasets_clean para metadados
        conn.execute("""
            CREATE TABLE IF NOT EXISTS datasets_clean (
                id TEXT PRIMARY KEY,
                original_dataset_id TEXT NOT NULL,
                original_name TEXT NOT NULL,
                cleaned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                rows_before INT NOT NULL,
                rows_after INT NOT NULL,
                columns_before INT NOT NULL,
                columns_after INT NOT NULL,
                null_percentages TEXT NOT NULL,
                cleaning_metrics TEXT NOT NULL
            )
        """)
        
        # Inserir metadados da limpeza
        import json
        conn.execute("""
            INSERT OR REPLACE INTO datasets_clean 
            (id, original_dataset_id, original_name, rows_before, rows_after, 
             columns_before, columns_after, null_percentages, cleaning_metrics)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            clean_table_name,
            dataset_id,
            dataset_name,
            initial_rows,
            final_rows,
            len(df.columns),
            final_cols,
            json.dumps(null_percentages),
            json.dumps({
                "rows_removed": initial_rows - final_rows,
                "rows_kept_percentage": (final_rows / initial_rows) * 100 if initial_rows > 0 else 0,
                "columns_changed": len(df.columns) != final_cols
            })
        ))
        
        # Preview dos dados limpos (primeiras 20 linhas)
        if isinstance(df_clean, pd.DataFrame):
            preview_data = df_clean.head(20).to_dict('records')
        else:  # Polars
            preview_data = df_clean.head(20).to_dicts()
        
        # Converter tipos de dados para JSON serializable
        for row in preview_data:
            for key, value in row.items():
                if (isinstance(df_clean, pd.DataFrame) and pd.isna(value)) or \
                   (not isinstance(df_clean, pd.DataFrame) and hasattr(value, 'is_null') and value.is_null()):
                    row[key] = None
                elif hasattr(value, 'isoformat'):  # datetime
                    row[key] = value.isoformat()
                elif hasattr(value, 'item'):  # numpy types
                    row[key] = value.item()
        
        # Fechar conexão
        close_duckdb(conn)
        
        # Resultado
        result = {
            "dataset_id": dataset_id,
            "clean_table": clean_table_name,
            "metrics": {
                "rows_before": initial_rows,
                "rows_after": final_rows,
                "rows_removed": initial_rows - final_rows,
                "rows_kept_percentage": (final_rows / initial_rows) * 100 if initial_rows > 0 else 0,
                "columns_before": len(df.columns),
                "columns_after": final_cols,
                "null_percentages": null_percentages
            },
            "preview": {
                "total_rows": len(preview_data),
                "data": preview_data
            }
        }
        
        logger.info(f"Limpeza concluída com sucesso: {clean_table_name}")
        return result
        
    except Exception as e:
        logger.error(f"Erro durante limpeza: {str(e)}")
        raise e
