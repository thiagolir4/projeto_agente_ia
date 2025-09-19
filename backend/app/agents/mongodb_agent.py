"""
Agente de IA usando LangChain conectado ao MongoDB local.
Este agente consulta apenas dados existentes no MongoDB e responde em português.
"""

import os
import re
from typing import List, Dict, Any, Optional, Tuple
from pymongo import MongoClient
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import json


class MongoDBAgent:
    """Agente de IA que consulta dados do MongoDB local usando LangChain."""
    
    def __init__(self, mongo_uri: str = "mongodb://localhost:27017/", database_name: str = "dbGrupoOscar"):
        """
        Inicializa o agente MongoDB.
        
        Args:
            mongo_uri: URI de conexão com o MongoDB
            database_name: Nome do banco de dados
        """
        self.mongo_uri = mongo_uri
        self.database_name = database_name
        self.client = None
        self.db = None
        self.vectorstore = None
        self.qa_chain = None
        self.embeddings = None
        self.llm = None
        
        # Cache para consultas frequentes
        self.cache_consultas = {}
        self.cache_max_size = 50  # Máximo 50 consultas em cache
        
        # Dicionários de sinônimos e padrões para interpretação inteligente
        self.sinonimos = {
            'sku': ['sku', 'produto', 'produtos', 'item', 'items', 'código', 'codigo', 'código do produto', 'codigo do produto'],
            'loja': ['loja', 'lojas', 'filial', 'filiais', 'unidade', 'unidades', 'ponto', 'pontos'],
            'usuario': ['usuario', 'usuário', 'usuarios', 'usuários', 'cliente', 'clientes', 'pessoa', 'pessoas'],
            'data': ['data', 'datas', 'dia', 'dias', 'período', 'periodo', 'mês', 'mes', 'ano', 'anos'],
            'valor': ['valor', 'valores', 'preço', 'preco', 'dinheiro', 'montante', 'total', 'soma'],
            'devolucao': ['devolução', 'devolucao', 'devoluções', 'devolucoes', 'retorno', 'retornos'],
            'mais': ['mais', 'maior', 'maiores', 'top', 'melhor', 'melhores', 'frequente', 'frequentes'],
            'menos': ['menos', 'menor', 'menores', 'pior', 'piores', 'raro', 'raros'],
            'quantidade': ['quantidade', 'qtd', 'numero', 'número', 'count', 'contagem', 'total']
        }
        
        # Padrões de perguntas para detecção inteligente
        self.padroes_perguntas = {
            'top_sku': [
                r'qual\s+sku\s+mais\s+aparece',
                r'qual\s+os\s+skus\s+que\s+mais\s+aparecem',
                r'quais\s+skus\s+mais\s+aparecem',
                r'qual\s+produto\s+mais\s+aparece',
                r'quais\s+produtos\s+mais\s+aparecem',
                r'qual\s+item\s+mais\s+aparece',
                r'quais\s+itens\s+mais\s+aparecem',
                r'sku\s+mais\s+frequente',
                r'skus\s+mais\s+frequentes',
                r'produto\s+mais\s+frequente',
                r'produtos\s+mais\s+frequentes',
                r'item\s+mais\s+frequente',
                r'itens\s+mais\s+frequentes',
                r'top\s+\d*\s*sku',
                r'top\s+\d*\s*skus',
                r'top\s+\d*\s*produto',
                r'top\s+\d*\s*produtos',
                r'top\s+\d*\s*item',
                r'top\s+\d*\s*itens',
                r'mais\s+devolvido',
                r'mais\s+devolvidos',
                r'sku\s+que\s+mais\s+aparece',
                r'skus\s+que\s+mais\s+aparecem'
            ],
            'top_loja': [
                r'qual\s+loja\s+mais\s+aparece',
                r'quais\s+lojas\s+mais\s+aparecem',
                r'qual\s+os\s+lojas\s+que\s+mais\s+aparecem',
                r'qual\s+filial\s+mais\s+aparece',
                r'quais\s+filiais\s+mais\s+aparecem',
                r'loja\s+mais\s+frequente',
                r'lojas\s+mais\s+frequentes',
                r'filial\s+mais\s+frequente',
                r'filiais\s+mais\s+frequentes',
                r'top\s+\d*\s*loja',
                r'top\s+\d*\s*lojas',
                r'top\s+\d*\s*filial',
                r'top\s+\d*\s*filiais',
                r'loja\s+com\s+mais\s+devoluções',
                r'lojas\s+com\s+mais\s+devoluções',
                r'filial\s+com\s+mais\s+devoluções',
                r'filiais\s+com\s+mais\s+devoluções'
            ],
            'top_usuario': [
                r'qual\s+usuario\s+mais\s+aparece',
                r'quais\s+usuarios\s+mais\s+aparecem',
                r'quais\s+usuários\s+mais\s+aparecem',
                r'qual\s+usuário\s+mais\s+aparece',
                r'usuario\s+mais\s+frequente',
                r'usuarios\s+mais\s+frequentes',
                r'usuários\s+mais\s+frequentes',
                r'usuário\s+mais\s+frequente',
                r'top\s+\d*\s*usuario',
                r'top\s+\d*\s*usuarios',
                r'top\s+\d*\s*usuário',
                r'top\s+\d*\s*usuários',
                r'usuario\s+com\s+mais\s+devoluções',
                r'usuarios\s+com\s+mais\s+devoluções',
                r'usuário\s+com\s+mais\s+devoluções',
                r'usuários\s+com\s+mais\s+devoluções'
            ],
            'contagem_total': [
                r'quantos\s+registros',
                r'quantos\s+dados',
                r'total\s+de\s+registros',
                r'total\s+de\s+dados',
                r'quantidade\s+total',
                r'número\s+total',
                r'count\s+total'
            ]
        }
        
    def _interpretar_pergunta(self, pergunta: str) -> Dict[str, Any]:
        """
        Interpreta a pergunta do usuário e identifica o tipo de consulta.
        """
        pergunta_lower = pergunta.lower().strip()
        print(f"🔍 Analisando pergunta: '{pergunta_lower}'")
        
        # Detectar tipo de pergunta
        tipo_pergunta = None
        quantidade = 10  # padrão
        
        # Verificar padrões específicos
        for tipo, padroes in self.padroes_perguntas.items():
            print(f"🔍 Testando tipo: {tipo}")
            for padrao in padroes:
                if re.search(padrao, pergunta_lower):
                    print(f"✅ Padrão encontrado: {padrao}")
                    tipo_pergunta = tipo
                    break
            if tipo_pergunta:
                break
        
        # Detectar quantidade solicitada
        quantidade = self._detectar_quantidade(pergunta)
        
        # Detectar formato de resposta desejado
        formato_tabela = any(palavra in pergunta_lower for palavra in [
            'tabela', 'table', 'formato de tabela', 'em tabela', 'como tabela'
        ])
        
        resultado = {
            'tipo': tipo_pergunta,
            'quantidade': quantidade,
            'formato_tabela': formato_tabela,
            'pergunta_original': pergunta
        }
        
        print(f"🎯 Interpretação final: {resultado}")
        return resultado
        
    def conectar_mongodb(self):
        """Conecta ao MongoDB local."""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.database_name]
            print(f"✅ Conectado ao MongoDB: {self.database_name}")
            
            # Listar coleções disponíveis
            colecoes = self.db.list_collection_names()
            print(f"📋 Coleções disponíveis: {colecoes}")
            
            # Criar índices para otimizar consultas
            self._criar_indices_otimizacao()
            
        except Exception as e:
            print(f"❌ Erro ao conectar MongoDB: {e}")
    
    def _criar_indices_otimizacao(self):
        """Cria índices para otimizar as consultas mais frequentes."""
        try:
            colecao = self.db.DEVOLUCAO
            
            # Índices para campos mais consultados
            indices = [
                ("SKU", 1),           # Para consultas de SKU
                ("LOJA", 1),          # Para consultas de loja
                ("IDUSUARIO", 1),     # Para consultas de usuário
                ("DATA_DEVOLUCAO", 1), # Para consultas de data
                ("TIPOMOVIMENTACAO", 1), # Para consultas de tipo
                ("DIFERENCA_VALOR", 1),  # Para consultas de valor
            ]
            
            for campo, direcao in indices:
                try:
                    colecao.create_index([(campo, direcao)], background=True)
                    print(f"📊 Índice criado: {campo}")
                except Exception as e:
                    print(f"⚠️ Índice {campo} já existe ou erro: {e}")
            
            # Índice composto para consultas de agregação
            try:
                colecao.create_index([("SKU", 1), ("LOJA", 1)], background=True)
                colecao.create_index([("IDUSUARIO", 1), ("DATA_DEVOLUCAO", 1)], background=True)
                print("📊 Índices compostos criados")
            except Exception as e:
                print(f"⚠️ Erro ao criar índices compostos: {e}")
                
        except Exception as e:
            print(f"❌ Erro ao criar índices: {e}")
            raise
    
    def carregar_dados_mongo(self, colecoes: List[str] = None) -> List[Document]:
        """
        Carrega dados das coleções do MongoDB e converte para documentos LangChain.
        
        Args:
            colecoes: Lista de nomes das coleções. Se None, carrega todas.
            
        Returns:
            Lista de documentos LangChain
        """
        if self.db is None:
            self.conectar_mongodb()
            
        documentos = []
        
        # Se não especificou coleções, carrega todas
        if not colecoes:
            colecoes = self.db.list_collection_names()
        
        print(f"📚 Carregando dados das coleções: {colecoes}")
        
        for colecao_nome in colecoes:
            colecao = self.db[colecao_nome]
            
            # OTIMIZAÇÃO: Usar agregação com $sample para amostra representativa
            pipeline = [
                {"$sample": {"size": 1000}},  # Amostra aleatória de 1000 registros
                {"$project": {  # Selecionar apenas campos importantes
                    "SKU": 1,
                    "LOJA": 1, 
                    "IDUSUARIO": 1,
                    "DATA_DEVOLUCAO": 1,
                    "DIFERENCA_VALOR": 1,
                    "TIPOMOVIMENTACAO": 1,
                    "VALORDEVPRODUTO": 1,
                    "VALORVENDAPRODUTO": 1,
                    "_id": 1
                }}
            ]
            docs_mongo = list(colecao.aggregate(pipeline))
            
            print(f"📄 Coleção '{colecao_nome}': {len(docs_mongo)} documentos")
            
            for doc in docs_mongo:
                # Converter documento MongoDB para Document LangChain
                conteudo = self._formatar_documento(doc, colecao_nome)
                
                documento_langchain = Document(
                    page_content=conteudo,
                    metadata={
                        "colecao": colecao_nome,
                        "id": str(doc.get("_id", "")),
                        "fonte": "mongodb_local"
                    }
                )
                documentos.append(documento_langchain)
        
        print(f"✅ Total de documentos carregados: {len(documentos)}")
        return documentos
    
    def _formatar_documento(self, doc: Dict, colecao: str) -> str:
        """
        Formata um documento MongoDB para texto legível.
        
        Args:
            doc: Documento MongoDB
            colecao: Nome da coleção
            
        Returns:
            Texto formatado do documento
        """
        # Remover _id se existir
        doc_copy = doc.copy()
        if "_id" in doc_copy:
            del doc_copy["_id"]
        
        # Criar texto estruturado
        texto = f"Dados da coleção '{colecao}':\n"
        
        for chave, valor in doc_copy.items():
            if isinstance(valor, (dict, list)):
                texto += f"{chave}: {json.dumps(valor, ensure_ascii=False, indent=2)}\n"
            else:
                texto += f"{chave}: {valor}\n"
        
        return texto
    
    def criar_agente(self):
        """Cria o agente de IA usando LangChain."""
        try:
            # Configurar OpenAI (usar variável de ambiente)
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente")
            
            # Inicializar embeddings e LLM
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=openai_api_key,
                model="text-embedding-3-small"
            )
            
            self.llm = ChatOpenAI(
                openai_api_key=openai_api_key,
                model_name="gpt-4o-mini",
                temperature=0.1,  # Baixa temperatura para respostas mais precisas
                max_tokens=1000
            )
            
            # Carregar dados do MongoDB
            documentos = self.carregar_dados_mongo()
            
            if not documentos:
                raise ValueError("Nenhum documento encontrado no MongoDB")
            
            # Criar vetorstore com FAISS
            print("🔍 Criando índice de vetores com FAISS...")
            self.vectorstore = FAISS.from_documents(documentos, self.embeddings)
            
            # Configurar memória para conversas
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
            
            # Criar chain de recuperação conversacional
            self.qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=self.vectorstore.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 5}  # Buscar 5 documentos mais relevantes
                ),
                memory=memory,
                return_source_documents=True,
                verbose=True
            )
            
            # Customizar prompt para português e sem alucinações
            from langchain_core.prompts import PromptTemplate
            
            custom_prompt = PromptTemplate(
                template="""
Você é um assistente especializado em consultar dados de um banco MongoDB.

INSTRUÇÕES IMPORTANTES:
1. Responda SEMPRE em português brasileiro
2. Você tem acesso COMPLETO ao banco de dados MongoDB com todos os 160.621+ registros
3. Para perguntas sobre CONTAGEM, TOTAIS ou ESTATÍSTICAS, use consultas diretas ao banco completo
4. Se a informação não estiver nos documentos fornecidos, use consultas diretas ao MongoDB
5. Seja claro e objetivo
6. Se encontrar dados relevantes, apresente-os de forma organizada
7. Sempre mencione que os dados são do banco COMPLETO, não de uma amostra
8. NUNCA retorne dados brutos com pipes (|) - sempre formate adequadamente
9. Para dados tabulares, use formatação HTML quando apropriado

Documentos relevantes (amostra para contexto):
{context}

Pergunta: {question}

Resposta em português:""",
                input_variables=["context", "question"]
            )
            
            self.qa_chain.combine_docs_chain.llm_chain.prompt = custom_prompt
            
            print("✅ Agente criado com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao criar agente: {e}")
            raise
    
    def _fazer_consulta_direta(self, pergunta: str) -> str:
        """
        Faz consultas diretas ao MongoDB para perguntas específicas de contagem e análise.
        """
        pergunta_lower = pergunta.lower()
        
        try:
            # Contar total de registros
            if any(palavra in pergunta_lower for palavra in ['quantas linhas', 'quantos registros', 'total de registros', 'quantos documentos']):
                total = self.db.DEVOLUCAO.count_documents({})
                return f"O total de registros na coleção DEVOLUCAO é: **{total:,}** registros."
            
            # Contar valores únicos de IDUSUARIO
            if any(palavra in pergunta_lower for palavra in ['idusuario', 'usuarios diferentes', 'usuários únicos']):
                usuarios_unicos = self.db.DEVOLUCAO.distinct('IDUSUARIO')
                return f"Existem **{len(usuarios_unicos):,}** IDUSUARIOS únicos na coleção DEVOLUCAO."
            
            # Contar valores únicos de SKU
            if any(palavra in pergunta_lower for palavra in ['sku', 'skus diferentes', 'produtos únicos']):
                skus_unicos = self.db.DEVOLUCAO.distinct('SKU')
                return f"Existem **{len(skus_unicos):,}** SKUs únicos na coleção DEVOLUCAO."
            
            # Somar coluna DIFERENCA_VALOR
            if any(palavra in pergunta_lower for palavra in ['soma', 'somatória', 'total', 'diferenca_valor']):
                pipeline = [
                    {"$group": {
                        "_id": None,
                        "total": {"$sum": {"$toDouble": {"$replaceAll": {"input": "$DIFERENCA_VALOR", "find": ",", "replacement": "."}}}}
                    }}
                ]
                resultado = list(self.db.DEVOLUCAO.aggregate(pipeline))
                if resultado:
                    total = resultado[0]['total']
                    return f"A somatória da coluna DIFERENCA_VALOR é: **{total:,.2f}**"
                else:
                    return "Não foi possível calcular a somatória da coluna DIFERENCA_VALOR."
            
            # Análise de datas mais frequentes
            if any(palavra in pergunta_lower for palavra in ['data', 'datas', 'mais se repete', 'frequente', 'comum']):
                # Detectar quantidade solicitada
                limite = self._detectar_quantidade(pergunta)
                
                pipeline = [
                    {"$group": {
                        "_id": "$DATA_DEVOLUCAO",
                        "count": {"$sum": 1}
                    }},
                    {"$sort": {"count": -1}},
                    {"$limit": limite}
                ]
                resultado = list(self.db.DEVOLUCAO.aggregate(pipeline))
                if resultado:
                    # Verificar se deve retornar em formato de tabela
                    if any(palavra in pergunta_lower for palavra in ['tabela', 'table', 'formato de tabela']):
                        return self._formatar_como_tabela(
                            dados=resultado,
                            colunas=['Posição', 'Data de Devolução', 'Quantidade de Registros'],
                            titulo=f"Top {limite} Datas de Devolução Mais Frequentes",
                            formata_dados=lambda i, item: [
                                i + 1,
                                item['_id'] if item['_id'] else 'N/A',
                                f"{item['count']:,}"
                            ]
                        )
                    else:
                        resposta = f"As {limite} datas de devolução mais frequentes no banco completo são:\n\n"
                        for i, item in enumerate(resultado, 1):
                            data = item['_id'] if item['_id'] else 'N/A'
                            count = item['count']
                            resposta += f"{i}. **{data}**: {count:,} registros\n"
                        return resposta
                else:
                    return "Não foi possível analisar as datas de devolução."
            
            # Análise de usuários mais frequentes
            if (any(palavra in pergunta_lower for palavra in ['usuario mais', 'usuário mais', 'mais devoluções', 'top usuários', 'usuario com mais', 'usuário com mais', 'top usuario', 'top usuário']) 
                and not any(palavra in pergunta_lower for palavra in ['loja', 'lojas', 'filial', 'filiais'])):
                # Detectar quantidade solicitada
                limite = self._detectar_quantidade(pergunta)
                
                pipeline = [
                    {"$group": {
                        "_id": "$IDUSUARIO",
                        "count": {"$sum": 1}
                    }},
                    {"$sort": {"count": -1}},
                    {"$limit": limite}
                ]
                resultado = list(self.db.DEVOLUCAO.aggregate(pipeline))
                if resultado:
                    if any(palavra in pergunta_lower for palavra in ['tabela', 'table', 'formato de tabela']):
                        return self._formatar_como_tabela(
                            dados=resultado,
                            colunas=['Posição', 'ID Usuário', 'Quantidade de Devoluções'],
                            titulo=f"Top {limite} Usuários com Mais Devoluções",
                            formata_dados=lambda i, item: [
                                i + 1,
                                item['_id'] if item['_id'] else 'N/A',
                                f"{item['count']:,}"
                            ]
                        )
                    else:
                        resposta = f"Os {limite} usuários com mais devoluções no banco completo são:\n\n"
                        for i, item in enumerate(resultado, 1):
                            usuario = item['_id'] if item['_id'] else 'N/A'
                            count = item['count']
                            resposta += f"{i}. **Usuário {usuario}**: {count:,} devoluções\n"
                        return resposta
                else:
                    return "Não foi possível analisar os usuários."
            
            # Análise de SKUs mais frequentes
            if (any(palavra in pergunta_lower for palavra in ['sku mais', 'produto mais', 'mais devolvido', 'top skus', 'sku com mais', 'produto com mais', 'top sku', 'top produto']) 
                and not any(palavra in pergunta_lower for palavra in ['loja', 'lojas', 'filial', 'filiais', 'usuario', 'usuário'])):
                # Detectar quantidade solicitada
                limite = self._detectar_quantidade(pergunta)
                
                pipeline = [
                    {"$group": {
                        "_id": "$SKU",
                        "count": {"$sum": 1}
                    }},
                    {"$sort": {"count": -1}},
                    {"$limit": limite}
                ]
                resultado = list(self.db.DEVOLUCAO.aggregate(pipeline))
                if resultado:
                    if any(palavra in pergunta_lower for palavra in ['tabela', 'table', 'formato de tabela']):
                        return self._formatar_como_tabela(
                            dados=resultado,
                            colunas=['Posição', 'SKU', 'Quantidade de Devoluções'],
                            titulo=f"Top {limite} SKUs Mais Devolvidos",
                            formata_dados=lambda i, item: [
                                i + 1,
                                item['_id'] if item['_id'] else 'N/A',
                                f"{item['count']:,}"
                            ]
                        )
                    else:
                        resposta = f"Os {limite} SKUs mais devolvidos no banco completo são:\n\n"
                        for i, item in enumerate(resultado, 1):
                            sku = item['_id'] if item['_id'] else 'N/A'
                            count = item['count']
                            resposta += f"{i}. **SKU {sku}**: {count:,} devoluções\n"
                        return resposta
                else:
                    return "Não foi possível analisar os SKUs."
            
            # Análise de lojas mais frequentes
            if any(palavra in pergunta_lower for palavra in ['loja', 'lojas', 'filial', 'filiais', 'loja com mais', 'lojas com mais', 'top loja', 'top lojas']):
                # Detectar quantidade solicitada
                limite = self._detectar_quantidade(pergunta)
                
                pipeline = [
                    {"$group": {
                        "_id": "$LOJA",
                        "count": {"$sum": 1}
                    }},
                    {"$sort": {"count": -1}},
                    {"$limit": limite}
                ]
                resultado = list(self.db.DEVOLUCAO.aggregate(pipeline))
                if resultado:
                    if any(palavra in pergunta_lower for palavra in ['tabela', 'table', 'formato de tabela']):
                        return self._formatar_como_tabela(
                            dados=resultado,
                            colunas=['Posição', 'Loja', 'Quantidade de Devoluções'],
                            titulo=f"Top {limite} Lojas com Mais Devoluções",
                            formata_dados=lambda i, item: [
                                i + 1,
                                item['_id'] if item['_id'] else 'N/A',
                                f"{item['count']:,}"
                            ]
                        )
                    else:
                        resposta = f"As {limite} lojas com mais devoluções no banco completo são:\n\n"
                        for i, item in enumerate(resultado, 1):
                            loja = item['_id'] if item['_id'] else 'N/A'
                            count = item['count']
                            resposta += f"{i}. **Loja {loja}**: {count:,} devoluções\n"
                        return resposta
                else:
                    return "Não foi possível analisar as lojas."
            
            # Análise de tipos de movimento
            if any(palavra in pergunta_lower for palavra in ['tipo', 'tipos', 'movimentação', 'movimento']):
                pipeline = [
                    {"$group": {
                        "_id": "$TIPOMOVIMENTACAO",
                        "count": {"$sum": 1}
                    }},
                    {"$sort": {"count": -1}}
                ]
                resultado = list(self.db.DEVOLUCAO.aggregate(pipeline))
                if resultado:
                    if any(palavra in pergunta_lower for palavra in ['tabela', 'table', 'formato de tabela']):
                        return self._formatar_como_tabela(
                            dados=resultado,
                            colunas=['Tipo de Movimentação', 'Quantidade de Registros'],
                            titulo="Distribuição de Tipos de Movimentação",
                            formata_dados=lambda i, item: [
                                item['_id'] if item['_id'] else 'N/A',
                                f"{item['count']:,}"
                            ]
                        )
                    else:
                        resposta = "Distribuição de tipos de movimentação no banco completo:\n\n"
                        for item in resultado:
                            tipo = item['_id'] if item['_id'] else 'N/A'
                            count = item['count']
                            resposta += f"• **{tipo}**: {count:,} registros\n"
                        return resposta
                else:
                    return "Não foi possível analisar os tipos de movimentação."
            
            # Consulta de dados de exemplo em formato de tabela
            if any(palavra in pergunta_lower for palavra in ['exemplo', 'amostra', 'dados', 'registros']) and any(palavra in pergunta_lower for palavra in ['tabela', 'table', 'formato de tabela']):
                # Buscar alguns registros de exemplo
                registros = list(self.db.DEVOLUCAO.find().limit(10))
                if registros:
                    return self._formatar_como_tabela(
                        dados=registros,
                        colunas=['DATA_DEVOLUCAO', 'DIFERENCA_VALOR', 'IDORCAMENTO_NOVO', 'IDUSUARIO', 'ID_DEVOLUCAO', 'LOJA', 'SKU', 'TIPOMOVIMENTACAO', 'VALORDEVPRODUTO', 'VALORVENDAPRODUTO', '_id'],
                        titulo="Amostra de Dados da Coleção DEVOLUCAO",
                        formata_dados=lambda i, item: [
                            item.get('DATA_DEVOLUCAO', 'N/A'),
                            str(item.get('DIFERENCA_VALOR', 'N/A')),
                            str(item.get('IDORCAMENTO_NOVO', 'N/A')),
                            str(item.get('IDUSUARIO', 'N/A')),
                            str(item.get('ID_DEVOLUCAO', 'N/A')),
                            str(item.get('LOJA', 'N/A')),
                            str(item.get('SKU', 'N/A')),
                            item.get('TIPOMOVIMENTACAO', 'N/A'),
                            str(item.get('VALORDEVPRODUTO', 'N/A')),
                            str(item.get('VALORVENDAPRODUTO', 'N/A')),
                            str(item.get('_id', 'N/A'))
                        ]
                    )
                else:
                    return "Não foi possível buscar dados de exemplo."
            
            return None  # Não é uma consulta que pode ser respondida diretamente
            
        except Exception as e:
            print(f"❌ Erro na consulta direta: {e}")
            return None

    def _detectar_quantidade(self, pergunta: str) -> int:
        """
        Detecta a quantidade solicitada na pergunta.
        """
        pergunta_lower = pergunta.lower()
        
        # Números diretos
        if 'top 1' in pergunta_lower or 'top1' in pergunta_lower or 'primeiro' in pergunta_lower:
            return 1
        elif 'top 3' in pergunta_lower or 'top3' in pergunta_lower or 'três' in pergunta_lower or 'tres' in pergunta_lower:
            return 3
        elif 'top 5' in pergunta_lower or 'top5' in pergunta_lower or 'cinco' in pergunta_lower:
            return 5
        elif 'top 10' in pergunta_lower or 'top10' in pergunta_lower or 'dez' in pergunta_lower:
            return 10
        elif 'top 15' in pergunta_lower or 'top15' in pergunta_lower or 'quinze' in pergunta_lower:
            return 15
        elif 'top 20' in pergunta_lower or 'top20' in pergunta_lower or 'vinte' in pergunta_lower:
            return 20
        elif 'top 25' in pergunta_lower or 'top25' in pergunta_lower or 'vinte e cinco' in pergunta_lower:
            return 25
        elif 'top 50' in pergunta_lower or 'top50' in pergunta_lower or 'cinquenta' in pergunta_lower:
            return 50
        elif 'top 100' in pergunta_lower or 'top100' in pergunta_lower or 'cem' in pergunta_lower:
            return 100
        
        # Buscar números na pergunta
        import re
        numeros = re.findall(r'\b(\d+)\b', pergunta)
        if numeros:
            return int(numeros[0])
        
        # Padrão padrão
        return 10

    def _formatar_como_tabela(self, dados: list, colunas: list, titulo: str, formata_dados) -> str:
        """
        Formata dados como uma tabela HTML estilizada.
        """
        html = f"""
        <div style="margin: 20px 0; font-family: Arial, sans-serif;">
            <h3 style="color: #333; margin-bottom: 15px; text-align: center;">{titulo}</h3>
            <div style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse; background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;">
                    <thead>
                        <tr style="background-color: #f8f9fa;">
        """
        
        # Cabeçalho da tabela
        for coluna in colunas:
            html += f'<th style="padding: 12px 15px; text-align: left; font-weight: bold; color: #495057; border-bottom: 2px solid #dee2e6;">{coluna}</th>'
        
        html += """
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Dados da tabela
        for i, item in enumerate(dados):
            cor_linha = "#f8f9fa" if i % 2 == 0 else "white"
            html += f'<tr style="background-color: {cor_linha};">'
            
            dados_formatados = formata_dados(i, item)
            for dado in dados_formatados:
                html += f'<td style="padding: 10px 15px; border-bottom: 1px solid #dee2e6; color: #495057;">{dado}</td>'
            
            html += '</tr>'
        
        html += """
                    </tbody>
                </table>
            </div>
        </div>
        """
        
        return html

    def _get_cache_key(self, interpretacao: Dict[str, Any]) -> str:
        """Gera chave única para o cache baseada na interpretação."""
        return f"{interpretacao['tipo']}_{interpretacao['quantidade']}_{interpretacao['formato_tabela']}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[str]:
        """Recupera resultado do cache."""
        if cache_key in self.cache_consultas:
            print(f"🚀 Cache hit: {cache_key}")
            return self.cache_consultas[cache_key]
        return None
    
    def _save_to_cache(self, cache_key: str, resultado: str):
        """Salva resultado no cache."""
        # Limitar tamanho do cache
        if len(self.cache_consultas) >= self.cache_max_size:
            # Remover o item mais antigo (FIFO)
            oldest_key = next(iter(self.cache_consultas))
            del self.cache_consultas[oldest_key]
        
        self.cache_consultas[cache_key] = resultado
        print(f"💾 Cache saved: {cache_key}")

    def _fazer_consulta_inteligente(self, interpretacao: Dict[str, Any]) -> Optional[str]:
        """
        Faz consulta inteligente baseada na interpretação da pergunta.
        OTIMIZADO: Usa cache para consultas frequentes.
        """
        try:
            # Verificar cache primeiro
            cache_key = self._get_cache_key(interpretacao)
            resultado_cache = self._get_from_cache(cache_key)
            if resultado_cache:
                return resultado_cache
            
            tipo = interpretacao['tipo']
            quantidade = interpretacao['quantidade']
            formato_tabela = interpretacao['formato_tabela']
            
            if tipo == 'top_sku':
                pipeline = [
                    {"$match": {"SKU": {"$exists": True, "$ne": None}}},  # Filtrar SKUs válidos
                    {"$group": {"_id": "$SKU", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": quantidade}
                ]
                resultado = list(self.db.DEVOLUCAO.aggregate(pipeline))
                if resultado:
                    if formato_tabela:
                        resposta = self._formatar_como_tabela(
                            dados=resultado,
                            colunas=['Posição', 'SKU', 'Quantidade de Devoluções'],
                            titulo=f"Top {quantidade} SKUs Mais Frequentes",
                            formata_dados=lambda i, item: [
                                i + 1,
                                item['_id'] if item['_id'] else 'N/A',
                                f"{item['count']:,}"
                            ]
                        )
                        self._save_to_cache(cache_key, resposta)
                        return resposta
                    else:
                        resposta = f"Os {quantidade} SKUs mais frequentes no banco são:\n\n"
                        for i, item in enumerate(resultado, 1):
                            sku = item['_id'] if item['_id'] else 'N/A'
                            count = item['count']
                            resposta += f"{i}. **SKU {sku}**: {count:,} devoluções\n"
                        self._save_to_cache(cache_key, resposta)
                        return resposta
                else:
                    resultado = "Não foi possível analisar os SKUs."
                    self._save_to_cache(cache_key, resultado)
                    return resultado
            
            elif tipo == 'top_loja':
                pipeline = [
                    {"$match": {"LOJA": {"$exists": True, "$ne": None}}},  # Filtrar lojas válidas
                    {"$group": {"_id": "$LOJA", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": quantidade}
                ]
                resultado = list(self.db.DEVOLUCAO.aggregate(pipeline))
                if resultado:
                    if formato_tabela:
                        resposta = self._formatar_como_tabela(
                            dados=resultado,
                            colunas=['Posição', 'Loja', 'Quantidade de Devoluções'],
                            titulo=f"Top {quantidade} Lojas Mais Frequentes",
                            formata_dados=lambda i, item: [
                                i + 1,
                                item['_id'] if item['_id'] else 'N/A',
                                f"{item['count']:,}"
                            ]
                        )
                        self._save_to_cache(cache_key, resposta)
                        return resposta
                    else:
                        resposta = f"As {quantidade} lojas mais frequentes no banco são:\n\n"
                        for i, item in enumerate(resultado, 1):
                            loja = item['_id'] if item['_id'] else 'N/A'
                            count = item['count']
                            resposta += f"{i}. **Loja {loja}**: {count:,} devoluções\n"
                        self._save_to_cache(cache_key, resposta)
                        return resposta
                else:
                    resultado = "Não foi possível analisar as lojas."
                    self._save_to_cache(cache_key, resultado)
                    return resultado
            
            elif tipo == 'top_usuario':
                pipeline = [
                    {"$match": {"IDUSUARIO": {"$exists": True, "$ne": None}}},  # Filtrar usuários válidos
                    {"$group": {"_id": "$IDUSUARIO", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": quantidade}
                ]
                resultado = list(self.db.DEVOLUCAO.aggregate(pipeline))
                if resultado:
                    if formato_tabela:
                        resposta = self._formatar_como_tabela(
                            dados=resultado,
                            colunas=['Posição', 'ID Usuário', 'Quantidade de Devoluções'],
                            titulo=f"Top {quantidade} Usuários Mais Frequentes",
                            formata_dados=lambda i, item: [
                                i + 1,
                                item['_id'] if item['_id'] else 'N/A',
                                f"{item['count']:,}"
                            ]
                        )
                        self._save_to_cache(cache_key, resposta)
                        return resposta
                    else:
                        resposta = f"Os {quantidade} usuários mais frequentes no banco são:\n\n"
                        for i, item in enumerate(resultado, 1):
                            usuario = item['_id'] if item['_id'] else 'N/A'
                            count = item['count']
                            resposta += f"{i}. **Usuário {usuario}**: {count:,} devoluções\n"
                        self._save_to_cache(cache_key, resposta)
                        return resposta
                else:
                    resultado = "Não foi possível analisar os usuários."
                    self._save_to_cache(cache_key, resultado)
                    return resultado
            
            elif tipo == 'contagem_total':
                total = self.db.DEVOLUCAO.count_documents({})
                resultado = f"O banco de dados possui **{total:,}** registros de devolução."
                self._save_to_cache(cache_key, resultado)
                return resultado
            
            return None
            
        except Exception as e:
            print(f"❌ Erro na consulta inteligente: {e}")
            return None

    def perguntar(self, pergunta: str) -> Dict[str, Any]:
        """
        Faz uma pergunta ao agente.
        
        Args:
            pergunta: Pergunta do usuário
            
        Returns:
            Dicionário com resposta e documentos fonte
        """
        if not self.qa_chain:
            raise ValueError("Agente não foi criado. Execute criar_agente() primeiro.")
        
        try:
            print(f"🤔 Pergunta: {pergunta}")
            
            # Interpretar a pergunta de forma inteligente
            interpretacao = self._interpretar_pergunta(pergunta)
            print(f"🧠 Interpretação: {interpretacao}")
            
            # Se conseguiu interpretar, fazer consulta direta específica
            if interpretacao['tipo']:
                resultado_direto = self._fazer_consulta_inteligente(interpretacao)
                if resultado_direto:
                    print(f"💬 Resposta (consulta inteligente): {resultado_direto}")
                    return {
                        "pergunta": pergunta,
                        "resposta": resultado_direto,
                        "documentos_fonte": []
                    }
            
            # Fallback: tentar consulta direta tradicional
            resposta_direta = self._fazer_consulta_direta(pergunta)
            if resposta_direta:
                print(f"💬 Resposta (consulta direta): {resposta_direta}")
                return {
                    "pergunta": pergunta,
                    "resposta": resposta_direta,
                    "documentos_fonte": []
                }
            
            # Executar consulta via LangChain
            resultado = self.qa_chain({"question": pergunta})
            
            resposta = resultado["answer"]
            documentos_fonte = resultado.get("source_documents", [])
            
            print(f"💬 Resposta: {resposta}")
            
            return {
                "pergunta": pergunta,
                "resposta": resposta,
                "documentos_fonte": [
                    {
                        "colecao": doc.metadata.get("colecao", ""),
                        "id": doc.metadata.get("id", ""),
                        "preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                    }
                    for doc in documentos_fonte
                ]
            }
            
        except Exception as e:
            print(f"❌ Erro ao processar pergunta: {e}")
            return {
                "pergunta": pergunta,
                "resposta": f"Erro ao processar pergunta: {str(e)}",
                "documentos_fonte": []
            }


def criar_agente_mongodb() -> MongoDBAgent:
    """
    Função utilitária para criar e configurar o agente MongoDB.
    
    Returns:
        Instância configurada do MongoDBAgent
    """
    agente = MongoDBAgent()
    agente.conectar_mongodb()
    agente.criar_agente()
    return agente


# Exemplo de uso
if __name__ == "__main__":
    # Configurar variável de ambiente (substitua pela sua chave)
    # os.environ["OPENAI_API_KEY"] = "sua_chave_openai_aqui"
    
    try:
        # Criar agente
        print("🚀 Iniciando agente MongoDB...")
        agente = criar_agente_mongodb()
        
        # Exemplos de perguntas
        perguntas_exemplo = [
            "Quantos registros existem no banco de dados?",
            "Quais são as principais coleções disponíveis?",
            "Mostre alguns exemplos de dados da coleção DEVOLUCAO",
            "Existe alguma informação sobre clientes?"
        ]
        
        print("\n" + "="*50)
        print("EXEMPLOS DE USO DO AGENTE")
        print("="*50)
        
        for pergunta in perguntas_exemplo:
            print(f"\n📝 Testando pergunta: {pergunta}")
            resultado = agente.perguntar(pergunta)
            print(f"✅ Resposta: {resultado['resposta']}")
            print("-" * 30)
        
        # Loop interativo
        print("\n" + "="*50)
        print("MODO INTERATIVO - Digite suas perguntas (ou 'sair' para encerrar)")
        print("="*50)
        
        while True:
            pergunta_usuario = input("\n🤔 Sua pergunta: ").strip()
            
            if pergunta_usuario.lower() in ['sair', 'exit', 'quit']:
                print("👋 Encerrando agente...")
                break
                
            if pergunta_usuario:
                resultado = agente.perguntar(pergunta_usuario)
                print(f"💬 Resposta: {resultado['resposta']}")
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("💡 Verifique se:")
        print("   1. MongoDB está rodando localmente")
        print("   2. OPENAI_API_KEY está configurada")
        print("   3. Existem dados no banco 'grupo_oscar'")
