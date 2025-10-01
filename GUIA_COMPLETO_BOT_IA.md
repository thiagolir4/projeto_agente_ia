# 🤖 Guia Completo do Bot de IA - Sistema de Análise Inteligente de Dados

## 📋 Índice

1. [Visão Geral](#-visão-geral)
2. [Tipos de Consultas Suportadas](#-tipos-de-consultas-suportadas)
3. [Parâmetros e Configurações](#-parâmetros-e-configurações)
4. [Sistema de Detecção de Fraude](#-sistema-de-detecção-de-fraude)
5. [Exemplos Práticos](#-exemplos-práticos)
6. [Troubleshooting](#-troubleshooting)

---

## 🎯 Visão Geral

O Bot de IA é um assistente conversacional especializado em análise de dados empresariais. Ele permite consultas em linguagem natural sobre dados de devoluções, cancelamentos, ajustes de estoque e vendas, além de detectar automaticamente padrões fraudulentos.

### ✨ Principais Características

- **Linguagem Natural**: Compreende perguntas em português brasileiro
- **Análise Inteligente**: Detecta automaticamente o tipo de consulta
- **Detecção de Fraude**: Algoritmos avançados para identificar suspeitas
- **Performance Otimizada**: Respostas em tempo real (< 2 segundos)
- **Interface Amigável**: Respostas formatadas em HTML com tabelas e gráficos

---

## 🔍 Tipos de Consultas Suportadas

### 1. **Rankings e Top Lists**

O bot pode gerar rankings de qualquer entidade nos dados:

#### **Sintaxe:**
```
"top [NÚMERO] [ENTIDADE] mais [CRITÉRIO] em [COLEÇÃO]"
```

#### **Exemplos:**
- `"top 10 lojas mais frequentes em devolução"`
- `"top 5 produtos mais devolvidos"`
- `"top 20 usuários que mais cancelam"`
- `"top 15 lojas com mais ajustes de estoque"`
- `"top 50 produtos mais vendidos"`

#### **Parâmetros Suportados:**
- **Quantidade**: 1, 3, 5, 10, 15, 20, 25, 50, 100
- **Entidades**: lojas, produtos, usuários, clientes, vendedores, datas
- **Critérios**: frequentes, devolvidos, cancelam, vendidos, compram
- **Coleções**: devolução, cancelamento, ajuste, venda

### 2. **Consultas Temporais**

Análise de dados por data específica ou período:

#### **Data Específica:**
```
"quantas [AÇÃO] no dia [DATA]"
```

**Exemplos:**
- `"quantas devoluções no dia 15/01/2025"`
- `"quantos cancelamentos no dia 16/01/2025"`
- `"quantos ajustes de estoque no dia 13/01/2025"`

#### **Período de Datas:**
```
"quantos [AÇÃO] entre [DATA_INICIO] e [DATA_FIM]"
```

**Exemplos:**
- `"quantas devoluções entre 01/01/2025 e 31/01/2025"`
- `"quantos cancelamentos entre 10/01/2025 e 20/01/2025"`

#### **Formatos de Data Suportados:**
- `DD/MM/AAAA` (ex: 15/01/2025)
- `DD/MM/AA` (ex: 15/01/25)
- `DD/MM` (ex: 15/01) - assume ano atual

### 3. **Contagens e Estatísticas**

Consultas sobre volumes e totais:

#### **Exemplos:**
- `"quantos registros existem na coleção de devolução"`
- `"total de registros de cancelamento"`
- `"quantas linhas tem a tabela de vendas"`
- `"contar todos os dados de ajuste"`

### 4. **Listagem de Dados**

Visualização de informações disponíveis:

#### **Exemplos:**
- `"quais dados estão disponíveis"`
- `"mostre as coleções existentes"`
- `"que informações posso consultar"`
- `"listar todas as tabelas"`

### 5. **Detecção de Inconsistências**

Análise de integridade dos dados:

#### **Exemplos:**
- `"verificar inconsistências nos dados"`
- `"existe algum problema nos dados"`
- `"analisar dados inconsistentes"`

---

## ⚙️ Parâmetros e Configurações

### **Parâmetros de Quantidade**

O bot detecta automaticamente a quantidade solicitada:

| Palavra-Chave | Número | Exemplo |
|---------------|--------|---------|
| `primeiro`, `top 1` | 1 | "primeiro produto mais vendido" |
| `top 3`, `três` | 3 | "top 3 lojas" |
| `top 5`, `cinco` | 5 | "top 5 produtos" |
| `top 10`, `dez` | 10 | "top 10 usuários" |
| `top 15`, `quinze` | 15 | "top 15 lojas" |
| `top 20`, `vinte` | 20 | "top 20 produtos" |
| `top 50`, `cinquenta` | 50 | "top 50 clientes" |
| `top 100`, `cem` | 100 | "top 100 vendas" |

### **Parâmetros de Formato**

#### **Tabela:**
- `"em formato de tabela"`
- `"como tabela"`
- `"em tabela"`

**Exemplo:**
```
"top 10 lojas mais frequentes em devolução em formato de tabela"
```

#### **Lista (padrão):**
- Formato padrão em lista numerada
- HTML formatado com cores e ícones

### **Parâmetros de Coleção**

O bot detecta automaticamente a coleção baseada em palavras-chave:

| Palavra-Chave | Coleção | Campo de Data |
|---------------|---------|---------------|
| `devolução`, `devoluções` | DEVOLUCAO | DATA_DEVOLUCAO |
| `cancelamento`, `cancelamentos` | CANCELAMENTO_2025 | DATACANCELAMENTO |
| `ajuste`, `ajustes`, `estoque` | AJUSTES_ESTOQUE_2025 | DATA |
| `venda`, `vendas` | VENDAS | DATA_VENDA |

---

## 🚨 Sistema de Detecção de Fraude

### **Como Ativar**

Digite qualquer uma dessas frases:
- `"faça uma análise de fraude"`
- `"relatório de fraude"`
- `"detectar fraude"`
- `"análise de fraude"`
- `"verificar suspeitas"`
- `"auditoria de fraude"`
- `"investigar fraude"`

### **Algoritmos Implementados**

#### 1. **Detecção de Volume Anômalo de Devoluções**

**O que detecta:** Produtos com devoluções acima do normal

**Critérios:**
- Risco ALTO: Devoluções > 3x a média histórica
- Risco MÉDIO: Devoluções > 2x a média histórica

**Exemplo de suspeita:**
```
Produto ABC123: 150 devoluções (média histórica: 30)
Nível de Risco: ALTO
```

#### 2. **Detecção de Movimentações Suspeitas**

**O que detecta:** Movimentações do mesmo produto/loja em curto intervalo

**Critérios:**
- Movimentações do mesmo SKU/loja em < 24 horas
- Diferentes tipos de movimentação simultâneas
- Classificação: ALTO risco

**Exemplo de suspeita:**
```
SKU XYZ789 - Loja 001:
- 14:30 - Ajuste de estoque: +50 unidades
- 15:45 - Devolução: -50 unidades
Nível de Risco: ALTO
```

#### 3. **Detecção de Clientes Reincidentes**

**O que detecta:** Clientes com histórico de problemas

**Critérios:**
- Risco ALTO: > 10 ocorrências de problemas
- Risco MÉDIO: 3-10 ocorrências
- Threshold mínimo: 3 ocorrências

**Exemplo de suspeita:**
```
Cliente 12345:
- 15 devoluções nos últimos 30 dias
- 8 cancelamentos
- 12 ajustes de estoque
Nível de Risco: ALTO
```

#### 4. **Detecção de Produtos Reincidentes**

**O que detecta:** Produtos com padrões suspeitos recorrentes

**Critérios:**
- Risco ALTO: > 10 ocorrências de problemas
- Risco MÉDIO: 3-10 ocorrências
- Threshold mínimo: 3 ocorrências

**Exemplo de suspeita:**
```
Produto DEF456:
- Aparece em 25 devoluções
- 18 cancelamentos relacionados
- 12 ajustes de estoque
Nível de Risco: ALTO
```

### **Relatório de Fraude**

O sistema gera um relatório completo contendo:

#### **Resumo Executivo:**
- Total de suspeitas encontradas
- Distribuição por nível de risco (ALTO/MÉDIO)
- Percentual de alto risco
- Tempo de análise

#### **Tipos de Fraude Detectados:**
- Lista de todos os tipos encontrados
- Quantidade de suspeitas por tipo

#### **Detalhes das Suspeitas:**
- Top 20 suspeitas mais críticas
- Tipo de fraude
- Nível de risco
- Detalhes específicos (SKU, loja, cliente, etc.)

#### **Exportação:**
- Botão para download em Excel
- Dataset completo com todas as suspeitas
- Formatação profissional

### **Configurações do Sistema**

```python
config = {
    'percentual_troca_suspeito': 0.15,        # 15% de trocas é suspeito
    'percentual_cancelamento_suspeito': 0.10, # 10% de cancelamentos é suspeito
    'intervalo_suspeito_horas': 24,           # Movimentações no mesmo dia
    'minimo_ocorrencias_reincidencia': 3,     # Mínimo para reincidência
    'diferenca_valor_suspeita': 0.20          # 20% de diferença é suspeita
}
```

---

## 💡 Exemplos Práticos

### **Exemplo 1: Ranking de Lojas**

**Pergunta:**
```
"top 10 lojas mais frequentes em devolução em formato de tabela"
```

**Resposta:**
- Tabela HTML formatada
- Colunas: Posição, Loja, Quantidade de Registros
- Cores e formatação profissional
- Tempo: < 1 segundo

### **Exemplo 2: Análise Temporal**

**Pergunta:**
```
"quantas devoluções entre 01/01/2025 e 31/01/2025"
```

**Resposta:**
```
No período de 01/01/2025 a 31/01/2025, foram encontrados 1.247 registros de devoluções na coleção DEVOLUCAO.
```

### **Exemplo 3: Detecção de Fraude**

**Pergunta:**
```
"faça uma análise de fraude"
```

**Resposta:**
- Relatório HTML completo
- Resumo executivo com KPIs
- Lista de suspeitas por tipo
- Tabela detalhada das top 20 suspeitas
- Botão de download Excel
- Tempo: 15-20 segundos

### **Exemplo 4: Consulta de Dados Disponíveis**

**Pergunta:**
```
"quais dados estão disponíveis"
```

**Resposta:**
- Lista de todas as coleções
- Quantidade de registros por coleção
- Status de cada coleção
- Dicas de como consultar

---

## 🔧 Troubleshooting

### **Problemas Comuns**

#### **1. "Não foi possível entender sua solicitação"**

**Causa:** Pergunta muito genérica ou fora do escopo

**Solução:**
- Seja mais específico: "top 10 lojas em devolução"
- Use palavras-chave conhecidas: lojas, produtos, usuários, devolução, cancelamento
- Verifique a ortografia

#### **2. "Coleção não encontrada"**

**Causa:** Palavra-chave não reconhecida

**Solução:**
- Use sinônimos: "devolução" em vez de "retorno"
- Verifique se a coleção existe: "quais dados estão disponíveis"
- Use termos específicos: "devolução", "cancelamento", "ajuste", "venda"

#### **3. "Erro ao processar pergunta"**

**Causa:** Problema técnico interno

**Solução:**
- Tente novamente em alguns segundos
- Reformule a pergunta
- Verifique se o MongoDB está rodando
- Verifique se a chave da OpenAI está configurada

#### **4. Análise de fraude demorada**

**Causa:** Grande volume de dados

**Solução:**
- Aguarde o processamento (pode levar até 60 segundos)
- O sistema processa até 500.000 registros
- Use filtros temporais se necessário

### **Dicas de Uso**

#### **Para Melhores Resultados:**

1. **Seja específico:**
   - ❌ "mostre dados"
   - ✅ "top 10 produtos mais vendidos"

2. **Use palavras-chave corretas:**
   - ✅ "devolução", "cancelamento", "ajuste", "venda"
   - ✅ "lojas", "produtos", "usuários", "clientes"

3. **Especifique formato quando necessário:**
   - ✅ "em formato de tabela"
   - ✅ "como lista"

4. **Para análises temporais:**
   - ✅ Use formato DD/MM/AAAA
   - ✅ Seja claro com períodos: "entre X e Y"

#### **Comandos Úteis:**

- `"quais dados estão disponíveis"` - Lista coleções
- `"quantos registros existem"` - Contagem total
- `"faça uma análise de fraude"` - Relatório completo
- `"verificar inconsistências"` - Análise de integridade

---

## 📊 Performance e Limitações

### **Métricas de Performance**

| Tipo de Consulta | Tempo Médio | Volume Suportado |
|------------------|-------------|------------------|
| Rankings simples | < 1 segundo | 500.000+ registros |
| Consultas temporais | < 2 segundos | 500.000+ registros |
| Análise de fraude | 15-20 segundos | 500.000+ registros |
| Importação de dados | 10.000 reg/s | Ilimitado |

### **Limitações Conhecidas**

- **Volume máximo testado:** 500.000 registros
- **Timeout de análise:** 60 segundos
- **Cache limitado:** 50 consultas recentes
- **Dependência:** Requer conexão com OpenAI API

### **Otimizações Implementadas**

- Índices MongoDB em campos críticos
- Sistema de cache LRU
- Amostragem inteligente para coleções grandes
- Pipeline de agregação otimizado

---

## 🚀 Próximas Funcionalidades

### **Em Desenvolvimento:**
- Análise de correlação entre variáveis
- Análise temporal avançada (sazonalidade)
- Machine Learning para classificação preditiva
- Dashboard visual com gráficos

### **Sugestões:**
- Análise de impacto financeiro
- Alertas em tempo real
- API REST para integração externa
- Relatórios em PDF

---

## 📞 Suporte

Para dúvidas ou problemas:

1. **Verifique os logs** da aplicação
2. **Consulte este guia** para exemplos
3. **Teste com perguntas simples** primeiro
4. **Verifique a conectividade** com MongoDB e OpenAI

---

*Documentação atualizada em: Janeiro 2025*
*Versão do Sistema: 1.0.0*

