import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    AZURE_OPENAI_CHAT_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "")
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "")
    AZURE_OPENAI_EMBEDDING_API_VERSION: str = os.getenv("AZURE_OPENAI_EMBEDDING_API_VERSION", "2024-02-01")
    
    # Standard OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Google Gemini
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Anthropic
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Minimax
    MINIMAX_API_KEY: str = os.getenv("MINIMAX_API_KEY", "")
    
    FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", "db/faiss_index")
    DATA_DIR: str = os.getenv("DATA_DIR", "data")

settings = Settings()

# Validate crucial settings
if not settings.AZURE_OPENAI_API_KEY and not settings.OPENAI_API_KEY and not settings.GOOGLE_API_KEY:
    print("WARNING: No LLM API Keys are set in the environment (.env).")
