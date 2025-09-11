import requests
import json
from io import StringIO
import pandas as pd
import re
from urllib.parse import urlparse, parse_qs


def detectar_delimitador(texto):
    """
    Detecta se o CSV usa vírgula ou ponto e vírgula.
    """
    primeira_linha = texto.split("\n", 1)[0]
    if ";" in primeira_linha and "," in primeira_linha:
        # Escolher pelo mais frequente
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
        gid = qs.get("gid", ["0"])[0]  # se não tiver gid, pega a primeira aba
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}", sheet_id, gid
    return url, None, None


import requests
import re
import json

def obter_nome_planilha_google_sheets(sheet_id, gid="0"):
    """
    Obtém o nome da planilha (arquivo) a partir do HTML público do Google Sheets.
    """
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit?gid={gid}"
    resp = requests.get(url)
    resp.raise_for_status()

    # Tenta pegar pelo docs-title-input
    match = re.search(r'class="docs-title-input"[^>]*value="([^"]+)"', resp.text)
    if match:
        return match.group(1).strip().replace(" ", "_")

    # Fallback: usa <title>
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
        print(f"🌐 Baixando CSV da URL: {url}")
        resp = requests.get(url)
        resp.raise_for_status()

        delimitador = detectar_delimitador(resp.text)
        print(f"📑 Delimitador detectado: '{delimitador}'")

        data = StringIO(resp.text)
        df = pd.read_csv(data, sep=delimitador, encoding="cp1252", dtype=str)

        # Nome da coleção: nome da aba no Google Sheets
        if sheet_id:
            nome_colecao = obter_nome_planilha_google_sheets(sheet_id)
        else:
            nome_colecao = urlparse(url).path.split("/")[-1].replace(".csv", "")


    else:
        print(f"📂 Lendo CSV local: {caminho_csv}")
        with open(caminho_csv, "r", encoding="cp1252") as f:
            conteudo = f.read()
        delimitador = detectar_delimitador(conteudo)
        print(f"📑 Delimitador detectado: '{delimitador}'")
        df = pd.read_csv(StringIO(conteudo), sep=delimitador, encoding="cp1252", dtype=str)
        nome_colecao = caminho_csv.split("/")[-1].replace(".csv", "")

    return df, nome_colecao
