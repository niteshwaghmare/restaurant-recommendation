from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration with LLM and API settings"""
    
    # OpenAI Models & Temperature
    MODEL_CREATIVE: str = "gpt-5-nano-2025-08-07"
    MODEL_STRUCTURED: str = "gpt-5-nano-2025-08-07"
    TEMP_CREATIVE: float = 0.7
    TEMP_STRUCTURED: float = 0.2
    
    # OpenAI API Key
    openai_api_key: str
    
    # LLM Parameters
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    
    # FastAPI Config
    app_title: str = "Restaurant Idea Generator"
    app_description: str = "AI-powered restaurant concept generator using LangChain and OpenAI"
    debug: bool = True
    
    # Logging
    log_level: str = "DEBUG"
    
    # Rate limiting
    requests_per_minute: int = 10
    
    class Config:
        env_file = Path(__file__).parent / ".env"
        case_sensitive = True


settings = Settings()
