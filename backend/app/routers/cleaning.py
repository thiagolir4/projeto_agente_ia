import logging
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.pipeline.limpeza import clean_dataset

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cleaning", tags=["cleaning"])

@router.post("/run/{dataset_id}")
async def run_cleaning(dataset_id: str) -> Dict[str, Any]:
    """
    Executa pipeline de limpeza em um dataset
    
    Args:
        dataset_id: ID do dataset a ser limpo
        
    Returns:
        Métricas de limpeza e preview dos dados limpos
    """
    logger.info(f"Iniciando limpeza do dataset: {dataset_id}")
    
    try:
        # Executar pipeline de limpeza
        result = clean_dataset(dataset_id)
        
        logger.info(f"Limpeza concluída com sucesso para dataset: {dataset_id}")
        
        return {
            "success": True,
            "message": f"Dataset {dataset_id} limpo com sucesso",
            "data": result
        }
        
    except ValueError as e:
        logger.error(f"Dataset não encontrado: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
        
    except Exception as e:
        logger.error(f"Erro durante limpeza: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno durante limpeza: {str(e)}")

