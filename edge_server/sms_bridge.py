import requests
import re
from flask import Flask, request, jsonify
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# =========================
# CONFIGURATION
# =========================

MODEL_NAME = "gemma4:latest"
GEMMA_API = "http://localhost:11434/api/chat"

# Android SMS Gateway
GATEWAY_URL = "http://192.168.1.161:8080/message"
GATEWAY_USER = "sms"
GATEWAY_PASSWORD = "qjunCGKe"


# =========================
# CLEAN GEMMA OUTPUT
# =========================

def clean_gemma_output(text):
    """
    Removes Gemma internal thinking tags.
    """
    text = re.sub(
        r'<\|channel>thought.*?<channel\|>',
        '',
        text,
        flags=re.DOTALL
    )

    return text.strip()


# =========================
# WEBHOOK
# =========================

@app.route('/webhook', methods=['GET', 'POST'])
def handle_sms():

    # -------------------------
    # GET TEST
    # -------------------------
    if request.method == 'GET':
        return "SMS AI Bridge Running", 200

    # -------------------------
    # DEBUG LOGGING
    # -------------------------
    print("\n========== NEW REQUEST ==========")
    print("METHOD:", request.method)
    print("HEADERS:", dict(request.headers))
    print("RAW DATA:", request.data)

    try:
        data = request.json
    except Exception:
        data = None

    print("JSON DATA:", data)

    if not data:
        return jsonify({
            "status": "ignored",
            "reason": "no json"
        }), 200

    # -------------------------
    # EXTRACT SMS DATA
    # -------------------------
    payload_in = data.get('payload', {})

    sender = payload_in.get('phoneNumber')
    incoming_text = payload_in.get('message')

    if not incoming_text:
        return jsonify({
            "status": "ignored",
            "reason": "no message"
        }), 200

    print(f"\n📩 SMS Received: '{incoming_text}' from {sender}")

    # =========================
    # ASK GEMMA
    # =========================

    print("🤖 Sending to Gemma...")

    try:
        response = requests.post(
            GEMMA_API,
            json={
                "model": MODEL_NAME,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant. "
                            "Keep replies very short for SMS."
                        )
                    },
                    {
                        "role": "user",
                        "content": incoming_text
                    }
                ],
                "stream": False
            },
            timeout=60
        )

        print("OLLAMA STATUS:", response.status_code)

        raw_answer = response.json().get(
            'message',
            {}
        ).get(
            'content',
            ''
        )

        ai_answer = clean_gemma_output(raw_answer)

        if not ai_answer:
            ai_answer = "No response generated."

    except Exception as e:
        print("❌ OLLAMA ERROR:", e)
        ai_answer = "AI service unavailable."

    print("🤖 AI Reply:", ai_answer)

    # =========================
    # SEND SMS BACK
    # =========================

    outbound = {
        "phoneNumbers": [sender],
        "textMessage": {
            "text": ai_answer
        }
    }

    print("📤 Sending SMS reply...")

    try:
        res = requests.post(
            GATEWAY_URL,
            json=outbound,
            auth=HTTPBasicAuth(
                GATEWAY_USER,
                GATEWAY_PASSWORD
            ),
            timeout=20
        )

        print("✅ SMS GATEWAY STATUS:", res.status_code)
        print("✅ SMS GATEWAY RESPONSE:", res.text)

        return jsonify({
            "status": "success",
            "phone_code": res.status_code,
            "reply": ai_answer
        }), 200

    except Exception as e:
        print("❌ PHONE GATEWAY ERROR:", e)

        return jsonify({
            "status": "failed",
            "error": str(e)
        }), 500


# =========================
# START SERVER
# =========================

if __name__ == '__main__':

    print("\n==============================")
    print(" OFFLINE SMS AI BRIDGE ACTIVE ")
    print("==============================")
    print(f"Model: {MODEL_NAME}")
    print("Webhook:")
    print("http://192.168.1.151:5000/webhook")
    print("==============================\n")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )