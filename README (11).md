# CodeAlpha — Task 4: AI-Powered Chatbot

> **CodeAlpha Cloud Computing Internship**

A production-ready AI chatbot with a **hybrid retrieval + generative** architecture, dark chat UI, embeddable website widget, and Anthropic Claude API integration — built with pure Python and Flask, zero external NLP libraries.

---

## 🤖 Architecture — Hybrid AI Model

```
User Input
    │
    ▼
┌──────────────────────────────────────┐
│  LAYER 1 — Retrieval-Based           │
│  • TF-IDF cosine similarity          │
│  • 13 intent categories              │
│  • 100+ training patterns            │
│  → ⚡ Instant response (<1ms)        │
└──────────────┬───────────────────────┘
               │ no intent match
               ▼
┌──────────────────────────────────────┐
│  LAYER 2 — Generative (Claude API)   │
│  • Anthropic claude-sonnet-4         │
│  • Full conversation history         │
│  • Custom system prompt              │
│  → ✦ AI-generated response           │
└──────────────┬───────────────────────┘
               │ API unavailable
               ▼
┌──────────────────────────────────────┐
│  LAYER 3 — Fallback                  │
│  • Polite default responses          │
│  → ↩ Graceful degradation            │
└──────────────────────────────────────┘
```

---

## ✨ Features

| Feature | Details |
|---|---|
| **Retrieval Engine** | TF-IDF cosine similarity + substring matching |
| **Generative AI** | Claude API for open-ended questions |
| **13 Intent Categories** | Greetings, pricing, support, refunds, orders, FAQ, and more |
| **Sentiment Detection** | Positive / negative / neutral (pure Python) |
| **Full Chat UI** | Dark-themed, sidebar with quick questions, source badges |
| **Embeddable Widget** | Floating chat bubble for any website |
| **Conversation History** | Last 6 messages sent to Claude for context |
| **Source Badges** | UI shows whether response is ⚡ Quick / ✦ AI / ↩ Fallback |
| **22 Unit Tests** | Full pytest suite |

---

## 🗂 Project Structure

```
CodeAlpha_AIChatbot/
│
├── src/
│   ├── app.py              # Flask server (routes + Claude API call)
│   └── chatbot_engine.py   # Retrieval engine, intents, sentiment
│
├── templates/
│   ├── index.html          # Full-page dark chat UI
│   └── widget.html         # Embeddable widget demo on a fake website
│
├── tests/
│   └── test_system.py      # 22 pytest unit tests
│
├── requirements.txt
└── README.md
```

---

## 🚀 How to Run (VS Code)

### 1. Clone and open
```bash
git clone https://github.com/<your-username>/CodeAlpha_AIChatbot.git
cd CodeAlpha_AIChatbot
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the server
```bash
cd src
python app.py
```

| URL | What it shows |
|---|---|
| `http://127.0.0.1:5000` | Full dark chat interface |
| `http://127.0.0.1:5000/widget` | Embeddable widget on a demo website |

### 5. Run tests
```bash
cd ..
python -m pytest tests/ -v
```

---

## 🎬 Demo Flow (for Screen Recording)

**Step 1 — Full chat UI** (`localhost:5000`)
- Click the welcome cards to auto-send questions
- Try the sidebar quick buttons (Pricing, Support, Hours)
- Notice source badges: ⚡ Quick (retrieval) vs ✦ AI (generative)

**Step 2 — Widget demo** (`localhost:5000/widget`)
- Show the fake "TechCorp" website
- Click the purple 🤖 button (bottom right)
- Chat with Nova inside the widget

**Step 3 — Intents covered** (type these in chat)
```
hello
what are your prices?
I forgot my password
track my order
what is your refund policy
```

**Step 4 — Terminal tests**
```bash
python -m pytest tests/ -v   # 22 passed ✅
```

---

## 🧠 Intent Categories (13 total)

| Intent | Example patterns |
|---|---|
| greeting | "hello", "hi", "good morning" |
| farewell | "bye", "goodbye", "see you" |
| thanks | "thank you", "appreciate it" |
| about | "who are you", "what can you do" |
| pricing | "how much", "cost", "subscription" |
| support | "help", "broken", "not working" |
| contact | "email", "phone", "live chat" |
| hours | "business hours", "when are you open" |
| order_status | "track order", "where is my package" |
| refund | "refund", "cancel order", "return" |
| products | "what do you offer", "catalog" |
| faq_password | "forgot password", "locked out" |
| faq_account | "create account", "sign up" |

---

## ☁️ Cloud Deployment

Deploy to any cloud platform:

```bash
# Google Cloud Run
gcloud run deploy nova-chatbot --source .

# AWS Elastic Beanstalk
eb init && eb create

# Azure Web Apps
az webapp up --name nova-chatbot
```

---

## 👨‍💻 Author

**[Your Name]**  
CodeAlpha Cloud Computing Intern  
[LinkedIn] | [GitHub]

---

## 📄 License

Submitted as part of the **CodeAlpha Internship Programme**.
