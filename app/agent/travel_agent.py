import asyncio
import re

from langchain_ollama import ChatOllama

from app.agent.intent import detect_intent
from app.agent.state import TravelState
from app.agent.mcp_client import MCPClientManager
from app.agent.context_builder import get_rag_context

class TravelAgent:

    def __init__(self):

        # =====================================================
        # Llama 3.1 8B
        # =====================================================

        self.llm = ChatOllama(
            model="llama3.1:8b",
            temperature=0.2,
        )

        # =====================================================
        # Conversation memory
        # =====================================================

        self.conversation_history = []

    # =========================================================
    # RAG
    # =========================================================

    def get_rag(
        self,
        question: str,
        k: int = 100,
    ) -> dict:

        return get_rag_context(
            question,
            k=k,
        )

    # =========================================================
    # WEATHER MCP
    # =========================================================

    async def get_weather(
        self,
        mcp: MCPClientManager,
        city: str = "Singapore",
        forecast_days: int = 3,
    ) -> str:

        result = await mcp.call_tool(
            "weather",
            "get_weather",
            {
                "city": city,
                "forecast_days": forecast_days,
            },
        )

        output = []

        for content in result.content:

            if hasattr(content, "text"):
                output.append(content.text)

        return "\n".join(output)

    # =========================================================
    # CURRENCY MCP
    # =========================================================

    async def get_currency(
        self,
        mcp: MCPClientManager,
        amount: float,
        from_currency: str,
        to_currency: str,
    ) -> str:

        result = await mcp.call_tool(
            "currency",
            "convert_currency",
            {
                "amount": amount,
                "from_currency": from_currency,
                "to_currency": to_currency,
            },
        )

        output = []

        for content in result.content:

            if hasattr(content, "text"):
                output.append(content.text)

        return "\n".join(output)

    # =========================================================
    # BUILD CONVERSATION HISTORY
    # =========================================================

    def get_history_text(self) -> str:

        if not self.conversation_history:
            return "No previous conversation."

        return "\n".join(
            [
                f"{item['role']}: {item['content']}"
                for item in self.conversation_history[-10:]
            ]
        )

    # =========================================================
    # SOURCE NORMALIZATION
    # =========================================================

    def normalize_sources(
        self,
        sources: list,
    ) -> list:

        """
        Convert retrieved source metadata into unique sources.

        Multiple retrieved chunks can belong to the same Markdown
        document. This prevents duplicate sources in the final
        response.
        """

        unique_sources = []
        seen = set()

        for source in sources:

            if not isinstance(source, dict):
                continue

            title = source.get(
                "title",
                source.get(
                    "filename",
                    source.get(
                        "source",
                        "Unknown source",
                    ),
                ),
            )

            url = source.get(
                "url",
                "",
            )

            key = (
                title,
                url,
            )

            if key in seen:
                continue

            seen.add(key)

            unique_sources.append(
                {
                    "title": title,
                    "url": url,
                }
            )

        return unique_sources

    
    # =========================================================
    # LLM RESPONSE
    # =========================================================
    
    def extract_currency_details(self, question: str) -> dict:
        """
        Extract amount, source currency, and target currency
        from the user's question.

        Examples:
            50000 INR to SGD
            100 USD in SGD
            convert 250 EUR to SGD
        """

        text = question.upper()

        # ---------------------------------------------------------
        # Currency aliases
        # ---------------------------------------------------------

        currency_aliases = {
            "INR": "INR",
            "RUPEE": "INR",
            "RUPEES": "INR",
            "₹": "INR",

            "SGD": "SGD",
            "SINGAPORE DOLLAR": "SGD",
            "SINGAPORE DOLLARS": "SGD",

            "USD": "USD",
            "US DOLLAR": "USD",
            "US DOLLARS": "USD",
            "DOLLAR": "USD",
            "DOLLARS": "USD",
            "$": "USD",

            "EUR": "EUR",
            "EURO": "EUR",
            "EUROS": "EUR",
            "€": "EUR",

            "GBP": "GBP",
            "POUND": "GBP",
            "POUNDS": "GBP",
            "£": "GBP",
        }

        # ---------------------------------------------------------
        # Find amount
        # ---------------------------------------------------------

        amount_match = re.search(
            r"(?:₹|\$|€|£)?\s*(\d+(?:,\d{3})*(?:\.\d+)?)",
            text,
        )

        amount = None

        if amount_match:
            amount = float(
                amount_match.group(1).replace(",", "")
            )

        # ---------------------------------------------------------
        # Find currencies
        # ---------------------------------------------------------

        found_currencies = []

        # Check longer aliases first
        aliases = sorted(
            currency_aliases.keys(),
            key=len,
            reverse=True,
        )

        for alias in aliases:

            pattern = rf"(?<![A-Z]){re.escape(alias)}(?![A-Z])"

            if re.search(pattern, text):

                currency = currency_aliases[alias]

                if currency not in found_currencies:
                    found_currencies.append(currency)

        # ---------------------------------------------------------
        # Determine source and target
        # ---------------------------------------------------------

        from_currency = None
        to_currency = None

        # Example:
        # 50000 INR to SGD
        # 100 USD in SGD
        conversion_match = re.search(
            r"(?:TO|IN)\s+([A-Z]{3})\b",
            text,
        )

        if len(found_currencies) >= 2:

            # Usually first currency = source
            # second currency = destination
            from_currency = found_currencies[0]
            to_currency = found_currencies[1]

        elif len(found_currencies) == 1:

            from_currency = found_currencies[0]

            # Default destination for Singapore travel
            if from_currency != "SGD":
                to_currency = "SGD"

        # ---------------------------------------------------------
        # Defaults
        # ---------------------------------------------------------

        if amount is None:
            amount = 1.0

        if from_currency is None:
            from_currency = "INR"

        if to_currency is None:
            to_currency = "SGD"

        return {
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
        }

    def extract_trip_days(self, question: str) -> int:
        """
        Extract the requested number of itinerary days.

        Examples:
            "3 day trip"       -> 3
            "5 day itinerary"  -> 5
            "plan a 7-day trip" -> 7

        Defaults to 3 days if no duration is specified.
        """

        text = question.lower()

        patterns = [
            r"\b(\d+)\s*[-]?\s*day\b",
            r"\b(\d+)\s*[-]?\s*days\b",
        ]

        for pattern in patterns:

            match = re.search(pattern, text)

            if match:
                days = int(match.group(1))

                # Keep the value within a reasonable range
                return max(1, min(days, 7))

        return 3

    async def generate_answer(
        self,
        state: TravelState,
        trip_days: int = 3
    ) -> str:

        history_text = self.get_history_text()

        # -----------------------------------------------------
        # MCP status
        # -----------------------------------------------------

        weather_section = (
            state.weather_result
            if state.weather_result
            else "Weather MCP was not called."
        )

        currency_section = (
            state.currency_result
            if state.currency_result
            else "Currency MCP was not called."
        )

        # -----------------------------------------------------
        # Source list
        # -----------------------------------------------------

        source_text = ""

        if state.rag_sources:

            source_lines = []

            for source in state.rag_sources:

                title = source.get(
                    "title",
                    "Unknown source",
                )

                url = source.get(
                    "url",
                    "",
                )

                if url:
                    source_lines.append(
                        f"- {title} | {url}"
                    )
                else:
                    source_lines.append(
                        f"- {title}"
                    )

            source_text = "\n".join(
                source_lines
            )

        else:

            source_text = (
                "No Knowledge Base sources were retrieved."
            )

        # -----------------------------------------------------
        # Prompt
        # -----------------------------------------------------

        prompt = f"""
    ```

    You are a factual Singapore travel assistant.

    Your job is to answer the user's question using ONLY the
    information supplied in this prompt.

    Do NOT use your pretrained knowledge to add Singapore-specific
    facts that are absent from the supplied Knowledge Base.

    ============================================================
    USER QUESTION
    =============

    {state.question}
    
    REQUESTED ITINERARY LENGTH
    ==========================

    The user requested a {trip_days}-day itinerary.

    You MUST produce exactly {trip_days} itinerary days.

    Do not reduce the itinerary to three days unless
    the user explicitly requested three days.

    ============================================================
    CONVERSATION HISTORY
    ====================

    {history_text}

    ============================================================
    KNOWLEDGE BASE
    ==============

    The following content was retrieved from the Singapore travel
    Knowledge Base.

    Treat this section as the ONLY authoritative source for
    Singapore destination facts.

    {state.rag_context}

    ============================================================
    RETRIEVED KNOWLEDGE BASE SOURCES
    ================================

    {source_text}

    ============================================================
    WEATHER MCP
    ===========

    {weather_section}

    ============================================================
    CURRENCY MCP
    ============

    {currency_section}

    ============================================================
    GROUNDING RULES
    ===============

    RULE 1 — DESTINATION FACTS

    Every Singapore-specific factual claim must be supported by
    the supplied Knowledge Base.

    This includes:

    * attractions
    * activities
    * neighbourhoods
    * restaurants
    * food
    * culture
    * heritage
    * nature
    * nightlife
    * shopping
    * museums
    * transport
    * itineraries
    * experiences
    * architecture

    Do NOT introduce an attraction merely because you know about it
    from general knowledge.

    If it is not present in the supplied Knowledge Base, do not
    recommend it.

    RULE 2 — RETRIEVED CHUNKS

    The Knowledge Base may contain multiple chunks from the same
    document.

    Do not treat the number of chunks as the number of sources.

    Use the actual source metadata when identifying sources.

    RULE 3 — WEATHER

    If Weather MCP information is supplied, it is the ONLY
    authoritative source for current weather and forecast data.

    Use the exact values supplied by the Weather MCP.

    For forecast information, preserve:

    * date
    * minimum temperature
    * maximum temperature
    * rain probability
    * rainfall

    Do not invent weather descriptions.

    For example, do NOT say:

    * sunny
    * mostly sunny
    * dry
    * heavy rain
    * significant rainfall

    unless that wording is explicitly supported by the MCP result.

    You may say "high rain probability" when the numerical
    probability clearly supports that description.

    RULE 4 — WEATHER-AWARE ITINERARY

    When the user asks for an itinerary adjusted to weather:

    For every day:

    1. Match the itinerary day to the corresponding forecast date.
    2. Examine the actual rain probability.
    3. Prefer activities that are supported by the Knowledge Base
    and are less affected by rain when rain probability is high.
    4. Do not create an outdoor-heavy itinerary when rain
    probability is high if suitable alternatives are available.
    5. If an outdoor activity is included despite high rain
    probability, explicitly label it:

    "Optional if weather improves."

    RULE 5 — INDOOR / OUTDOOR CLASSIFICATION

    Do not assume an activity is indoor or outdoor unless the
    Knowledge Base explicitly supports that classification.

    If the Knowledge Base says that an attraction is a museum,
    gallery, conservatory, shopping location, etc., you may use
    that information only to the extent that the retrieved text
    supports it.

    Do not invent additional physical characteristics.

    RULE 6 — TIMES

    You may suggest planning times such as:

    9:00 AM
    11:00 AM
    2:00 PM
    5:00 PM

    These are AI-generated itinerary suggestions.

    They are NOT official opening hours.

    Never claim that a location opens or closes at a particular
    time unless that information is explicitly supplied.

    RULE 7 — CURRENCY

    If Currency MCP was not called, do not mention a currency
    conversion as if one was performed.

    If Currency MCP was called, use its exact result.

    Do not calculate your own exchange rate.

    RULE 8 — MISSING INFORMATION

    If the Knowledge Base does not contain enough information,
    say:

    "The current Knowledge Base does not contain enough information
    to fully answer this part."

    Do not fill the missing information from general knowledge.

    RULE 9 — SOURCES

    Only list Knowledge Base sources that were actually retrieved.

    Do not invent sources.

    Do not claim that every source in the corpus was used.

    RULE 10 — RECOMMENDATIONS

    The following distinction is mandatory:

    Knowledge Base facts:
    Facts explicitly supported by retrieved documents.

    MCP information:
    Current information returned by MCP tools.

    AI-generated recommendations:
    The itinerary structure, grouping, sequencing, prioritization,
    and weather-based adjustments generated by you.

    An itinerary recommendation is an AI-generated recommendation
    even when every activity used in it comes from the Knowledge Base.

    RULE 11 — NO FALSE CLAIMS

    Never say:

    "All attractions are supported by the Knowledge Base"

    unless you have verified every attraction individually.

    Instead, only recommend activities that appear in the supplied
    context.

    RULE 12 — NO UNUSED MCP CLAIMS

    If Weather MCP was not called, do not say that Weather MCP
    provided information.

    If Currency MCP was not called, do not say that Currency MCP
    provided information.

    ============================================================
    ITINERARY LOGIC
    ===============

    If the user requests a three-day itinerary and weather data is
    available:

    Day 1 must correspond to the first forecast date.

    Day 2 must correspond to the second forecast date.

    Day 3 must correspond to the third forecast date.

    Use the actual rain probabilities.

    Example:

    If:

    Day 1 = 70%
    Day 2 = 83%
    Day 3 = 85%

    then do NOT describe Day 1 or Day 3 as having low rain risk.

    Do NOT say:

    "mostly sunny"

    unless the MCP explicitly says that.

    The numerical forecast takes priority.

    ============================================================
    RESPONSE FORMAT
    ===============

    For a normal Singapore travel question, answer naturally.

    For an itinerary request:

    ## Trip Plan

    You MUST create exactly {trip_days} itinerary days.

    For each day, use this structure:

    ### Day N — [Theme]

    * Morning:
    * Afternoon:
    * Evening:

    Continue sequentially until exactly Day {trip_days}.

    For example, if the requested itinerary length is 5 days,
    the response MUST contain:

    ### Day 1
    ### Day 2
    ### Day 3
    ### Day 4
    ### Day 5

    Do NOT stop after Day 3.

    Do NOT add extra days beyond Day {trip_days}.

    ## Weather Considerations

    Explain how the Weather MCP forecast affected the plan.

    If weather data is available, include a table containing
    only the forecast days supplied by the Weather MCP:

    | Day | Date | Rain Probability | Forecast Rainfall | Planning Approach |
    | --- | ---- | ---------------- | ----------------- | ----------------- |

    Use exact numerical values from MCP.

    ## Knowledge Base Sources

    List only the retrieved Knowledge Base sources actually used.

    ## MCP Information

    List only MCP tools that were actually called.

    ## Recommendation Type

    * Knowledge Base facts:
    * MCP information:
    * AI-generated recommendations:

    ============================================================
    FINAL VALIDATION
    ================

    Before returning the answer, silently verify:

    1. Every Singapore-specific attraction is in the supplied KB.
    2. Every weather number matches Weather MCP exactly.
    3. Every forecast date matches MCP exactly.
    4. No unsupported attraction was introduced.
    5. No unsupported opening hours were introduced.
    6. No unsupported prices were introduced.
    7. No unsupported transport schedules were introduced.
    8. Outdoor activities on high-rain days are clearly weather-dependent.
    9. Sources listed were actually retrieved.
    10. Unused MCP tools are not claimed as sources.
    11. AI-generated itinerary recommendations are explicitly
        identified.
    12. Do not claim that AI-generated recommendations are
        "Knowledge Base facts."

    Now answer the user.
    """

        response = await self.llm.ainvoke(
            prompt
        )

        return (
            response.content
            if hasattr(response, "content")
            else str(response)
        )

    # =========================================================
    # MAIN AGENT METHOD
    # =========================================================

    async def ask(
        self,
        question: str,
    ) -> dict:

        print("\n" + "=" * 60)
        print("SINGAPORE TRAVEL ASSISTANT")
        print("=" * 60)

        # =====================================================
        # 1. INTENT
        # =====================================================

        print(
            "\n[1/5] Detecting intent..."
        )

        intent = detect_intent(
            question
        )

        print(
            f"[2/5] Intent detected: "
            f"{intent.intent_type.value}"
        )

        # =====================================================
        # 2. STATE
        # =====================================================

        state = TravelState(
            question=question,
            intent=intent,
            conversation_history=(
                self.conversation_history.copy()
            ),
        )
        
        trip_days = self.extract_trip_days(question)

        print(
            f"[INFO] Trip duration detected: {trip_days} day(s)"
        )

        # =====================================================
        # 3. RAG
        # =====================================================

        if intent.needs_rag:

            print(
                "[3/5] Searching Singapore knowledge base..."
            )

            rag_result = self.get_rag(
                question,
                k=100,
            )

            state.rag_context = (
                rag_result.get(
                    "context",
                    "",
                )
            )

            raw_sources = (
                rag_result.get(
                    "sources",
                    [],
                )
            )

            state.rag_sources = (
                self.normalize_sources(
                    raw_sources
                )
            )

            print(
                f"[3/5] Retrieved "
                f"{len(raw_sources)} chunk/source entries."
            )

            print(
                f"[3/5] Unique sources: "
                f"{len(state.rag_sources)}."
            )

        else:

            print(
                "[3/5] RAG not required."
            )

        # =====================================================
        # 4. MCP
        # =====================================================

        if (
            intent.needs_weather
            or intent.needs_currency
        ):

            print(
                "[4/5] Connecting to MCP servers..."
            )

            async with MCPClientManager() as mcp:

                # -------------------------------------------------
                # WEATHER
                # -------------------------------------------------

                if intent.needs_weather:

                    print(
                        "[4/5] Calling Weather MCP..."
                    )

                    try:

                        state.weather_result = (
                            await self.get_weather(
                                mcp,
                                city="Singapore",
                                forecast_days=trip_days,
                            )
                        )

                        print(
                            "[4/5] Weather MCP response received."
                        )

                    except Exception as exc:

                        state.weather_result = (
                            "Weather MCP failed to retrieve "
                            f"current information: {exc}"
                        )

                        print(
                            "[4/5] Weather MCP failed."
                        )

                # -------------------------------------------------
                # CURRENCY
                # -------------------------------------------------

                if intent.needs_currency:

                    print(
                        "[4/5] Calling Currency MCP..."
                    )

                    # try:

                    #     # -------------------------------------------------
                    #     # Phase 1 test conversion
                    #     # -------------------------------------------------
                    #     #
                    #     # Dynamic extraction will be implemented later.
                    #     #

                    #     state.currency_result = (
                    #         await self.get_currency(
                    #             mcp,
                    #             amount=50000,
                    #             from_currency="INR",
                    #             to_currency="SGD",
                    #         )
                    #     )

                    #     print(
                    #         "[4/5] Currency MCP response received."
                    #     )

                    # except Exception as exc:

                    #     state.currency_result = (
                    #         "Currency MCP failed to retrieve "
                    #         f"exchange information: {exc}"
                    #     )

                    #     print(
                    #         "[4/5] Currency MCP failed."
                    #     )
                    
                    try:

                        # ---------------------------------------------------------
                        # Extract currency details from user question
                        # ---------------------------------------------------------

                        currency_details = self.extract_currency_details(
                            question
                        )

                        amount = currency_details["amount"]
                        from_currency = currency_details["from_currency"]
                        to_currency = currency_details["to_currency"]

                        print(
                            "[4/5] Currency request: "
                            f"{amount} {from_currency} -> {to_currency}"
                        )

                        # ---------------------------------------------------------
                        # Call Currency MCP dynamically
                        # ---------------------------------------------------------

                        state.currency_result = (
                            await self.get_currency(
                                mcp,
                                amount=amount,
                                from_currency=from_currency,
                                to_currency=to_currency,
                            )
                        )

                        print(
                            "[4/5] Currency MCP response received."
                        )

                    except Exception as exc:

                        state.currency_result = (
                            "Currency MCP failed to retrieve "
                            f"exchange information: {exc}"
                        )

                        print(
                            "[4/5] Currency MCP failed."
                        )

        else:

            print(
                "[4/5] No MCP tools required."
            )

        # =====================================================
        # 5. GENERATION
        # =====================================================

        print(
            "[5/5] Generating response with "
            "Llama 3.1 8B..."
        )

        state.answer = await self.generate_answer(
            state,
            trip_days=trip_days
        )

        print(
            "[5/5] Response generated."
        )

        # =====================================================
        # MEMORY
        # =====================================================

        self.conversation_history.append(
            {
                "role": "user",
                "content": question,
            }
        )

        self.conversation_history.append(
            {
                "role": "assistant",
                "content": state.answer,
            }
        )

        # Keep recent conversation only.
        self.conversation_history = (
            self.conversation_history[-10:]
        )

        # =====================================================
        # RETURN
        # =====================================================

        return {
            "answer": state.answer,
            "intent": intent,
            "sources": state.rag_sources,
            "weather": state.weather_result,
            "currency": state.currency_result,
        }

# =============================================================

# COMMAND-LINE TEST

# =============================================================

async def main():

    agent = TravelAgent()

    print("=" * 60)
    print("SINGAPORE TRAVEL ASSISTANT")
    print("=" * 60)

    while True:

        question = input(
            "\nEnter your travel question "
            "(or type 'exit' to quit): "
        ).strip()

        if not question:
            continue

        if question.lower() in {
            "exit",
            "quit",
        }:

            print(
                "\nGoodbye!"
            )

            break

        try:

            result = await agent.ask(
                question
            )

            print(
                "\n" + "=" * 60
            )

            print(
                "FINAL ANSWER"
            )

            print(
                "=" * 60
            )

            print(
                result["answer"]
            )

            print(
                "\n" + "=" * 60
            )

            print(
                "SOURCES"
            )

            print(
                "=" * 60
            )

            if result["sources"]:

                for source in result["sources"]:

                    print(
                        f"- {source['title']}"
                    )

                    if source.get("url"):

                        print(
                            f"  {source['url']}"
                        )

            else:

                print(
                    "No Knowledge Base sources used."
                )

        except Exception as exc:

            print(
                "\n" + "=" * 60
            )

            print(
                "ERROR"
            )

            print(
                "=" * 60
            )

            print(
                f"{type(exc).__name__}: {exc}"
            )

if __name__ == "__main__":

    asyncio.run(main())
