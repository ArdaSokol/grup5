# app.py
# Sadeleştirilmiş giriş noktası

from agno.agent import Agent

from models.custom_qwen import CustomChatModel
from app_tools import CURRENT_TOOLS, ANALYSIS_TOOLS

AGENT_INSTRUCTIONS = (
    "Kullanıcının mesajındaki müşteri numarasını doğal dilden kendin tespit et. "
    "Belirlediğinde get_customer_details tool'unu çağır. "
    "Sonucu kısa özetle; ham JSON gösterme. "
    "Numara belirsizse kısa bir netleştirme sorusu sor."
)

def build_agent() -> Agent:
    return Agent(
        model=CustomChatModel(),
        tools=[*ANALYSIS_TOOLS, *CURRENT_TOOLS],
        instructions=AGENT_INSTRUCTIONS,
        markdown=True,
    )


if __name__ == "__main__":
    agent = build_agent()
    # Örnek kullanım
    while True:
        prompt = input()
        print("input alındı")
        agent.print_response(input , stream=False)
        print("cevap verildi")
    #agent.print_response("müşteri numaram 17953063, hesap detaylarımı getirir misin?", stream=False)
    #agent.print_response("2025051600000210 kartımda para var mı yoksa nasıl kredi çekebilirim ", stream=False)
    #agent.print_response("Müşteri numarası 17953063 ve kart numarası 2025051600000210 için bana kredi teklifini hesaplar mısın? başka bilgim yok kredi kartı bakiyeme göre bir tekilf ver ve kredi kartımda kaç tl var onuda söyle", stream=False)
