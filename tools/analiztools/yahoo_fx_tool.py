# tools/analiztools/yahoo_fx_tool.py
"""
yahoo_fx_rates: Yahoo Finance üzerinden döviz paritesi fiyatları.
- Girdi: "pairs" listesi. Örn:
    ["USDTRY", "EURUSD", "GBPUSD"]  # sembol kökleri
  veya insan-dostu biçimler:
    ["USD/TRY", "EUR-USD", "gbp usd"]  -> otomatik "USDTRY","EURUSD","GBPUSD"
- Çıkış: her sembol için son fiyat, yüzde değişim, zaman damgası vb.

Notlar:
- Yahoo FX sembolleri genelde "XXXYYY=X" şeklindedir; yfinance bunu otomatik map’ler:
  "USDTRY" için yfinance sembolü "USDTRY=X" olur.
- BIST döviz kurları için de aynı yapı geçerlidir (örn. "EURTRY" -> "EURTRY=X").
"""

import re
import time
from typing import Dict, List, Optional
from agno.tools import tool

try:
    import yfinance as yf
except Exception as e:
    yf = None

def _norm_pair(p: str) -> str:
    # "usd/try", "usd-try", "usd try" -> "USDTRY"
    s = re.sub(r"[^a-zA-Z]", "", p).upper()
    if len(s) != 6:
        return s  # zayıf doğrulama; kullanıcı "EURUSD" gibi verir
    return s

def _to_yahoo_fx_symbol(k: str) -> str:
    # "USDTRY" -> "USDTRY=X"; eğer zaten "=X" ile gelmişse dokunma
    return k if k.endswith("=X") else (k + "=X")

def _get_fx_quote(symbol: str) -> Dict:
    t = yf.Ticker(symbol)
    info = t.fast_info if hasattr(t, "fast_info") else {}
    price = getattr(t, "history", None)
    last = None
    ts = None
    try:
        h = price(period="1d", interval="1m")
        if not h.empty:
            last = float(h["Close"].dropna().iloc[-1])
            ts = h.index[-1].to_pydatetime().isoformat()
    except Exception:
        pass
    if last is None:
        # fast_info fallback
        last = float(info.get("last_price")) if info and info.get("last_price") is not None else None
    return {
        "symbol": symbol,
        "last": last,
        "currency": info.get("currency") if info else None,
        "exchange": info.get("exchange") if info else None,
        "previous_close": float(info.get("previous_close")) if info and info.get("previous_close") is not None else None,
        "year_high": float(info.get("year_high")) if info and info.get("year_high") is not None else None,
        "year_low": float(info.get("year_low")) if info and info.get("year_low") is not None else None,
        "timestamp": ts,
    }

@tool(
    name="yahoo_fx_rates",
    description="Yahoo Finance üzerinden döviz paritelerini getirir. Örn: pairs=['USDTRY','EURUSD'] veya ['USD/TRY','EUR-USD']."
)
def yahoo_fx_rates(pairs: Optional[List[str]] = None) -> Dict:
    """
    :param pairs: list[str]  (None ise varsayılan ['USDTRY','EURUSD','GBPUSD','EURTRY','USDTRY'])
    """
    if yf is None:
        raise RuntimeError("yfinance bulunamadı. Lütfen: pip install yfinance")

    if not pairs:
        pairs = ["USDTRY", "EURUSD", "GBPUSD", "EURTRY", "USDJPY"]

    norm = [_norm_pair(p) for p in pairs]
    syms = [_to_yahoo_fx_symbol(p) for p in norm]

    out: Dict[str, Dict] = {}
    for s in syms:
        try:
            out[s] = _get_fx_quote(s)
        except Exception as e:
            out[s] = {"symbol": s, "error": str(e)}

    return {
        "as_of": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "source": "Yahoo Finance (yfinance)",
        "pairs": pairs,
        "results": out,
    }
