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

@app.get("/health")
async def health_check():
    """Endpoint para verificar o status da aplicação"""
    return {"status": "ok"}

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {"message": "Bem-vindo ao Projeto Agente IA API"}

@app.get("/datasets")
async def list_datasets():
    """Endpoint para listar datasets (mock)"""
    return {
        "success": True,
        "message": "Datasets listados com sucesso",
        "data": {
            "datasets": [
                {"id": "test_001", "name": "Dataset de Teste", "row_count": 100}
            ]
        }
    }

@app.post("/datasets/upload")
async def upload_dataset():
    """Endpoint para upload (mock)"""
    return {
        "success": True,
        "message": "Dataset enviado com sucesso",
        "data": {
            "dataset_id": "test_001",
            "row_count": 100,
            "columns": ["col1", "col2", "col3"]
        }
    }

@app.get("/datasets/{dataset_id}/preview")
async def preview_dataset(dataset_id: str):
    """Endpoint para preview (mock)"""
    return {
        "success": True,
        "message": "Preview gerado com sucesso",
        "data": {
            "preview": [
                ["1", "A", "100"],
                ["2", "B", "200"],
                ["3", "C", "300"]
            ],
            "total_rows": 100,
            "columns": ["ID", "Nome", "Valor"]
        }
    }

@app.post("/cleaning/run/{dataset_id}")
async def run_cleaning(dataset_id: str):
    """Endpoint para limpeza (mock)"""
    return {
        "success": True,
        "message": f"Dataset {dataset_id} limpo com sucesso",
        "data": {
            "dataset_id": dataset_id,
            "cleaned_rows": 95,
            "original_rows": 100,
            "cleaning_stats": {"duplicates_removed": 5}
        }
    }

@app.post("/vectors/index/{dataset_id}")
async def index_vectors(dataset_id: str):
    """Endpoint para indexação (mock)"""
    return {
        "success": True,
        "message": f"Dataset {dataset_id} indexado com sucesso",
        "data": {
            "dataset_id": dataset_id,
            "chunks_inserted": 95,
            "session_id": "test_session"
        }
    }

@app.post("/chat/data")
async def chat_data():
    """Endpoint para chat (mock)"""
    return {
        "success": True,
        "message": "Análise concluída com sucesso",
        "data": {
            "response": "| Coluna | Valor |\n|--------|-------|\n| ID | 1 |\n| Nome | A |\n| Valor | 100 |"
        }
    }

@app.post("/chat/insight")
async def chat_insight():
    """Endpoint para insights (mock)"""
    return {
        "success": True,
        "message": "Insights gerados com sucesso",
        "data": {
            "insights": "• Total de registros: 100\n• Colunas principais: ID, Nome, Valor\n• Dados bem estruturados"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor simples...")
    print("📍 Endpoint: http://localhost:8000")
    print("🔗 Health check: http://localhost:8000/health")
    uvicorn.run(app, host="0.0.0.0", port=8000)

