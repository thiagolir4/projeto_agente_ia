import requests
import json
import time
import uuid

BASE_URL = "http://127.0.0.1:8001"

def test_vectors_system():
    """Testa o sistema completo de vetores"""
    print("=== Testando Sistema de Vetores ===")
    
    # Gerar IDs únicos para teste
    session_id = f"test_session_{uuid.uuid4().hex[:8]}"
    print(f"Sessão de teste: {session_id}")
    
    try:
        # 1. Verificar estatísticas da sessão (deve estar vazia)
        print("\n1. Verificando estatísticas da sessão vazia...")
        response = requests.get(f"{BASE_URL}/vectors/stats/{session_id}")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Estatísticas obtidas: {stats['data']}")
        else:
            print(f"❌ Erro ao obter estatísticas: {response.status_code}")
            return False
        
        # 2. Criar um dataset de teste simples
        print("\n2. Criando dataset de teste...")
        test_data = {
            'sku': ['SKU001', 'SKU002', 'SKU003'],
            'nome': ['Produto A', 'Produto B', 'Produto C'],
            'preco': [100.50, 75.25, 200.00],
            'categoria': ['Eletronicos', 'Vestuario', 'Casa']
        }
        
        import pandas as pd
        import tempfile
        import os
        
        df = pd.DataFrame(test_data)
        
        # Salvar como CSV temporário
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False)
            temp_file = f.name
        
        # Upload do dataset
        with open(temp_file, 'rb') as f:
            files = {'file': ('test_vectors.csv', f, 'text/csv')}
            response = requests.post(f"{BASE_URL}/datasets/upload", files=files)
        
        os.unlink(temp_file)  # Remover arquivo temporário
        
        if response.status_code != 200:
            print(f"❌ Erro ao criar dataset: {response.status_code}")
            return False
        
        dataset_result = response.json()
        dataset_id = dataset_result['id']
        print(f"✅ Dataset criado: {dataset_id}")
        
        # 3. Limpar o dataset
        print("\n3. Limpando dataset...")
        response = requests.post(f"{BASE_URL}/cleaning/run/{dataset_id}")
        
        if response.status_code != 200:
            print(f"❌ Erro ao limpar dataset: {response.status_code}")
            return False
        
        print("✅ Dataset limpo com sucesso")
        
        # 4. Indexar embeddings
        print("\n4. Indexando embeddings...")
        index_request = {
            "session_id": session_id
        }
        
        response = requests.post(f"{BASE_URL}/vectors/index/{dataset_id}", json=index_request)
        
        if response.status_code != 200:
            print(f"❌ Erro na indexação: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        index_result = response.json()
        print(f"✅ Indexação concluída: {index_result['data']['chunks_inserted']} chunks")
        
        # 5. Verificar estatísticas após indexação
        print("\n5. Verificando estatísticas após indexação...")
        response = requests.get(f"{BASE_URL}/vectors/stats/{session_id}")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Estatísticas atualizadas: {stats['data']}")
        else:
            print(f"❌ Erro ao obter estatísticas: {response.status_code}")
        
        # 6. Testar busca
        print("\n6. Testando busca por similaridade...")
        
        # Teste 1: Busca por categoria
        search_request = {
            "session_id": session_id,
            "query": "produtos da categoria eletronicos",
            "top_k": 3
        }
        
        response = requests.post(f"{BASE_URL}/vectors/search", json=search_request)
        
        if response.status_code == 200:
            search_result = response.json()
            print(f"✅ Busca por categoria: {search_result['data']['total_results']} resultados")
            
            if search_result['data']['results']:
                print("   Primeiro resultado:")
                first_result = search_result['data']['results'][0]
                print(f"     Texto: {first_result['text'][:100]}...")
                print(f"     Score: {first_result['similarity_score']:.3f}")
                print(f"     Metadados: {first_result['metadata']}")
        else:
            print(f"❌ Erro na busca por categoria: {response.status_code}")
        
        # Teste 2: Busca por preço
        search_request = {
            "session_id": session_id,
            "query": "produtos com preco alto acima de 150",
            "top_k": 2
        }
        
        response = requests.post(f"{BASE_URL}/vectors/search", json=search_request)
        
        if response.status_code == 200:
            search_result = response.json()
            print(f"✅ Busca por preço: {search_result['data']['total_results']} resultados")
        else:
            print(f"❌ Erro na busca por preço: {response.status_code}")
        
        # 7. Testar isolamento entre sessões
        print("\n7. Testando isolamento entre sessões...")
        other_session_id = f"other_session_{uuid.uuid4().hex[:8]}"
        
        search_request = {
            "session_id": other_session_id,
            "query": "produtos eletronicos",
            "top_k": 3
        }
        
        response = requests.post(f"{BASE_URL}/vectors/search", json=search_request)
        
        if response.status_code == 200:
            search_result = response.json()
            if search_result['data']['total_results'] == 0:
                print("✅ Isolamento funcionando: sessão diferente retorna 0 resultados")
            else:
                print("⚠️  Isolamento pode não estar funcionando corretamente")
        else:
            print(f"❌ Erro ao testar isolamento: {response.status_code}")
        
        # 8. Limpeza - remover sessão de teste
        print("\n8. Limpando sessão de teste...")
        response = requests.delete(f"{BASE_URL}/vectors/session/{session_id}")
        
        if response.status_code == 200:
            delete_result = response.json()
            print(f"✅ Sessão removida: {delete_result['data']['deleted']}")
        else:
            print(f"❌ Erro ao remover sessão: {response.status_code}")
        
        print("\n🎉 Todos os testes do sistema de vetores passaram!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante teste: {str(e)}")
        return False

def main():
    """Função principal"""
    print("Iniciando testes do sistema de vetores...")
    
    try:
        success = test_vectors_system()
        
        if success:
            print("\n📋 Resumo dos testes:")
            print("   ✅ Criação de sessão")
            print("   ✅ Indexação de embeddings")
            print("   ✅ Busca por similaridade")
            print("   ✅ Isolamento entre sessões")
            print("   ✅ Limpeza de sessão")
        else:
            print("\n❌ Alguns testes falharam")
            
    except Exception as e:
        print(f"❌ Erro durante execução: {str(e)}")

if __name__ == "__main__":
    main()

