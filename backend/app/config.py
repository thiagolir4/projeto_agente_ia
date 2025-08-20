from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Configuracoes da aplicacao via variaveis de ambiente"""
    
    # OpenAI API
    OPENAI_API_KEY: str = ""
    
    # Diretorios e caminhos
    CHROMA_DIR: str = "./chroma_db"
    DUCKDB_PATH: str = "./data/finance.duckdb"
    
    # Configuracoes do servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instancia global das configuracoes
settings = Settings()

# Criar diretorios necessarios
os.makedirs(os.path.dirname(settings.DUCKDB_PATH), exist_ok=True)
os.makedirs(settings.CHROMA_DIR, exist_ok=True)

