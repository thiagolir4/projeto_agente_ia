# 📚 Documentação Técnica - Sistema de Análise Inteligente de Dados

## 🎯 Visão Geral do Projeto

Este sistema foi desenvolvido para democratizar a análise de dados, permitindo que pessoas sem conhecimento técnico avançado possam extrair insights valiosos de seus dados através de uma interface conversacional com IA.

### Objetivos Principais:

- **Simplificar análise de dados** para usuários não técnicos
- **Automatizar processamento** de arquivos CSV
- **Fornecer interface conversacional** para consultas em linguagem natural
- **Garantir escalabilidade** e performance com grandes volumes de dados

---

## 🏗️ Arquitetura do Sistema

### Estrutura Geral:

```
Frontend (Interface Web) ↔ Backend  ↔ IA (OpenAI) ↔ Banco (MongoDB)
```

### Componentes Principais:

1. **Interface Web** - Flask com templates HTML
2. **Processador de Dados** - Pandas para manipulação de CSV
3. **Agente IA** - LangChain + OpenAI para análise conversacional
4. **Banco de Dados** - MongoDB para armazenamento
5. **Sistema de Histórico** - Persistência de conversas

---

## 📁 Estrutura Detalhada dos Arquivos

### `main.py` - Aplicação Principal

**Responsabilidade**: Orquestrar toda a aplicação e gerenciar rotas web.

#### Funções Principais:

**`get_mongodb_agent()`**

- **O que faz**: Inicializa o agente IA quando necessário (lazy loading)
- **Por que assim**: Economiza recursos - só cria o agente quando há uma consulta
- **Como funciona**: Verifica se já existe, se não, cria nova instância e conecta ao MongoDB

**`inicializar_historico()`**

- **O que faz**: Carrega o histórico de conversas anteriores
- **Por que assim**: Mantém continuidade das conversas entre sessões
- **Como funciona**: Conecta ao MongoDB, busca última sessão ativa

**`salvar_mensagem_historico()`**

- **O que faz**: Salva cada mensagem do chat no banco de dados
- **Por que assim**: Permite análise posterior e continuidade de contexto
- **Como funciona**: Insere mensagem com timestamp no MongoDB

#### Rotas Web:

**`/` (GET)**

- **Função**: Página principal
- **O que faz**: Lista coleções disponíveis e carrega histórico de chat
- **Decisão**: Interface única para todas as funcionalidades

**`/importar` (POST)**

- **Função**: Importar dados CSV
- **O que faz**: Processa upload de arquivo ou link do Google Sheets
- **Decisão**: Suporte a múltiplas fontes de dados

**`/colecao/<nome>` (GET)**

- **Função**: Visualizar dados de uma coleção
- **O que faz**: Exibe dados com paginação
- **Decisão**: Paginação para performance com grandes volumes

**`/chat` (POST)**

- **Função**: Processar consultas do usuário
- **O que faz**: Envia pergunta para IA e retorna resposta
- **Decisão**: API RESTful para comunicação assíncrona

---

### `backend/app/modules/importar_csv.py` - Processador de Dados

#### Funções Principais:

**`normalizar_dataframe(df, nome_arquivo)`**

- **O que faz**: Limpa e padroniza dados do CSV
- **Por que assim**: Dados CSV podem ter problemas de encoding e formatação
- **Como funciona**:
  1. Corrige encoding (acentos, caracteres especiais)
  2. Converte tudo para string (consistência)
  3. Remove espaços em branco desnecessários

**`gerar_hash_colunas(df)`**

- **O que faz**: Cria identificador único para cada linha
- **Por que assim**: Evita duplicatas e permite atualizações incrementais
- **Como funciona**: Gera SHA256 hash baseado em todos os valores da linha

**`importar_csv_para_mongo(caminho, nome_arquivo)`**

- **O que faz**: Processa e importa dados para o MongoDB
- **Por que assim**: Centraliza todo o processo de importação
- **Como funciona**:
  1. Carrega CSV (local ou URL)
  2. Normaliza dados
  3. Gera hashes únicos
  4. Insere no MongoDB com controle de duplicatas

### `backend/app/modules/detector_fraude.py` - Sistema de Detecção de Fraude

#### Responsabilidades:

- **Detectar padrões suspeitos** em dados de vendas e movimentações
- **Classificar riscos** (ALTO/MÉDIO) para cada suspeita
- **Gerar relatórios detalhados** com recomendações específicas
- **Integrar-se com o agente IA** para análise automática

#### Algoritmos Implementados:

**`detectar_volume_anomalo_devolucoes()`**

- **O que faz**: Identifica produtos com devoluções acima do normal
- **Por que assim**: Devoluções excessivas podem indicar fraude
- **Como funciona**: Calcula estatísticas históricas e identifica outliers

**`detectar_movimentacoes_suspeitas_curto_intervalo()`**

- **O que faz**: Detecta movimentações suspeitas em curto espaço de tempo
- **Por que assim**: Movimentações muito próximas podem indicar manipulação
- **Como funciona**: Analisa intervalos temporais entre movimentações

**`detectar_clientes_reincidentes()`**

- **O que faz**: Identifica clientes com histórico de problemas
- **Por que assim**: Clientes reincidentes podem indicar padrões fraudulentos
- **Como funciona**: Conta ocorrências por cliente e identifica frequências anômalas

**`detectar_produtos_reincidentes()`**

- **O que faz**: Identifica produtos com padrões suspeitos recorrentes
- **Por que assim**: Produtos problemáticos podem indicar fraude sistemática
- **Como funciona**: Analisa frequência de problemas por produto

---

### `backend/app/utils/utils.py` - Utilitários

#### Funções Principais:

**`corrigir_encoding_dataframe(df)`**

- **O que faz**: Corrige problemas de encoding em português
- **Por que assim**: CSVs podem vir com encoding incorreto (cp1252 vs UTF-8)
- **Como funciona**: Mapeia caracteres mal codificados para corretos

**`detectar_delimitador(texto)`**

- **O que faz**: Identifica se CSV usa vírgula ou ponto e vírgula
- **Por que assim**: Diferentes regiões usam delimitadores diferentes
- **Como funciona**: Analisa primeira linha e conta ocorrências

**`ajustar_link_google_sheets(url)`**

- **O que faz**: Converte link de visualização em link de exportação CSV
- **Por que assim**: Google Sheets precisa de URL específica para exportar
- **Como funciona**: Extrai ID da planilha e monta URL de exportação

**`carregar_csv(caminho_csv)`**

- **O que faz**: Carrega CSV de arquivo local ou URL
- **Por que assim**: Suporte flexível a diferentes fontes de dados
- **Como funciona**: Detecta tipo de fonte e aplica método apropriado

---

### `backend/app/modules/historico_conversas.py` - Sistema de Histórico

#### Responsabilidades:

- **Persistir conversas** entre sessões
- **Gerenciar sessões** de usuário
- **Fornecer estatísticas** de uso

#### Por que implementado assim:

- **Continuidade**: Usuário não perde contexto entre sessões
- **Análise**: Permite entender padrões de uso
- **Escalabilidade**: Suporte a múltiplos usuários

---

### `backend/app/agents/mongodb_agent.py` - Agente IA

#### Responsabilidades:

- **Interpretar perguntas** em linguagem natural
- **Gerar consultas MongoDB** apropriadas
- **Processar resultados** e gerar insights
- **Manter contexto** da conversa
- **Detectar intenções específicas** (análise de fraude, consultas de data, rankings)
- **Executar análises especializadas** automaticamente

#### Funcionalidades Avançadas:

**`_interpretar_pergunta(pergunta)`**

- **O que faz**: Analisa a pergunta e identifica o tipo de consulta
- **Por que assim**: Permite roteamento inteligente para diferentes funcionalidades
- **Como funciona**: Usa regex e palavras-chave para classificar a intenção

**`_fazer_consulta_inteligente(interpretacao)`**

- **O que faz**: Executa a consulta apropriada baseada na interpretação
- **Por que assim**: Centraliza a lógica de roteamento e execução
- **Como funciona**: Chama funções específicas baseadas no tipo de consulta

**`_executar_analise_fraude()`**

- **O que faz**: Executa análise completa de fraude quando solicitado
- **Por que assim**: Integra detecção de fraude com o sistema de IA
- **Como funciona**: Chama o detector de fraude e formata o resultado

**`_consultar_por_data_especifica(pergunta)`**

- **O que faz**: Processa consultas por data específica
- **Por que assim**: Permite consultas temporais precisas
- **Como funciona**: Extrai data da pergunta e consulta MongoDB

**`_consultar_por_periodo_datas(pergunta)`**

- **O que faz**: Processa consultas por período de datas
- **Por que assim**: Suporta análises temporais complexas
- **Como funciona**: Extrai intervalo de datas e consulta MongoDB

**`_fazer_consulta_direta(pergunta)`**

- **O que faz**: Executa consultas diretas (rankings, contagens)
- **Por que assim**: Otimiza consultas que não precisam de IA
- **Como funciona**: Usa agregações MongoDB para resultados rápidos

#### Por que implementado assim:

- **Flexibilidade**: Suporta diferentes tipos de consulta
- **Inteligência**: Entende intenção do usuário
- **Escalabilidade**: Pode ser estendido facilmente
- **Performance**: Consultas diretas são mais rápidas
- **Especialização**: Funcionalidades específicas para cada tipo de análise

---

## 🤖 Sistema de IA - Como Funciona

### Arquitetura da IA:

```
Pergunta do Usuário → Agente IA → Consulta MongoDB → Resposta Processada
```

### Fluxo de Processamento:

1. **Recepção**: Usuário faz pergunta em linguagem natural
2. **Interpretação**: Sistema analisa a pergunta e identifica o tipo de consulta
3. **Roteamento**: Direciona para função específica baseada na intenção:
   - **Análise de fraude**: Executa algoritmos de detecção
   - **Consultas de data**: Processa datas específicas ou períodos
   - **Rankings**: Executa agregações MongoDB diretas
   - **Consultas gerais**: Usa IA para interpretação complexa
4. **Execução**: Executa a consulta apropriada (MongoDB ou análise especializada)
5. **Formatação**: Gera resposta formatada (HTML, tabelas, relatórios)
6. **Resposta**: Retorna resultado estruturado e visualmente atrativo

### Por que OpenAI + LangChain:

- **OpenAI**: Melhor modelo de linguagem disponível
- **LangChain**: Framework que facilita integração e controle
- **Flexibilidade**: Permite customização e extensão

---

## 🗄️ Banco de Dados - MongoDB

### Por que MongoDB:

- **Flexibilidade**: Aceita dados não estruturados (CSV com colunas variáveis)
- **Performance**: Índices otimizados para consultas rápidas
- **Escalabilidade**: Suporta grandes volumes de dados
- **JSON nativo**: Integração natural com JavaScript (frontend)

### Estrutura de Dados:

**Coleções de Dados**:

- Nome baseado no arquivo CSV
- Documentos com estrutura flexível
- Campo `_hash` para controle de duplicatas

**Coleção `historico_conversas`**:

- Sessões agrupadas por ID único
- Mensagens com timestamp e tipo (usuário/agente)
- Estatísticas de uso

### Índices Criados:

- `_hash` (único) - Previne duplicatas
- Campos frequentes (SKU, LOJA, etc.) - Acelera consultas

---

## 🎨 Frontend - Interface Web

### Tecnologias Escolhidas:

- **Bootstrap**: Design responsivo sem complexidade
- **JavaScript Vanilla**: Sem frameworks pesados
- **HTML Templates**: Simplicidade e performance

### Por que essa abordagem:

- **Simplicidade**: Fácil manutenção e modificação
- **Performance**: Carregamento rápido
- **Responsividade**: Funciona em qualquer dispositivo

### Funcionalidades da Interface:

**Seção de Importação**:

- Upload de arquivo ou link
- Feedback visual do progresso
- Mensagens de erro claras

**Chat Interativo**:

- Interface conversacional
- Histórico persistente
- Indicador de "digitando"

**Visualização de Dados**:

- Tabelas paginadas
- Navegação intuitiva
- Filtros por quantidade

---

## 🔧 Decisões Técnicas Importantes

### 1. **Lazy Loading do Agente IA**

**Decisão**: Agente só é criado quando necessário
**Por que**: Economiza recursos e acelera inicialização
**Impacto**: Primeira consulta pode ser mais lenta

### 2. **Hash para Controle de Duplicatas**

**Decisão**: SHA256 baseado em todos os campos
**Por que**: Evita importações duplicadas
**Impacto**: Pequeno overhead computacional, mas grande benefício

### 3. **Encoding Automático**

**Decisão**: Tenta UTF-8, fallback para cp1252
**Por que**: CSVs podem ter diferentes encodings
**Impacto**: Maior compatibilidade com arquivos diversos

### 4. **Paginação no Frontend**

**Decisão**: 20 registros por página (padrão)
**Por que**: Performance e usabilidade
**Impacto**: Interface responsiva mesmo com milhões de registros

### 5. **Histórico de Conversas**

**Decisão**: Persistir todas as mensagens
**Por que**: Continuidade e análise de uso
**Impacto**: Crescimento do banco, mas valor agregado

---

## 🚀 Fluxo Completo de Uso

### 1. **Inicialização**:

```
Usuário acessa → Flask inicia → MongoDB conecta → Histórico carrega
```

### 2. **Importação de Dados**:

```
Upload CSV → Detecta encoding → Normaliza dados → Gera hashes → Insere MongoDB
```

### 3. **Consulta com IA**:

```
Pergunta → Agente IA → Analisa dados → Gera resposta → Salva histórico
```

### 4. **Visualização**:

```
Seleciona coleção → MongoDB query → Pagina resultados → Exibe tabela
```

---

## 📊 Métricas e Performance

### Otimizações Implementadas:

- **Índices MongoDB**: Consultas sub-segundo
- **Lazy Loading**: Inicialização rápida
- **Paginação**: Interface responsiva
- **Hash único**: Importações eficientes

### Limitações Conhecidas:

- **Primeira consulta**: Pode demorar para inicializar IA
- **Arquivos muito grandes**: Pode consumir muita memória
- **Muitas consultas**: Pode esgotar créditos OpenAI

---

## 🔮 Extensões Futuras Possíveis

### Melhorias Técnicas:

1. **Cache de consultas** - Reduz custos OpenAI
2. **Processamento assíncrono** - Para arquivos grandes
3. **Múltiplos formatos** - Excel, JSON, XML
4. **Dashboard visual** - Gráficos e métricas
5. **API RESTful** - Integração com outros sistemas

### Melhorias de UX:

1. **Autocompletar** - Sugestões de perguntas
2. **Templates** - Perguntas pré-definidas
3. **Exportar resultados** - PDF, Excel
4. **Compartilhamento** - Links para análises
5. **Notificações** - Alertas baseados em dados

---

## 🛡️ Considerações de Segurança

### Implementadas:

- **Validação de entrada** - Sanitização de dados
- **Controle de arquivos** - Tipos permitidos
- **Timeout de conexão** - Evita travamentos

### Recomendações:

- **HTTPS em produção** - Criptografia de dados
- **Autenticação** - Controle de acesso
- **Rate limiting** - Previne abuso
- **Backup regular** - Proteção de dados

---

## 📈 Monitoramento e Logs

### Logs Implementados:

- **Inicialização** - Status dos serviços
- **Importações** - Sucesso/erro de arquivos
- **Consultas IA** - Performance e erros
- **Conexões DB** - Status de conectividade

### Métricas Importantes:

- **Tempo de resposta** - Performance geral
- **Taxa de erro** - Estabilidade
- **Uso de recursos** - CPU, memória, disco
- **Consultas por minuto** - Carga do sistema

---

## 🎯 Conclusão

Este sistema foi projetado com foco em **simplicidade**, **performance** e **escalabilidade**. Cada decisão técnica foi tomada considerando:

1. **Facilidade de uso** para usuários não técnicos
2. **Manutenibilidade** do código
3. **Performance** com grandes volumes de dados
4. **Flexibilidade** para futuras extensões

A arquitetura modular permite evolução gradual e adaptação a diferentes necessidades, mantendo sempre a simplicidade como prioridade principal.
