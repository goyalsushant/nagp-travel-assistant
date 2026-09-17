from enum import Enum
from dataclasses import dataclass


class IntentType(str, Enum):

    RAG = "RAG"
    WEATHER = "WEATHER"
    CURRENCY = "CURRENCY"
    RAG_WEATHER = "RAG + WEATHER"
    RAG_CURRENCY = "RAG + CURRENCY"
    RAG_WEATHER_CURRENCY = "RAG + WEATHER + CURRENCY"
    UNKNOWN = "UNKNOWN"


@dataclass
class Intent:

    intent_type: IntentType
    needs_rag: bool = False
    needs_weather: bool = False
    needs_currency: bool = False


def detect_intent(question: str) -> Intent:


    """
    Deterministic rule-based intent detection.

    RAG:
        Used for Singapore destination/travel knowledge.

    Weather:
        Used when the user asks about current/future weather
        or explicitly asks for weather-aware planning.

    Currency:
        Used when the user asks about currency, exchange rates,
        conversion, budgets, or supported currencies.
    """

    text = question.lower()

    # =========================================================
    # WEATHER
    # =========================================================

    weather_keywords = [
        "weather",
        "forecast",
        "rain",
        "raining",
        "rainfall",
        "precipitation",
        "temperature",
        "temperatures",
        "humidity",
        "sunny",
        "storm",
        "storms",
        "thunderstorm",
        "thunderstorms",
        "climate",
    ]

    needs_weather = any(
        keyword in text
        for keyword in weather_keywords
    )

    # =========================================================
    # CURRENCY
    # =========================================================

    currency_keywords = [
        "currency",
        "convert",
        "conversion",
        "exchange rate",
        "exchange rates",
        "exchange",
        "inr",
        "sgd",
        "usd",
        "eur",
        "gbp",
        "dollar",
        "dollars",
        "rupee",
        "rupees",
        "budget",
        "cost in",
    ]

    needs_currency = any(
        keyword in text
        for keyword in currency_keywords
    )

    # =========================================================
    # RAG / SINGAPORE TRAVEL KNOWLEDGE
    # =========================================================

    travel_keywords = [
        # General travel
        "singapore",
        "trip",
        "travel",
        "travelling",
        "traveling",
        "tourist",
        "tourism",
        "holiday",
        "vacation",
        "plan",
        "planning",
        "itinerary",
        "itineraries",
        "itinerar",
        # Attractions / activities
        "attraction",
        "attractions",
        "place",
        "places",
        "visit",
        "visiting",
        "things to do",
        "thing to do",
        "activity",
        "activities",
        "experience",
        "experiences",
        "sightseeing",
        "must-visit",
        "must visit",
        # Categories in the knowledge base
        "nature",
        "city in nature",
        "culture",
        "cultural",
        "heritage",
        "neighbourhood",
        "neighborhood",
        "food",
        "restaurant",
        "restaurants",
        "dining",
        "shopping",
        "nightlife",
        "night life",
        "after dark",
        "museum",
        "museums",
        "gallery",
        "galleries",
        "family",
        "children",
        "kids",
        "indoor",
        "outdoor",
        "iconic",
        "architecture",
        # Transport / practical travel
        "transport",
        "transportation",
        "getting around",
        "mrt",
        "travel tips",
        "travel information",
        # Recommendation language
        "suggest",
        "suggestion",
        "suggestions",
        "recommend",
        "recommendation",
        "recommendations",
        "best",
        "where should",
        "what should",
    ]

    needs_rag = any(
        keyword in text
        for keyword in travel_keywords
    )

    # =========================================================
    # DETERMINE COMBINED INTENT
    # =========================================================

    if (
        needs_rag
        and needs_weather
        and needs_currency
    ):
        intent_type = IntentType.RAG_WEATHER_CURRENCY

    elif needs_rag and needs_weather:
        intent_type = IntentType.RAG_WEATHER

    elif needs_rag and needs_currency:
        intent_type = IntentType.RAG_CURRENCY

    elif needs_weather:
        intent_type = IntentType.WEATHER

    elif needs_currency:
        intent_type = IntentType.CURRENCY

    elif needs_rag:
        intent_type = IntentType.RAG

    else:
        intent_type = IntentType.UNKNOWN

    return Intent(
        intent_type=intent_type,
        needs_rag=needs_rag,
        needs_weather=needs_weather,
        needs_currency=needs_currency,
    )
