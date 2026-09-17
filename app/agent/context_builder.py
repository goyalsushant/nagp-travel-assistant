from app.rag.retriever import search


def get_rag_context(query: str, k: int = 100):
    """
    Retrieve relevant Singapore travel knowledge
    and format it for the LLM.
    """

    documents = search(query, k=k)

    if not documents:
        return {
            "context": "",
            "sources": [],
        }

    context_parts = []
    sources = []

    for index, document in enumerate(documents, start=1):

        content = document.page_content
        metadata = document.metadata

        title = metadata.get(
            "title",
            "Unknown source"
        )

        url = metadata.get(
            "url",
            metadata.get(
                "source",
                ""
            )
        )

        context_parts.append(
            f"""
--- KNOWLEDGE CHUNK {index} ---

Source: {title}
URL: {url}

{content}
"""
        )

        source = {
            "title": title,
            "url": url,
        }

        if source not in sources:
            sources.append(source)

    return {
        "context": "\n".join(context_parts),
        "sources": sources,
    }