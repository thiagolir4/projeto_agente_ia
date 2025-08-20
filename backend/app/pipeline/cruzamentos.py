import pandas as pd
import polars as pl
import logging
from typing import Dict, Any, List, Union, Tuple
from app.db import get_duckdb, close_duckdb
from app.config import settings
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def regra_estoque_vs_vendas(estoque_df: Union[pd.DataFrame, pl.DataFrame], 
                           vendas_df: Union[pd.DataFrame, pl.DataFrame]) -> List[Dict[str, Any]]:
    """
    Regra 1: Análise de estoque vs vendas
    
    Args:
        estoque_df: DataFrame com colunas [sku, data, estoque_disponivel]
        vendas_df: DataFrame com colunas [sku, data, vendas]
        
    Returns:
        Lista de resultados com flags e scores
    """
    logger.info("Executando regra: estoque vs vendas")
    
    try:
        # Converter para pandas se necessário
        if isinstance(estoque_df, pl.DataFrame):
            estoque_df = estoque_df.to_pandas()
        if isinstance(vendas_df, pl.DataFrame):
            vendas_df = vendas_df.to_pandas()
        
        # Normalizar nomes de colunas
        estoque_cols = {col: col.lower().replace(' ', '_') for col in estoque_df.columns}
        vendas_cols = {col: col.lower().replace(' ', '_') for col in vendas_df.columns}
        
        estoque_df = estoque_df.rename(columns=estoque_cols)
        vendas_df = vendas_df.rename(columns=vendas_cols)
        
        # Verificar colunas necessárias
        required_estoque = ['sku', 'data', 'estoque_disponivel']
        required_vendas = ['sku', 'data', 'vendas']
        
        if not all(col in estoque_df.columns for col in required_estoque):
            logger.warning(f"Colunas de estoque não encontradas. Disponíveis: {list(estoque_df.columns)}")
            return []
            
        if not all(col in vendas_df.columns for col in required_vendas):
            logger.warning(f"Colunas de vendas não encontradas. Disponíveis: {list(vendas_df.columns)}")
            return []
        
        # Converter datas se necessário
        if 'data' in estoque_df.columns:
            estoque_df['data'] = pd.to_datetime(estoque_df['data'], errors='coerce')
        if 'data' in vendas_df.columns:
            vendas_df['data'] = pd.to_datetime(vendas_df['data'], errors='coerce')
        
        # Fazer join por SKU e período (mês)
        estoque_df['ano_mes'] = estoque_df['data'].dt.to_period('M')
        vendas_df['ano_mes'] = vendas_df['data'].dt.to_period('M')
        
        # Agregar estoque por SKU e mês
        estoque_agg = estoque_df.groupby(['sku', 'ano_mes'])['estoque_disponivel'].sum().reset_index()
        
        # Agregar vendas por SKU e mês
        vendas_agg = vendas_df.groupby(['sku', 'ano_mes'])['vendas'].sum().reset_index()
        
        # Merge
        merged = pd.merge(estoque_agg, vendas_agg, on=['sku', 'ano_mes'], how='inner')
        
        if merged.empty:
            logger.info("Nenhum match encontrado entre estoque e vendas")
            return []
        
        # Calcular flags e scores
        results = []
        for _, row in merged.iterrows():
            estoque = row['estoque_disponivel']
            vendas = row['vendas']
            
            # Flag se vendas > estoque
            flag = vendas > estoque
            
            # Score de severidade
            if estoque > 0:
                score = (vendas - estoque) / estoque
            else:
                score = 0 if vendas == 0 else 1.0
            
            # Converter período para string
            periodo_str = str(row['ano_mes'])
            
            results.append({
                'regra': 'estoque_vs_vendas',
                'sku': row['sku'],
                'data': periodo_str,
                'valor_base': float(estoque),
                'valor_comparado': float(vendas),
                'score': float(score),
                'flag': bool(flag)
            })
        
        logger.info(f"Regra estoque vs vendas: {len(results)} resultados processados")
        return results
        
    except Exception as e:
        logger.error(f"Erro na regra estoque vs vendas: {str(e)}")
        return []

def regra_divergencia_preco(precos_df: Union[pd.DataFrame, pl.DataFrame], 
                           vendas_df: Union[pd.DataFrame, pl.DataFrame]) -> List[Dict[str, Any]]:
    """
    Regra 2: Análise de divergência de preços
    
    Args:
        precos_df: DataFrame com colunas [sku, data, preco_tabela]
        vendas_df: DataFrame com colunas [sku, data, preco_vendido]
        
    Returns:
        Lista de resultados com flags e scores
    """
    logger.info("Executando regra: divergência de preços")
    
    try:
        # Converter para pandas se necessário
        if isinstance(precos_df, pl.DataFrame):
            precos_df = precos_df.to_pandas()
        if isinstance(vendas_df, pl.DataFrame):
            vendas_df = vendas_df.to_pandas()
        
        # Normalizar nomes de colunas
        precos_cols = {col: col.lower().replace(' ', '_') for col in precos_df.columns}
        vendas_cols = {col: col.lower().replace(' ', '_') for col in vendas_df.columns}
        
        precos_df = precos_df.rename(columns=precos_cols)
        vendas_df = vendas_df.rename(columns=vendas_cols)
        
        # Verificar colunas necessárias
        required_precos = ['sku', 'data', 'preco_tabela']
        required_vendas = ['sku', 'data', 'preco_vendido']
        
        if not all(col in precos_df.columns for col in required_precos):
            logger.warning(f"Colunas de preços não encontradas. Disponíveis: {list(precos_df.columns)}")
            return []
            
        if not all(col in vendas_df.columns for col in required_vendas):
            logger.warning(f"Colunas de vendas não encontradas. Disponíveis: {list(vendas_df.columns)}")
            return []
        
        # Converter datas se necessário
        if 'data' in precos_df.columns:
            precos_df['data'] = pd.to_datetime(precos_df['data'], errors='coerce')
        if 'data' in vendas_df.columns:
            vendas_df['data'] = pd.to_datetime(vendas_df['data'], errors='coerce')
        
        # Fazer join por SKU e data
        merged = pd.merge(precos_df, vendas_df, on=['sku', 'data'], how='inner')
        
        if merged.empty:
            logger.info("Nenhum match encontrado entre preços e vendas")
            return []
        
        # Obter threshold de divergência do .env ou usar padrão
        try:
            threshold_percent = float(os.getenv('PRECO_DIVERGENCIA_THRESHOLD', 10.0))
        except:
            threshold_percent = 10.0
        
        logger.info(f"Threshold de divergência: {threshold_percent}%")
        
        # Calcular divergências
        results = []
        for _, row in merged.iterrows():
            preco_tabela = row['preco_tabela']
            preco_vendido = row['preco_vendido']
            
            if pd.isna(preco_tabela) or pd.isna(preco_vendido) or preco_tabela == 0:
                continue
            
            # Calcular delta percentual
            delta_percent = ((preco_vendido - preco_tabela) / preco_tabela) * 100
            
            # Flag se divergência acima do threshold
            flag = abs(delta_percent) > threshold_percent
            
            # Score é o delta percentual
            score = delta_percent
            
            # Converter data para string
            data_str = row['data'].strftime('%Y-%m-%d') if hasattr(row['data'], 'strftime') else str(row['data'])
            
            results.append({
                'regra': 'divergencia_preco',
                'sku': row['sku'],
                'data': data_str,
                'valor_base': float(preco_tabela),
                'valor_comparado': float(preco_vendido),
                'score': float(score),
                'flag': bool(flag)
            })
        
        logger.info(f"Regra divergência de preços: {len(results)} resultados processados")
        return results
        
    except Exception as e:
        logger.error(f"Erro na regra divergência de preços: {str(e)}")
        return []

def executar_regras_cruzamento(datasets: Dict[str, str]) -> Dict[str, Any]:
    """
    Executa todas as regras de cruzamento disponíveis
    
    Args:
        datasets: Dicionário com IDs dos datasets {estoque_id, vendas_id, precos_id}
        
    Returns:
        Dicionário com resultados consolidados e resumo
    """
    logger.info("Iniciando execução das regras de cruzamento")
    
    try:
        conn = get_duckdb()
        results = []
        
        # Regra 1: Estoque vs Vendas
        if 'estoque_id' in datasets and 'vendas_id' in datasets:
            logger.info("Executando regra estoque vs vendas")
            
            # Carregar datasets limpos
            estoque_clean = f"{datasets['estoque_id']}_clean"
            vendas_clean = f"{datasets['vendas_id']}_clean"
            
            # Verificar se as tabelas existem
            estoque_exists = conn.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{estoque_clean}'").fetchone()[0]
            vendas_exists = conn.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{vendas_clean}'").fetchone()[0]
            
            if estoque_exists and vendas_exists:
                estoque_df = conn.execute(f"SELECT * FROM {estoque_clean}").df()
                vendas_df = conn.execute(f"SELECT * FROM {vendas_clean}").df()
                
                regra_results = regra_estoque_vs_vendas(estoque_df, vendas_df)
                results.extend(regra_results)
            else:
                logger.warning(f"Tabelas limpas não encontradas: estoque={estoque_exists}, vendas={vendas_exists}")
        
        # Regra 2: Divergência de Preços
        if 'precos_id' in datasets and 'vendas_id' in datasets:
            logger.info("Executando regra divergência de preços")
            
            # Carregar datasets limpos
            precos_clean = f"{datasets['precos_id']}_clean"
            vendas_clean = f"{datasets['vendas_id']}_clean"
            
            # Verificar se as tabelas existem
            precos_exists = conn.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{precos_clean}'").fetchone()[0]
            vendas_exists = conn.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{vendas_clean}'").fetchone()[0]
            
            if precos_exists and vendas_exists:
                precos_df = conn.execute(f"SELECT * FROM {precos_clean}").df()
                vendas_df = conn.execute(f"SELECT * FROM {vendas_clean}").df()
                
                regra_results = regra_divergencia_preco(precos_df, vendas_df)
                results.extend(regra_results)
            else:
                logger.warning(f"Tabelas limpas não encontradas: precos={precos_exists}, vendas={vendas_exists}")
        
        # Fechar conexão
        close_duckdb(conn)
        
        # Gerar resumo
        summary = gerar_resumo_analise(results)
        
        return {
            "results": results,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Erro durante execução das regras: {str(e)}")
        close_duckdb(conn)
        raise e

def gerar_resumo_analise(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Gera resumo da análise com contagens e top scores
    
    Args:
        results: Lista de resultados das regras
        
    Returns:
        Dicionário com resumo consolidado
    """
    if not results:
        return {
            "total_registros": 0,
            "contagem_por_regra": {},
            "top_10_scores": []
        }
    
    # Contagem por regra
    contagem_por_regra = {}
    for result in results:
        regra = result['regra']
        contagem_por_regra[regra] = contagem_por_regra.get(regra, 0) + 1
    
    # Top 10 maiores scores (absolutos)
    sorted_results = sorted(results, key=lambda x: abs(x['score']), reverse=True)
    top_10_scores = sorted_results[:10]
    
    # Converter para formato serializável
    top_10_formatted = []
    for result in top_10_scores:
        top_10_formatted.append({
            'regra': result['regra'],
            'sku': result['sku'],
            'data': result['data'],
            'score': result['score'],
            'flag': result['flag']
        })
    
    return {
        "total_registros": len(results),
        "contagem_por_regra": contagem_por_regra,
        "top_10_scores": top_10_formatted
    }

