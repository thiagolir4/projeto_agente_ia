#!/usr/bin/env python3
"""
Teste dos agentes DataAgent e InsightAgent
"""

import asyncio
import sys
import os

# Adicionar o diretório app ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.agents.data_agent import get_data_agent, clear_all_memory
from app.agents.insight_agent import process_insights

async def test_data_agent():
    """Testa o DataAgent"""
    print("🧪 Testando DataAgent...")
    
    try:
        # Criar agente para sessão de teste
        session_id = "test_session_001"
        agent = get_data_agent(session_id)
        
        print(f"✅ DataAgent criado para sessão: {session_id}")
        print(f"📋 Modelo: {agent.model}")
        print(f"🛠️  Ferramentas disponíveis: {len(agent.tools)}")
        
        # Testar ferramentas
        print("\n🔧 Testando ferramentas...")
        
        # Testar get_session_info
        from app.agents.data_agent import get_session_info
        session_info = get_session_info(session_id)
        print(f"📊 Informações da sessão: {session_info}")
        
        # Testar format_table_markdown
        import pandas as pd
        from app.agents.data_agent import format_table_markdown
        
        test_df = pd.DataFrame({
            'Coluna1': ['Valor1', 'Valor2', None],
            'Coluna2': [100, 200, 300]
        })
        
        markdown_table = format_table_markdown(test_df)
        print(f"📋 Tabela Markdown gerada:\n{markdown_table}")
        
        print("✅ DataAgent testado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar DataAgent: {str(e)}")
        return False

async def test_insight_agent():
    """Testa o InsightAgent"""
    print("\n🧪 Testando InsightAgent...")
    
    try:
        # Dados de teste (simulando saída do DataAgent)
        test_context = """
| Coluna | Valor | Tipo |
|--------|-------|------|
| ID     | 1     | Int  |
| Nome   | João  | Str  |
| Idade  | 25    | Int  |
| Cidade | SP    | Str  |
        """
        
        # Processar insights
        insights = await process_insights(test_context)
        
        print(f"✅ Insights gerados com sucesso!")
        print(f"📊 Resultado:\n{insights}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar InsightAgent: {str(e)}")
        return False

async def test_integration():
    """Testa a integração entre os agentes"""
    print("\n🧪 Testando integração dos agentes...")
    
    try:
        # Simular fluxo completo
        session_id = "test_integration_001"
        
        # 1. DataAgent gera tabela
        print("1️⃣ DataAgent gerando tabela...")
        data_agent = get_data_agent(session_id)
        
        # Simular resposta do DataAgent
        mock_data_response = """
| Produto | Preço | Estoque |
|---------|-------|---------|
| A       | 10.50| 100     |
| B       | 25.00| 50      |
| C       | 15.75| 75      |
        """
        
        print(f"📊 Tabela gerada:\n{mock_data_response}")
        
        # 2. InsightAgent processa a tabela
        print("2️⃣ InsightAgent processando tabela...")
        insights = await process_insights(mock_data_response)
        
        print(f"💡 Insights gerados:\n{insights}")
        
        print("✅ Integração testada com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar integração: {str(e)}")
        return False

async def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes dos agentes...\n")
    
    # Limpar memória antes dos testes
    clear_all_memory()
    
    # Executar testes
    tests = [
        test_data_agent(),
        test_insight_agent(),
        test_integration()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    # Verificar resultados
    print("\n📊 Resultados dos testes:")
    print("=" * 50)
    
    test_names = ["DataAgent", "InsightAgent", "Integração"]
    passed = 0
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"❌ {test_names[i]}: FALHOU - {str(result)}")
        elif result:
            print(f"✅ {test_names[i]}: PASSOU")
            passed += 1
        else:
            print(f"❌ {test_names[i]}: FALHOU")
    
    print("=" * 50)
    print(f"🎯 Total: {passed}/{len(tests)} testes passaram")
    
    if passed == len(tests):
        print("🎉 Todos os testes passaram!")
        return 0
    else:
        print("⚠️  Alguns testes falharam!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

