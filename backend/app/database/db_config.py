# Configurações de conexão ao MongoDB
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "dbGrupoOscar")

# Configurações da OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

print(f"MongoDB URI: {MONGO_URI}")
print(f"Database: {DB_NAME}")
print(f"OpenAI Key: {'Configurada' if OPENAI_API_KEY else 'Nao configurada'}")

