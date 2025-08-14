# app_tools/current_tools.py
import os
import uuid
from typing import Any, Dict, List

import requests
from agno.tools import tool

HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "60"))
FORTUNA_APP_KEY = os.getenv("FORTUNA_APP_KEY", "KrroGJz9ndy5FQ0BaWvwlmrCq1tFKT2HEbbybyRxuRBAbZL6zD")

# --- Endpoints ---
FORTUNA_ACCOUNT_URL = "http://devfortunav3.intertech.com.tr/Intertech.Fortuna.WebApi.Services/api/fortuna/GetAccountDetail"
FORTUNA_CARD_SUMMARY_URL = "https://devfortunav3.intertech.com.tr/Intertech.Fortuna.WebApi.Services/api/fortuna/GetCardSummaryInfo"


# --- Shared header builder ---
def _header() -> Dict[str, Any]:
    return {
        "AppKey": FORTUNA_APP_KEY,
        "Channel": "STARTECH",
        "ChannelSessionId": str(uuid.uuid4()),
        "ChannelRequestId": str(uuid.uuid4()),
        "SessionLanguage": "TR",
    }


# ========= Tool 1: get_customer_details =========

GET_CUSTOMER_DETAILS_DESC = """
[Tool: get_customer_details]

NE ZAMAN KULLANILIR?
- Kullanıcı müşteri numarasına göre hesap/IBAN/bakiye/hareket bilgisi istiyorsa.
- Metindeki 6–10 haneli SADECE RAKAM içeren diziyi müşteri no olarak al.

NASIL KULLANILIR?
- 'customer_number' alanını metinden çıkar.
- 'account_suffix' ve 'branch_code' verilmemişse varsayılanları kullan (351 ve 9142).

DİKKAT/KAÇIN:
- IBAN (TR...) ya da kart numarasını müşteri numarası sanma.
- Birden fazla aday varsa en olası olanı seç; eşit belirsizlikte KISA bir netleştirme sor.
- Tool çıktısını direk kullanıcıya dökme; özetleme asistanda yapılır.
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
    resp = requests.post(FORTUNA_ACCOUNT_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=HTTP_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


@tool(
    name="get_customer_details",
    description=GET_CUSTOMER_DETAILS_DESC
)
def get_customer_details_tool(customer_number: int, account_suffix: int = 351, branch_code: int = 9142):
    return _get_customer_details_impl(customer_number, account_suffix, branch_code)


def get_customer_details(customer_number: int, account_suffix: int = 351, branch_code: int = 9142) -> Dict[str, Any]:
    
    return _get_customer_details_impl(customer_number, account_suffix, branch_code)


# ========= Tool 2: get_card_summary_info =========

GET_CARD_SUMMARY_INFO_DESC = """
[Tool: get_card_summary_info]

NE ZAMAN KULLANILIR?
- Kullanıcı kart özeti / kart bilgileri istiyorsa ve kart numarası sağlıyorsa.
- Metindeki 14–19 haneli SADECE RAKAM içeren diziyi kart numarası olarak al (ör: 16 hane).

NASIL KULLANILIR?
- 'card_no' parametresini metinden çıkarıp gönder.
- Yalnızca rakamları kullan; boşluk veya tireleri kaldır.
- Emin değilsen (birden fazla 16 haneli sayı vb.), KISA bir netleştirme sor.

DİKKAT/KAÇIN:
- Müşteri numarasını (genelde 6–10 hane) kart numarası sanma.
- IBAN (TR...) kart numarası değildir.
- Tool çıktısını doğrudan gösterme; asistanda kısa özetle.
-özetlerken json vermeden yap.
"""


def _get_card_summary_info_impl(card_no: int):
    payload = {
        "Header": _header(),
        "Parameters": [{
            "CardNo": int(card_no)
        }],
    }
    resp = requests.post(FORTUNA_CARD_SUMMARY_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=HTTP_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


@tool(
    name="get_card_summary_info",
    description=GET_CARD_SUMMARY_INFO_DESC
)
def get_card_summary_info_tool(card_no: int):
    return _get_card_summary_info_impl(card_no)


def get_card_summary_info(card_no: int) -> Dict[str, Any]:
    return _get_card_summary_info_impl(card_no)


# ========= OpenAI-compatible tool schemas =========
TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_customer_details",
            "description": GET_CUSTOMER_DETAILS_DESC,
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_number": {
                        "type": "integer",
                        "description": "6–10 haneli SADECE RAKAM müşteri numarası. IBAN/kart numarası DEĞİL."
                    },
                    "account_suffix": {
                        "type": "integer",
                        "description": "Hesap ek numarası (varsayılan 351). Emin değilsen gönderme."
                    },
                    "branch_code": {
                        "type": "integer",
                        "description": "Şube kodu (varsayılan 9142). Emin değilsen gönderme."
                    },
                },
                "required": ["customer_number"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_card_summary_info",
            "description": GET_CARD_SUMMARY_INFO_DESC,
            "parameters": {
                "type": "object",
                "properties": {
                    "card_no": {
                        "type": "integer",
                        "description": "Kart numarası (genelde 16 hane, SADECE RAKAM). Boşluk/tire kaldır."
                    }
                },
                "required": ["card_no"],
                "additionalProperties": False,
            },
        },
    },{
        "type": "function",
        "function": {
            "name": "analyze_credit_offer",
            "description": "Hesap bakiyesi ve kredi kartı borcuna göre kredi skoru ve teklif hesaplar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_number": {
                        "type": "integer",
                        "description": "6-10 haneli müşteri numarası"
                    },
                    "card_no": {
                        "type": "integer",
                        "description": "Kart numarası (16 haneli)"
                    },
                    "account_suffix": {
                        "type": "integer",
                        "description": "Varsayılan 351"
                    },
                    "branch_code": {
                        "type": "integer",
                        "description": "Varsayılan 9142"
                    },
                },
                "required": ["customer_number", "card_no"],
                "additionalProperties": False
            }
        }
    }
]


# ========= Export list for Agent convenience =========
CURRENT_TOOLS = [get_customer_details_tool, get_card_summary_info_tool]
