/**
 * NeuralChat - AI Chatbot with Contextual Memory
 * Frontend JS — calls Claude API directly with sliding context window
 */

const CLAUDE_API_URL = "https://api.anthropic.com/v1/messages";
const CLAUDE_MODEL = "claude-sonnet-4-20250514";

// ===== STATE =====
const state = {
  sessionId: generateId(),
  domain: "ecommerce",
  contextWindow: [],        // Sliding context window
  messageCount: 0,
  isTyping: false,
  lastIntent: null,
  lastConfidence: 0
};

// Domain configs
const DOMAINS = {
  ecommerce: {
    name: "Aria",
    avatarLetter: "A",
    title: "E-Commerce Support",
    personality: `You are Aria, a friendly and helpful AI customer support assistant for ShopSmart E-Commerce.
Your expertise: order tracking, returns & refunds, product info, shipping, payments, promotions.
Policies: Free returns within 30 days, standard shipping 3-5 days, express 1-2 days, refunds in 5-7 business days.`,
    quickPrompts: [
      { icon: "📦", label: "Track an order", msg: "Where is my order #12345?" },
      { icon: "↩", label: "Return an item", msg: "I want to return a damaged item I received" },
      { icon: "💰", label: "Refund policy", msg: "What is your refund policy?" },
      { icon: "🚚", label: "Shipping info", msg: "How long does shipping take?" }
    ]
  },
  banking: {
    name: "Nova",
    avatarLetter: "N",
    title: "Banking & Finance",
    personality: `You are Nova, a professional and trustworthy AI assistant for SecureBank Financial Services.
Your expertise: account inquiries, transactions, loans, cards, fraud prevention, transfers, investments.
Policies: Never share sensitive account data, all sensitive actions need identity verification, fraud must be reported within 60 days.`,
    quickPrompts: [
      { icon: "💳", label: "Check balance", msg: "How do I check my account balance?" },
      { icon: "🔒", label: "Block my card", msg: "I lost my card, how do I block it immediately?" },
      { icon: "💸", label: "Transfer money", msg: "How do I transfer money to another account?" },
      { icon: "📊", label: "Loan rates", msg: "What are your current personal loan interest rates?" }
    ]
  },
  general: {
    name: "Claude",
    avatarLetter: "C",
    title: "General Assistant",
    personality: `You are a knowledgeable, helpful AI assistant. You can assist with a wide range of topics including research, writing, problem-solving, recommendations, and general Q&A.`,
    quickPrompts: [
      { icon: "💡", label: "Get help", msg: "What can you help me with?" },
      { icon: "📝", label: "Write something", msg: "Help me write a professional email" },
      { icon: "🔍", label: "Research", msg: "Explain how transformer models work" },
      { icon: "🎯", label: "Recommend", msg: "Recommend a good productivity system" }
    ]
  }
};

// Intent detection patterns (client-side)
const INTENT_PATTERNS = {
  ecommerce: {
    "order_status": ["order", "track", "tracking", "shipped", "delivery", "package", "arrived", "where is"],
    "return_refund": ["return", "refund", "money back", "exchange", "send back", "damaged", "broken", "cancel"],
    "shipping": ["shipping", "delivery", "ship", "express", "standard", "address"],
    "product_inquiry": ["product", "available", "stock", "color", "size", "review", "compare"],
    "payment": ["payment", "charge", "bill", "invoice", "credit", "debit", "price", "cost"]
  },
  banking: {
    "account_inquiry": ["balance", "account", "statement", "how much", "funds"],
    "transaction_issue": ["transaction", "transfer", "charge", "history", "activity"],
    "fraud_security": ["fraud", "stolen", "unauthorized", "block", "freeze", "lost card"],
    "loan_inquiry": ["loan", "mortgage", "borrow", "credit", "interest", "apply"],
    "card_services": ["card", "pin", "limit", "activate", "new card"]
  },
  general: {
    "help_request": ["help", "assist", "how to", "guide", "steps"],
    "information": ["what", "who", "when", "where", "why", "explain"],
    "recommendation": ["recommend", "suggest", "best", "should i", "advice"]
  }
};

function detectIntent(message, domain) {
  const msg = message.toLowerCase();
  const patterns = INTENT_PATTERNS[domain] || INTENT_PATTERNS.general;
  let best = { intent: "general_query", score: 0 };

  for (const [intent, keywords] of Object.entries(patterns)) {
    const score = keywords.filter(kw => msg.includes(kw)).length;
    if (score > best.score) best = { intent, score };
  }

  const confidence = Math.min(best.score / 3, 1);
  return { intent: best.intent, confidence };
}

const SUGGESTIONS = {
  ecommerce: {
    "order_status": ["Track my order", "Cancel my order", "Request a refund"],
    "return_refund": ["Start a return", "Refund timeline", "Exchange instead"],
    "shipping": ["Shipping costs", "Express delivery", "Track shipment"],
    "general_query": ["View my orders", "Return policy", "Contact support"]
  },
  banking: {
    "account_inquiry": ["View transactions", "Account settings", "Download statement"],
    "fraud_security": ["Dispute a charge", "Report fraud", "New card"],
    "loan_inquiry": ["Loan calculator", "Apply now", "Current rates"],
    "general_query": ["Transfer money", "Check balance", "Find ATM"]
  },
  general: {
    "general_query": ["Tell me more", "Related topics", "Help with something else"]
  }
};

function getSuggestions(intent, domain) {
  const d = SUGGESTIONS[domain] || SUGGESTIONS.general;
  return d[intent] || d["general_query"] || [];
}

// ===== CORE: Build System Prompt with Memory Context =====
function buildSystemPrompt(domain) {
  const config = DOMAINS[domain];
  let prompt = config.personality + "\n\n";

  prompt += `IMPORTANT RULES:
1. You have access to the full conversation history. Use it actively — reference earlier messages when relevant.
2. When the user refers to something mentioned before (e.g., "that order", "the problem I mentioned"), look back at the conversation context.
3. Be concise and actionable — 2-4 sentences unless more detail is needed.
4. Always end with a helpful follow-up offer or next step.
5. Use a warm, professional tone that matches your persona.
6. If you're unsure about something specific, acknowledge it and offer alternatives.`;

  return prompt;
}

// ===== CORE: Call Claude API =====
async function callClaudeAPI(userMessage) {
  const systemPrompt = buildSystemPrompt(state.domain);

  // Build messages with full context window
  const messages = [
    ...state.contextWindow,
    { role: "user", content: userMessage }
  ];

  const response = await fetch(CLAUDE_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": "YOUR_API_KEY",
      "anthropic-dangerous-direct-browser-access": "true"
    },
    body: JSON.stringify({
      model: CLAUDE_MODEL,
      max_tokens: 1000,
      system: systemPrompt,
      messages: messages
    })
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.error?.message || "API call failed");
  }

  const data = await response.json();
  const assistantMsg = data.content?.[0]?.text || "I'm sorry, I couldn't generate a response.";

  // Update context window (sliding — keep last 10 exchanges = 20 messages)
  state.contextWindow.push({ role: "user", content: userMessage });
  state.contextWindow.push({ role: "assistant", content: assistantMsg });

  if (state.contextWindow.length > 20) {
    state.contextWindow = state.contextWindow.slice(-20);
  }

  return assistantMsg;
}

// ===== UI FUNCTIONS =====
function generateId() {
  return Math.random().toString(36).substr(2, 8).toUpperCase();
}

function formatTime(date = new Date()) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function updateSidebar() {
  const el = (id) => document.getElementById(id);
  el('sessionId').textContent = state.sessionId;
  el('contextDepth').textContent = `${state.contextWindow.length / 2 | 0} exchanges`;

  if (state.lastIntent) {
    el('lastIntent').textContent = state.lastIntent.replace(/_/g, ' ');
    el('confidenceFill').style.width = `${state.lastConfidence * 100}%`;
  }
}

function showWelcome(show) {
  const welcome = document.getElementById('welcomeMessage');
  if (welcome) welcome.style.display = show ? 'flex' : 'none';
}

function appendMessage(role, content, meta = {}) {
  showWelcome(false);
  const container = document.getElementById('messagesContainer');
  const config = DOMAINS[state.domain];

  const div = document.createElement('div');
  div.className = `message ${role}`;

  const avatarLetter = role === 'bot' ? config.avatarLetter : '👤';
  const intentBadge = (role === 'bot' && meta.intent)
    ? `<span class="intent-badge">${meta.intent.replace(/_/g, ' ')}</span>`
    : '';

  div.innerHTML = `
    <div class="msg-avatar">${role === 'bot' ? config.avatarLetter : '?'}</div>
    <div class="msg-content">
      <div class="msg-bubble">${formatText(content)}</div>
      <div class="msg-meta">${formatTime()}${intentBadge}</div>
    </div>
  `;

  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
}

function formatText(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>');
}

function showTyping() {
  const container = document.getElementById('messagesContainer');
  const div = document.createElement('div');
  div.className = 'typing-indicator';
  div.id = 'typingIndicator';
  const config = DOMAINS[state.domain];

  div.innerHTML = `
    <div class="msg-avatar" style="background:linear-gradient(135deg,#6c63ff,#ff6584);color:white">${config.avatarLetter}</div>
    <div class="typing-dots">
      <span></span><span></span><span></span>
    </div>
  `;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function hideTyping() {
  const indicator = document.getElementById('typingIndicator');
  if (indicator) indicator.remove();
}

function showSuggestions(suggestions) {
  const bar = document.getElementById('suggestionsBar');
  const list = document.getElementById('suggestionsList');

  if (!suggestions || suggestions.length === 0) {
    bar.style.display = 'none';
    return;
  }

  list.innerHTML = suggestions.map(s =>
    `<button class="suggestion-chip" onclick="sendMessage('${s}')">${s}</button>`
  ).join('');

  bar.style.display = 'block';
}

function updateQuickPrompts() {
  const config = DOMAINS[state.domain];
  const container = document.getElementById('quickPromptList');

  container.innerHTML = config.quickPrompts.map(p =>
    `<button class="quick-btn" data-msg="${p.msg}">${p.icon} ${p.label}</button>`
  ).join('');

  // Re-attach listeners
  container.querySelectorAll('.quick-btn').forEach(btn => {
    btn.addEventListener('click', () => sendMessage(btn.dataset.msg));
  });
}

function updateAgentInfo() {
  const config = DOMAINS[state.domain];
  document.getElementById('agentAvatar').textContent = config.avatarLetter;
  document.getElementById('agentName').textContent = config.name;
  document.querySelector('.agent-status').innerHTML =
    `<span class="status-dot"></span> Online · ${config.title}`;
}

// ===== SEND MESSAGE =====
async function sendMessage(text = null) {
  const input = document.getElementById('messageInput');
  const message = text || input.value.trim();

  if (!message || state.isTyping) return;

  state.isTyping = true;
  if (!text) input.value = '';
  resizeTextarea(input);

  document.getElementById('sendBtn').disabled = true;
  document.getElementById('charCount').textContent = '0 / 500';
  showSuggestions([]);

  // Detect intent
  const { intent, confidence } = detectIntent(message, state.domain);
  state.lastIntent = intent;
  state.lastConfidence = confidence;
  state.messageCount++;

  // Show user message
  appendMessage('user', message);

  // Show typing
  showTyping();
  updateSidebar();

  try {
    // Call Claude API
    const response = await callClaudeAPI(message);
    hideTyping();

    // Show bot response
    appendMessage('bot', response, { intent });

    // Show suggestions
    const suggestions = getSuggestions(intent, state.domain);
    showSuggestions(suggestions);

  } catch (error) {
    hideTyping();
    const container = document.getElementById('messagesContainer');
    const div = document.createElement('div');
    div.className = 'message bot';
    div.innerHTML = `
      <div class="msg-avatar" style="background:#ff6584;color:white">!</div>
      <div class="msg-content">
        <div class="error-bubble">⚠️ ${error.message || 'Something went wrong. Please try again.'}</div>
        <div class="msg-meta">${formatTime()}</div>
      </div>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  } finally {
    state.isTyping = false;
    document.getElementById('sendBtn').disabled = false;
    updateSidebar();
  }
}

function resizeTextarea(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
  updateSidebar();
  updateAgentInfo();

  const input = document.getElementById('messageInput');
  const sendBtn = document.getElementById('sendBtn');

  // Enter to send (Shift+Enter for newline)
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  input.addEventListener('input', () => {
    resizeTextarea(input);
    const len = input.value.length;
    document.getElementById('charCount').textContent = `${len} / 500`;
    if (len > 500) input.value = input.value.slice(0, 500);
  });

  sendBtn.addEventListener('click', () => sendMessage());

  // Domain switching
  document.querySelectorAll('.domain-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.domain-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.domain = btn.dataset.domain;
      state.contextWindow = []; // Reset context on domain change
      state.sessionId = generateId();
      updateAgentInfo();
      updateQuickPrompts();
      updateSidebar();

      // Clear chat
      const container = document.getElementById('messagesContainer');
      container.innerHTML = '';

      // Show welcome again
      container.innerHTML = `
        <div class="welcome-message" id="welcomeMessage">
          <div class="welcome-icon">⬡</div>
          <h2>Hi, I'm ${DOMAINS[state.domain].name}!</h2>
          <p>Switched to <strong>${DOMAINS[state.domain].title}</strong> mode. Context memory has been reset.</p>
          <div class="welcome-features">
            <div class="feature-tag">🧠 Context Memory</div>
            <div class="feature-tag">🎯 Intent Detection</div>
            <div class="feature-tag">💬 Multi-turn Dialogue</div>
          </div>
        </div>`;

      showSuggestions([]);
    });
  });

  // Quick prompts
  document.querySelectorAll('.quick-btn').forEach(btn => {
    btn.addEventListener('click', () => sendMessage(btn.dataset.msg));
  });

  // Clear memory
  document.getElementById('clearMemory').addEventListener('click', () => {
    state.contextWindow = [];
    state.sessionId = generateId();
    state.lastIntent = null;
    state.lastConfidence = 0;
    updateSidebar();

    const container = document.getElementById('messagesContainer');
    const notice = document.createElement('div');
    notice.style.cssText = 'text-align:center;color:#555566;font-size:12px;padding:12px;';
    notice.textContent = '🗑 Memory cleared — fresh context started';
    container.appendChild(notice);
    container.scrollTop = container.scrollHeight;
  });
});