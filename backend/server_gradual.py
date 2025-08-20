from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Projeto Agente IA", version="1.0.0")

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints básicos
@app.get("/health")
async def health_check():
    """Endpoint para verificar o status da aplicação"""
    return {"status": "ok"}

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {"message": "Bem-vindo ao Projeto Agente IA API"}

# Carregar routers gradualmente
print("Carregando routers...")

try:
    print("1. Testando import de datasets...")
    from app.routers import datasets
    app.include_router(datasets.router)
    print("✅ Router datasets carregado")
except Exception as e:
    print(f"❌ Erro ao carregar datasets: {e}")

try:
    print("2. Testando import de cleaning...")
    from app.routers import cleaning
    app.include_router(cleaning.router)
    print("✅ Router cleaning carregado")
except Exception as e:
    print(f"❌ Erro ao carregar cleaning: {e}")

try:
    print("3. Testando import de analysis...")
    from app.routers import analysis
    app.include_router(analysis.router)
    print("✅ Router analysis carregado")
except Exception as e:
    print(f"❌ Erro ao carregar analysis: {e}")

try:
    print("4. Testando import de vectors...")
    from app.routers import vectors
    app.include_router(vectors.router)
    print("✅ Router vectors carregado")
except Exception as e:
    print(f"❌ Erro ao carregar vectors: {e}")

try:
    print("5. Testando import de chat...")
    from app.routers import chat
    app.include_router(chat.router)
    print("✅ Router chat carregado")
except Exception as e:
    print(f"❌ Erro ao carregar chat: {e}")

print("Carregamento de routers concluído!")

if __name__ == "__main__":
    import uvicorn
    print("Iniciando servidor...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
