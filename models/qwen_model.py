from agno.models.openai.like import OpenAILike

llm = OpenAILike(
    id="default",  # model adı
    api_key="dummy-key",
    base_url="https://api-qwen-31-load-predictor-tmp-automation-test-3.apps.datascience.prod2.deniz.denizbank.com/v1",
    temperature=0.7,        # 🔹 yaratıcı / deterministiklik ayarı
    max_tokens=512,         # 🔹 çıktı uzunluğu
    # <think> çıktısını kapatır
    request_params={
        "extra_body": {  # <-- EK PARAMETRELER BURAYA
            "chat_template_kwargs": {
                "enable_thinking": False
            }
        }
    }
)
