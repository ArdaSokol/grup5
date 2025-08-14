from typing import Any, Dict
from agno.tools import tool
from agno.tools.reasoning import ReasoningTools
from .current_tools import _get_customer_details_impl, _get_card_summary_info_impl

def _get_account_balance(raw: Dict[str, Any]) -> float:
    # Basit: sözlükte 'Balance' veya 'AvailableBalance' varsa al; yoksa derine bak.
    for key in ("Balance", "AvailableBalance"):
        if key in raw:
            try:
                return float(raw[key])
            except Exception:
                pass
    if isinstance(raw, dict):
        for v in raw.values():
            if isinstance(v, dict):
                bal = _get_account_balance(v)
                if bal:
                    return bal
    return 0.0

def _get_card_debt(raw: Dict[str, Any]) -> float:
    """
    Senin verdiğin forma göre:
    Data.TotalBalance_YI, Data.TotalBalance_YD, Data.TotalBalance_YE alanlarını toplayıp toplam borç döndürür.
    """
    data = raw.get("Data", {}) if isinstance(raw, dict) else {}
    total = 0.0
    for f in ("TotalBalance_YI", "TotalBalance_YD", "TotalBalance_YE"):
        try:
            total += float(data.get(f, 0.0))
        except Exception:
            pass
    return total

def _calculate_offer(balance: float, debt: float) -> Dict[str, Any]:
    """
    ŞİMDİLİK BASİT KURAL:
      - her ne olursa olsun 10000 tl ver kredi
    """
    return {
        "score": 700,                              # sabit/placeholder skor
        "total_debt": round(float(debt), 2),
        "account_balance": round(float(balance), 2),
        "offer_amount": 10000,                     # <<< SABİT TEKLİF
        "utilization": None                        # istersen burada oran hesaplamıyoruz
    }

@tool(
    name="analyze_credit_offer",
    description="(Geçici) Hesap bakiyesi ve kart borcundan bağımsız olarak 10.000 ₺ kredi teklif eder; raporlama için bakiye ve borcu döndürür."
)
def analyze_credit_offer_tool(
    customer_number: int,
    card_no: int,
    account_suffix: int = 351,
    branch_code: int = 9142
) -> Dict[str, Any]:
    # Hesap ve kart servislerini yine çağırıyoruz (raporlama alanları için).
    account_raw = _get_customer_details_impl(
        customer_number=int(customer_number),
        account_suffix=int(account_suffix),
        branch_code=int(branch_code)
    )
    balance = _get_account_balance(account_raw)

    card_raw = _get_card_summary_info_impl(card_no=int(card_no))
    debt = _get_card_debt(card_raw)

    return _calculate_offer(balance, debt)

ANALYSIS_TOOLS = [
    ReasoningTools(add_instructions=True),
    analyze_credit_offer_tool
]
