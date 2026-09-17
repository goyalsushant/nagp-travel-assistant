from app.rag.generator import get_llm
from app.rag.retriever import search


SYSTEM_PROMPT = """
You are a Singapore travel planning assistant.

Your job is to answer destination-related questions using
the supplied knowledge-base context.

Follow these rules strictly:

1. Use the knowledge-base context for destination facts.
2. Do not invent attractions, transportation information,
   cultural information, restaurants, or other destination facts.
3. If the context does not contain enough information to
   answer the question, clearly state that the knowledge
   base does not contain sufficient information.
4. You may organize and summarize the supplied information.
5. Clearly distinguish factual information from your own
   travel recommendations.
6. Do not treat knowledge-base information as current weather,
   currency rates, opening hours, or other live information.
7. Keep the answer useful and well structured.

Knowledge-base context:
{context}

User question:
{question}
"""


def format_context(documents):
    """Format retrieved documents for the LLM."""

    context_parts = []

    for document in documents:
        source = document.metadata.get(
            "title",
            document.metadata.get("filename", "Unknown source"),
        )

        context_parts.append(
            f"Source: {source}\n"
            f"Content:\n{document.page_content}"
        )

    return "\n\n---\n\n".join(context_parts)


def answer_question(question: str, k: int = 100):
    """Retrieve relevant knowledge and generate a grounded answer."""

    documents = search(question, k=k)

    if not documents:
        return {
            "answer": (
                "I don't have enough information in the "
                "Singapore travel knowledge base to answer "
                "that question."
            ),
            "sources": [],
        }

    context = format_context(documents)

    prompt = SYSTEM_PROMPT.format(
        context=context,
        question=question,
    )

    llm = get_llm()

    response = llm.invoke(prompt)

    sources = []

    for document in documents:
        metadata = document.metadata

        source = {
            "title": metadata.get("title", "Unknown source"),
            "url": metadata.get("url"),
        }

        if source not in sources:
            sources.append(source)

    return {
        "answer": response.content,
        "sources": sources,
    }