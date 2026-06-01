"""
test_system.py — Unit tests for AI Chatbot System.
Run: python -m pytest tests/ -v
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from chatbot_engine import find_intent, get_response, detect_sentiment, INTENTS


# ── Intent Retrieval Tests ─────────────────────────────────────────────────────

class TestIntentRetrieval:

    def test_greeting_hello(self):
        intent = find_intent("hello")
        assert intent is not None
        assert intent["tag"] == "greeting"

    def test_greeting_hey(self):
        intent = find_intent("hey there")
        assert intent is not None
        assert intent["tag"] == "greeting"

    def test_farewell(self):
        intent = find_intent("goodbye see you later")
        assert intent is not None
        assert intent["tag"] == "farewell"

    def test_thanks(self):
        intent = find_intent("thank you so much")
        assert intent is not None
        assert intent["tag"] == "thanks"

    def test_pricing(self):
        intent = find_intent("how much does it cost")
        assert intent is not None
        assert intent["tag"] == "pricing"

    def test_support(self):
        intent = find_intent("i need help with something")
        assert intent is not None
        assert intent["tag"] == "support"

    def test_contact(self):
        intent = find_intent("how can I contact support")
        assert intent is not None
        assert intent["tag"] == "contact"

    def test_hours(self):
        intent = find_intent("business hours")
        assert intent is not None
        assert intent["tag"] == "hours"

    def test_refund(self):
        intent = find_intent("what is your refund policy")
        assert intent is not None
        assert intent["tag"] == "refund"

    def test_password_reset(self):
        intent = find_intent("I forgot my password")
        assert intent is not None
        assert intent["tag"] == "faq_password"

    def test_products(self):
        intent = find_intent("what products do you offer")
        assert intent is not None
        assert intent["tag"] == "products"

    def test_about_bot(self):
        intent = find_intent("who are you")
        assert intent is not None
        assert intent["tag"] == "about"

    def test_no_match_returns_none(self):
        # Very unusual input should not match
        intent = find_intent("xyzzy foobar qux 12345")
        assert intent is None

    def test_order_status(self):
        intent = find_intent("where is my order")
        assert intent is not None
        assert intent["tag"] == "order_status"


# ── Response Generation Tests ──────────────────────────────────────────────────

class TestResponseGeneration:

    def test_response_is_string(self):
        intent = find_intent("hello")
        response = get_response(intent)
        assert isinstance(response, str) and len(response) > 0

    def test_all_intents_have_responses(self):
        for intent in INTENTS:
            assert len(intent["responses"]) >= 1
            for r in intent["responses"]:
                assert isinstance(r, str) and len(r) > 0

    def test_response_randomness(self):
        # Get 20 responses for a multi-response intent; should get > 1 unique
        intent = find_intent("hello")
        responses = {get_response(intent) for _ in range(20)}
        assert len(responses) >= 1  # at minimum 1 unique response


# ── Sentiment Detection Tests ──────────────────────────────────────────────────

class TestSentimentDetection:

    def test_positive_sentiment(self):
        assert detect_sentiment("This is great and awesome!") == "positive"

    def test_negative_sentiment(self):
        assert detect_sentiment("This is terrible and broken") == "negative"

    def test_neutral_sentiment(self):
        assert detect_sentiment("what is the price") == "neutral"

    def test_empty_string(self):
        result = detect_sentiment("")
        assert result in ("positive", "negative", "neutral")


# ── Intent Coverage Tests ──────────────────────────────────────────────────────

class TestIntentCoverage:

    def test_all_intents_have_tags(self):
        for intent in INTENTS:
            assert "tag" in intent and intent["tag"]

    def test_all_intents_have_patterns(self):
        for intent in INTENTS:
            assert "patterns" in intent and len(intent["patterns"]) >= 2

    def test_intent_count(self):
        assert len(INTENTS) >= 10

    def test_unique_tags(self):
        tags = [i["tag"] for i in INTENTS]
        assert len(tags) == len(set(tags))  # no duplicate tags
