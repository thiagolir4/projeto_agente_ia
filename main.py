# -*- coding: utf-8 -*-
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from pymongo import MongoClient
from bson import ObjectId
import sys
import os
import tempfile
import json

# Adicionar o backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))

# Imports do backend
import database.db_config as db_config
from modules.importar_csv import importar_csv_para_mongo
from agents.mongodb_agent import MongoDBAgent

# Configurar Flask com templates do frontend
app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')
app.secret_key = "supersecret"

client = MongoClient(db_config.MONGO_URI)
db = client[db_config.DB_NAME]

# Inicializar agente MongoDB (lazy loading)
mongodb_agent = None

def get_mongodb_agent():
    """Obtém ou cria o agente MongoDB"""
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
            print("✅ Agente MongoDB inicializado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao inicializar agente: {e}")
            return None
    return mongodb_agent


@app.route("/")
def index():
    colecoes = db.list_collection_names()
    return render_template("index.html", colecoes=colecoes)

@app.route("/health")
def health():
    return jsonify({"status": "ok", "message": "Aplicação funcionando"})


@app.route("/importar", methods=["POST"])
def importar():
    caminho = None
    nome_arquivo = None

    # Caso seja um link informado no input texto
    if request.form.get("caminho"):
        caminho = request.form.get("caminho")

    # Caso seja upload de arquivo
    elif "arquivo" in request.files:
        arquivo = request.files["arquivo"]
        if arquivo.filename != "":
            temp_dir = tempfile.gettempdir()
            caminho = os.path.join(temp_dir, arquivo.filename)
            arquivo.save(caminho)
            nome_arquivo = os.path.splitext(arquivo.filename)[0]  # <<< nome sem extensão

    if not caminho:
        flash("❌ Informe um link ou envie um arquivo CSV")
        return redirect(url_for("index"))

    try:
        importar_csv_para_mongo(caminho, nome_arquivo=nome_arquivo)
        flash(f"✅ Importação concluída: {nome_arquivo or caminho}")
    except Exception as e:
        flash(f"❌ Erro durante importação: {e}")

    return redirect(url_for("index"))


@app.route("/colecao/<nome>")
def ver_colecao(nome):
    # Parâmetros de paginação
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    skip = (page - 1) * per_page

    try:
        total_docs = db[nome].count_documents({})
        docs = list(db[nome].find().skip(skip).limit(per_page))

        # Converte ObjectId para string
        for d in docs:
            if "_id" in d and isinstance(d["_id"], ObjectId):
                d["_id"] = str(d["_id"])

        colunas = sorted({key for doc in docs for key in doc.keys() if key != "_hash"})
        for d in docs:
         d.pop("_hash", None)  # remove do documento

        
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
        flash(f"❌ Erro ao acessar coleção: {e}")
        return redirect(url_for("index"))


@app.route("/colecao/<nome>/excluir", methods=["POST"])
def excluir_colecao(nome):
    db[nome].drop()
    flash(f"❌ Coleção '{nome}' excluída")
    return redirect(url_for("index"))


@app.route("/chat", methods=["POST"])
def chat():
    """Endpoint para chat com o agente IA"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({"error": "Mensagem vazia"}), 400
        
        # Obter agente MongoDB
        agent = get_mongodb_agent()
        if not agent:
            return jsonify({
                "error": "Agente não disponível. Verifique se o MongoDB está rodando e se a OPENAI_API_KEY está configurada."
            }), 500
        
        # Processar pergunta
        resultado = agent.perguntar(message)
        
        return jsonify({
            "response": resultado["resposta"],
            "sources": resultado.get("documentos_fonte", [])
        })
        
    except Exception as e:
        print(f"❌ Erro no chat: {e}")
        return jsonify({
            "error": f"Erro interno: {str(e)}"
        }), 500


if __name__ == "__main__":
    print("🚀 Iniciando aplicação Flask...")
    print("📊 MongoDB:", db_config.MONGO_URI)
    print("🗄️  Database:", db_config.DB_NAME)
    
    print("🌐 Acesse: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)