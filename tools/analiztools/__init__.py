# tools/analiztools/__init__.py
from .risk_score import risk_score_tool
from .yahoo_fx_tool import yahoo_fx_rates

CURRENT_ANALYSIS_TOOLS = [
    risk_score_tool,
    yahoo_fx_rates
]

__all__ = [
    "risk_score_tool",
    "yahoo_fx_rates"
    "CURRENT_ANALYSIS_TOOLS",
]
