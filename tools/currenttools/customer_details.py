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

FORTUNA_ACCOUNT_URL = (
    "http://devfortunav3.intertech.com.tr/Intertech.Fortuna.WebApi.Services/api/fortuna/GetAccountDetail"
)

def _header() -> Dict[str, Any]:
    return {
        "AppKey": FORTUNA_APP_KEY,
        "Channel": "STARTECH",
        "ChannelSessionId": str(uuid.uuid4()),
        "ChannelRequestId": str(uuid.uuid4()),
        "SessionLanguage": "TR",
    }

GET_CUSTOMER_DETAILS_DESC = """
[Tool: get_customer_details]
Ne zaman kullanılır?
- Kullanıcı müşteri numarasına göre hesap/IBAN/bakiye/hareket bilgisi istiyorsa.
"""

def _get_customer_details_impl(customer_number: int, account_suffix: int = 351, branch_code: int = 9142):
    payload = {
        "Header": _header(),
        "Parameters": [{
            "AccountInfo": {
                "AccountSuffix": int(account_suffix),
                "BranchCode": int(branch_code),
                "CustomerNo": int(customer_number),
            },
            "IBANNo": "",
        }],
    }
    resp = requests.post(
        FORTUNA_ACCOUNT_URL,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=HTTP_TIMEOUT
    )
    resp.raise_for_status()
    return resp.json()

@tool(name="get_customer_details", description=GET_CUSTOMER_DETAILS_DESC)
def get_customer_details_tool(customer_number: int, account_suffix: int = 351, branch_code: int = 9142):
    return _get_customer_details_impl(customer_number, account_suffix, branch_code)
