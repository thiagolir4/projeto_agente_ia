#!/bin/bash

echo "========================================"
echo "   Setup do Projeto Agente IA"
echo "========================================"
echo

echo "[1/4] Configurando Backend..."
cd backend

echo "Criando ambiente virtual..."
python3 -m venv .venv

echo "Ativando ambiente virtual..."
source .venv/bin/activate

echo "Instalando dependencias Python..."
pip install -r requirements.txt

echo "Configurando variaveis de ambiente..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "Arquivo .env criado. Edite com suas chaves API."
fi

echo
echo "[2/4] Configurando Frontend..."
cd ../frontend

echo "Instalando dependencias Node.js..."
npm install

echo "Configurando variaveis de ambiente..."
if [ ! -f .env.local ]; then
    cp env.local.example .env.local
fi

echo
echo "[3/4] Verificando instalacao..."
cd ../backend
source .venv/bin/activate
echo "Testando endpoint /health..."
python -c "import requests; print('Status:', requests.get('http://localhost:8000/health').json())" 2>/dev/null || echo "Backend nao esta rodando ainda"

echo
echo "[4/4] Instalacao concluida!"
echo
echo "Para executar o projeto:"
echo
echo "Backend (Terminal 1):"
echo "  cd backend"
echo "  source .venv/bin/activate"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo
echo "Frontend (Terminal 2):"
echo "  cd frontend"
echo "  npm run dev"
echo
echo "URLs:"
echo "  Backend: http://localhost:8000"
echo "  Frontend: http://localhost:3000"
echo "  Health Check: http://localhost:8000/health"
echo
