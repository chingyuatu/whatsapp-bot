import os
import logging
from flask import Flask, request
from groq import Groq
import requests

# 1. 基礎設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 2. 初始化 API 客戶端
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")  # 從 BotFather 拿到的 Token
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"

# 暫存對話紀錄 (重啟會消失)
chat_history = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    logger.info(f"Received from Telegram: {data}")

    # 3. 檢查是否有訊息進入
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        incoming_msg = data["message"]["text"]

        # 處理對話歷史邏輯
        if chat_id not in chat_history:
            chat_history[chat_id] = []

        chat_history[chat_id].append({"role": "user", "content": incoming_msg})

        try:
            # 4. 呼叫 Groq Llama 3.3
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=chat_history[chat_id],
                max_tokens=1024
            )
            reply_text = response.choices[0].message.content

            # 存入助手回應
            chat_history[chat_id].append({"role": "assistant", "content": reply_text})

            # 限制長度避免爆 Token
            if len(chat_history[chat_id]) > 20:
                chat_history[chat_id] = chat_history[chat_id][-20:]

        except Exception as e:
            reply_text = f"抱歉，系統出錯了：{str(e)}"
            logger.error(f"Error: {e}")

        # 5. 回傳訊息給使用者
        send_telegram_message(chat_id, reply_text)

    return "OK", 200

def send_telegram_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        logger.error(f"Send failed: {e}")

@app.route("/", methods=["GET"])
def index():
    return "Telegram Agent is alive!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
