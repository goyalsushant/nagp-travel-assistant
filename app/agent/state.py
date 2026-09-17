from dataclasses import dataclass, field
from typing import Any


@dataclass
class TravelState:
    question: str

    intent: Any = None

    rag_context: str = ""
    rag_sources: list[dict] = field(default_factory=list)

    weather_result: str = ""
    currency_result: str = ""

    answer: str = ""

    conversation_history: list[dict] = field(default_factory=list)