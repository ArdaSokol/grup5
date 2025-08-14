# tools/analiztools/risk_score.py
from agno.tools import tool
from typing import Dict, Any

RISK_SCORE_DESC = """
[Tool: risk_score]

Ne zaman kullanılır?
- Kullanıcıdan gelen özet metriklerle (utilization, late_payments, income, tenure_months vb.)
  basit bir risk skoru/segmenti istendiğinde.

Not:
- Bu sadece örnek bir kural setidir; gerçek model değildir.
"""

def _risk_score_impl(features: Dict[str, Any]) -> Dict[str, Any]:
    utilization = float(features.get("utilization", 0.0))       # 0-1 arası beklenir
    late = int(features.get("late_payments", 0))
    income = float(features.get("income", 0.0))
    tenure = int(features.get("tenure_months", 0))

    score = 700  # baz skor

    # utilization yüksekse düşür
    score -= int(utilization * 200)          # %80 -> -160 gibi

    # gecikmeler daha ağır çarpsın
    score -= late * 25

    # gelir yükseldikçe biraz arttır
    if income > 0:
        score += min(int(income / 10000) * 5, 50)  # tavan +50

    # müşteri kıdemi (tenure) artı puan
    score += min(tenure // 12 * 10, 50)  # her yıl +10, tavan +50

    # sınırlama
    score = max(300, min(score, 900))

    segment = (
        "Low Risk" if score >= 750 else
        "Medium Risk" if score >= 650 else
        "High Risk"
    )

    return {"score": score, "segment": segment}

@tool(name="risk_score", description=RISK_SCORE_DESC)
def risk_score_tool(features: Dict[str, Any]):
    return _risk_score_impl(features)
