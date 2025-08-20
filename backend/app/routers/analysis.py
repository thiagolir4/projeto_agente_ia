import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.pipeline.cruzamentos import executar_regras_cruzamento

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis", tags=["analysis"])

class AnalysisRequest(BaseModel):
    """Modelo para requisição de análise"""
    datasets: Dict[str, str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "datasets": {
                    "estoque_id": "ds_estoque_123",
                    "vendas_id": "ds_vendas_456",
                    "precos_id": "ds_precos_789"
                }
            }
        }

@router.post("/run")
async def run_analysis(request: AnalysisRequest) -> Dict[str, Any]:
    """
    Executa regras de cruzamento e análise
    
    Args:
        request: Dados dos datasets para análise
        
    Returns:
        Resultados consolidados com tabela única e resumo
    """
    logger.info(f"Iniciando análise com datasets: {request.datasets}")
    
    try:
        # Validar datasets fornecidos
        if not request.datasets:
            raise HTTPException(status_code=400, detail="Nenhum dataset fornecido")
        
        # Verificar se pelo menos um par de datasets está disponível
        required_pairs = [
            ('estoque_id', 'vendas_id'),  # Para regra estoque vs vendas
            ('precos_id', 'vendas_id')    # Para regra divergência de preços
        ]
        
        valid_pairs = []
        for pair in required_pairs:
            if pair[0] in request.datasets and pair[1] in request.datasets:
                valid_pairs.append(pair)
        
        if not valid_pairs:
            raise HTTPException(
                status_code=400, 
                detail="Pelo menos um par de datasets deve ser fornecido: (estoque_id, vendas_id) ou (precos_id, vendas_id)"
            )
        
        logger.info(f"Pares válidos encontrados: {valid_pairs}")
        
        # Executar regras de cruzamento
        results = executar_regras_cruzamento(request.datasets)
        
        logger.info(f"Análise concluída: {results['summary']['total_registros']} registros processados")
        
        return {
            "success": True,
            "message": "Análise executada com sucesso",
            "data": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro durante análise: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno durante análise: {str(e)}")
