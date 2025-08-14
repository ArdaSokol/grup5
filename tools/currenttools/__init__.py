from .customer_details import get_customer_details_tool
from .card_summary import get_card_summary_tool

CURRENT_TOOLS = [
    get_customer_details_tool,
    get_card_summary_tool,
]

__all__ = [
    "get_customer_details_tool",
    "get_card_summary_tool",
    "CURRENT_TOOLS",
]