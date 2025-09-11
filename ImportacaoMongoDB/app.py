from flask import Flask, request, render_template, redirect, url_for, flash
from pymongo import MongoClient
from bson import ObjectId
import database.db_config as db_config
from modules.importar_csv import importar_csv_para_mongo
import os
import tempfile

app = Flask(__name__)
app.secret_key = "supersecret"

client = MongoClient(db_config.MONGO_URI)
db = client[db_config.DB_NAME]


@app.route("/")
def index():
    colecoes = db.list_collection_names()
    return render_template("index.html", colecoes=colecoes)


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


@app.route("/colecao/<nome>/excluir", methods=["POST"])
def excluir_colecao(nome):
    db[nome].drop()
    flash(f"❌ Coleção '{nome}' excluída")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
