print("Teste básico iniciado")

try:
    print("1. Importando sys...")
    import sys
    print(f"Python version: {sys.version}")
    
    print("2. Importando pandas...")
    import pandas as pd
    print("Pandas OK")
    
    print("3. Importando chromadb...")
    import chromadb
    print("ChromaDB OK")
    
    print("4. Testando módulo config...")
    from app.config import settings
    print("Config OK")
    
    print("5. Testando módulo db...")
    from app.db import get_duckdb
    print("DB OK")
    
    print("6. Testando módulo vectors...")
    from app.vectors import create_text_chunks
    print("Vectors OK")
    
    print("7. Testando routers...")
    from app.routers.datasets import router
    print("Datasets router OK")
    
    from app.routers.cleaning import router as cleaning_router
    print("Cleaning router OK")
    
    from app.routers.analysis import router as analysis_router
    print("Analysis router OK")
    
    from app.routers.vectors import router as vectors_router
    print("Vectors router OK")
    
    print("8. Testando app principal...")
    from app.main import app
    print("App principal OK")
    print(f"Total de rotas: {len(app.routes)}")
    
    print("\n🎉 Todos os testes passaram!")
    
except Exception as e:
    print(f"\n❌ Erro: {str(e)}")
    import traceback
    traceback.print_exc()




