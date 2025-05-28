import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "ChatBot Tutor Virtual"
    PROJECT_VERSION: str = "1.0.0"
    
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_HOST: str = (
        "localhost" if os.getenv("ENV", "").lower() == "local" else os.getenv("POSTGRES_HOST", "db")
    )


    TEST_DATABASE_URL: str = os.getenv("TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/tutor_virtual_test")
    
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "tutor_virtual")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
   
    
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    GROQ_MODEL_NAME: str = os.getenv("GROQ_MODEL_NAME", "llama3-8b-8192")
    
    # Configuración de Google AI Studio
    GOOGLE_AI_API_KEY: str = os.getenv("GOOGLE_AI_API_KEY")
    GOOGLE_AI_MODEL_NAME: str = os.getenv("GOOGLE_AI_MODEL_NAME", "gemma-2-9b-it")
    
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "uploads")
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    

settings = Settings()
