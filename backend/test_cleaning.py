import requests
import json
import time

BASE_URL = "http://127.0.0.1:8001"

def test_cleaning_pipeline():
    """Testa o pipeline completo de limpeza"""
    print("=== Testando Pipeline de Limpeza ===")
    
    try:
        # 1. Primeiro, verificar se há datasets disponíveis
        print("1. Verificando datasets disponíveis...")
        response = requests.get(f"{BASE_URL}/datasets")
        
        if response.status_code != 200:
            print(f"❌ Erro ao listar datasets: {response.status_code}")
            return False
        
        datasets = response.json()["datasets"]
        
        if not datasets:
            print("❌ Nenhum dataset disponível para teste")
            print("   Primeiro faça upload de um CSV via /datasets/upload")
            return False
        
        # Usar o primeiro dataset disponível
        dataset = datasets[0]
        dataset_id = dataset["id"]
        dataset_name = dataset["name"]
        
        print(f"✅ Dataset encontrado: {dataset_id} ({dataset_name})")
        print(f"   Linhas: {dataset['row_count']}")
        print(f"   Colunas: {len(dataset['schema'])}")
        
        # 2. Executar pipeline de limpeza
        print(f"\n2. Executando pipeline de limpeza em {dataset_id}...")
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/cleaning/run/{dataset_id}")
        end_time = time.time()
        
        if response.status_code != 200:
            print(f"❌ Erro na limpeza: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        result = response.json()
        cleaning_time = end_time - start_time
        
        print(f"✅ Limpeza concluída em {cleaning_time:.2f}s")
        
        # 3. Analisar resultados
        data = result["data"]
        metrics = data["metrics"]
        
        print(f"\n3. Resultados da Limpeza:")
        print(f"   Tabela limpa: {data['clean_table']}")
        print(f"   Linhas antes: {metrics['rows_before']}")
        print(f"   Linhas depois: {metrics['rows_after']}")
        print(f"   Linhas removidas: {metrics['rows_removed']}")
        print(f"   % mantidas: {metrics['rows_kept_percentage']:.1f}%")
        print(f"   Colunas antes: {metrics['columns_before']}")
        print(f"   Colunas depois: {metrics['columns_after']}")
        
        # 4. Verificar preview dos dados limpos
        preview = data["preview"]
        print(f"\n4. Preview dos Dados Limpos:")
        print(f"   Total de linhas no preview: {preview['total_rows']}")
        
        if preview['data']:
            print(f"   Primeira linha:")
            first_row = preview['data'][0]
            for key, value in first_row.items():
                print(f"     {key}: {value}")
        
        # 5. Verificar tabela limpa no DuckDB
        print(f"\n5. Verificando tabela limpa no banco...")
        
        # Listar datasets novamente para ver se a tabela limpa foi criada
        response = requests.get(f"{BASE_URL}/datasets")
        if response.status_code == 200:
            all_datasets = response.json()["datasets"]
            clean_datasets = [d for d in all_datasets if d["id"].endswith("_clean")]
            
            if clean_datasets:
                print(f"✅ Tabelas limpas encontradas: {len(clean_datasets)}")
                for clean_ds in clean_datasets:
                    print(f"   - {clean_ds['id']}: {clean_ds['name']} ({clean_ds['row_count']} linhas)")
            else:
                print("⚠️  Nenhuma tabela limpa encontrada na listagem")
        
        print(f"\n✅ Pipeline de limpeza testado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante teste: {str(e)}")
        return False

def test_error_handling():
    """Testa tratamento de erros do pipeline"""
    print("\n=== Testando Tratamento de Erros ===")
    
    # Teste com dataset inexistente
    print("1. Testando dataset inexistente...")
    try:
        response = requests.post(f"{BASE_URL}/cleaning/run/invalid_id")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Erro: {e}")

def main():
    """Função principal de teste"""
    print("Iniciando testes do Pipeline de Limpeza...")
    
    # Aguardar servidor iniciar
    print("Aguardando servidor iniciar...")
    time.sleep(2)
    
    # Teste principal
    if not test_cleaning_pipeline():
        print("❌ Teste principal falhou")
        return
    
    # Testes de erro
    test_error_handling()
    
    print("\n🎉 Todos os testes do pipeline de limpeza passaram!")

if __name__ == "__main__":
    main()

