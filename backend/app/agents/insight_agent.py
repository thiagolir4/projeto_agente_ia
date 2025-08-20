from agno.agent import Agent
from agno.tools import Function
from typing import Dict, Any, List
import re

def extract_key_metrics(context: str) -> Dict[str, Any]:
    """
    Extrai métricas-chave do contexto fornecido pelo DataAgent
    
    Args:
        context: Saída do DataAgent (tabelas Markdown)
        
    Returns:
        Dicionário com métricas extraídas
    """
    metrics = {
        'total_records': 0,
        'columns': [],
        'data_types': {},
        'missing_values': {},
        'unique_values': {},
        'numeric_columns': [],
        'categorical_columns': []
    }
    
    # Extrair informações das tabelas Markdown
    lines = context.split('\n')
    in_table = False
    headers = []
    
    for line in lines:
        line = line.strip()
        
        # Detectar início de tabela
        if line.startswith('|') and '---' not in line and len(line) > 1:
            if not in_table:
                in_table = True
                headers = [h.strip() for h in line.split('|')[1:-1]]
                metrics['columns'] = headers
            else:
                # Contar linhas de dados
                if not line.startswith('| ---'):
                    metrics['total_records'] += 1
                    
                    # Analisar valores
                    values = [v.strip() for v in line.split('|')[1:-1]]
                    for i, (header, value) in enumerate(zip(headers, values)):
                        if header not in metrics['data_types']:
                            metrics['data_types'][header] = []
                        
                        # Detectar tipo de dado
                        if value == 'N/D':
                            if header not in metrics['missing_values']:
                                metrics['missing_values'][header] = 0
                            metrics['missing_values'][header] += 1
                        else:
                            # Tentar converter para número
                            try:
                                float(value.replace(',', '').replace('%', ''))
                                if header not in metrics['numeric_columns']:
                                    metrics['numeric_columns'].append(header)
                            except:
                                if header not in metrics['categorical_columns']:
                                    metrics['categorical_columns'].append(header)
        
        # Detectar fim de tabela
        elif not line.startswith('|') and in_table:
            in_table = False
    
    return metrics

def generate_executive_summary(metrics: Dict[str, Any]) -> str:
    """
    Gera resumo executivo baseado nas métricas extraídas
    
    Args:
        metrics: Métricas extraídas do contexto
        
    Returns:
        Resumo executivo em formato de bullet points
    """
    summary = []
    
    # Informações gerais
    summary.append(f"• **Volume de dados**: {metrics['total_records']} registros")
    summary.append(f"• **Estrutura**: {len(metrics['columns'])} colunas")
    
    # Análise de tipos de dados
    if metrics['numeric_columns']:
        summary.append(f"• **Colunas numéricas**: {', '.join(metrics['numeric_columns'])}")
    
    if metrics['categorical_columns']:
        summary.append(f"• **Colunas categóricas**: {', '.join(metrics['categorical_columns'])}")
    
    # Qualidade dos dados
    total_missing = sum(metrics['missing_values'].values())
    if total_missing > 0:
        missing_percentage = (total_missing / (metrics['total_records'] * len(metrics['columns']))) * 100
        summary.append(f"• **Qualidade**: {missing_percentage:.1f}% de valores ausentes")
    
    return summary

def generate_recommendations(metrics: Dict[str, Any], context: str) -> List[str]:
    """
    Gera recomendações baseadas nas métricas e contexto
    
    Args:
        metrics: Métricas extraídas
        context: Contexto completo do DataAgent
        
    Returns:
        Lista de recomendações
    """
    recommendations = []
    
    # Recomendações baseadas no volume de dados
    if metrics['total_records'] < 100:
        recommendations.append("• **Amostra pequena**: Considere coletar mais dados para análises robustas")
    elif metrics['total_records'] > 10000:
        recommendations.append("• **Volume alto**: Dados suficientes para análises estatísticas avançadas")
    
    # Recomendações baseadas na qualidade
    total_missing = sum(metrics['missing_values'].values())
    if total_missing > 0:
        missing_percentage = (total_missing / (metrics['total_records'] * len(metrics['columns']))) * 100
        if missing_percentage > 20:
            recommendations.append("• **Qualidade crítica**: Implementar estratégias de limpeza de dados")
        elif missing_percentage > 5:
            recommendations.append("• **Qualidade moderada**: Considerar técnicas de imputação para valores ausentes")
    
    # Recomendações baseadas nos tipos de dados
    if len(metrics['numeric_columns']) >= 2:
        recommendations.append("• **Análise multivariada**: Dados numéricos permitem análises de correlação")
    
    if len(metrics['categorical_columns']) >= 2:
        recommendations.append("• **Segmentação**: Dados categóricos permitem análises por grupos")
    
    # Recomendações específicas baseadas no contexto
    if 'financeiro' in context.lower() or 'valor' in context.lower():
        recommendations.append("• **Análise temporal**: Considerar tendências e sazonalidade nos dados financeiros")
    
    if 'cliente' in context.lower() or 'usuário' in context.lower():
        recommendations.append("• **Comportamento**: Analisar padrões de comportamento dos clientes")
    
    return recommendations

def analyze_data_patterns(context: str) -> str:
    """
    Analisa padrões nos dados fornecidos
    
    Args:
        context: Contexto do DataAgent
        
    Returns:
        Análise de padrões em formato de bullet points
    """
    patterns = []
    
    # Detectar padrões nas tabelas
    lines = context.split('\n')
    in_table = False
    table_data = []
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('|') and '---' not in line and len(line) > 1:
            if not in_table:
                in_table = True
                table_data = []
            else:
                if not line.startswith('| ---'):
                    values = [v.strip() for v in line.split('|')[1:-1]]
                    table_data.append(values)
        
        elif not line.startswith('|') and in_table:
            in_table = False
            
            # Analisar padrões na tabela
            if table_data:
                # Verificar se há valores repetidos
                for col_idx in range(len(table_data[0])):
                    col_values = [row[col_idx] for row in table_data if col_idx < len(row)]
                    unique_values = set(col_values)
                    
                    if len(unique_values) == 1 and len(col_values) > 1:
                        patterns.append(f"• **Coluna {col_idx + 1}**: Valor constante ({list(unique_values)[0]})")
                    elif len(unique_values) < len(col_values) * 0.5:
                        patterns.append(f"• **Coluna {col_idx + 1}**: Baixa variabilidade ({len(unique_values)} valores únicos)")
    
    if not patterns:
        patterns.append("• **Variabilidade**: Dados apresentam boa distribuição de valores")
    
    return patterns

# Criar InsightAgent
insight_agent = Agent(
    name="InsightAgent",
    model="gpt-4o",
    instructions="""Você é um agente especializado em gerar insights executivos a partir de dados. Suas responsabilidades são:

1. **Analisar a saída do DataAgent** (tabelas Markdown)
2. **Gerar resumo executivo** em bullet points claros e objetivos
3. **Fornecer recomendações** baseadas nos dados, SEM opiniões não fundamentadas
4. **Identificar padrões** nos dados quando relevante

**Regras importantes:**
- Seja objetivo e técnico
- Base todas as afirmações nos dados fornecidos
- Use bullet points para clareza
- Se não houver dados suficientes, indique claramente
- NUNCA invente informações ou faça suposições não fundamentadas

**Formato de resposta:**
```
## Resumo Executivo
[bullet points baseados nos dados]

## Recomendações
[recomendações objetivas e fundamentadas]

## Padrões Identificados
[padrões observados nos dados, se houver]
```""",
            tools=[
            Function(
                name="extract_key_metrics",
                function=extract_key_metrics,
                description="Extrai métricas-chave do contexto fornecido pelo DataAgent"
            ),
            Function(
                name="generate_executive_summary",
                function=generate_executive_summary,
                description="Gera resumo executivo baseado nas métricas extraídas"
            ),
            Function(
                name="generate_recommendations",
                function=generate_recommendations,
                description="Gera recomendações baseadas nas métricas e contexto"
            ),
            Function(
                name="analyze_data_patterns",
                function=analyze_data_patterns,
                description="Analisa padrões nos dados fornecidos"
            )
        ]
)

async def process_insights(context: str) -> str:
    """
    Processa o contexto do DataAgent e gera insights
    
    Args:
        context: Saída do DataAgent
        
    Returns:
        Insights formatados
    """
    try:
        # Extrair métricas
        metrics = extract_key_metrics(context)
        
        # Gerar resumo executivo
        summary = generate_executive_summary(metrics)
        
        # Gerar recomendações
        recommendations = generate_recommendations(metrics, context)
        
        # Analisar padrões
        patterns = analyze_data_patterns(context)
        
        # Formatar resposta
        response = "## Resumo Executivo\n"
        response += "\n".join(summary) + "\n\n"
        
        response += "## Recomendações\n"
        response += "\n".join(recommendations) + "\n\n"
        
        response += "## Padrões Identificados\n"
        response += "\n".join(patterns)
        
        return response
        
    except Exception as e:
        return f"**Erro ao processar insights: {str(e)}**"
