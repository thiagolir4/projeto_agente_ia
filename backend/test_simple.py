#!/usr/bin/env python3

print("Testando imports...")

try:
    import fastapi
    print("✅ FastAPI importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar FastAPI: {e}")

try:
    import uvicorn
    print("✅ Uvicorn importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar Uvicorn: {e}")

try:
    import pandas as pd
    print("✅ Pandas importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar Pandas: {e}")

try:
    import polars as pl
    print("✅ Polars importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar Polars: {e}")

try:
    import duckdb
    print("✅ DuckDB importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar DuckDB: {e}")

try:
    import chromadb
    print("✅ ChromaDB importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar ChromaDB: {e}")

try:
    from agno.agent import Agent
    print("✅ Agno Agent importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar Agno Agent: {e}")

try:
    from agno.tools import Function
    print("✅ Agno Function importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar Agno Function: {e}")

print("\nTeste concluído!")

