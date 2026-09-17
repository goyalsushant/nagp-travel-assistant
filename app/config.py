import os
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "nomic-embed-text"
)