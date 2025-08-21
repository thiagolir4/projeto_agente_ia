#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("=== Teste da Aplicação ===")

try:
    # Teste 1: Imports básicos
    print("1. Testando imports básicos...")
    import sys
    print(f"   Python: {sys.version}")
    
    import pandas as pd
    print("   Pandas: OK")
    
    import chromadb
    print("   ChromaDB: OK")
    
    # Teste 2: Módulos da aplicação
    print("\n2. Testando módulos da aplicação...")
    
    from app.config import settings
    print("   Config: OK")
    
    from app.db import get_duckdb, close_duckdb
    print("   Database: OK")
    
    from app.vectors import create_text_chunks
    print("   Vectors: OK")
    
    # Teste 3: Routers
    print("\n3. Testando routers...")
    
    from app.routers.datasets import router as datasets_router
    print("   Datasets router: OK")
    
    from app.routers.cleaning import router as cleaning_router
    print("   Cleaning router: OK")
    
    from app.routers.analysis import router as analysis_router
    print("   Analysis router: OK")
    
    from app.routers.vectors import router as vectors_router
    print("   Vectors router: OK")
    
    # Teste 4: Aplicação principal
    print("\n4. Testando aplicação principal...")
    
    from app.main import app
    print("   App principal: OK")
    print(f"   Total de rotas: {len(app.routes)}")
    
    # Mostrar algumas rotas
    print("\n   Rotas principais:")
    for route in app.routes:
        if hasattr(route, 'path') and route.path:
            print(f"     {route.path} [{', '.join(route.methods) if hasattr(route, 'methods') else 'N/A'}]")
    
    # Teste 5: Função de chunks
    print("\n5. Testando função de chunks...")
    
    test_df = pd.DataFrame({
        'sku': ['SKU001', 'SKU002'],
        'nome': ['Produto A', 'Produto B'],
        'preco': [100.50, 75.25]
    })
    
    chunks = create_text_chunks(test_df)
    print(f"   Chunks criados: {len(chunks)}")
    
    for i, chunk in enumerate(chunks):
        print(f"   Chunk {i+1}: {chunk['text'][:50]}...")
    
    print("\n🎉 Todos os testes passaram! A aplicação está funcionando corretamente.")
    
except Exception as e:
    print(f"\n❌ Erro durante teste: {str(e)}")
    import traceback
    traceback.print_exc()




