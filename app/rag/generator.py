import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()


def get_llm():
    """Return the configured Ollama chat model."""

    model = os.getenv(
        "LLM_MODEL",
        "llama3.1:8b",
    )

    return ChatOllama(
        model=model,
        temperature=0,
    )