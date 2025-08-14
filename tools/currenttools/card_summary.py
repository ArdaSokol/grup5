import os
import uuid
from typing import Any, Dict
import requests
from agno.tools import tool

HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "60"))
FORTUNA_APP_KEY = os.getenv(
    "FORTUNA_APP_KEY",
    "KrroGJz9ndy5FQ0BaWvwlmrCq1tFKT2HEbbybyRxuRBAbZL6zD"
)

FORTUNA_CARD_URL = (
    "https://devfortunav3.intertech.com.tr/Intertech.Fortuna.WebApi.Services/api/fortuna/GetCardSummaryInfo"
)

def _header() -> Dict[str, Any]:
    return {
        "AppKey": FORTUNA_APP_KEY,
        "Channel": "STARTECH",
        "ChannelSessionId": str(uuid.uuid4()),
        "ChannelRequestId": str(uuid.uuid4()),
        "SessionLanguage": "TR",
    }

GET_CARD_SUMMARY_DESC = """
[Tool: get_card_summary]
Ne zaman kullanılır?
- Kullanıcı kart numarasına göre kart özeti (limit, bakiye, borç vb.) istiyorsa.
"""

def _get_card_summary_impl(card_number: int):
    payload = {
        "Header": _header(),
        "Parameters": [{
            "CardNo": int(card_number)
        }],
    }
    resp = requests.post(
        FORTUNA_CARD_URL,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=HTTP_TIMEOUT
    )
    resp.raise_for_status()
    return resp.json()

@tool(name="get_card_summary", description=GET_CARD_SUMMARY_DESC)
def get_card_summary_tool(card_number: int):
    return _get_card_summary_impl(card_number)
