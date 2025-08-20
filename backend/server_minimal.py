from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Teste Mínimo", version="1.0.0")

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Endpoint para verificar o status da aplicação"""
    return {"status": "ok"}

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {"message": "Servidor mínimo funcionando!"}

if __name__ == "__main__":
    import uvicorn
    print("Iniciando servidor mínimo...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

