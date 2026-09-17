from langchain_chroma import Chroma

from app.rag.embeddings import get_embeddings


CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "singapore_travel"


def get_vector_store():
    """Load the existing Singapore travel vector store."""

    embeddings = get_embeddings()

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )


# def search(query: str, k: int = 5):
#     """Retrieve the most relevant travel knowledge for a query."""

#     vector_store = get_vector_store()

#     return vector_store.similarity_search(
#         query,
#         k=k,
#     )

def search(query: str, k: int = 100):
    vector_store = get_vector_store()

    results = vector_store.similarity_search(
        query,
        k=k,
    )

    print("\n" + "=" * 60)
    print(f"RETRIEVED {len(results)} CHUNKS")
    print("=" * 60)

    for i, doc in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print("Source:", doc.metadata.get("filename"))
        print("Title:", doc.metadata.get("title"))
        print("URL:", doc.metadata.get("url") or doc.metadata.get("source"))
        print("Content preview:")
        print(doc.page_content[:500].replace("\n", " "))

    print("\n" + "=" * 60)

    return results