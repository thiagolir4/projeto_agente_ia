from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.agents.data_agent import get_data_agent
from app.agents.insight_agent import process_insights
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

class DataRequest(BaseModel):
    """Request para análise de dados"""
    session_id: str
    prompt: str

class InsightRequest(BaseModel):
    """Request para geração de insights"""
    session_id: str
    context: str

class ChatResponse(BaseModel):
    """Resposta padrão do chat"""
    success: bool
    message: str
    data: Dict[str, Any] = {}

@router.post("/data", response_model=ChatResponse)
async def chat_data(request: DataRequest):
    """
    Endpoint para análise de dados usando DataAgent
    
    Args:
        request: Request com session_id e prompt
        
    Returns:
        Resposta com tabelas Markdown dos dados
    """
    try:
        logger.info(f"Processando request de dados para sessão: {request.session_id}")
        
        # Validar session_id
        if not request.session_id or not request.session_id.strip():
            raise HTTPException(status_code=400, detail="session_id é obrigatório")
        
        # Validar prompt
        if not request.prompt or not request.prompt.strip():
            raise HTTPException(status_code=400, detail="prompt é obrigatório")
        
        # Obter DataAgent para a sessão
        data_agent = get_data_agent(request.session_id)
        
        # Executar análise
        logger.info(f"Executando DataAgent com prompt: {request.prompt}")
        response = await data_agent.run(request.prompt)
        
        # Verificar se a resposta contém tabelas Markdown
        if not response or not isinstance(response, str):
            raise HTTPException(status_code=500, detail="Resposta inválida do DataAgent")
        
        # Verificar se há pelo menos uma tabela na resposta
        if '|' not in response or '---' not in response:
            logger.warning(f"Resposta do DataAgent não contém tabelas Markdown: {response[:200]}...")
            # Adicionar instrução para o usuário
            response += "\n\n**Nota**: Se você esperava uma tabela, tente reformular sua pergunta."
        
        logger.info(f"DataAgent executado com sucesso para sessão: {request.session_id}")
        
        return ChatResponse(
            success=True,
            message="Análise de dados concluída com sucesso",
            data={
                "session_id": request.session_id,
                "prompt": request.prompt,
                "response": response,
                "response_type": "markdown_table"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar request de dados: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao processar análise de dados: {str(e)}"
        )

@router.post("/insight", response_model=ChatResponse)
async def chat_insight(request: InsightRequest):
    """
    Endpoint para geração de insights usando InsightAgent
    
    Args:
        request: Request com session_id e context (saída do DataAgent)
        
    Returns:
        Resposta com insights em formato de bullet points
    """
    try:
        logger.info(f"Processando request de insights para sessão: {request.session_id}")
        
        # Validar session_id
        if not request.session_id or not request.session_id.strip():
            raise HTTPException(status_code=400, detail="session_id é obrigatório")
        
        # Validar context
        if not request.context or not request.context.strip():
            raise HTTPException(status_code=400, detail="context é obrigatório")
        
        # Verificar se o context contém dados (tabelas Markdown)
        if '|' not in request.context or '---' not in request.context:
            raise HTTPException(
                status_code=400, 
                detail="Context deve conter dados em formato de tabela Markdown"
            )
        
        # Processar insights
        logger.info(f"Executando InsightAgent para sessão: {request.session_id}")
        insights = await process_insights(request.context)
        
        if not insights:
            raise HTTPException(status_code=500, detail="Falha ao gerar insights")
        
        logger.info(f"InsightAgent executado com sucesso para sessão: {request.session_id}")
        
        return ChatResponse(
            success=True,
            message="Insights gerados com sucesso",
            data={
                "session_id": request.session_id,
                "insights": insights,
                "response_type": "executive_summary"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar request de insights: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao gerar insights: {str(e)}"
        )

@router.get("/sessions/{session_id}/info")
async def get_session_info(session_id: str):
    """
    Endpoint para obter informações de uma sessão
    
    Args:
        session_id: ID da sessão
        
    Returns:
        Informações da sessão
    """
    try:
        logger.info(f"Obtendo informações da sessão: {session_id}")
        
        # Validar session_id
        if not session_id or not session_id.strip():
            raise HTTPException(status_code=400, detail="session_id é obrigatório")
        
        # Obter DataAgent para verificar se existe
        from app.agents.data_agent import get_session_info as get_session_data_info
        
        session_info = get_session_data_info(session_id)
        
        return ChatResponse(
            success=True,
            message="Informações da sessão obtidas com sucesso",
            data={
                "session_id": session_id,
                "session_info": session_info
            }
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter informações da sessão: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao obter informações da sessão: {str(e)}"
        )

@router.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """
    Endpoint para limpar memória de uma sessão
    
    Args:
        session_id: ID da sessão
        
    Returns:
        Confirmação de limpeza
    """
    try:
        logger.info(f"Limpando memória da sessão: {session_id}")
        
        # Validar session_id
        if not session_id or not session_id.strip():
            raise HTTPException(status_code=400, detail="session_id é obrigatório")
        
        # Limpar memória da sessão
        from app.agents.data_agent import clear_session_memory
        clear_session_memory(session_id)
        
        return ChatResponse(
            success=True,
            message=f"Memória da sessão {session_id} limpa com sucesso",
            data={
                "session_id": session_id,
                "cleared": True
            }
        )
        
    except Exception as e:
        logger.error(f"Erro ao limpar sessão: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao limpar sessão: {str(e)}"
        )
