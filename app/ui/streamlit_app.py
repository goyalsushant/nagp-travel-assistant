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
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL
    ======================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 90% 5%,
                rgba(14, 165, 233, 0.08),
                transparent 25%
            ),
            radial-gradient(
                circle at 5% 10%,
                rgba(20, 184, 166, 0.08),
                transparent 25%
            );
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }


    /* ========================================================
       HERO
    ======================================================== */

    .hero {
        padding: 2.2rem 2.4rem;
        border-radius: 24px;

        background:
            linear-gradient(
                135deg,
                #0f766e 0%,
                #0891b2 55%,
                #2563eb 100%
            );

        color: white;

        margin-bottom: 1.6rem;

        box-shadow:
            0 15px 40px rgba(15, 118, 110, 0.20);
    }

    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        margin-bottom: 0.4rem;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        line-height: 1.6;
        opacity: 0.92;
        max-width: 800px;
    }


    /* ========================================================
       CAPABILITY CARDS
    ======================================================== */

    .capability-card {
        background: rgba(255, 255, 255, 0.78);

        border: 1px solid rgba(148, 163, 184, 0.22);

        border-radius: 18px;

        padding: 1.25rem;

        min-height: 155px;

        box-shadow:
            0 8px 25px rgba(15, 23, 42, 0.05);
    }

    .capability-icon {
        font-size: 1.8rem;
        margin-bottom: 0.45rem;
    }

    .capability-title {
        font-size: 1rem;
        font-weight: 750;
        color: #0f172a;
        margin-bottom: 0.35rem;
    }

    .capability-text {
        color: #64748b;
        font-size: 0.87rem;
        line-height: 1.5;
    }


    /* ========================================================
       BADGES
    ======================================================== */

    .badge {
        display: inline-block;

        padding: 0.32rem 0.7rem;

        border-radius: 999px;

        font-size: 0.76rem;

        font-weight: 700;

        margin-right: 0.35rem;

        margin-bottom: 0.35rem;
    }

    .badge-green {
        background: #dcfce7;
        color: #166534;
    }

    .badge-blue {
        background: #dbeafe;
        color: #1e40af;
    }

    .badge-orange {
        background: #ffedd5;
        color: #9a3412;
    }

    .badge-purple {
        background: #f3e8ff;
        color: #6b21a8;
    }


    /* ========================================================
       SOURCE CARDS
    ======================================================== */

    .source-card {
        padding: 0.8rem 0.95rem;

        margin-bottom: 0.65rem;

        border-radius: 12px;

        background: #f8fafc;

        border: 1px solid #e2e8f0;
    }

    .source-title {
        font-weight: 700;

        font-size: 0.9rem;

        color: #0f172a;

        margin-bottom: 0.2rem;
    }

    .source-url {
        font-size: 0.76rem;

        color: #64748b;

        word-break: break-all;
    }


    /* ========================================================
       SIDEBAR
    ======================================================== */

    [data-testid="stSidebar"] {
        border-right:
            1px solid rgba(148, 163, 184, 0.18);
    }

    .sidebar-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0f172a;
    }

    .sidebar-subtitle {
        color: #64748b;
        font-size: 0.85rem;
        line-height: 1.5;
        margin-top: 0.2rem;
    }


    /* ========================================================
       CHAT
    ======================================================== */

    [data-testid="stChatMessage"] {
        border-radius: 18px;
    }

    [data-testid="stChatMessage"] p {
        line-height: 1.65;
    }


    /* ========================================================
       EMPTY STATE
    ======================================================== */

    .empty-state {
        text-align: center;

        padding: 2.5rem 1rem;

        color: #64748b;
    }

    .empty-icon {
        font-size: 3rem;
        margin-bottom: 0.6rem;
    }

    .empty-title {
        font-size: 1.3rem;
        font-weight: 750;
        color: #0f172a;
    }


    /* ========================================================
       FOOTER
    ======================================================== */

    .footer {
        text-align: center;

        color: #94a3b8;

        font-size: 0.76rem;

        margin-top: 3rem;

        padding-top: 1rem;

        border-top:
            1px solid #e2e8f0;
    }
    
    .footer { position: fixed; bottom: 0; left: 21rem; right: 0; text-align: center; color: #94a3b8; font-size: 0.76rem; padding: 0.65rem 1rem; background: rgba(255, 255, 255, 0.92); border-top: 1px solid #e2e8f0; backdrop-filter: blur(8px); z-index: 999; }

section[data-testid="stSidebar"][aria-expanded="false"] ~ div .footer { left: 0; }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "agent" not in st.session_state:

    st.session_state.agent = TravelAgent()


if "messages" not in st.session_state:

    st.session_state.messages = []



# # ============================================================
# # HEADER
# # ============================================================

# st.title("✈️ Singapore Travel Assistant")

# st.markdown(
#     """
# Plan your Singapore trip using:

# - 📚 Singapore travel knowledge base
# - 🌦️ Current weather from Weather MCP
# - 💱 Currency conversion from Currency MCP
# - 🤖 Llama 3.1 8B for response generation
# """
# )

# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">
            🌴 Singapore Travel Assistant
        </div>
        <div class="hero-subtitle">
            Plan smarter Singapore trips using a grounded
            travel knowledge base, Weather MCP, Currency MCP,
            and Llama 3.1 8B.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)



# ============================================================
# SIDEBAR
# ============================================================

# with st.sidebar:

#     st.header("Travel Assistant")

#     st.markdown(
#         """
# ### Available capabilities

# **Knowledge Base**
# - Attractions
# - Activities
# - Culture
# - Food
# - Neighbourhoods
# - Nature
# - Nightlife
# - Shopping
# - Transport
# - Itineraries

# **MCP Tools**
# - Weather
# - Currency
# """
#     )

#     st.divider()

#     if st.button("🗑️ Clear Conversation"):

#         st.session_state.messages = []
#         st.session_state.agent = TravelAgent()

#         st.rerun()

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-title">
            🌴 Travel Assistant
        </div>

        <div class="sidebar-subtitle">
            Your Singapore trip planning companion.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # --------------------------------------------------------
    # AI SYSTEM
    # --------------------------------------------------------

    st.markdown("### 🤖 AI System")

    st.markdown(
        """
        <span class="badge badge-purple">
            Llama 3.1 8B
        </span>

        <span class="badge badge-blue">
            RAG
        </span>

        <span class="badge badge-green">
            MCP
        </span>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # --------------------------------------------------------
    # KNOWLEDGE BASE
    # --------------------------------------------------------

    st.markdown("### 📚 Knowledge Base")

    st.markdown(
        """
        - 🌿 Nature & outdoor
        - 🏛️ Culture & heritage
        - 🍜 Food & dining
        - 👨‍👩‍👧 Family activities
        - 🏙️ Iconic architecture
        - 🏘️ Neighbourhoods
        - 🌙 Nightlife
        - 🛍️ Shopping
        - 🖼️ Museums & galleries
        - 🗺️ Itineraries
        - ✨ Unique experiences
        """
    )

    st.divider()

    # --------------------------------------------------------
    # MCP
    # --------------------------------------------------------

    st.markdown("### 🔌 MCP Tools")

    st.markdown(
        """
        <span class="badge badge-green">
            🌦️ Weather
        </span>

        <span class="badge badge-orange">
            💱 Currency
        </span>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # --------------------------------------------------------
    # CLEAR CHAT
    # --------------------------------------------------------

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True,
    ):

        st.session_state.messages = []

        st.session_state.agent = TravelAgent()

        st.session_state.pending_question = None

        st.rerun()


# ============================================================
# EMPTY STATE / CAPABILITIES
# ============================================================

if not st.session_state.messages:

    st.markdown("### What can I help you with?")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            """
            <div class="capability-card">
                <div class="capability-icon">
                    🗺️
                </div>
                <div class="capability-title">
                    Trip Planning
                </div>
                <div class="capability-text">
                    Build Singapore itineraries based
                    on your trip duration and interests.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            """
            <div class="capability-card">
                <div class="capability-icon">
                    🌦️
                </div>
                <div class="capability-title">
                    Weather
                </div>
                <div class="capability-text">
                    Get current conditions and forecasts
                    through the Weather MCP.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:

        st.markdown(
            """
            <div class="capability-card">
                <div class="capability-icon">
                    💱
                </div>
                <div class="capability-title">
                    Currency
                </div>
                <div class="capability-text">
                    Convert currencies using the
                    Currency MCP.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:

        st.markdown(
            """
            <div class="capability-card">
                <div class="capability-icon">
                    📚
                </div>
                <div class="capability-title">
                    Grounded Answers
                </div>
                <div class="capability-text">
                    Singapore destination information
                    is grounded in retrieved knowledge.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("")

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
                
# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        Singapore Travel Assistant
        · RAG + MCP + Llama 3.1 8B
    </div>
    """,
    unsafe_allow_html=True,
)