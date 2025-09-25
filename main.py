# -*- coding: utf-8 -*-
"""
Sistema de Análise Inteligente de Dados - Grupo Oscar
Aplicação Flask principal para gerenciamento de dados com IA
"""
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from pymongo import MongoClient
from bson import ObjectId
import sys
import os
import tempfile
from datetime import datetime

# Adiciona o backend ao path do Python
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))

# Imports dos módulos do backend
import database.db_config as db_config
from modules.importar_csv import importar_csv_para_mongo
from agents.mongodb_agent import MongoDBAgent
from modules.historico_conversas import obter_gerenciador

# Configuração da aplicação Flask
app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')
app.secret_key = "supersecret"

# Conexão com o banco de dados MongoDB
client = MongoClient(db_config.MONGO_URI)
db = client[db_config.DB_NAME]

# Agente IA será inicializado quando necessário (lazy loading)
mongodb_agent = None

# Gerenciador de histórico de conversas
gerenciador_historico = obter_gerenciador()
sessao_atual = None
historico_atual = []

def get_mongodb_agent():
    """
    Obtém ou cria o agente MongoDB para consultas com IA
    """
    global mongodb_agent
    if mongodb_agent is None:
        try:
            print("🤖 Inicializando agente MongoDB...")
            mongodb_agent = MongoDBAgent(
                mongo_uri=db_config.MONGO_URI,
                database_name=db_config.DB_NAME
            )
            mongodb_agent.conectar_mongodb()
            mongodb_agent.criar_agente()
            print("Agente MongoDB inicializado com sucesso!")
        except Exception as e:
            print(f"Erro ao inicializar agente: {e}")
            print("Verifique se o MongoDB está rodando e se a chave da OpenAI está configurada.")
            return None
    return mongodb_agent


def inicializar_historico():
    """Inicializa o histórico de conversas."""
    global sessao_atual, historico_atual
    
    try:
        gerenciador_historico.conectar()
        sessao_atual, historico_atual = gerenciador_historico.carregar_ultima_sessao()
        print(f"Histórico inicializado - Sessão: {sessao_atual}")
        print(f"{len(historico_atual)} mensagens carregadas")
    except Exception as e:
        print(f"Erro ao inicializar histórico: {e}")
        # Criar nova sessão mesmo com erro
        sessao_atual = gerenciador_historico.gerar_id_sessao()
        historico_atual = []
        print(f"Nova sessão criada: {sessao_atual}")


def salvar_mensagem_historico(tipo: str, conteudo: str):
    """Salva uma mensagem no histórico."""
    global sessao_atual, historico_atual
    
    try:
        if sessao_atual:
            gerenciador_historico.salvar_mensagem(sessao_atual, tipo, conteudo)
            
            # Adicionar à lista local
            mensagem = {
                "tipo": tipo,
                "conteudo": conteudo,
                "timestamp": datetime.now().isoformat()
            }
            historico_atual.append(mensagem)
            
    except Exception as e:
        print(f"Erro ao salvar mensagem no histórico: {e}")


@app.route("/")
def index():
    # Filtrar coleções para não mostrar coleções do sistema
    todas_colecoes = db.list_collection_names()
    colecoes = [col for col in todas_colecoes if col not in ['historico_conversas', 'system.indexes']]
    return render_template("index.html", colecoes=colecoes, historico=historico_atual)

@app.route("/health")
def health():
    return jsonify({"status": "ok", "message": "Aplicação funcionando"})


@app.route("/importar", methods=["POST"])
def importar():
    caminho = None
    nome_arquivo = None

    if request.form.get("caminho"):
        caminho = request.form.get("caminho")
    elif "arquivo" in request.files:
        arquivo = request.files["arquivo"]
        if arquivo.filename != "":
            temp_dir = tempfile.gettempdir()
            caminho = os.path.join(temp_dir, arquivo.filename)
            arquivo.save(caminho)
            nome_arquivo = os.path.splitext(arquivo.filename)[0]

    if not caminho:
        flash("Informe um link ou envie um arquivo CSV")
        return redirect(url_for("index"))

    try:
        importar_csv_para_mongo(caminho, nome_arquivo=nome_arquivo)
        flash(f"Importação concluída: {nome_arquivo or caminho}")
    except Exception as e:
        flash(f"Erro durante importação: {e}")

    return redirect(url_for("index"))


@app.route("/colecao/<nome>")
def ver_colecao(nome):
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    skip = (page - 1) * per_page

    try:
        total_docs = db[nome].count_documents({})
        docs = list(db[nome].find().skip(skip).limit(per_page))

        for documento in docs:
            if "_id" in documento and isinstance(documento["_id"], ObjectId):
                documento["_id"] = str(documento["_id"])

        colunas = sorted({key for doc in docs for key in doc.keys() if key != "_hash"})
        for documento in docs:
            documento.pop("_hash", None)

        
        total_pages = (total_docs + per_page - 1) // per_page

        return render_template(
            "colecao.html",
            nome=nome,
            docs=docs,
            colunas=colunas,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )
    except Exception as e:
        flash(f"Erro ao acessar coleção: {e}")
        return redirect(url_for("index"))


@app.route("/colecao/<nome>/excluir", methods=["POST"])
def excluir_colecao(nome):
    db[nome].drop()
    flash(f"Coleção '{nome}' excluída")
    return redirect(url_for("index"))


@app.route("/chat", methods=["POST"])
def chat():
    """Endpoint para chat com o agente IA"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({"error": "Mensagem vazia"}), 400
        
        salvar_mensagem_historico("usuario", message)
        
        agent = get_mongodb_agent()
        if not agent:
            return jsonify({
                "error": "Agente não disponível. Verifique se o MongoDB está rodando e se a OPENAI_API_KEY está configurada."
            }), 500
        
        resultado = agent.perguntar(message)
        salvar_mensagem_historico("agente", resultado["resposta"])
        
        return jsonify({
            "response": resultado["resposta"],
            "sources": resultado.get("documentos_fonte", [])
        })
        
    except Exception as e:
        print(f"Erro no chat: {e}")
        return jsonify({
            "error": f"Erro interno: {str(e)}"
        }), 500


@app.route("/historico/limpar", methods=["POST"])
def limpar_historico():
    """Limpa todo o histórico de conversas."""
    try:
        gerenciador_historico.limpar_todo_historico()
        global historico_atual
        historico_atual = []
        return jsonify({"success": True, "message": "Histórico limpo com sucesso!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/historico/estatisticas")
def estatisticas_historico():
    """Retorna estatísticas do histórico."""
    try:
        stats = gerenciador_historico.obter_estatisticas()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/historico/sessoes")
def listar_sessoes():
    """Lista todas as sessões de conversa."""
    try:
        sessoes = gerenciador_historico.listar_sessoes()
        return jsonify(sessoes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/historico/sessao/<sessao_id>")
def carregar_sessao(sessao_id):
    """Carrega mensagens de uma sessão específica."""
    try:
        mensagens = gerenciador_historico.carregar_historico_sessao(sessao_id)
        return jsonify(mensagens)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("Iniciando aplicação Flask...")
    print("MongoDB:", db_config.MONGO_URI)
    print("Database:", db_config.DB_NAME)
    
    print("Inicializando histórico de conversas...")
    inicializar_historico()
    
    print("Acesse: http://localhost:5000")
    
    app.run(debug=True, host='127.0.0.1', port=5000)