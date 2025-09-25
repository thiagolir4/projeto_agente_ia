"""
Módulo para gerenciar o histórico de conversas persistente.
Salva e carrega conversas do MongoDB para manter o histórico entre sessões.
"""

import json
from datetime import datetime
from typing import List, Dict, Any
from pymongo import MongoClient
from database import db_config


class GerenciadorHistorico:
    """Gerencia o histórico de conversas persistente no MongoDB."""
    
    def __init__(self, mongo_uri: str = None, database_name: str = None):
        """
        Inicializa o gerenciador de histórico.
        
        Args:
            mongo_uri: URI de conexão MongoDB
            database_name: Nome do banco de dados
        """
        self.mongo_uri = mongo_uri or db_config.MONGO_URI
        self.database_name = database_name or db_config.DB_NAME
        self.client = None
        self.db = None
        self.colecao_historico = None
        
    def conectar(self):
        """Conecta ao MongoDB e configura a coleção de histórico."""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.database_name]
            self.colecao_historico = self.db['historico_conversas']
            
            # Criar índice para otimizar consultas por sessão
            self.colecao_historico.create_index("sessao_id")
            self.colecao_historico.create_index("timestamp")
            
            print("✅ Conectado ao MongoDB para histórico de conversas")
            
        except Exception as e:
            print(f"❌ Erro ao conectar para histórico: {e}")
            raise
    
    def gerar_id_sessao(self) -> str:
        """Gera um ID único para a sessão atual."""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def salvar_mensagem(self, sessao_id: str, tipo: str, conteudo: str, timestamp: datetime = None) -> str:
        """
        Salva uma mensagem no histórico.
        
        Args:
            sessao_id: ID da sessão
            tipo: 'usuario' ou 'agente'
            conteudo: Conteúdo da mensagem
            timestamp: Timestamp da mensagem (opcional)
            
        Returns:
            ID da mensagem salva
        """
        if self.colecao_historico is None:
            self.conectar()
        
        if timestamp is None:
            timestamp = datetime.now()
        
        mensagem = {
            "sessao_id": sessao_id,
            "tipo": tipo,
            "conteudo": conteudo,
            "timestamp": timestamp,
            "criado_em": datetime.now()
        }
        
        try:
            resultado = self.colecao_historico.insert_one(mensagem)
            print(f"💾 Mensagem salva: {tipo} - {conteudo[:50]}...")
            return str(resultado.inserted_id)
        except Exception as e:
            print(f"❌ Erro ao salvar mensagem: {e}")
            return None
    
    def carregar_historico_sessao(self, sessao_id: str) -> List[Dict[str, Any]]:
        """
        Carrega o histórico de uma sessão específica.
        
        Args:
            sessao_id: ID da sessão
            
        Returns:
            Lista de mensagens ordenadas por timestamp
        """
        if self.colecao_historico is None:
            self.conectar()
        
        try:
            mensagens = list(
                self.colecao_historico.find(
                    {"sessao_id": sessao_id}
                ).sort("timestamp", 1)
            )
            
            # Converter ObjectId para string
            for msg in mensagens:
                msg['_id'] = str(msg['_id'])
                if 'timestamp' in msg and isinstance(msg['timestamp'], datetime):
                    msg['timestamp'] = msg['timestamp'].isoformat()
                if 'criado_em' in msg and isinstance(msg['criado_em'], datetime):
                    msg['criado_em'] = msg['criado_em'].isoformat()
            
            print(f"📚 Carregadas {len(mensagens)} mensagens da sessão {sessao_id}")
            return mensagens
            
        except Exception as e:
            print(f"❌ Erro ao carregar histórico: {e}")
            return []
    
    def carregar_ultima_sessao(self) -> tuple:
        """
        Carrega a última sessão ativa.
        
        Returns:
            Tupla (sessao_id, mensagens)
        """
        if self.colecao_historico is None:
            self.conectar()
        
        try:
            # Buscar a sessão mais recente
            ultima_sessao = self.colecao_historico.find_one(
                {},
                sort=[("timestamp", -1)]
            )
            
            if ultima_sessao is not None:
                sessao_id = ultima_sessao['sessao_id']
                mensagens = self.carregar_historico_sessao(sessao_id)
                return sessao_id, mensagens
            else:
                # Criar nova sessão se não existir histórico
                nova_sessao = self.gerar_id_sessao()
                return nova_sessao, []
                
        except Exception as e:
            print(f"❌ Erro ao carregar última sessão: {e}")
            return self.gerar_id_sessao(), []
    
    def listar_sessoes(self) -> List[Dict[str, Any]]:
        """
        Lista todas as sessões disponíveis.
        
        Returns:
            Lista de sessões com informações básicas
        """
        if self.colecao_historico is None:
            self.conectar()
        
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$sessao_id",
                        "primeira_mensagem": {"$min": "$timestamp"},
                        "ultima_mensagem": {"$max": "$timestamp"},
                        "total_mensagens": {"$sum": 1}
                    }
                },
                {
                    "$sort": {"ultima_mensagem": -1}
                }
            ]
            
            sessoes = list(self.colecao_historico.aggregate(pipeline))
            
            # Converter timestamps para string
            for sessao in sessoes:
                if 'primeira_mensagem' in sessao and isinstance(sessao['primeira_mensagem'], datetime):
                    sessao['primeira_mensagem'] = sessao['primeira_mensagem'].isoformat()
                if 'ultima_mensagem' in sessao and isinstance(sessao['ultima_mensagem'], datetime):
                    sessao['ultima_mensagem'] = sessao['ultima_mensagem'].isoformat()
            
            return sessoes
            
        except Exception as e:
            print(f"❌ Erro ao listar sessões: {e}")
            return []
    
    def limpar_historico_sessao(self, sessao_id: str) -> bool:
        """
        Remove o histórico de uma sessão específica.
        
        Args:
            sessao_id: ID da sessão
            
        Returns:
            True se removido com sucesso
        """
        if self.colecao_historico is None:
            self.conectar()
        
        try:
            resultado = self.colecao_historico.delete_many({"sessao_id": sessao_id})
            print(f"🗑️ Removidas {resultado.deleted_count} mensagens da sessão {sessao_id}")
            return True
        except Exception as e:
            print(f"❌ Erro ao limpar histórico: {e}")
            return False
    
    def limpar_todo_historico(self) -> bool:
        """
        Remove todo o histórico de conversas.
        
        Returns:
            True se removido com sucesso
        """
        if self.colecao_historico is None:
            self.conectar()
        
        try:
            resultado = self.colecao_historico.delete_many({})
            print(f"🗑️ Removidas {resultado.deleted_count} mensagens de todo o histórico")
            return True
        except Exception as e:
            print(f"❌ Erro ao limpar todo histórico: {e}")
            return False
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do histórico.
        
        Returns:
            Dicionário com estatísticas
        """
        if self.colecao_historico is None:
            self.conectar()
        
        try:
            total_mensagens = self.colecao_historico.count_documents({})
            total_sessoes = len(self.colecao_historico.distinct("sessao_id"))
            
            # Mensagens por tipo
            pipeline = [
                {"$group": {"_id": "$tipo", "count": {"$sum": 1}}}
            ]
            mensagens_por_tipo = list(self.colecao_historico.aggregate(pipeline))
            
            return {
                "total_mensagens": total_mensagens,
                "total_sessoes": total_sessoes,
                "mensagens_por_tipo": mensagens_por_tipo
            }
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
            return {}


# Instância global do gerenciador
gerenciador_historico = GerenciadorHistorico()


def obter_gerenciador() -> GerenciadorHistorico:
    """Retorna a instância global do gerenciador de histórico."""
    return gerenciador_historico
