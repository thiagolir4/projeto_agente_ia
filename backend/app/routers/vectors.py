import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.vectors import upsert_dataset_embeddings, search, get_session_stats

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vectors", tags=["vectors"])

class IndexRequest(BaseModel):
    """Modelo para requisição de indexação"""
    session_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sessao_123"
            }
        }

class SearchRequest(BaseModel):
    """Modelo para requisição de busca"""
    session_id: str
    query: str
    top_k: Optional[int] = 8
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sessao_123",
                "query": "SKU com vendas altas",
                "top_k": 5
            }
        }

@router.post("/index/{dataset_id}")
async def index_dataset(dataset_id: str, request: IndexRequest) -> Dict[str, Any]:
    """
    Indexa embeddings de um dataset limpo
    
    Args:
        dataset_id: ID do dataset a ser indexado
        request: Dados da sessão
        
    Returns:
        Estatísticas da indexação
    """
    logger.info(f"Iniciando indexação do dataset: {dataset_id} para sessão: {request.session_id}")
    
    try:
        # Validar parâmetros
        if not request.session_id.strip():
            raise HTTPException(status_code=400, detail="session_id não pode estar vazio")
        
        if not dataset_id.strip():
            raise HTTPException(status_code=400, detail="dataset_id não pode estar vazio")
        
        # Executar indexação
        stats = upsert_dataset_embeddings(dataset_id, request.session_id)
        
        logger.info(f"Indexação concluída com sucesso: {stats['chunks_inserted']} chunks")
        
        return {
            "success": True,
            "message": f"Dataset {dataset_id} indexado com sucesso para sessão {request.session_id}",
            "data": stats
        }
        
    except ValueError as e:
        logger.error(f"Dataset não encontrado: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Erro durante indexação: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno durante indexação: {str(e)}")

@router.post("/search")
async def search_vectors(request: SearchRequest) -> Dict[str, Any]:
    """
    Busca por similaridade nos embeddings
    
    Args:
        request: Dados da busca (sessão, query, top_k)
        
    Returns:
        Resultados da busca com metadados
    """
    logger.info(f"Executando busca para sessão: {request.session_id}, query: {request.query}")
    
    try:
        # Validar parâmetros
        if not request.session_id.strip():
            raise HTTPException(status_code=400, detail="session_id não pode estar vazio")
        
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="query não pode estar vazio")
        
        if request.top_k <= 0 or request.top_k > 100:
            raise HTTPException(status_code=400, detail="top_k deve estar entre 1 e 100")
        
        # Executar busca
        search_results = search(request.session_id, request.query, request.top_k)
        
        logger.info(f"Busca concluída: {search_results['total_results']} resultados")
        
        return {
            "success": True,
            "message": "Busca executada com sucesso",
            "data": search_results
        }
        
    except Exception as e:
        logger.error(f"Erro durante busca: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno durante busca: {str(e)}")

@router.get("/stats/{session_id}")
async def get_vectors_stats(session_id: str) -> Dict[str, Any]:
    """
    Obtém estatísticas de uma sessão de vetores
    
    Args:
        session_id: ID da sessão
        
    Returns:
        Estatísticas da sessão
    """
    logger.info(f"Obtendo estatísticas da sessão: {session_id}")
    
    try:
        if not session_id.strip():
            raise HTTPException(status_code=400, detail="session_id não pode estar vazio")
        
        # Obter estatísticas
        stats = get_session_stats(session_id)
        
        return {
            "success": True,
            "message": "Estatísticas obtidas com sucesso",
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao obter estatísticas: {str(e)}")

@router.delete("/session/{session_id}")
async def delete_session(session_id: str) -> Dict[str, Any]:
    """
    Remove uma sessão de vetores e todos os seus embeddings
    
    Args:
        session_id: ID da sessão a ser removida
        
    Returns:
        Confirmação da remoção
    """
    logger.info(f"Removendo sessão: {session_id}")
    
    try:
        if not session_id.strip():
            raise HTTPException(status_code=400, detail="session_id não pode estar vazio")
        
        # Importar cliente Chroma
        from app.vectors import client
        
        if not client:
            raise HTTPException(status_code=500, detail="Cliente Chroma não disponível")
        
        # Tentar remover coleção
        collection_name = f"session_{session_id}"
        try:
            client.delete_collection(name=collection_name)
            logger.info(f"Sessão {session_id} removida com sucesso")
            
            return {
                "success": True,
                "message": f"Sessão {session_id} removida com sucesso",
                "data": {
                    "session_id": session_id,
                    "collection_name": collection_name,
                    "deleted": True
                }
            }
            
        except Exception as e:
            logger.warning(f"Coleção {collection_name} não encontrada ou já removida")
            return {
                "success": True,
                "message": f"Sessão {session_id} não encontrada",
                "data": {
                    "session_id": session_id,
                    "collection_name": collection_name,
                    "deleted": False
                }
            }
        
    except Exception as e:
        logger.error(f"Erro ao remover sessão: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao remover sessão: {str(e)}")

