import pandas as pd

def normalizar_dataframe(df, nome_arquivo):
    """
    Aplica regras de normalização comuns e específicas por tipo de planilha.
    """

    # Normalizações comuns
    if "SKU" in df.columns:
        df["SKU"] = df["SKU"].astype(str)

    if "DATA" in df.columns:
        df["DATA"] = pd.to_datetime(df["DATA"], format="%d/%m/%Y", errors="coerce")

    # Regras específicas
    if "ajustes_estoque_2025" in nome_arquivo.lower():
        mapeamento = {
            "SA?DA DO ESTOQUE": "SAÍDA DO ESTOQUE",
            "AJUSTE CONTAGEM SAIDA": "AJUSTE CONTAGEM SAÍDA",
        }
        if "TIPO_AJUSTE" in df.columns:
            df["TIPO_AJUSTE"] = df["TIPO_AJUSTE"].replace(mapeamento)

    elif "devolucao" in nome_arquivo.lower():
        mapeamento = {
            "Sa?a": "Saída"
        }
        if "TIPOMOVIMENTACAO" in df.columns:
            df["TIPOMOVIMENTACAO"] = df["TIPOMOVIMENTACAO"].replace(mapeamento)
            
    elif "cancelamento" in nome_arquivo.lower():
        mapeamento = {
            "NÃ£o": "Não"
        }
        if "ATIVO_CANCELADO" in df.columns:
            df["ATIVO_CANCELADO"] = df["ATIVO_CANCELADO"].replace(mapeamento)
        if "CONFIRMADO_CANCELADO" in df.columns:
            df["CONFIRMADO_CANCELADO"] = df["CONFIRMADO_CANCELADO"].replace(mapeamento)

    return df
