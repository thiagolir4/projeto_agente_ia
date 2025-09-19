import os
import pandas as pd
import hashlib
from pymongo import MongoClient, errors
from database import db_config
from utils.utils import carregar_csv
# Função de normalização simplificada (removida dependência do normalizer.py)
from errors.error_handler import ImportErrorHandler


def normalizar_dataframe(df, nome_arquivo):
    """
    Função de normalização simplificada para o DataFrame.
    """
    # Converter colunas para string para evitar problemas de tipo
    for col in df.columns:
        df[col] = df[col].astype(str)
    
    # Remover espaços em branco no início e fim
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    
    return df


def gerar_hash_colunas(df):
    """
    Gera hash SHA256 para cada linha de um DataFrame de forma vetorizada.
    """
    # Concatena todas as colunas em uma string única por linha
    concatenado = df.astype(str).agg("|".join, axis=1)
    return concatenado.apply(lambda x: hashlib.sha256(x.encode("utf-8")).hexdigest())


def importar_csv_para_mongo(caminho, nome_arquivo=None):
    try:
        # Carregar DataFrame + nome sugerido
        df, nome_base = carregar_csv(caminho)
        if not nome_arquivo:
            nome_arquivo = nome_base

        # Normalização
        df = normalizar_dataframe(df, nome_arquivo)

        # Criar hash de forma vetorizada (mais rápido)
        df["_hash"] = gerar_hash_colunas(df)

        # Conectar Mongo
        client = MongoClient(db_config.MONGO_URI)
        db = client[db_config.DB_NAME]
        colecao = db[nome_arquivo]

        # Criar índice único no hash (se não existir)
        try:
            colecao.create_index("_hash", unique=True)
        except errors.OperationFailure:
            pass  # índice já existe

        # Converter para dicionários
        registros = df.to_dict(orient="records")

        # Inserção em lote (ignora duplicados automaticamente)
        try:
            result = colecao.insert_many(registros, ordered=False)
            inseridos = len(result.inserted_ids)
        except errors.BulkWriteError as bwe:
            # Conta só os documentos que entraram
            inseridos = bwe.details["nInserted"]

        print(f"✅ Inseridos {inseridos} novos registros na coleção '{nome_arquivo}'")

    except Exception as e:
        ImportErrorHandler.erro_generico(e)
