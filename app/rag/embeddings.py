import os

from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings


load_dotenv()


def get_embeddings():
    """Return the configured Ollama embedding model."""

    model = os.getenv(
        "EMBEDDING_MODEL",
        "nomic-embed-text",
    )

    return OllamaEmbeddings(
        model=model,
    )