import json
import ssl
import urllib.request

# API endpoint
API_BASE = "https://api-qwen-31-load-predictor-tmp-automation-test-3.apps.datascience.prod2.deniz.denizbank.com"
MODEL = "default"  # Bulduğumuz çalışan model

url = f"{API_BASE}/v1/chat/completions"

# Gönderilecek veri
payload = {
    "model": MODEL,
    "temperature": 0.2,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user",   "content": "Merhaba! Bu model ile sohbet edelim."}
    ]
}

# JSON'u byte'a çevir
data = json.dumps(payload).encode("utf-8")

# HTTP isteği oluştur
req = urllib.request.Request(
    url,
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST",
)

# SSL context (kurumsal CA gerekiyorsa burada eklenir)
ctx = ssl.create_default_context()

try:
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        body = resp.read().decode("utf-8")
        response_json = json.loads(body)

        # Tam JSON yanıtını göster
        print(json.dumps(response_json, indent=2, ensure_ascii=False))

        # Sadece asistanın cevabını yazdır
        print("\nAssistant:", response_json["choices"][0]["message"]["content"])
    except urllib.error.HTTPError as e:
    print(f"❌ HTTP Hatası: {e.code} - {e.reason}")
    print(e.read().decode())
except Exception as e:
    print(f"❌ Bağlantı Hatası: {e}")
