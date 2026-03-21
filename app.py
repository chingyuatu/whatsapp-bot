import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from google import genai

app = Flask(__name__)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

chat_history = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")

    print(f"收到訊息: {incoming_msg} 來自: {sender}")

    if sender not in chat_history:
        chat_history[sender] = []

    chat_history[sender].append({
        "role": "user",
        "parts": [{"text": incoming_msg}]
    })

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=chat_history[sender]
        )
        reply_text = response.text
        print(f"Gemini 回覆: {reply_text}")
