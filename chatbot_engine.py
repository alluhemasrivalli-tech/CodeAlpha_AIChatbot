"""
chatbot_engine.py — Hybrid retrieval-based + generative AI chatbot engine.

Architecture:
  1. RETRIEVAL LAYER  — matches user input against predefined intents using
                        TF-IDF cosine similarity (no external API needed)
  2. GENERATIVE LAYER — calls Anthropic Claude API for open-ended questions
                        that don't match any intent pattern
  3. FALLBACK         — polite default response if both layers fail

Intent categories (commercial use patterns):
  - greetings / farewells
  - product / service inquiries
  - pricing
  - support / help
  - company information
  - order / booking status
  - FAQs
"""

import re
import math
from typing import Optional


# ── Intent Knowledge Base ─────────────────────────────────────────────────────

INTENTS = [
    {
        "tag": "greeting",
        "patterns": [
            "hello", "hi", "hey", "good morning", "good afternoon",
            "good evening", "howdy", "what's up", "greetings", "hi there", "yo"
        ],
        "responses": [
            "Hello! 👋 Welcome! How can I assist you today?",
            "Hi there! Great to see you. What can I help you with?",
            "Hey! I'm here and ready to help. What's on your mind?",
        ]
    },
    {
        "tag": "farewell",
        "patterns": [
            "bye", "goodbye", "see you", "take care", "farewell",
            "see ya", "later", "good night", "thanks bye", "that's all"
        ],
        "responses": [
            "Goodbye! 👋 Have a wonderful day!",
            "Take care! Feel free to come back anytime.",
            "Bye! It was great chatting with you. 😊",
        ]
    },
    {
        "tag": "thanks",
        "patterns": [
            "thank you", "thanks", "thank you so much", "thanks a lot",
            "appreciate it", "great thanks", "many thanks", "thx", "ty"
        ],
        "responses": [
            "You're welcome! 😊 Is there anything else I can help you with?",
            "Happy to help! Let me know if you need anything else.",
            "Anytime! Don't hesitate to ask if you have more questions.",
        ]
    },
    {
        "tag": "about",
        "patterns": [
            "who are you", "what are you", "tell me about yourself",
            "what can you do", "what is this chatbot", "are you a bot",
            "are you human", "what is your name"
        ],
        "responses": [
            "I'm an AI-powered assistant built with a hybrid retrieval + generative model. I can answer questions, help with support, provide information about products and services, and much more! 🤖",
            "I'm your smart assistant! I combine pattern matching and AI to give you fast, accurate answers. Ask me anything!",
        ]
    },
    {
        "tag": "pricing",
        "patterns": [
            "how much does it cost", "what is the price", "pricing",
            "how much is it", "cost", "fees", "charges", "payment",
            "subscription", "plan", "how much", "price list", "rate"
        ],
        "responses": [
            "💰 Our pricing is flexible! We offer Free, Pro (₹999/month), and Enterprise plans. Would you like details on a specific plan?",
            "We have plans to suit every budget — starting completely free! Type 'pricing details' or visit our pricing page for a full breakdown.",
        ]
    },
    {
        "tag": "support",
        "patterns": [
            "help", "support", "i need help", "having a problem",
            "something is wrong", "not working", "issue", "bug",
            "error", "trouble", "can't", "cannot", "broken", "fix"
        ],
        "responses": [
            "I'm sorry to hear you're having trouble! 🛠️ Could you describe the issue in more detail? I'll do my best to help.",
            "Let's get this sorted out! Please describe the problem and I'll guide you through the solution.",
        ]
    },
    {
        "tag": "contact",
        "patterns": [
            "contact us", "email address", "phone number", "reach you",
            "get in touch", "customer service", "talk to human",
            "speak to agent", "live chat", "how can i contact",
            "contact support team", "how to reach"
        ],
        "responses": [
            "📞 You can reach our team at:\n• Email: support@example.com\n• Phone: +91-9876543210\n• Live Chat: Available Mon–Sat, 9AM–6PM\n\nOr I can try to help you right here!",
        ]
    },
    {
        "tag": "hours",
        "patterns": [
            "business hours", "working hours", "opening hours",
            "when are you open", "what time do you open",
            "open on weekend", "are you closed", "timings",
            "office hours", "hours of operation", "when do you close"
        ],
        "responses": [
            "🕐 We're available:\n• Monday – Friday: 9:00 AM – 6:00 PM\n• Saturday: 10:00 AM – 4:00 PM\n• Sunday: Closed\n\nOur chatbot is available 24/7 though!",
        ]
    },
    {
        "tag": "order_status",
        "patterns": [
            "order status", "where is my order", "track order",
            "my order", "delivery", "shipment", "tracking",
            "when will it arrive", "dispatch", "shipped"
        ],
        "responses": [
            "📦 To track your order, please provide your Order ID and I'll pull up the details! You can also check your email for the tracking link.",
        ]
    },
    {
        "tag": "refund",
        "patterns": [
            "refund", "money back", "cancel order", "return",
            "cancellation", "get my money back", "refund policy",
            "how to return", "exchange"
        ],
        "responses": [
            "💳 Our refund policy: Full refunds are available within 30 days of purchase. To initiate a refund, email refunds@example.com with your order ID. Processing takes 5–7 business days.",
        ]
    },
    {
        "tag": "products",
        "patterns": [
            "products", "services", "what do you offer", "what do you sell",
            "features", "what is available", "catalog", "portfolio",
            "offerings", "solutions", "packages"
        ],
        "responses": [
            "🛍️ We offer a range of products and services including:\n• Software solutions\n• Cloud hosting\n• AI tools\n• Support packages\n\nWould you like details on any specific product?",
        ]
    },
    {
        "tag": "faq_password",
        "patterns": [
            "forgot password", "reset password", "change password",
            "can't login", "lost password", "password reset",
            "locked out", "account access"
        ],
        "responses": [
            "🔑 To reset your password:\n1. Click 'Forgot Password' on the login page\n2. Enter your registered email\n3. Check your inbox for a reset link (valid for 1 hour)\n\nStill having trouble? Contact support@example.com",
        ]
    },
    {
        "tag": "faq_account",
        "patterns": [
            "create account", "sign up", "register", "new account",
            "how to join", "make account", "get started"
        ],
        "responses": [
            "🚀 Getting started is easy!\n1. Click 'Sign Up' on our homepage\n2. Enter your name, email, and password\n3. Verify your email\n4. You're in! 🎉\n\nNeed help? I'm right here.",
        ]
    },
]


# ── TF-IDF Retrieval Engine ───────────────────────────────────────────────────

def _tokenize(text: str) -> list:
    return re.findall(r"\b\w+\b", text.lower())


def _tfidf_score(query_tokens: list, doc_tokens: list) -> float:
    """Simple term-frequency based cosine similarity."""
    if not doc_tokens or not query_tokens:
        return 0.0
    doc_set   = set(doc_tokens)
    query_set = set(query_tokens)
    intersection = query_set & doc_set
    if not intersection:
        return 0.0
    # Cosine similarity approximation
    return len(intersection) / (math.sqrt(len(query_set)) * math.sqrt(len(doc_set)))


def find_intent(user_input: str, threshold: float = 0.2) -> Optional[dict]:
    """
    Return the best-matching intent if similarity exceeds threshold, else None.

    Scoring:
      1. Full pattern in query string          → 0.95 (length-boosted)
      2. All pattern words present in query    → 0.80 (length-boosted)
      3. TF-IDF cosine similarity              → raw score
      Short single-word patterns get a length penalty so longer
      specific patterns always win over generic single words.
    """
    query_lower  = user_input.lower().strip()
    query_tokens = _tokenize(user_input)
    query_set    = set(query_tokens)

    best_score   = 0.0
    best_intent  = None

    for intent in INTENTS:
        for pattern in intent["patterns"]:
            pat_lower  = pattern.lower().strip()
            pat_tokens = _tokenize(pattern)
            pat_set    = set(pat_tokens)
            pat_len    = len(pat_tokens)

            # Length boost: longer, more specific patterns score higher
            length_boost = min(1.0, 0.5 + 0.1 * pat_len)  # 0.6 for 1-word, 1.0 for 5+ words

            score = 0.0

            # 1. Full pattern is a substring of query
            if pat_lower in query_lower:
                score = 0.95 * length_boost

            # 2. All words of pattern appear in query
            elif pat_set and pat_set.issubset(query_set):
                score = 0.80 * length_boost

            # 3. TF-IDF similarity
            else:
                raw = _tfidf_score(query_tokens, pat_tokens)
                score = raw * length_boost

            if score > best_score:
                best_score  = score
                best_intent = intent

    return best_intent if best_score >= threshold else None


def get_response(intent: dict) -> str:
    import random
    return random.choice(intent["responses"])


# ── Sentiment detector (basic) ────────────────────────────────────────────────

def detect_sentiment(text: str) -> str:
    """Returns 'positive', 'negative', or 'neutral'."""
    pos = {"great","good","awesome","excellent","love","happy","amazing","wonderful","fantastic","perfect","thanks","thank"}
    neg = {"bad","terrible","worst","hate","awful","horrible","disappointed","angry","frustrated","useless","broken","wrong"}
    tokens = set(_tokenize(text))
    p = len(tokens & pos)
    n = len(tokens & neg)
    if p > n: return "positive"
    if n > p: return "negative"
    return "neutral"
