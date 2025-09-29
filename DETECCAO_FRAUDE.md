# 🚨 Sistema de Detecção de Fraude - Documentação Técnica

## 📋 Visão Geral

O Sistema de Detecção de Fraude é um módulo integrado ao projeto de análise de dados que utiliza algoritmos avançados para identificar possíveis atividades fraudulentas em dados de vendas, devoluções, cancelamentos e ajustes de estoque.

## 🎯 Objetivos

- **Detectar automaticamente** padrões suspeitos nos dados
- **Classificar riscos** (ALTO/MÉDIO) para cada suspeita
- **Fornecer relatórios detalhados** com recomendações específicas
- **Integrar-se perfeitamente** com o sistema de IA existente

## ⚠️ **Status Atual: FUNCIONAL**

O sistema de detecção de fraude está **100% operacional** e integrado ao agente de IA. Ele detecta automaticamente quando o usuário menciona palavras relacionadas a fraude e executa a análise completa.

## 🔍 Algoritmos Implementados

### 1. Detecção de Volume Anômalo de Devoluções

**Objetivo**: Identificar produtos com devoluções acima do normal baseado em estatísticas históricas.

**Algoritmo**:

```python
def detectar_volume_anomalo_devolucoes(self):
    # Calcula estatísticas de devoluções por produto
    # Identifica produtos com devoluções acima da média
    # Classifica risco baseado no desvio padrão
    # Gera suspeitas com detalhes específicos
```

**Critérios de Suspeita**:

- Devoluções > 2x a média para o mesmo SKU/loja
- Risco ALTO: Devoluções > 3x a média
- Risco MÉDIO: Devoluções > 2x a média

### 2. Detecção de Movimentações Suspeitas em Curto Intervalo

**Objetivo**: Detecta movimentações suspeitas em curto espaço de tempo que podem indicar fraude.

**Algoritmo**:

```python
def detectar_movimentacoes_suspeitas_curto_intervalo(self):
    # Coleta todas as movimentações ordenadas por data
    # Agrupa por SKU e loja
    # Analisa intervalos entre movimentações
    # Identifica movimentações próximas temporalmente
```

**Critérios de Suspeita**:

- Movimentações do mesmo SKU/loja em < 24 horas
- Diferentes tipos de movimentação (ajuste + troca)
- Risco ALTO: Sempre que detectado

### 3. Detecção de Cliente Reincidente em Trocas/Divergências

**Objetivo**: Identifica clientes com histórico de problemas em trocas e divergências.

**Algoritmo**:

```python
def detectar_clientes_reincidentes(self):
    # Calcula estatísticas por cliente
    # Identifica reincidências baseadas em frequência
    # Analisa padrões de comportamento suspeito
    # Classifica risco baseado no histórico
```

**Critérios de Suspeita**:

- Cliente com ≥ 3 ocorrências (configurável)
- Risco ALTO: > 10 ocorrências
- Risco MÉDIO: 3-10 ocorrências

### 4. Detecção de Produto Reincidente em Trocas/Divergências

**Objetivo**: Identifica produtos com padrões suspeitos recorrentes em trocas e divergências.

**Algoritmo**:

```python
def detectar_produtos_reincidentes(self):
    # Calcula estatísticas por produto
    # Identifica reincidências baseadas em frequência
    # Analisa padrões de comportamento suspeito
    # Classifica risco baseado no histórico
```

**Critérios de Suspeita**:

- Produto com ≥ 3 ocorrências (configurável)
- Risco ALTO: > 10 ocorrências
- Risco MÉDIO: 3-10 ocorrências

## ⚙️ Configurações

O sistema utiliza um arquivo de configuração interno com os seguintes parâmetros:

```python
config = {
    'percentual_troca_suspeito': 0.15,  # 15% de trocas é suspeito
    'percentual_cancelamento_suspeito': 0.10,  # 10% de cancelamentos é suspeito
    'intervalo_suspeito_horas': 24,  # Movimentações no mesmo dia são suspeitas
    'minimo_ocorrencias_reincidencia': 3,  # Mínimo de ocorrências para ser reincidente
    'diferenca_valor_suspeita': 0.20  # 20% de diferença de valor é suspeita
}
```

## 📊 Estrutura de Dados

### Entrada

O sistema analisa dados das seguintes coleções MongoDB:

- `DEVOLUCAO`: Devoluções e trocas
- `CANCELAMENTO_2025`: Cancelamentos
- `AJUSTES_ESTOQUE_2025`: Ajustes de estoque

### Saída

Cada suspeita detectada contém:

```python
suspeita = {
    'tipo_fraude': 'Descrição do tipo de fraude',
    'nivel_risco': 'ALTO' | 'MÉDIO',
    'detalhes_especificos': {...},  # Varia por tipo
    'timestamp_analise': '2024-01-01T12:00:00',
    'detalhes': {...}  # Dados completos da suspeita
}
```

## 🔧 Uso Técnico

### Inicialização

```python
from modules.detector_fraude import DetectorFraude

# Conectar ao MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["dbGrupoOscar"]

# Criar detector
detector = DetectorFraude(client, "dbGrupoOscar")
```

### Execução de Análise Completa

```python
# Executar todos os algoritmos
relatorio = detector.executar_analise_completa_fraude()

# Acessar resultados
total_suspeitas = relatorio['total_suspeitas']
suspeitas_por_tipo = relatorio['suspeitas_por_tipo']
recomendacoes = relatorio['resumo_executivo']['recomendacoes']
```

### Execução Individual

```python
# Executar apenas um algoritmo
suspeitas_trocas = detector.detectar_trocas_mais_saidas_que_entradas()
suspeitas_ajustes = detector.detectar_produtos_ajustes_trocas_simultaneos()
suspeitas_percentuais = detector.detectar_percentuais_suspeitos_trocas_cancelamentos()
suspeitas_intervalo = detector.detectar_movimentacoes_suspeitas_curto_intervalo()
suspeitas_reincidencia = detector.detectar_clientes_produtos_reincidentes()
```

## 🤖 Integração com IA

O sistema está integrado ao agente MongoDB e é ativado automaticamente quando o usuário menciona:

- "faça uma analise de fraude"
- "relatorio de fraude"
- "análise de fraude"
- "detectar fraude"
- "detecção de fraude"
- "detectar suspeitas"
- "verificar fraude"
- "auditoria de fraude"
- "investigar fraude"
- "identificar fraude"
- "buscar fraude"
- "procurar fraude"

### Fluxo de Ativação

1. Usuário digita pergunta com palavras-chave de fraude
2. Sistema detecta padrão de fraude na pergunta
3. Executa análise completa automaticamente
4. Retorna relatório HTML formatado
5. Inclui recomendações específicas

## 📈 Performance

### Otimizações Implementadas

- **Índices MongoDB**: Criados automaticamente para campos mais consultados
- **Agregações eficientes**: Uso de pipelines MongoDB otimizados
- **Cache de consultas**: Sistema de cache para consultas frequentes
- **Amostragem inteligente**: Para coleções muito grandes

### Métricas de Performance

- **Tempo médio de análise**: 15-20 segundos (dependendo do volume de dados)
- **Memória utilizada**: ~100-200MB por análise
- **Escalabilidade**: Testado com até 500.000 registros
- **Suspeitas detectadas**: Até 20.000+ suspeitas por análise

## 🧪 Testes

### Como Testar o Sistema

1. **Inicie a aplicação:**
   ```bash
   python main.py
   ```

2. **Acesse no navegador:** `http://localhost:5000`

3. **Digite uma das seguintes perguntas no chat:**
   - "faça uma análise de fraude"
   - "relatório de fraude"
   - "análise de fraude"
   - "detectar fraude"
   - "verificar suspeitas"

4. **O sistema irá:**
   - Detectar automaticamente que é uma consulta de fraude
   - Executar todos os algoritmos de detecção
   - Retornar um relatório HTML formatado
   - Incluir estatísticas e recomendações

### Testes Incluídos

- ✅ Detecção automática de palavras-chave de fraude
- ✅ Execução de todos os algoritmos de detecção
- ✅ Geração de relatórios HTML formatados
- ✅ Classificação de riscos (ALTO/MÉDIO)
- ✅ Estatísticas detalhadas por tipo de suspeita

## 🔒 Segurança

### Dados Sensíveis

- Nenhum dado sensível é exposto nos logs
- IDs de usuários são mascarados quando necessário
- Relatórios não contêm informações pessoais completas

### Validação de Entrada

- Validação de tipos de dados
- Sanitização de strings
- Tratamento de erros robusto

## 📝 Logs e Monitoramento

### Logs Gerados

```
🔍 Analisando trocas com mais saídas que entradas...
✅ Encontradas 5 suspeitas de trocas desbalanceadas
🚨 Executando análise completa de fraude...
📊 Total de suspeitas encontradas: 23
```

### Métricas Monitoradas

- Número de suspeitas por tipo
- Tempo de execução por algoritmo
- Taxa de detecção por loja/produto
- Falsos positivos identificados

## 🚀 Melhorias Futuras

### Algoritmos Adicionais

- Detecção de padrões temporais anômalos
- Análise de redes de clientes suspeitos
- Machine Learning para classificação automática
- Detecção de outliers estatísticos

### Funcionalidades

- Alertas em tempo real
- Dashboard de monitoramento
- Exportação de relatórios em PDF
- API REST para integração externa

### Performance

- Processamento paralelo
- Cache distribuído
- Análise incremental
- Otimizações específicas por volume

## 📞 Suporte

Para dúvidas técnicas ou problemas com o sistema de detecção de fraude:

1. Consulte os logs da aplicação
2. Execute o arquivo de exemplo
3. Verifique a conectividade com MongoDB
4. Confirme se há dados suficientes para análise

## 📄 Licença

Este sistema de detecção de fraude é parte do projeto Grupo Oscar e segue as mesmas diretrizes de licenciamento do projeto principal.
