#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("=== Teste Simples do Sistema de Vetores ===")

try:
    # Teste 1: Importar módulos básicos
    print("1. Testando imports básicos...")
    import sys
    print(f"   Python: {sys.version}")
    
    import pandas as pd
    print("   Pandas: OK")
    
    import chromadb
    print("   ChromaDB: OK")
    
    # Teste 2: Importar módulo de vetores
    print("\n2. Testando módulo de vetores...")
    from app.vectors import create_text_chunks
    print("   create_text_chunks: OK")
    
    # Teste 3: Testar função de chunks
    print("\n3. Testando criação de chunks...")
    test_df = pd.DataFrame({
        'sku': ['SKU001', 'SKU002'],
        'nome': ['Produto A', 'Produto B'],
        'preco': [100.50, 75.25]
    })
    
    chunks = create_text_chunks(test_df)
    print(f"   Chunks criados: {len(chunks)}")
    
    for i, chunk in enumerate(chunks):
        print(f"   Chunk {i+1}: {chunk['text'][:50]}...")
    
    print("\n✅ Todos os testes passaram!")
    
except Exception as e:
    print(f"\n❌ Erro durante teste: {str(e)}")
    import traceback
    traceback.print_exc()




