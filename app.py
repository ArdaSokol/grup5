from agno.agent import Agent
from models.qwen_model import llm
from tools.currenttools import CURRENT_TOOLS
from tools.analiztools import CURRENT_ANALYSIS_TOOLS


ALL_TOOLS = CURRENT_TOOLS + CURRENT_ANALYSIS_TOOLS

agent = Agent(
    model=llm,
    tools=ALL_TOOLS,
    instructions=[
        "Kısa, adım adım düşün ve gerekirse aracı kullan.",
        "Tablo gerekiyorsa tablolu yaz."
    ],
    markdown=True,
    show_tool_calls=True
)

if __name__ == "__main__":
    agent.print_response("17953063 müşteri numarası için hesap bilgilerini verir misin?")
    agent.print_response("Kredi kartı numaram 2025051600000210. Bilgileri bana getirir misiniz?")
    agent.print_response(
    "Kullanım oranım 0,45, 1 gecikmeli ödemem oldu, gelirim 50.000 ve vadem 36 ay. Lütfen risk puanımı hesaplayın."
)
