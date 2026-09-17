from pathlib import Path

import frontmatter
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from app.rag.embeddings import get_embeddings


DATA_DIR = Path("data/singapore")
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "singapore_travel"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
BATCH_SIZE = 20


def load_documents():
    """Load Markdown files and extract their front matter as metadata."""

    documents = []

    files = list(DATA_DIR.glob("*.md"))

    if not files:
        raise FileNotFoundError(
            f"No Markdown files found in {DATA_DIR.absolute()}"
        )

    for file_path in files:
        post = frontmatter.load(str(file_path))

        metadata = {
            key: str(value)
            for key, value in post.metadata.items()
        }

        metadata["filename"] = file_path.name

        document = Document(
            page_content=post.content,
            metadata=metadata
        )

        documents.append(document)

    return documents


def split_documents(documents):
    """Split documents into semantically useful chunks."""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\n## ",
            "\n### ",
            "\n\n",
            "\n",
            ". ",
            " ",
        ],
    )

    return splitter.split_documents(documents)


def create_vector_store(chunks):
    """Create the Chroma vector store and add documents in batches."""

    embeddings = get_embeddings()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )

    total_chunks = len(chunks)

    for start in range(0, total_chunks, BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]
        end = start + len(batch)

        print(
            f"Processing chunks "
            f"{start + 1}-{end} of {total_chunks}"
        )

        vector_store.add_documents(batch)

    return vector_store


def main():
    """Build the Singapore travel knowledge base."""

    print("Loading travel documents...")
    documents = load_documents()
    print(f"Loaded {len(documents)} document(s).")

    print("Splitting documents...")
    chunks = split_documents(documents)
    print(f"Created {len(chunks)} chunks.")

    print("Building vector store...")
    create_vector_store(chunks)

    print("Knowledge base created successfully.")


if __name__ == "__main__":
    main()