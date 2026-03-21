import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai

app = Flask(__name__)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

chat_history = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")

    if sender not in chat_history:
        chat_history[sender] = []

    chat_history[sender].append({
        "role": "user",
        "parts": [incoming_msg]
    })

    try:
        chat = model.start_chat(history=chat_history[sender][:-1])
        response = chat.send_message(incoming_msg)
        reply_text = response.text

        chat_history[sender].append({
            "role": "model",
            "parts": [reply_text]
        })

        if len(chat_history[sender]) > 20:
            chat_history[sender] = chat_history[sender][-20:]

    except Exception as e:
        reply_text = f"Error: {str(e)}"

    resp = MessagingResponse()
    resp.message(reply_text)
    return str(resp)

@app.route("/", methods=["GET"])
def index():
    return "WhatsApp Bot is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
