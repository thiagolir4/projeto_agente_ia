import pandas as pd
import requests
import json
import io
import tempfile
import os

BASE_URL = "http://127.0.0.1:8001"

def create_sample_datasets():
    """Cria datasets de exemplo para testar as regras de cruzamento"""
    print("=== Criando Datasets de Exemplo ===")
    
    # 1. Dataset de Estoque
    print("1. Criando dataset de estoque...")
    estoque_data = {
        'sku': ['SKU001', 'SKU002', 'SKU003', 'SKU004', 'SKU005'],
        'data': ['2024-01-01', '2024-01-01', '2024-01-01', '2024-01-01', '2024-01-01'],
        'estoque_disponivel': [100, 50, 200, 75, 150]
    }
    
    estoque_df = pd.DataFrame(estoque_data)
    
    # Salvar como CSV temporário
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        estoque_df.to_csv(f.name, index=False)
        temp_file = f.name
    
    # Upload do dataset de estoque
    with open(temp_file, 'rb') as f:
        files = {'file': ('estoque_sample.csv', f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/datasets/upload", files=files)
    
    os.unlink(temp_file)  # Remover arquivo temporário
    
    if response.status_code != 200:
        print(f"❌ Erro ao criar dataset de estoque: {response.status_code}")
        return None
    
    estoque_result = response.json()
    estoque_id = estoque_result['id']
    print(f"✅ Dataset de estoque criado: {estoque_id}")
    
    # 2. Dataset de Vendas
    print("2. Criando dataset de vendas...")
    vendas_data = {
        'sku': ['SKU001', 'SKU002', 'SKU003', 'SKU004', 'SKU005'],
        'data': ['2024-01-01', '2024-01-01', '2024-01-01', '2024-01-01', '2024-01-01'],
        'vendas': [120, 45, 180, 80, 160],
        'preco_vendido': [25.50, 15.75, 45.00, 30.25, 55.80]
    }
    
    vendas_df = pd.DataFrame(vendas_data)
    
    # Salvar como CSV temporário
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        vendas_df.to_csv(f.name, index=False)
        temp_file = f.name
    
    # Upload do dataset de vendas
    with open(temp_file, 'rb') as f:
        files = {'file': ('vendas_sample.csv', f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/datasets/upload", files=files)
    
    os.unlink(temp_file)  # Remover arquivo temporário
    
    if response.status_code != 200:
        print(f"❌ Erro ao criar dataset de vendas: {response.status_code}")
        return None
    
    vendas_result = response.json()
    vendas_id = vendas_result['id']
    print(f"✅ Dataset de vendas criado: {vendas_id}")
    
    # 3. Dataset de Preços
    print("3. Criando dataset de preços...")
    precos_data = {
        'sku': ['SKU001', 'SKU002', 'SKU003', 'SKU004', 'SKU005'],
        'data': ['2024-01-01', '2024-01-01', '2024-01-01', '2024-01-01', '2024-01-01'],
        'preco_tabela': [25.00, 15.50, 45.00, 30.00, 55.00]
    }
    
    precos_df = pd.DataFrame(precos_data)
    
    # Salvar como CSV temporário
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        precos_df.to_csv(f.name, index=False)
        temp_file = f.name
    
    # Upload do dataset de preços
    with open(temp_file, 'rb') as f:
        files = {'file': ('precos_sample.csv', f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/datasets/upload", files=files)
    
    os.unlink(temp_file)  # Remover arquivo temporário
    
    if response.status_code != 200:
        print(f"❌ Erro ao criar dataset de preços: {response.status_code}")
        return None
    
    precos_result = response.json()
    precos_id = precos_result['id']
    print(f"✅ Dataset de preços criado: {precos_id}")
    
    return {
        'estoque_id': estoque_id,
        'vendas_id': vendas_id,
        'precos_id': precos_id
    }

def clean_datasets(dataset_ids):
    """Executa limpeza nos datasets criados"""
    print("\n=== Executando Limpeza dos Datasets ===")
    
    for name, dataset_id in dataset_ids.items():
        print(f"Limpando {name}: {dataset_id}")
        
        response = requests.post(f"{BASE_URL}/cleaning/run/{dataset_id}")
        
        if response.status_code == 200:
            print(f"✅ {name} limpo com sucesso")
        else:
            print(f"❌ Erro ao limpar {name}: {response.status_code}")

def test_analysis(dataset_ids):
    """Testa o endpoint de análise"""
    print("\n=== Testando Endpoint de Análise ===")
    
    # Teste com todos os datasets
    analysis_request = {
        "datasets": dataset_ids
    }
    
    print(f"Enviando requisição: {json.dumps(analysis_request, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/analysis/run", json=analysis_request)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Análise executada com sucesso!")
        
        # Mostrar resumo
        summary = result['data']['summary']
        print(f"\n📊 Resumo da Análise:")
        print(f"   Total de registros: {summary['total_registros']}")
        print(f"   Contagem por regra: {summary['contagem_por_regra']}")
        
        # Mostrar top scores
        if summary['top_10_scores']:
            print(f"\n🏆 Top Scores:")
            for i, score in enumerate(summary['top_10_scores'][:5], 1):
                print(f"   {i}. {score['regra']} - SKU: {score['sku']} - Score: {score['score']:.2f}")
        
        # Mostrar alguns resultados
        results = result['data']['results']
        if results:
            print(f"\n📋 Primeiros Resultados:")
            for i, result in enumerate(results[:3], 1):
                print(f"   {i}. Regra: {result['regra']}, SKU: {result['sku']}, Score: {result['score']:.2f}, Flag: {result['flag']}")
        
        return True
    else:
        print(f"❌ Erro na análise: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def main():
    """Função principal"""
    print("Iniciando criação e teste dos datasets de exemplo...")
    
    try:
        # 1. Criar datasets
        dataset_ids = create_sample_datasets()
        if not dataset_ids:
            print("❌ Falha ao criar datasets")
            return
        
        print(f"\n📁 Datasets criados:")
        for name, dataset_id in dataset_ids.items():
            print(f"   {name}: {dataset_id}")
        
        # 2. Limpar datasets
        clean_datasets(dataset_ids)
        
        # 3. Testar análise
        success = test_analysis(dataset_ids)
        
        if success:
            print("\n🎉 Todos os testes passaram com sucesso!")
            print(f"\n📋 Para testar manualmente:")
            print(f"   POST {BASE_URL}/analysis/run")
            print(f"   Body: {json.dumps({'datasets': dataset_ids}, indent=2)}")
        else:
            print("\n❌ Teste de análise falhou")
            
    except Exception as e:
        print(f"❌ Erro durante execução: {str(e)}")

if __name__ == "__main__":
    main()
