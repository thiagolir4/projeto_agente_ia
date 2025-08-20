import requests
import json
import time

BASE_URL = "http://127.0.0.1:8001"

def test_health():
    """Testa o endpoint de health"""
    print("=== Testando Health Check ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro: {e}")
        return False

def test_list_datasets_empty():
    """Testa listagem de datasets vazia"""
    print("\n=== Testando Listagem de Datasets (vazia) ===")
    try:
        response = requests.get(f"{BASE_URL}/datasets")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro: {e}")
        return False

def test_upload_dataset():
    """Testa upload de um dataset"""
    print("\n=== Testando Upload de Dataset ===")
    try:
        # Arquivo CSV de teste
        files = {'file': ('test_data.csv', open('test_data.csv', 'rb'), 'text/csv')}
        response = requests.post(f"{BASE_URL}/datasets/upload", files=files)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Dataset ID: {data['id']}")
            print(f"Nome: {data['name']}")
            print(f"Linhas: {data['row_count']}")
            print(f"Schema: {data['schema']}")
            return data['id']
        else:
            print(f"Erro: {response.text}")
            return None
    except Exception as e:
        print(f"Erro: {e}")
        return None

def test_list_datasets_with_data(dataset_id):
    """Testa listagem de datasets com dados"""
    print("\n=== Testando Listagem de Datasets (com dados) ===")
    try:
        response = requests.get(f"{BASE_URL}/datasets")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Total de datasets: {len(data['datasets'])}")
        for dataset in data['datasets']:
            print(f"- {dataset['id']}: {dataset['name']} ({dataset['row_count']} linhas)")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro: {e}")
        return False

def test_preview_dataset(dataset_id):
    """Testa preview de um dataset"""
    print(f"\n=== Testando Preview do Dataset {dataset_id} ===")
    try:
        response = requests.get(f"{BASE_URL}/datasets/{dataset_id}/preview")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Nome: {data['name']}")
            print(f"Colunas: {data['columns']}")
            print(f"Total de linhas no preview: {data['total_rows']}")
            print(f"Primeira linha: {data['rows'][0] if data['rows'] else 'N/A'}")
        else:
            print(f"Erro: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro: {e}")
        return False

def test_error_handling():
    """Testa tratamento de erros"""
    print("\n=== Testando Tratamento de Erros ===")
    
    # Teste com arquivo vazio
    print("1. Testando arquivo vazio...")
    try:
        files = {'file': ('empty.csv', b'', 'text/csv')}
        response = requests.post(f"{BASE_URL}/datasets/upload", files=files)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Erro: {e}")
    
    # Teste com arquivo não-CSV
    print("2. Testando arquivo não-CSV...")
    try:
        files = {'file': ('test.txt', b'Hello World', 'text/plain')}
        response = requests.post(f"{BASE_URL}/datasets/upload", files=files)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Erro: {e}")
    
    # Teste com dataset inexistente
    print("3. Testando dataset inexistente...")
    try:
        response = requests.get(f"{BASE_URL}/datasets/invalid_id/preview")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Erro: {e}")

def main():
    """Função principal de teste"""
    print("Iniciando testes da API de Datasets...")
    
    # Aguardar servidor iniciar
    print("Aguardando servidor iniciar...")
    time.sleep(2)
    
    # Testes básicos
    if not test_health():
        print("❌ Health check falhou")
        return
    
    if not test_list_datasets_empty():
        print("❌ Listagem vazia falhou")
        return
    
    # Teste de upload
    dataset_id = test_upload_dataset()
    if not dataset_id:
        print("❌ Upload falhou")
        return
    
    # Aguardar processamento
    time.sleep(1)
    
    # Testes com dados
    if not test_list_datasets_with_data(dataset_id):
        print("❌ Listagem com dados falhou")
        return
    
    if not test_preview_dataset(dataset_id):
        print("❌ Preview falhou")
        return
    
    # Testes de erro
    test_error_handling()
    
    print("\n✅ Todos os testes básicos passaram!")
    print(f"Dataset criado com ID: {dataset_id}")

if __name__ == "__main__":
    main()

