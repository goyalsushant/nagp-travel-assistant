# Singapore Travel Assistant

An AI-powered Singapore travel assistant that combines **Retrieval-Augmented Generation (RAG)** with **MCP-based tools** for current weather and currency information.

The application uses a Singapore-specific knowledge base to provide grounded travel recommendations and can retrieve live information through MCP servers.

---

## Features

* Singapore travel question answering using RAG
* Knowledge base built from Singapore travel resources
* Multiple categorized Singapore travel documents
* Top-K semantic retrieval from ChromaDB
* Rule-based intent detection
* Weather information through a Weather MCP server
* Currency conversion through a Currency MCP server
* Weather-aware itinerary planning
* Conversation history / basic memory
* Local Llama 3.1 8B model through Ollama
* Streamlit web interface
* Source attribution for retrieved knowledge-base content

---

## Architecture

```text
                         ┌──────────────────────┐
                         │   Streamlit UI       │
                         │  streamlit_app.py    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Travel Agent      │
                         │   travel_agent.py    │
                         └──────────┬───────────┘
                                    │
                  ┌─────────────────┼─────────────────┐
                  │                 │                 │
                  ▼                 ▼                 ▼
          ┌──────────────┐  ┌──────────────┐     ┌──────────────┐
          │ Intent       │  │ RAG          │     │ MCP Tools    │
          │ Detection    │  │ Retrieval    │     │              │
          └──────────────┘  └──────┬───────┘     └──────┬───────┘
                                   │                    │
                                   ▼                    ├──────────────┐
                            ┌──────────────┐            │              │
                            │  ChromaDB    │            ▼              ▼
                            │ Vector Store │    ┌────────────┐ ┌────────────┐
                            └──────┬───────┘    │  Weather   │ │  Currency  │
                                   │            │    MCP     │ │    MCP     │
                                   ▼            └────────────┘ └────────────┘
                         ┌──────────────────┐
                         │ Singapore        │
                         │ Knowledge Base   │
                         └──────────────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Llama 3.1 8B / Ollama│
                         │ Response Generation  │
                         └──────────────────────┘
```

---

## Project Structure

```text
.
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── llm.py
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── context_builder.py
│   │   ├── intent.py
│   │   ├── mcp_client.py
│   │   ├── state.py
│   │   ├── travel_agent.py
│   │   └── test_context.py
│   │
│   ├── mcp_client/
│   │   ├── test_currency_client.py
│   │   └── test_weather_client.py
│   │
│   ├── mcp_servers/
│   │   ├── __init__.py
│   │   ├── currency_server.py
│   │   └── weather_server.py
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── embeddings.py
│   │   ├── generator.py
│   │   ├── ingest.py
│   │   ├── qa.py
│   │   └── retriever.py
│   │
│   └── ui/
│       └── streamlit_app.py
│
├── data/
│   └── singapore/
│       ├── visitsingapore_city_nature.md
│       ├── visitsingapore_culture_heritage.md
│       ├── visitsingapore_essential_information.md
│       ├── visitsingapore_family_fun.md
│       ├── visitsingapore_iconic.md
│       ├── visitsingapore_itineraries.md
│       ├── visitsingapore_neighbourhood.md
│       ├── visitsingapore_night_life.md
│       ├── visitsingapore_unique_experiences.md
│       └── wikivoyage_singapore.md
│
├── chroma_db/
│
├── category_scrapper.py
├── url_to_markdown.py
├── test_rag.py
├── test_retrieval.py
├── ply_test.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

## Technologies Used

| Component            | Technology                                        |
| -------------------- | ------------------------------------------------- |
| Programming Language | Python                                            |
| LLM                  | Llama 3.1 8B                                      |
| LLM Runtime          | Ollama                                            |
| LLM Framework        | LangChain                                         |
| Vector Database      | ChromaDB                                          |
| Embeddings           | Sentence Transformer / configured embedding model |
| Retrieval            | Semantic similarity search                        |
| Tool Protocol        | MCP                                               |
| Weather              | Weather MCP server                                |
| Currency             | Currency MCP server                               |
| UI                   | Streamlit                                         |

---

## Knowledge Base

The Singapore knowledge base is divided into multiple documents to improve retrieval relevance.

Current categories include:

* Essential Information
* Itineraries
* Neighbourhoods
* Nightlife
* Unique Experiences
* City & Nature
* Culture & Heritage
* Family Fun
* Iconic Attractions
* General Singapore information

The documents are stored under:

```text
data/singapore/
```

The knowledge base is ingested into ChromaDB and queried using semantic similarity retrieval.

---

## RAG Pipeline

The RAG pipeline works approximately as follows:

```text
User Question
     │
     ▼
Intent Detection
     │
     ▼
Retrieve relevant documents
     │
     ▼
Semantic similarity search
     │
     ▼
Top-K chunks
     │
     ▼
Build RAG context
     │
     ▼
Llama 3.1 8B
     │
     ▼
Grounded answer
```

The current retrieval configuration uses:

```python
k=10
```

This can be adjusted in the retrieval/agent configuration if more or fewer chunks are required.

---

## Intent Detection

The application currently uses lightweight rule-based intent detection.

Supported intent combinations include:

```text
RAG
WEATHER
CURRENCY
RAG + WEATHER
RAG + CURRENCY
RAG + WEATHER + CURRENCY
UNKNOWN
```

Examples:

### RAG

```text
What are the best things to do in Singapore?
```

### Weather

```text
What is the weather forecast for Singapore?
```

### Currency

```text
Convert 50000 INR to SGD.
```

### RAG + Weather

```text
Plan a three-day Singapore trip according to the weather forecast.
```

### RAG + Currency

```text
Plan a Singapore trip with a budget of 50000 INR.
```

---

## MCP Integration

The application uses MCP servers to retrieve information that should not be treated as static knowledge-base information.

### Weather MCP

The Weather MCP is used for current/future weather information.

Example request:

```text
What is the weather forecast for Singapore?
```

The agent can use the returned forecast when creating weather-aware recommendations.

For example, an itinerary request can combine:

```text
Singapore Knowledge Base
        +
Weather MCP
        +
Llama 3.1 8B
```

---

### Currency MCP

The Currency MCP is used for currency conversion.

Example:

```text
Convert 50000 INR to SGD.
```

Currency information is retrieved through the MCP server rather than being hard-coded into the travel knowledge base.

---

## Weather-Aware Itineraries

For itinerary requests that mention weather, the agent combines:

1. Singapore travel knowledge from RAG
2. Current forecast from Weather MCP
3. LLM-generated itinerary organization

For example:

```text
User
 │
 ▼
"Plan a 3-day Singapore trip according to the weather"
 │
 ├──► RAG
 │       └── Singapore attractions and activities
 │
 └──► Weather MCP
         └── Forecast for requested days
                  │
                  ▼
             Llama 3.1 8B
                  │
                  ▼
          Weather-aware itinerary
```

The prompt instructs the model to avoid presenting unsupported attraction details, opening hours, prices, or operating information as facts.

---

## LLM Grounding

The response-generation prompt follows several grounding rules.

### Knowledge Base

Singapore-specific destination facts should come from the retrieved knowledge base.

### Weather

Current weather information should come from the Weather MCP.

### Currency

Currency information should come from the Currency MCP.

### Recommendations

The model may organize and combine retrieved information into an itinerary, but unsupported destination facts should not be introduced as factual information.

---

## Conversation Memory

The `TravelAgent` maintains a lightweight conversation history.

Recent user and assistant messages are stored and passed to the LLM when generating subsequent responses.

This allows follow-up questions such as:

```text
User:
Plan a three-day Singapore trip.

User:
Make Day 2 more family-friendly.
```

The second request can use the previous conversation context.

---

## Installation

### 1. Clone the project

Clone or download the project into a local directory.

---

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Ollama Setup

Install Ollama and make sure it is running.

Pull the required model:

```bash
ollama pull llama3.1:8b
```

Verify the model:

```bash
ollama list
```

You should see:

```text
llama3.1:8b
```

---

## Environment Configuration

Create a `.env` file in the project root if required by the configured MCP servers or application settings.

Example:

```env
# Add required API keys/configuration here
# according to the configured MCP servers.
```

Do not commit API keys or other secrets to Git.

---

## Building the Vector Database

The project contains ingestion functionality under:

```text
app/rag/ingest.py
```

The Singapore source documents are located at:

```text
data/singapore/
```

Run the ingestion process according to the implementation in `app/rag/ingest.py`.

This creates/populates the local:

```text
chroma_db/
```

vector database.

If the knowledge-base documents are changed, rerun the ingestion process so the vector store reflects the updated data.

---

## Running the Streamlit Application

From the project root:

```bash
streamlit run app/ui/streamlit_app.py
```

The application will start the Streamlit development server.

Open the displayed local URL in a browser.

---

## Example Questions

### Travel Planning

```text
Plan a three-day Singapore trip.
```

### Weather

```text
What is the weather forecast for Singapore?
```

### Weather-Aware Planning

```text
Plan a three-day Singapore trip and adjust it according to the weather forecast.
```

### Attractions

```text
What are some unique experiences in Singapore?
```

### Family Travel

```text
What are some family-friendly things to do in Singapore?
```

### Nightlife

```text
What can I do in Singapore at night?
```

### Currency

```text
Convert 50000 INR to SGD.
```

---

## Testing

The repository contains several test files for validating individual components.

### RAG Testing

```bash
python test_rag.py
```

### Retrieval Testing

```bash
python test_retrieval.py
```

Additional component-level tests are available under:

```text
app/agent/test_context.py
app/mcp_client/test_weather_client.py
app/mcp_client/test_currency_client.py
```

---

## Example Processing Flow

For:

```text
Plan a three-day Singapore trip and adjust it according to the weather forecast.
```

The application performs:

```text
1. Detect intent
       │
       ▼
   RAG + WEATHER
       │
       ├───────────────────┐
       ▼                   ▼
2. Search KB         3. Weather MCP
       │                   │
       ▼                   ▼
4. Retrieve         5. Current forecast
   relevant chunks
       │                   │
       └─────────┬─────────┘
                 ▼
        6. Build context
                 │
                 ▼
        7. Llama 3.1 8B
                 │
                 ▼
        8. Final itinerary
```

---

## Response Structure

For itinerary requests, the application is designed to produce a response containing:

```text
Trip Plan

Day 1
Day 2
Day 3

Weather Considerations

Knowledge Base Sources

MCP Information

Recommendation Type
```

This makes it possible to distinguish:

* Information retrieved from the Singapore knowledge base
* Current information retrieved through MCP
* AI-generated organization and recommendations

---

## Data Sources

The current knowledge base contains Singapore travel information sourced from:

* Wikivoyage Singapore
* Visit Singapore

The source URLs are retained as metadata during ingestion and can be displayed with retrieved results.

---

## Design Decisions

### Why RAG?

Singapore travel information is stored separately from the language model so that the assistant can ground destination-specific answers in a controlled knowledge base.

### Why MCP?

Weather and currency information are dynamic. MCP allows the application to retrieve current information through dedicated tools instead of relying on static documents or model knowledge.

### Why Rule-Based Intent Detection?

Intent detection is intentionally lightweight and deterministic. It decides whether the request requires:

```text
RAG
Weather MCP
Currency MCP
```

without requiring another LLM call.

### Why Llama 3.1 8B?

The project uses a locally hosted model through Ollama, allowing response generation without requiring a hosted LLM API.

---

## Limitations

The current implementation is a Phase 1 travel assistant.

Current limitations include:

* Intent detection is keyword/rule based.
* Currency amount and currency extraction may require further enhancement depending on the current implementation.
* Retrieval quality depends on the contents and chunking of the knowledge base.
* The assistant should not be treated as a real-time booking system.
* Attraction opening hours and ticket availability should not be assumed unless present in the supplied context.
* Weather information depends on the availability and response of the Weather MCP server.
* The conversation memory is currently lightweight and in-memory.
* The knowledge base currently focuses on Singapore.

---

## Future Improvements

Potential future improvements include:

* Better natural-language intent detection
* Dynamic currency amount/currency extraction
* Improved retrieval and reranking
* Metadata-aware retrieval by category/subcategory
* Better handling of follow-up questions
* Persistent conversation memory
* More MCP tools
* Restaurant and reservation integration
* Transport information
* More destinations
* Improved itinerary optimization
* Better source-level citations
* Automated evaluation of RAG answers
* Retrieval quality metrics

---

## Project Status

**Current status: Phase 1**

Implemented:

* Singapore knowledge base
* Categorized travel documents
* ChromaDB vector retrieval
* Top-K retrieval
* Rule-based intent detection
* Llama 3.1 8B response generation
* Weather MCP integration
* Currency MCP integration
* Weather-aware itinerary generation
* Streamlit interface
* Basic conversation memory

The application is currently functional as a Singapore-focused RAG + MCP travel assistant.