from pymongo import MongoClient
from errors.error_handler import ImportErrorHandler
import database.db_config as db_config


def inserir_mongo(nome_colecao, df):
    """
    Insere os registros de um DataFrame em uma coleção MongoDB.
    """
    try:
        client = MongoClient(db_config.MONGO_URI)
        db = client[db_config.DB_NAME]
        colecao = db[nome_colecao]

        registros = df.to_dict(orient="records")

        if registros:
            colecao.insert_many(registros)
            print(f"✅ Inseridos {len(registros)} registros na coleção '{nome_colecao}'")
        else:
            print(f"⚠️ Nenhum registro encontrado para inserir na coleção '{nome_colecao}'")

    except Exception as e:
        ImportErrorHandler.erro_mongo(str(e))
