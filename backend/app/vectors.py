import chromadb
import pandas as pd
import logging
from typing import Dict, Any, List, Optional
from app.db import get_duckdb, close_duckdb
from app.config import settings
import json
import hashlib

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar cliente Chroma
try:
    # Usar cliente em memória para testes
    client = chromadb.Client()
    logger.info(f"Cliente Chroma em memória inicializado")
except Exception as e:
    logger.error(f"Erro ao inicializar Chroma: {str(e)}")
    client = None

def create_text_chunks(df: pd.DataFrame, chunk_size: int = 100) -> List[Dict[str, Any]]:
    """
    Cria chunks de texto a partir do DataFrame
    
    Args:
        df: DataFrame com dados limpos
        chunk_size: Tamanho máximo de cada chunk
        
    Returns:
        Lista de chunks com texto e metadados
    """
    chunks = []
    
    # Se o DataFrame for pequeno, criar um chunk por linha
    if len(df) <= chunk_size:
        for idx, row in df.iterrows():
            # Criar texto compacto da linha
            text_parts = []
            for col, value in row.items():
                if pd.notna(value):
                    text_parts.append(f"{col}: {value}")
            
            text = " | ".join(text_parts)
            
            # Extrair metadados
            metadata = {
                'row_index': int(idx),
                'total_rows': len(df)
            }
            
            # Adicionar metadados específicos se disponíveis
            if 'sku' in df.columns and pd.notna(row['sku']):
                metadata['sku'] = str(row['sku'])
            if 'data' in df.columns and pd.notna(row['data']):
                metadata['data'] = str(row['data'])
            if 'loja' in df.columns and pd.notna(row['loja']):
                metadata['loja'] = str(row['loja'])
            
            chunks.append({
                'text': text,
                'metadata': metadata,
                'row_data': row.to_dict()
            })
    else:
        # Para DataFrames grandes, criar chunks por janelas
        for start_idx in range(0, len(df), chunk_size):
            end_idx = min(start_idx + chunk_size, len(df))
            chunk_df = df.iloc[start_idx:end_idx]
            
            # Criar texto compacto do chunk
            text_parts = []
            for col in chunk_df.columns:
                unique_values = chunk_df[col].dropna().unique()
                if len(unique_values) > 0:
                    if len(unique_values) <= 5:
                        text_parts.append(f"{col}: {', '.join(map(str, unique_values))}")
                    else:
                        text_parts.append(f"{col}: {len(unique_values)} valores únicos")
            
            text = " | ".join(text_parts)
            
            # Metadados do chunk
            metadata = {
                'chunk_start': start_idx,
                'chunk_end': end_idx,
                'total_rows': len(df),
                'chunk_size': len(chunk_df)
            }
            
            # Adicionar metadados específicos se disponíveis
            if 'sku' in chunk_df.columns:
                skus = chunk_df['sku'].dropna().unique()
                if len(skus) > 0:
                    metadata['skus'] = list(map(str, skus[:10]))  # Limitar a 10 SKUs
            
            chunks.append({
                'text': text,
                'metadata': metadata,
                'row_data': chunk_df.to_dict('records')
            })
    
    return chunks

def upsert_dataset_embeddings(dataset_id: str, session_id: str) -> Dict[str, Any]:
    """
    Indexa embeddings de um dataset limpo no Chroma
    
    Args:
        dataset_id: ID do dataset a ser indexado
        session_id: ID da sessão para isolamento
        
    Returns:
        Dicionário com estatísticas da indexação
    """
    logger.info(f"Iniciando indexação de embeddings para dataset: {dataset_id}")
    
    if not client:
        raise RuntimeError("Cliente Chroma não inicializado")
    
    try:
        # Conectar ao DuckDB
        conn = get_duckdb()
        
        # Verificar se a tabela limpa existe
        clean_table = f"{dataset_id}_clean"
        table_exists = conn.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{clean_table}'").fetchone()[0]
        
        if not table_exists:
            raise ValueError(f"Tabela limpa {clean_table} não encontrada")
        
        # Carregar dados limpos
        df = conn.execute(f"SELECT * FROM {clean_table}").df()
        logger.info(f"Dados carregados: {len(df)} linhas, {len(df.columns)} colunas")
        
        # Criar ou obter coleção
        collection_name = f"session_{session_id}"
        try:
            collection = client.get_collection(name=collection_name)
            logger.info(f"Coleção existente obtida: {collection_name}")
        except:
            collection = client.create_collection(
                name=collection_name,
                metadata={"description": f"Embeddings para sessão {session_id}"}
            )
            logger.info(f"Nova coleção criada: {collection_name}")
        
        # Criar chunks de texto
        chunks = create_text_chunks(df, chunk_size=50)  # Chunk menor para evitar estourar memória
        logger.info(f"Chunks criados: {len(chunks)}")
        
        # Preparar dados para inserção
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            # Gerar ID único para o chunk
            chunk_id = f"{dataset_id}_{session_id}_{i}_{hashlib.md5(chunk['text'].encode()).hexdigest()[:8]}"
            
            # Adicionar metadados da sessão
            chunk_metadata = chunk['metadata'].copy()
            chunk_metadata.update({
                'session_id': session_id,
                'dataset_id': dataset_id,
                'chunk_id': chunk_id
            })
            
            documents.append(chunk['text'])
            metadatas.append(chunk_metadata)
            ids.append(chunk_id)
        
        # Inserir no Chroma em lotes para evitar estourar memória
        batch_size = 100
        total_inserted = 0
        
        for i in range(0, len(documents), batch_size):
            batch_end = min(i + batch_size, len(documents))
            batch_docs = documents[i:batch_end]
            batch_metadatas = metadatas[i:batch_end]
            batch_ids = ids[i:batch_end]
            
            try:
                collection.upsert(
                    documents=batch_docs,
                    metadatas=batch_metadatas,
                    ids=batch_ids
                )
                total_inserted += len(batch_docs)
                logger.info(f"Lote inserido: {i+1}-{batch_end}/{len(documents)}")
            except Exception as e:
                logger.error(f"Erro ao inserir lote {i+1}-{batch_end}: {str(e)}")
                continue
        
        # Fechar conexão
        close_duckdb(conn)
        
        # Estatísticas
        stats = {
            "dataset_id": dataset_id,
            "session_id": session_id,
            "total_rows": len(df),
            "total_chunks": len(chunks),
            "chunks_inserted": total_inserted,
            "collection_name": collection_name
        }
        
        logger.info(f"Indexação concluída: {total_inserted} chunks inseridos")
        return stats
        
    except Exception as e:
        logger.error(f"Erro durante indexação: {str(e)}")
        close_duckdb(conn)
        raise e

def search(session_id: str, query: str, top_k: int = 8) -> Dict[str, Any]:
    """
    Busca por similaridade no Chroma
    
    Args:
        session_id: ID da sessão para filtrar resultados
        query: Texto da consulta
        top_k: Número máximo de resultados
        
    Returns:
        Dicionário com resultados da busca
    """
    logger.info(f"Executando busca para sessão: {session_id}, query: {query}")
    
    if not client:
        raise RuntimeError("Cliente Chroma não inicializado")
    
    try:
        # Obter coleção da sessão
        collection_name = f"session_{session_id}"
        try:
            collection = client.get_collection(name=collection_name)
        except:
            logger.warning(f"Coleção {collection_name} não encontrada")
            return {
                "query": query,
                "session_id": session_id,
                "results": [],
                "total_results": 0
            }
        
        # Executar busca
        results = collection.query(
            query_texts=[query],
            n_results=top_k,
            where={"session_id": session_id}  # Filtro adicional por segurança
        )
        
        # Processar resultados
        processed_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}
                distance = results['distances'][0][i] if results['distances'] and results['distances'][0] else 0.0
                
                processed_results.append({
                    'text': doc,
                    'metadata': metadata,
                    'similarity_score': 1.0 - distance,  # Converter distância para similaridade
                    'rank': i + 1
                })
        
        # Estatísticas da busca
        search_stats = {
            "query": query,
            "session_id": session_id,
            "results": processed_results,
            "total_results": len(processed_results),
            "top_k": top_k
        }
        
        logger.info(f"Busca concluída: {len(processed_results)} resultados encontrados")
        return search_stats
        
    except Exception as e:
        logger.error(f"Erro durante busca: {str(e)}")
        raise e

def get_session_stats(session_id: str) -> Dict[str, Any]:
    """
    Obtém estatísticas de uma sessão
    
    Args:
        session_id: ID da sessão
        
    Returns:
        Dicionário com estatísticas da sessão
    """
    if not client:
        raise RuntimeError("Cliente Chroma não inicializado")
    
    try:
        collection_name = f"session_{session_id}"
        try:
            collection = client.get_collection(name=collection_name)
        except:
            return {
                "session_id": session_id,
                "exists": False,
                "total_documents": 0
            }
        
        # Obter estatísticas da coleção
        collection_info = collection.get()
        
        stats = {
            "session_id": session_id,
            "exists": True,
            "total_documents": len(collection_info['ids']) if collection_info['ids'] else 0,
            "collection_name": collection_name
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas da sessão: {str(e)}")
        return {
            "session_id": session_id,
            "exists": False,
            "error": str(e)
        }
