from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    openai_endpoint: str = ""
    openai_key: str = ""
    openai_chat_deployment: str = "gpt-4o-mini"
    openai_embed_deployment: str = "text-embedding-3-small"
    
    search_endpoint: str = ""
    search_admin_key: str = ""
    search_index: str = "filings"
    
    foundry_endpoint: Optional[str] = None
    foundry_api_key: Optional[str] = None
    
    document_intel_account_url: str = ""
    document_intel_key: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
