from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import datasets, cleaning, analysis, vectors, chat

app = FastAPI(title="Projeto Agente IA", version="1.0.0")

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(datasets.router)
app.include_router(cleaning.router)
app.include_router(analysis.router)
app.include_router(vectors.router)
app.include_router(chat.router)

@app.get("/health")
async def health_check():
    """Endpoint para verificar o status da aplicação"""
    return {"status": "ok"}

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {"message": "Bem-vindo ao Projeto Agente IA API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

