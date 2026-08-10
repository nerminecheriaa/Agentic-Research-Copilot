from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str = ""
    tavily_api_key: str = ""

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "research_copilot"

    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "agentic-research-copilot"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
