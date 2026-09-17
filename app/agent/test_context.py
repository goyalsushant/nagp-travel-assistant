from app.agent.context_builder import get_rag_context


query = "Plan a three-day Singapore sightseeing itinerary"

result = get_rag_context(query, k=8)

print("=" * 60)
print("RAG CONTEXT")
print("=" * 60)

print(result["context"])

print("\n" + "=" * 60)
print("SOURCES")
print("=" * 60)

for source in result["sources"]:
    print(f"- {source['title']}")
    print(f"  {source['url']}")