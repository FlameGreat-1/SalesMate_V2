from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class ConversationStage(str, Enum):
    GREETING = "greeting"
    DISCOVERY = "discovery"
    RECOMMENDATION = "recommendation"
    COMPARISON = "comparison"
    OBJECTION_HANDLING = "objection_handling"
    CLOSING = "closing"


class UserIntent(str, Enum):
    GREETING = "greeting"
    BROWSING = "browsing"
    REQUESTING_RECOMMENDATION = "requesting_recommendation"
    COMPARING_PRODUCTS = "comparing_products"
    ASKING_QUESTION = "asking_question"
    READY_TO_BUY = "ready_to_buy"
    OBJECTION = "objection"
    UNKNOWN = "unknown"


class StockStatus(str, Enum):
    IN_STOCK = "in_stock"
    OUT_OF_STOCK = "out_of_stock"
    LOW_STOCK = "low_stock"
    DISCONTINUED = "discontinued"
    PRE_ORDER = "pre_order"


class PriceTier(str, Enum):
    BUDGET = "budget"
    MID_RANGE = "mid_range"
    PREMIUM = "premium"
    LUXURY = "luxury"


class LLMProvider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
