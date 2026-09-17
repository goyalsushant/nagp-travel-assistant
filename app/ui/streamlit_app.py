import asyncio
import sys
import threading
from pathlib import Path

import streamlit as st


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.agent.travel_agent import TravelAgent


# ============================================================
# RUN ASYNC CODE SAFELY FROM STREAMLIT
# ============================================================

def run_async(coro):
    """
    Run an async coroutine in a dedicated thread.

    This avoids event-loop conflicts caused by repeatedly
    calling asyncio.run() during Streamlit reruns.
    """

    result = {}
    error = {}

    def runner():

        try:

            loop = asyncio.new_event_loop()

            asyncio.set_event_loop(loop)

            try:

                result["value"] = loop.run_until_complete(coro)

            finally:

                loop.close()

        except Exception as exc:

            error["value"] = exc

    thread = threading.Thread(
        target=runner
    )

    thread.start()

    thread.join()

    if "value" in error:

        raise error["value"]

    return result.get("value")


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Singapore Travel Assistant",
    page_icon="✈️",
    layout="wide",
)


# ============================================================
# SESSION STATE
# ============================================================

if "agent" not in st.session_state:

    st.session_state.agent = TravelAgent()


if "messages" not in st.session_state:

    st.session_state.messages = []



# ============================================================
# HEADER
# ============================================================

st.title("✈️ Singapore Travel Assistant")

st.markdown(
    """
Plan your Singapore trip using:

- 📚 Singapore travel knowledge base
- 🌦️ Current weather from Weather MCP
- 💱 Currency conversion from Currency MCP
- 🤖 Llama 3.1 8B for response generation
"""
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("Travel Assistant")

    st.markdown(
        """
### Available capabilities

**Knowledge Base**
- Attractions
- Activities
- Culture
- Food
- Neighbourhoods
- Nature
- Nightlife
- Shopping
- Transport
- Itineraries

**MCP Tools**
- Weather
- Currency
"""
    )

    st.divider()

    if st.button("🗑️ Clear Conversation"):

        st.session_state.messages = []
        st.session_state.agent = TravelAgent()

        st.rerun()


# ============================================================
# DISPLAY PREVIOUS MESSAGES
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        # ----------------------------------------------------
        # Display metadata for assistant messages
        # ----------------------------------------------------

        if message["role"] == "assistant":

            result = message.get("result")

            if result:

                sources = result.get("sources", [])

                if sources:

                    with st.expander("📚 Knowledge Base Sources"):

                        seen = set()

                        for source in sources:

                            title = source.get(
                                "title",
                                "Unknown source",
                            )

                            url = source.get(
                                "url",
                                "",
                            )

                            key = (title, url)

                            if key in seen:
                                continue

                            seen.add(key)

                            st.markdown(
                                f"**{title}**"
                            )

                            if url:
                                st.markdown(
                                    url
                                )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask me about travelling to Singapore..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    # --------------------------------------------------------
    # Display user message
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    # --------------------------------------------------------
    # Generate assistant response
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "Planning your Singapore trip..."
        ):

            try:

                result = run_async(
                    # st.session_state.agent.ask(
                    #     question
                    # )
                    TravelAgent().ask(question)
                )

                answer = result.get(
                    "answer",
                    "I was unable to generate a response.",
                )

                st.markdown(answer)

                # ------------------------------------------------
                # Sources
                # ------------------------------------------------

                sources = result.get(
                    "sources",
                    [],
                )

                if sources:

                    with st.expander(
                        "📚 Knowledge Base Sources"
                    ):

                        seen = set()

                        for source in sources:

                            title = source.get(
                                "title",
                                "Unknown source",
                            )

                            url = source.get(
                                "url",
                                "",
                            )

                            key = (title, url)

                            if key in seen:
                                continue

                            seen.add(key)

                            st.markdown(
                                f"**{title}**"
                            )

                            if url:
                                st.markdown(
                                    url
                                )

                # ------------------------------------------------
                # MCP information
                # ------------------------------------------------

                weather = result.get(
                    "weather",
                    "",
                )

                currency = result.get(
                    "currency",
                    "",
                )

                if weather:

                    with st.expander(
                        "🌦️ Weather MCP"
                    ):

                        st.text(weather)

                if currency:

                    with st.expander(
                        "💱 Currency MCP"
                    ):

                        st.text(currency)

                # ------------------------------------------------
                # Store assistant response
                # ------------------------------------------------

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "result": result,
                    }
                )

            except Exception as exc:

                error_message = (
                    "Sorry, something went wrong while "
                    "processing your request.\n\n"
                    f"`{type(exc).__name__}: {exc}`"
                )

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )