"""
app.py — AI Chatbot Flask server.

Flow per message:
  1. Check retrieval engine  → instant response for known intents
  2. If no match             → call Anthropic Claude API (generative)
  3. Stream response back    → smooth typing effect in the UI

Endpoints:
  GET  /          → Chat UI page
  POST /chat      → Process a message, return JSON response
  GET  /widget    → Embeddable widget demo page
"""

import os, sys, random, datetime
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify, render_template
from chatbot_engine import find_intent, get_response, detect_sentiment

app = Flask(__name__, template_folder="../templates")
app.secret_key = "CodeAlpha_Chatbot_2024"

# ── Anthropic API call ────────────────────────────────────────────────────────

def call_claude(user_message: str, history: list) -> str:
    """Call Anthropic Claude API for open-ended generative responses."""
    try:
        import urllib.request, json

        messages = history[-6:] + [{"role": "user", "content": user_message}]

        payload = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 300,
            "system": (
                "You are a helpful, friendly customer support chatbot for a software company. "
                "Keep responses concise (2-4 sentences max), warm, and professional. "
                "Use occasional emojis. If asked about specific account details, order numbers, "
                "or private data, politely say you cannot access that and suggest contacting support."
            ),
            "messages": messages
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={"Content-Type": "application/json", "anthropic-version": "2023-06-01"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["content"][0]["text"]

    except Exception as e:
        return None  # fallback to default response


# ── Routes ─────────────────────────────────────────────────────────────────────

FALLBACK_RESPONSES = [
    "I'm not sure about that, but I'd love to help! Could you rephrase or give me more details? 🤔",
    "That's a great question! Let me connect you with our support team for a precise answer. 📞",
    "I don't have that information right now, but our team at support@example.com can definitely help!",
]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/widget")
def widget():
    return render_template("widget.html")


@app.route("/chat", methods=["POST"])
def chat():
    data    = request.get_json() or {}
    message = data.get("message", "").strip()
    history = data.get("history", [])

    if not message:
        return jsonify({"response": "Please type a message!", "source": "system"})

    # Detect sentiment for logging / tone adjustment
    sentiment = detect_sentiment(message)

    # ── Layer 1: Retrieval ────────────────────────────────────────────
    intent = find_intent(message)
    if intent:
        response = get_response(intent)
        return jsonify({
            "response":  response,
            "source":    "retrieval",
            "intent":    intent["tag"],
            "sentiment": sentiment,
            "timestamp": datetime.datetime.now().strftime("%H:%M")
        })

    # ── Layer 2: Generative (Claude API) ─────────────────────────────
    ai_response = call_claude(message, history)
    if ai_response:
        return jsonify({
            "response":  ai_response,
            "source":    "generative",
            "intent":    "ai_generated",
            "sentiment": sentiment,
            "timestamp": datetime.datetime.now().strftime("%H:%M")
        })

    # ── Layer 3: Fallback ─────────────────────────────────────────────
    return jsonify({
        "response":  random.choice(FALLBACK_RESPONSES),
        "source":    "fallback",
        "intent":    "unknown",
        "sentiment": sentiment,
        "timestamp": datetime.datetime.now().strftime("%H:%M")
    })


if __name__ == "__main__":
    print("=" * 55)
    print("  CodeAlpha — AI Chatbot System")
    print("  Chat UI  : http://127.0.0.1:5000")
    print("  Widget   : http://127.0.0.1:5000/widget")
    print("=" * 55)
    app.run(debug=True, host="0.0.0.0", port=5000)
