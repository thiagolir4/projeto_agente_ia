# 🚀 Quick Start - Projeto Agente IA

## Instalação Rápida

### Windows

```cmd
# Execute o script de setup
setup.bat

# Ou manualmente:
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy env.example .env

cd ..\frontend
npm install
copy env.local.example .env.local
```

### Linux/Mac

```bash
# Execute o script de setup
./setup.sh

# Ou manualmente:
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env

cd ../frontend
npm install
cp env.local.example .env.local
```

## Execução

### Terminal 1 - Backend

```bash
cd backend
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 - Frontend

```bash
cd frontend
npm run dev
```

## Verificação

- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **Health Check**: http://localhost:8000/health

## Estrutura Criada

✅ **Backend Python (FastAPI)**

- Rota `/health` funcionando
- Configuração Pydantic
- Dependências instaladas

✅ **Frontend Next.js (TypeScript)**

- Páginas: `/`, `/chat`, `/upload`, `/finance`
- Componentes: Navbar, ChatBox, FileUploader, DataTable
- Tailwind CSS configurado

✅ **Configuração**

- `.gitignore` completo
- Scripts de setup
- Documentação atualizada

## Próximos Passos

1. Editar `.env` com suas chaves API
2. Implementar integração com OpenAI
3. Conectar upload de arquivos com backend
4. Adicionar dados financeiros reais
5. Implementar autenticação
