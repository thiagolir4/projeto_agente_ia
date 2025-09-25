import pandas as pd
import hashlib
from pymongo import MongoClient, errors
from database import db_config
from utils.utils import carregar_csv, corrigir_encoding_dataframe
from errors.error_handler import ImportErrorHandler


def normalizar_dataframe(df, nome_arquivo):
    """
    Normaliza o DataFrame aplicando correções de encoding e limpeza de dados
    """
    df = corrigir_encoding_dataframe(df)
    
    for col in df.columns:
        df[col] = df[col].astype(str)
    
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    
    return df


def gerar_hash_colunas(df):
    """
    Gera hash SHA256 para cada linha do DataFrame para identificar duplicatas
    """
    concatenado = df.astype(str).agg("|".join, axis=1)
    return concatenado.apply(lambda x: hashlib.sha256(x.encode("utf-8")).hexdigest())


def importar_csv_para_mongo(caminho, nome_arquivo=None):
    try:
        df, nome_base = carregar_csv(caminho)
        if not nome_arquivo:
            nome_arquivo = nome_base

        df = normalizar_dataframe(df, nome_arquivo)
        df["_hash"] = gerar_hash_colunas(df)

        client = MongoClient(db_config.MONGO_URI)
        db = client[db_config.DB_NAME]
        colecao = db[nome_arquivo]

        try:
            colecao.create_index("_hash", unique=True)
        except errors.OperationFailure:
            pass

        registros = df.to_dict(orient="records")

        try:
            result = colecao.insert_many(registros, ordered=False)
            inseridos = len(result.inserted_ids)
        except errors.BulkWriteError as bwe:
            inseridos = bwe.details["nInserted"]

        print(f"Inseridos {inseridos} novos registros na coleção '{nome_arquivo}'")

    except Exception as e:
        ImportErrorHandler.erro_generico(e)
