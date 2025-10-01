import requests
from io import StringIO
import pandas as pd
import re
from urllib.parse import urlparse, parse_qs
from datetime import datetime


def corrigir_encoding_dataframe(df):
    """
    Corrige problemas de encoding em DataFrames, especialmente caracteres acentuados
    """
    correcoes = {
        'Sa?a': 'Saída',
        'SA?DA': 'SAIDA',
        'Entrada ': 'Entrada',
        'NÃ£o	': 'Não',
        'NÃ£o': 'Não'
       
    }
    
    for coluna in df.columns:
        if df[coluna].dtype == 'object':
            for char_errado, char_correto in correcoes.items():
                df[coluna] = df[coluna].astype(str).str.replace(char_errado, char_correto, regex=False)
    
    return df


def detectar_delimitador(texto):
    """
    Detecta se o CSV usa vírgula ou ponto e vírgula.
    """
    primeira_linha = texto.split("\n", 1)[0]
    if ";" in primeira_linha and "," in primeira_linha:
        return ";" if primeira_linha.count(";") > primeira_linha.count(",") else ","
    elif ";" in primeira_linha:
        return ";"
    else:
        return ","


def ajustar_link_google_sheets(url):
    """
    Converte link de Google Sheets em link de exportação CSV.
    Inclui suporte a 'gid' (aba da planilha).
    """
    if "docs.google.com/spreadsheets" in url:
        sheet_id = url.split("/d/")[1].split("/")[0]
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        gid = qs.get("gid", ["0"])[0]
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}", sheet_id, gid
    return url, None, None


def obter_nome_planilha_google_sheets(sheet_id, gid="0"):
    """
    Obtém o nome da planilha (arquivo) a partir do HTML público do Google Sheets.
    """
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit?gid={gid}"
    resp = requests.get(url)
    resp.raise_for_status()

    match = re.search(r'class="docs-title-input"[^>]*value="([^"]+)"', resp.text)
    if match:
        return match.group(1).strip().replace(" ", "_")

    match = re.search(r"<title>(.*?) - Google Sheets</title>", resp.text)
    if match:
        return match.group(1).strip().replace(" ", "_")

    return f"planilha_{sheet_id}"



def carregar_csv(caminho_csv):
    """
    Carrega CSV seja de URL (Google Sheets incluso) ou arquivo local.
    Retorna DataFrame e nome base sugerido para coleção.
    """
    if caminho_csv.startswith("http://") or caminho_csv.startswith("https://"):
        
        # Ajustar se for Google Sheets
        url, sheet_id, gid = ajustar_link_google_sheets(caminho_csv)
        print(f"Baixando CSV da URL: {url}")
        resp = requests.get(url)
        resp.raise_for_status()

        delimitador = detectar_delimitador(resp.text)
        print(f"Delimitador detectado: '{delimitador}'")

        data = StringIO(resp.text)
        try:
            df = pd.read_csv(data, sep=delimitador, encoding="utf-8", dtype=str)
        except UnicodeDecodeError:
            data = StringIO(resp.text)
            df = pd.read_csv(data, sep=delimitador, encoding="cp1252", dtype=str)
            df = corrigir_encoding_dataframe(df)
        if sheet_id:
            nome_colecao = obter_nome_planilha_google_sheets(sheet_id)
        else:
            nome_colecao = urlparse(url).path.split("/")[-1].replace(".csv", "")


    else:
        print(f"Lendo CSV local: {caminho_csv}")
        try:
            with open(caminho_csv, "r", encoding="utf-8") as f:
                conteudo = f.read()
        except UnicodeDecodeError:
            with open(caminho_csv, "r", encoding="cp1252") as f:
                conteudo = f.read()
        
        delimitador = detectar_delimitador(conteudo)
        print(f"Delimitador detectado: '{delimitador}'")
        
        try:
            df = pd.read_csv(StringIO(conteudo), sep=delimitador, encoding="utf-8", dtype=str)
        except UnicodeDecodeError:
            df = pd.read_csv(StringIO(conteudo), sep=delimitador, encoding="cp1252", dtype=str)
            df = corrigir_encoding_dataframe(df)
        nome_colecao = caminho_csv.split("/")[-1].replace(".csv", "")

    return df, nome_colecao

# -*- coding: utf-8 -*-
"""
Normalizador de DataFrames antes de inserção no MongoDB
"""


def normalizar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza os dados do DataFrame:
      - Converte colunas que contenham 'data' no nome para datetime.
      - Remove espaços extras dos nomes das colunas.
      - Remove linhas completamente vazias.
    """
    # Limpar nomes de colunas
    df.columns = [col.strip().upper() for col in df.columns]

    # Remover linhas totalmente vazias
    df = df.dropna(how="all")

    # Converter colunas que contenham "DATA" no nome
    for col in df.columns:
        if "DATA" in col.upper():
            try:
                df[col] = pd.to_datetime(
                    df[col],
                    format="%d/%m/%Y",
                    errors="coerce"  # valores inválidos viram NaT
                )
            except Exception:
                pass  # mantém original caso não seja conversível

    # Remover linhas onde todas as colunas de data são NaT
    df = df.dropna(how="all")

    return df
