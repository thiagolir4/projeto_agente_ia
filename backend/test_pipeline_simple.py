import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.pipeline.limpeza import clean_dataset
import pandas as pd

def test_pipeline_directly():
    """Testa o pipeline diretamente sem servidor"""
    print("=== Testando Pipeline de Limpeza Diretamente ===")
    
    try:
        # Testar com um dataset existente
        dataset_id = "ds_d3e7e5e5"  # Usar o dataset que já existe
        
        print(f"Executando limpeza no dataset: {dataset_id}")
        
        # Executar pipeline
        result = clean_dataset(dataset_id)
        
        print("✅ Pipeline executado com sucesso!")
        print(f"Tabela limpa: {result['clean_table']}")
        print(f"Linhas antes: {result['metrics']['rows_before']}")
        print(f"Linhas depois: {result['metrics']['rows_after']}")
        print(f"Colunas antes: {result['metrics']['columns_before']}")
        print(f"Colunas depois: {result['metrics']['columns_after']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_pipeline_directly()

