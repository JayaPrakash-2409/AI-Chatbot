 HEAD
# 🤖 AI Chatbot with Contextual Memory

A production-ready, domain-aware AI chatbot powered by Claude (claude-sonnet-4), featuring a **sliding context window** for multi-turn dialogue, intent detection, and a polished dark UI.

---

## 🏗️ Architecture

```
contextual-chatbot/
├── app.py                  # Flask REST API backend
├── chatbot_engine.py       # Core chatbot logic + intent detection
├── domain_configs.py       # Domain personas (E-Commerce, Banking, General)
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html          # Chat UI template
├── static/
│   ├── css/style.css       # Dark industrial UI styles
│   └── js/chatbot.js       # Frontend + Claude API integration
└── README.md
```

---

## 🧠 How Contextual Memory Works

The chatbot uses a **sliding context window** — a technique used in production LLM systems:

```
User: "I ordered something last week"
Bot:  "Sure! Could you share your order number?"
User: "It's #12345"
Bot:  "I see order #12345 shipped on Monday..." ← Remembers previous context!
User: "When will it arrive?"
Bot:  "Your order #12345 should arrive..." ← Still remembers!
```

### Implementation:
1. Each turn appends `{role: "user/assistant", content: "..."}` to a window array
2. The window keeps the **last 20 messages** (10 exchanges)
3. All history is sent to Claude's API on every turn — it sees the full conversation
4. When domain switches, the context window resets

---

## 🚀 Quick Start

### Option 1: Open `index.html` directly (Frontend-only mode)
The frontend JS calls Claude API directly from the browser — no backend needed for testing!

```bash
# Just open the HTML file (requires internet for Claude API)
open templates/index.html
```

### Option 2: Run Flask Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
# Visit: http://localhost:5000
```

### Option 3: Production with Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 🌐 REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Send a message, get contextual response |
| `GET`  | `/api/session/:id` | Retrieve session history |
| `DELETE` | `/api/session/:id` | Clear session memory |
| `GET`  | `/api/sessions` | List all active sessions |
| `GET`  | `/api/health` | Health check |
| `GET`  | `/api/domains` | List available domains |

### Example API Call:

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Where is my order?",
    "session_id": "abc123",
    "domain": "ecommerce"
  }'
```

### Response:
```json
{
  "session_id": "abc123",
  "response": "I'd be happy to help track your order! Could you share your order number?",
  "intent": "order_status",
  "confidence": 0.85,
  "suggestions": ["Track my order", "Cancel my order", "Request a refund"],
  "context_length": 1
}
```

---

## 🎭 Supported Domains

| Domain | Agent Name | Expertise |
|--------|-----------|-----------|
| 🛒 E-Commerce | Aria | Orders, returns, refunds, shipping, products |
| 🏦 Banking | Nova | Accounts, loans, cards, fraud, transfers |
| 🤖 General | Claude | General Q&A, research, writing, advice |

---

## ⚙️ Configuration

Set environment variables in a `.env` file:

```env
SECRET_KEY=your-flask-secret-key
```

The Claude API key is handled by the Anthropic platform when deployed on Claude.ai artifacts.
For standalone deployment, add your API key in `chatbot.js`:
```javascript
headers: {
  "x-api-key": "your-anthropic-api-key",
  ...
}
```

---

## 🔧 Extending the Chatbot

### Add a New Domain:
1. Add domain config to `domain_configs.py` → `DOMAIN_CONFIGS`
2. Add intent patterns to `INTENT_PATTERNS`
3. Add suggestions to `SUGGESTIONS` in `chatbot.js`
4. Add quick prompts to `DOMAINS` in `chatbot.js`

### Fine-tune for Custom Data:
Replace the Claude API call with your locally fine-tuned model:
```python
# In chatbot_engine.py, swap Claude API for local model:
from transformers import pipeline
chatbot_pipeline = pipeline("text-generation", model="your-fine-tuned-model")
```

---

## 🧪 Training on Domain-Specific Data

For production fine-tuning on your own data:

```python
# Fine-tune DialoGPT on your chat logs
from transformers import (AutoTokenizer, AutoModelForCausalLM, 
                           TrainingArguments, Trainer)

model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")

# Load your domain-specific chat data
# train_dataset = load_your_chat_logs("data/support_chats.json")

training_args = TrainingArguments(
    output_dir="./models/domain-chatbot",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    save_steps=500,
    logging_steps=100,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)
trainer.train()
```

---

## 📊 Features

- ✅ **Contextual Memory** — Sliding window of last 10 exchanges
- ✅ **Multi-Domain** — E-Commerce, Banking, General personas
- ✅ **Intent Detection** — Keyword-based intent classification
- ✅ **Smart Suggestions** — Context-aware follow-up prompts
- ✅ **Session Management** — Persistent sessions via REST API
- ✅ **Dark UI** — Professional chat interface
- ✅ **REST API** — Easy business integration
- ✅ **Mobile Responsive** — Works on all devices
=======
AI Chatbot with Contextual Memory

Overview
This project is an AI-powered chatbot capable of remembering previous interactions and generating contextual responses.

 Features
- Context-aware conversation
- Streamlit UI
- Session memory
- Intelligent responses

 Technologies Used
- Python
- Streamlit
- NLP

 Installation

```bash
pip install -r requirements.txt
streamlit run app.py
```

 Author
Jayaprakash
 351d724dbf98d79c9e712a1ae1b0845cd814d168
