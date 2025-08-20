# Projeto Agente IA

## Visão Geral

Este é um monorepo que implementa um sistema de agente de IA com backend em Python (FastAPI) e frontend em Next.js. O projeto visa criar uma plataforma completa para análise de dados, chat com IA e upload de arquivos.

## Stack Tecnológica

### Backend

- **Python 3.11** - Linguagem principal
- **FastAPI** - Framework web moderno e rápido
- **Pydantic** - Validação de dados e configurações
- **Pandas & Polars** - Manipulação de dados
- **DuckDB** - Banco de dados analítico
- **ChromaDB** - Vector database para embeddings
- **Uvicorn** - Servidor ASGI

### Frontend

- **Next.js 14** - Framework React com App Router
- **TypeScript** - Tipagem estática
- **React** - Biblioteca de interface
- **Tailwind CSS** - Framework CSS utilitário

## Estrutura do Projeto

```
projeto_agente_ia/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── config.py
│   ├── requirements.txt
│   ├── env.example
│   └── .venv/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx
│   │   │   ├── chat/
│   │   │   ├── upload/
│   │   │   └── finance/
│   │   └── components/
│   │       ├── Navbar.tsx
│   │       ├── ChatBox.tsx
│   │       ├── FileUploader.tsx
│   │       └── DataTable.tsx
│   ├── package.json
│   └── env.local.example
├── .gitignore
└── README.md
```

## Objetivos do MVP

1. **Sistema de Chat** - Interface para conversação com IA
2. **Upload de Arquivos** - Sistema para carregar e processar documentos
3. **Análise Financeira** - Dashboard para análise de dados financeiros
4. **API REST** - Backend robusto com endpoints para todas as funcionalidades
5. **Interface Moderna** - Frontend responsivo e intuitivo

## Como Executar

### Pré-requisitos

- Python 3.11+
- Node.js 18+
- npm ou yarn

### Backend

1. **Criar ambiente virtual:**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# ou
source .venv/bin/activate  # Linux/Mac
```

2. **Instalar dependências:**

```bash
pip install -r requirements.txt
```

3. **Configurar variáveis de ambiente:**

```bash
cp env.example .env
# Editar .env com suas chaves
```

4. **Executar servidor:**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

1. **Instalar dependências:**

```bash
cd frontend
npm install
```

2. **Configurar variáveis de ambiente:**

```bash
cp env.local.example .env.local
```

3. **Executar em modo desenvolvimento:**

```bash
npm run dev
```

## Endpoints da API

- `GET /health` - Status da aplicação
- `GET /` - Endpoint raiz
- `POST /chat` - Envio de mensagens para IA (a implementar)
- `POST /upload` - Upload de arquivos (a implementar)
- `GET /finance/data` - Dados financeiros (a implementar)

## Rotas do Frontend

- `/` - Página inicial com visão geral
- `/chat` - Interface de chat com IA
- `/upload` - Sistema de upload de arquivos
- `/finance` - Dashboard de análise financeira

## Critérios de Aceite

- [x] Backend responde em `/health` com status OK
- [x] Frontend abre em `/` com navbar funcional
- [x] Estrutura de rotas implementada
- [x] Componentes básicos criados
- [x] Configuração de ambiente completa
- [x] Interface responsiva com Tailwind CSS
- [x] Sistema de navegação entre páginas
- [x] Componentes interativos (ChatBox, FileUploader, DataTable)

## Comandos de Desenvolvimento

### Backend

```bash
# Ativar ambiente virtual
cd backend
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Executar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Verificar endpoints
curl http://localhost:8000/health
```

### Frontend

```bash
# Instalar dependências
cd frontend
npm install

# Executar em desenvolvimento
npm run dev

# Build para produção
npm run build

# Executar build
npm start
```

## Desenvolvimento

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Implemente as mudanças
4. Execute os testes
5. Faça commit e push
6. Abra um Pull Request

## Próximos Passos

1. **Integração com OpenAI API** - Conectar chat com GPT
2. **Processamento de arquivos** - Implementar análise de documentos
3. **Dados financeiros reais** - Conectar com APIs de mercado
4. **Autenticação** - Sistema de login e usuários
5. **Persistência de dados** - Banco de dados para histórico
6. **Testes automatizados** - Unit e integration tests

## Licença

Este projeto está sob a licença MIT.
