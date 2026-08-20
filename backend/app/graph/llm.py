from langchain_groq import ChatGroq

from app.config import settings

# llama-3.3-70b : bon compromis qualité/vitesse/coût pour du grading et de la génération.
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=settings.groq_api_key,
    temperature=0,
)
