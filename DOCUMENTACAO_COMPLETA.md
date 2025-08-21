# 📚 Documentação Completa - Projeto Agente IA

## 🏗️ Visão Geral da Arquitetura

O **Projeto Agente IA** é uma aplicação full-stack que combina análise de dados inteligente com interface web moderna. O sistema utiliza agentes de IA especializados para processar, analisar e gerar insights a partir de dados estruturados.

### **Arquitetura Geral**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Banco de      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   Dados        │
│   Porta 3000    │    │   Porta 8000    │    │   (DuckDB +    │
└─────────────────┘    └─────────────────┘    │   ChromaDB)     │
                                              └─────────────────┘
```

---

## 🎯 **Backend (FastAPI - Python)**

### **Estrutura de Diretórios**

```
backend/
├── app/
│   ├── agents/           # Agentes de IA especializados
│   ├── routers/          # Endpoints da API REST
│   ├── pipeline/         # Pipeline de processamento de dados
│   ├── chroma_db/        # Banco de dados vetorial
│   ├── data/             # Dados e arquivos temporários
│   ├── config.py         # Configurações da aplicação
│   ├── db.py            # Conexões com bancos de dados
│   ├── main.py          # Ponto de entrada da aplicação
│   └── vectors.py       # Operações com vetores
├── requirements.txt      # Dependências Python
└── env.example          # Variáveis de ambiente
```

### **1. Agentes de IA (`/app/agents/`)**

#### **DataAgent (`data_agent.py`)**

**Responsabilidade**: Análise e consulta de dados estruturados

**Funcionalidades**:

- Execução de queries SQL (apenas SELECT) no DuckDB
- Busca por similaridade usando vetores
- Formatação de resultados em tabelas Markdown
- Gestão de sessões de usuário
- Informações sobre tabelas e metadados

**Métodos Principais**:

```python
class SimpleDataAgent:
    async def run(prompt: str) -> str  # Processa prompts do usuário

def execute_duckdb_query(query: str, session_id: str) -> str
def search_vectors_tool(query: str, session_id: str, top_k: int) -> str
def get_session_info(session_id: str) -> str
def format_table_markdown(df: pd.DataFrame) -> str
```

**Exemplos de Uso**:

- "Mostre os primeiros 10 registros"
- "Execute: SELECT \* FROM dados LIMIT 5"
- "Quais colunas estão disponíveis?"
- "Busque por dados similares a 'vendas'"

#### **InsightAgent (`insight_agent.py`)**

**Responsabilidade**: Geração de insights executivos e recomendações

**Funcionalidades**:

- Extração de métricas-chave dos dados
- Geração de resumos executivos
- Recomendações baseadas na qualidade dos dados
- Identificação de padrões e anomalias

**Métodos Principais**:

```python
def extract_key_metrics(context: str) -> Dict[str, Any]
def generate_executive_summary(metrics: Dict[str, Any]) -> str
def generate_recommendations(metrics: Dict[str, Any], context: str) -> List[str]
def analyze_data_patterns(context: str) -> str
async def process_insights(context: str) -> str
```

**Saída Típica**:

```markdown
## Resumo Executivo

• Volume de dados: 1,250 registros
• Estrutura: 8 colunas
• Colunas numéricas: valor, quantidade, preco

## Recomendações

• Qualidade moderada: 3.2% de valores ausentes
• Análise multivariada: Dados numéricos permitem análises de correlação

## Padrões Identificados

• Variabilidade: Dados apresentam boa distribuição de valores
```

### **2. Rotas da API (`/app/routers/`)**

#### **Chat Router (`chat.py`)**

**Endpoint Base**: `/chat`

**Endpoints Disponíveis**:

1. **POST `/chat/data`**

   - **Função**: Análise de dados usando DataAgent
   - **Request Body**:
     ```json
     {
       "session_id": "string",
       "prompt": "string"
     }
     ```
   - **Response**:
     ```json
     {
       "success": true,
       "message": "Análise de dados concluída com sucesso",
       "data": {
         "session_id": "string",
         "prompt": "string",
         "response": "string (markdown)",
         "response_type": "markdown_table"
       }
     }
     ```

2. **POST `/chat/insight`**

   - **Função**: Geração de insights usando InsightAgent
   - **Request Body**:
     ```json
     {
       "session_id": "string",
       "context": "string (saída do DataAgent)"
     }
     ```
   - **Response**:
     ```json
     {
       "success": true,
       "message": "Insights gerados com sucesso",
       "data": {
         "session_id": "string",
         "insights": "string (markdown)",
         "response_type": "executive_summary"
       }
     }
     ```

3. **GET `/chat/sessions/{session_id}/info`**

   - **Função**: Informações sobre uma sessão específica
   - **Response**: Detalhes das tabelas e registros disponíveis

4. **DELETE `/chat/sessions/{session_id}`**
   - **Função**: Limpeza de memória de uma sessão específica

#### **Datasets Router (`datasets.py`)**

**Endpoint Base**: `/datasets`

**Funcionalidades**:

- Upload e processamento de arquivos CSV
- Validação de dados
- Criação de sessões de análise
- Gestão de metadados

#### **Cleaning Router (`cleaning.py`)**

**Endpoint Base**: `/cleaning`

**Funcionalidades**:

- Limpeza automática de dados
- Tratamento de valores ausentes
- Normalização de tipos de dados
- Validação de integridade

#### **Analysis Router (`analysis.py`)**

**Endpoint Base**: `/analysis`

**Funcionalidades**:

- Análises estatísticas básicas
- Geração de relatórios
- Exportação de resultados

#### **Vectors Router (`vectors.py`)**

**Endpoint Base**: `/vectors`

**Funcionalidades**:

- Indexação de dados em vetores
- Busca por similaridade semântica
- Gestão de embeddings

### **3. Pipeline de Processamento (`/app/pipeline/`)**

#### **Limpeza (`limpeza.py`)**

**Responsabilidade**: Preparação e limpeza de dados brutos

**Processos**:

- Remoção de duplicatas
- Tratamento de valores nulos
- Normalização de formatos
- Validação de tipos de dados

#### **Cruzamentos (`cruzamentos.py`)**

**Responsabilidade**: Análise de relacionamentos entre datasets

**Funcionalidades**:

- Join entre tabelas
- Análise de correlações
- Identificação de padrões

### **4. Banco de Dados (`/app/db.py`)**

#### **DuckDB**

**Tipo**: Banco de dados analítico em memória
**Uso**: Armazenamento temporário de dados de sessão
**Estrutura**: Tabelas por sessão (`ds_{session_id}_clean`)

#### **ChromaDB**

**Tipo**: Banco de dados vetorial
**Uso**: Indexação semântica para busca por similaridade
**Funcionalidades**: Embeddings, busca por proximidade

### **5. Configurações (`/app/config.py`)**

**Variáveis de Ambiente**:

```python
# OpenAI API Configuration
OPENAI_API_KEY: str

# Database and Storage Paths
CHROMA_DIR: str = "./chroma_db"
DUCKDB_PATH: str = "./data/finance.duckdb"

# Server Configuration
HOST: str = "0.0.0.0"
PORT: int = 8000
```

---

## 🎨 **Frontend (Next.js - TypeScript)**

### **Estrutura de Diretórios**

```
frontend/
├── src/
│   ├── app/              # Páginas da aplicação (App Router)
│   │   ├── chat/         # Interface de chat
│   │   ├── upload/       # Upload de arquivos
│   │   ├── finance/      # Consultas financeiras
│   │   ├── globals.css   # Estilos globais
│   │   ├── layout.tsx    # Layout principal
│   │   └── page.tsx      # Página inicial
│   ├── components/       # Componentes reutilizáveis
│   │   ├── ChatBox.tsx   # Interface de chat
│   │   ├── DataTable.tsx # Tabela de dados
│   │   ├── FileUploader.tsx # Upload de arquivos
│   │   └── Navbar.tsx    # Navegação
│   └── lib/              # Utilitários e configurações
├── package.json          # Dependências Node.js
├── tailwind.config.js    # Configuração Tailwind CSS
└── next.config.js        # Configuração Next.js
```

### **1. Páginas da Aplicação**

#### **Página Inicial (`/`)**

**Funcionalidades**:

- Apresentação do projeto
- Links para funcionalidades principais
- Dashboard de status

#### **Chat (`/chat`)**

**Funcionalidades**:

- Interface de conversa com agentes IA
- Gestão de sessões
- Histórico de conversas
- Renderização de markdown

#### **Upload (`/upload`)**

**Funcionalidades**:

- Upload de arquivos CSV
- Validação de formato
- Preview dos dados
- Inicialização de sessão de análise

#### **Finance (`/finance`)**

**Funcionalidades**:

- Consultas financeiras
- Análise de dados econômicos
- Integração com APIs externas

### **2. Componentes Principais**

#### **ChatBox (`ChatBox.tsx`)**

**Responsabilidade**: Interface principal de chat

**Funcionalidades**:

- Envio de mensagens
- Recebimento de respostas
- Renderização de markdown
- Gestão de estado da conversa

**Props**:

```typescript
interface ChatBoxProps {
  sessionId: string;
  onNewSession?: () => void;
  onClearChat?: () => void;
}
```

#### **DataTable (`DataTable.tsx`)**

**Responsabilidade**: Exibição de dados em formato tabular

**Funcionalidades**:

- Paginação
- Ordenação
- Filtros
- Exportação

**Props**:

```typescript
interface DataTableProps {
  data: any[];
  columns: string[];
  pageSize?: number;
  onPageChange?: (page: number) => void;
}
```

#### **FileUploader (`FileUploader.tsx`)**

**Responsabilidade**: Upload e processamento de arquivos

**Funcionalidades**:

- Drag & drop
- Validação de arquivos
- Preview de dados
- Upload progressivo

#### **Navbar (`Navbar.tsx`)**

**Responsabilidade**: Navegação principal

**Funcionalidades**:

- Menu de navegação
- Indicador de status
- Links para funcionalidades

### **3. Estilização e UI**

#### **Tailwind CSS**

**Framework**: Tailwind CSS v3.3.0
**Configuração**: `tailwind.config.js`
**Características**: Utility-first, responsivo, customizável

#### **Componentes de Design**

- **Botões**: Azuis para ações primárias, cinzas para secundárias
- **Cards**: Fundo branco com bordas arredondadas
- **Tabelas**: Linhas alternadas, hover effects
- **Formulários**: Inputs com bordas e focus states

---

## 🔧 **Configuração e Instalação**

### **1. Requisitos do Sistema**

#### **Backend**

- Python 3.8+
- pip
- Ambiente virtual (venv)

#### **Frontend**

- Node.js 18+
- npm ou yarn

### **2. Instalação**

#### **Backend**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
copy env.example .env
```

#### **Frontend**

```bash
cd frontend
npm install
copy env.local.example .env.local
```

### **3. Configuração de Ambiente**

#### **Backend (`.env`)**

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database and Storage Paths
CHROMA_DIR=./chroma_db
DUCKDB_PATH=./data/finance.duckdb

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

#### **Frontend (`.env.local`)**

```env
# Configurações da API
NEXT_PUBLIC_API_BASE=http://localhost:8000

# Outras configurações (opcional)
NEXT_PUBLIC_APP_NAME=Projeto Agente IA
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### **4. Execução**

#### **Backend**

```bash
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### **Frontend**

```bash
cd frontend
npm run dev
```

---

## 🚀 **Funcionalidades e Fluxos**

### **1. Fluxo de Upload e Análise**

```
1. Usuário faz upload de CSV
   ↓
2. Sistema valida formato e conteúdo
   ↓
3. Dados são limpos e processados
   ↓
4. Tabela é criada no DuckDB (ds_{session_id}_clean)
   ↓
5. Dados são indexados no ChromaDB
   ↓
6. Sessão é criada e usuário pode fazer consultas
```

### **2. Fluxo de Chat com Agentes**

```
1. Usuário envia pergunta
   ↓
2. Sistema identifica tipo de consulta
   ↓
3. DataAgent processa e retorna dados em Markdown
   ↓
4. Opcional: InsightAgent gera insights
   ↓
5. Resposta é renderizada na interface
```

### **3. Tipos de Consultas Suportadas**

#### **Consultas SQL**

- Apenas SELECT (por segurança)
- Tabelas específicas por sessão
- Limites de resultados

#### **Busca por Similaridade**

- Busca semântica em vetores
- Configurável (top_k)
- Metadados incluídos

#### **Informações de Sessão**

- Status das tabelas
- Contagem de registros
- Metadados disponíveis

---

## 📊 **APIs e Endpoints**

### **1. Endpoints Principais**

| Método | Endpoint                   | Descrição           | Status |
| ------ | -------------------------- | ------------------- | ------ |
| GET    | `/`                        | Página inicial      | ✅     |
| GET    | `/health`                  | Health check        | ✅     |
| POST   | `/chat/data`               | Análise de dados    | ✅     |
| POST   | `/chat/insight`            | Geração de insights | ✅     |
| GET    | `/chat/sessions/{id}/info` | Info da sessão      | ✅     |
| DELETE | `/chat/sessions/{id}`      | Limpar sessão       | ✅     |
| POST   | `/datasets/upload`         | Upload de arquivos  | ✅     |
| POST   | `/cleaning/process`        | Limpeza de dados    | ✅     |
| GET    | `/analysis/summary`        | Resumo estatístico  | ✅     |
| POST   | `/vectors/index`           | Indexação vetorial  | ✅     |

### **2. Códigos de Status HTTP**

- **200**: Sucesso
- **400**: Bad Request (dados inválidos)
- **404**: Not Found (recurso não encontrado)
- **500**: Internal Server Error (erro interno)

### **3. Formatos de Resposta**

#### **Sucesso**

```json
{
  "success": true,
  "message": "Operação realizada com sucesso",
  "data": { ... }
}
```

#### **Erro**

```json
{
  "success": false,
  "message": "Descrição do erro",
  "error": "Detalhes técnicos"
}
```

---

## 🧪 **Testes e Qualidade**

### **1. Testes Disponíveis**

#### **Backend**

- `test_agents.py`: Testes dos agentes IA
- `test_api.py`: Testes da API REST
- `test_app.py`: Testes da aplicação
- `test_cleaning.py`: Testes do pipeline de limpeza
- `test_vectors.py`: Testes de operações vetoriais

#### **Execução de Testes**

```bash
cd backend
.venv\Scripts\activate
python -m pytest test_*.py
```

### **2. Validação de Código**

#### **Python**

- Type hints
- Docstrings
- PEP 8 compliance
- Error handling

#### **TypeScript**

- Strict mode
- Interface definitions
- Type safety
- ESLint configuration

---

## 🔒 **Segurança e Boas Práticas**

### **1. Medidas de Segurança**

- **CORS**: Configurado para localhost apenas
- **SQL Injection**: Queries limitadas a SELECT
- **File Upload**: Validação de tipos e tamanhos
- **Session Management**: Isolamento por sessão

### **2. Boas Práticas Implementadas**

- **Separação de Responsabilidades**: Cada módulo tem função específica
- **Error Handling**: Tratamento robusto de erros
- **Logging**: Sistema de logs estruturado
- **Configuration Management**: Variáveis de ambiente
- **Async/Await**: Operações assíncronas para performance

---

## 📈 **Monitoramento e Logs**

### **1. Sistema de Logs**

#### **Backend**

- **Nível**: INFO por padrão
- **Formato**: Estruturado com timestamps
- **Rotação**: Por arquivo de log

#### **Frontend**

- **Console**: Logs de desenvolvimento
- **Error Tracking**: Captura de erros do usuário

### **2. Métricas Disponíveis**

- **Performance**: Tempo de resposta da API
- **Uso**: Número de sessões ativas
- **Erros**: Taxa de erro por endpoint
- **Recursos**: Uso de memória e CPU

---

## 🚀 **Deploy e Produção**

### **1. Ambiente de Desenvolvimento**

- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **Hot Reload**: Ativado para desenvolvimento

### **2. Ambiente de Produção**

#### **Backend**

```bash
# Build da aplicação
pip install -r requirements.txt

# Execução em produção
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### **Frontend**

```bash
# Build de produção
npm run build

# Execução
npm run start
```

### **3. Docker (Opcional)**

```dockerfile
# Backend Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🔮 **Roadmap e Melhorias Futuras**

### **1. Funcionalidades Planejadas**

- **Autenticação**: Sistema de login e usuários
- **Persistência**: Banco de dados PostgreSQL
- **Cache**: Redis para performance
- **WebSockets**: Chat em tempo real
- **Notificações**: Sistema de alertas

### **2. Melhorias Técnicas**

- **Microserviços**: Separação em serviços independentes
- **API Gateway**: Centralização de rotas
- **Load Balancer**: Distribuição de carga
- **Monitoring**: Prometheus + Grafana
- **CI/CD**: Pipeline automatizado

### **3. Integrações**

- **OpenAI**: GPT-4 para análises avançadas
- **Google Analytics**: Métricas de uso
- **Slack**: Notificações e integração
- **Zapier**: Automações externas

---

## 📞 **Suporte e Contato**

### **1. Documentação Adicional**

- **README.md**: Visão geral do projeto
- **QUICKSTART.md**: Guia de início rápido
- **INSTALACAO.md**: Instruções detalhadas de instalação

### **2. Troubleshooting Comum**

#### **Erro: "Erro interno ao processar análise de dados"**

- **Causa**: Problema com biblioteca agno
- **Solução**: Implementação corrigida com SimpleDataAgent

#### **Erro: "Tabela não encontrada"**

- **Causa**: Sessão expirada ou dados não carregados
- **Solução**: Fazer upload de dados novamente

#### **Erro: "CORS"**

- **Causa**: Configuração incorreta de origens
- **Solução**: Verificar configuração CORS no backend

### **3. Recursos Úteis**

- **FastAPI Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Frontend**: http://localhost:3000

---

## 📝 **Conclusão**

O **Projeto Agente IA** representa uma solução completa e moderna para análise de dados inteligente. Com arquitetura bem estruturada, agentes especializados e interface intuitiva, o sistema oferece:

✅ **Backend robusto** com FastAPI e agentes IA  
✅ **Frontend moderno** com Next.js e TypeScript  
✅ **Processamento inteligente** de dados  
✅ **Interface de chat** natural e intuitiva  
✅ **Arquitetura escalável** e bem documentada

O projeto está pronto para uso em desenvolvimento e pode ser facilmente adaptado para produção com as melhorias planejadas.

---

_Documentação gerada em: Janeiro 2025_  
_Versão: 1.0.0_  
_Projeto: Agente IA - Sistema de Análise Inteligente de Dados_
