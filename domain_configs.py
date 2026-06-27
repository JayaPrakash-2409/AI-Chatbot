"""
Domain Configurations for the Contextual Chatbot
Supports: E-Commerce, Banking, General
"""

DOMAIN_CONFIGS = {
    "ecommerce": {
        "name": "Aria",
        "company": "ShopSmart E-Commerce",
        "personality": "Friendly, helpful, and solution-oriented. You care about customer satisfaction above all.",
        "expertise": [
            "Order tracking and management",
            "Returns, refunds, and exchanges",
            "Product information and recommendations",
            "Shipping and delivery queries",
            "Account and payment issues",
            "Promotions and discount codes",
            "Loyalty program management"
        ],
        "policies": [
            "Free returns within 30 days of purchase",
            "Standard shipping: 3-5 business days",
            "Express shipping: 1-2 business days",
            "Price match guarantee within 7 days",
            "Refunds processed within 5-7 business days",
            "Customer satisfaction is our #1 priority"
        ]
    },
    "banking": {
        "name": "Nova",
        "company": "SecureBank Financial Services",
        "personality": "Professional, precise, and trustworthy. You prioritize security and accuracy in all financial matters.",
        "expertise": [
            "Account balance and transaction inquiries",
            "Fund transfers and payments",
            "Loan and credit card applications",
            "Fraud detection and card blocking",
            "Interest rates and investment options",
            "Online banking support",
            "Branch and ATM locations"
        ],
        "policies": [
            "Never share full account numbers or passwords",
            "All sensitive actions require identity verification",
            "Fraud disputes must be reported within 60 days",
            "Zero liability policy for unauthorized transactions",
            "Loans subject to credit approval and terms",
            "For urgent security issues, call 1-800-SECURE"
        ]
    },
    "general": {
        "name": "Claude Assistant",
        "company": "AI Support",
        "personality": "Knowledgeable, helpful, and adaptable. You can assist with a wide range of topics.",
        "expertise": [
            "General knowledge and Q&A",
            "Problem-solving and recommendations",
            "Research and information gathering",
            "Writing and editing assistance",
            "Technical support guidance",
            "Planning and scheduling help"
        ],
        "policies": [
            "Always provide accurate and helpful information",
            "Acknowledge when information is uncertain",
            "Refer to specialists for professional advice",
            "Maintain conversational context throughout"
        ]
    }
}

INTENT_PATTERNS = {
    "ecommerce": {
        "order_status": ["order", "track", "tracking", "shipped", "delivery", "where is", "status", "package", "arrived", "delivered"],
        "return_refund": ["return", "refund", "money back", "exchange", "send back", "damaged", "broken", "wrong item", "cancel order"],
        "product_inquiry": ["product", "item", "available", "stock", "color", "size", "specification", "review", "quality", "compare"],
        "shipping": ["shipping", "delivery", "ship", "fast", "express", "standard", "international", "address", "location"],
        "payment_issue": ["payment", "charge", "bill", "invoice", "credit card", "debit", "declined", "paid", "price"],
        "account_help": ["account", "login", "password", "sign in", "profile", "email", "register", "subscription"],
        "promotion": ["discount", "coupon", "promo", "sale", "offer", "deal", "code", "voucher", "loyalty", "points"]
    },
    "banking": {
        "account_inquiry": ["balance", "account", "statement", "summary", "details", "how much", "funds", "available"],
        "transaction_issue": ["transaction", "transfer", "charge", "payment", "sent", "received", "history", "activity"],
        "fraud_security": ["fraud", "stolen", "unauthorized", "suspicious", "block", "freeze", "report", "lost card"],
        "loan_inquiry": ["loan", "mortgage", "borrow", "credit", "interest rate", "emi", "apply", "eligibility"],
        "card_services": ["card", "debit card", "credit card", "pin", "limit", "activate", "cancel card", "new card"],
        "transfer": ["transfer", "send money", "wire", "neft", "rtgs", "imps", "beneficiary", "recipient"],
        "investment": ["invest", "fixed deposit", "fd", "mutual fund", "savings", "interest", "returns", "portfolio"]
    },
    "general": {
        "information_request": ["what", "who", "when", "where", "why", "how", "explain", "tell me", "describe"],
        "help_request": ["help", "assist", "support", "guide", "show me", "how to", "steps", "tutorial"],
        "opinion_request": ["recommend", "suggest", "best", "better", "should i", "advice", "think"],
        "general_query": ["hi", "hello", "hey", "thanks", "thank you", "bye", "goodbye"]
    }
}

# Sample FAQ data for domain knowledge
DOMAIN_FAQS = {
    "ecommerce": [
        {"q": "How do I track my order?", "a": "Go to 'My Orders' in your account, click your order, and use the tracking number provided."},
        {"q": "What is your return policy?", "a": "We offer free returns within 30 days of purchase for most items in original condition."},
        {"q": "How long does shipping take?", "a": "Standard shipping takes 3-5 business days. Express shipping is 1-2 business days."},
        {"q": "How do I cancel my order?", "a": "Orders can be cancelled within 1 hour of placement. Go to My Orders > Select Order > Cancel."},
        {"q": "When will I get my refund?", "a": "Refunds are processed within 5-7 business days after we receive your returned item."},
        {"q": "Do you offer price matching?", "a": "Yes! We offer price match within 7 days of purchase if you find a lower price elsewhere."},
    ],
    "banking": [
        {"q": "How do I check my balance?", "a": "Log in to online banking, use our mobile app, or check at any ATM."},
        {"q": "How do I dispute a transaction?", "a": "Go to Account > Transactions > Select transaction > Dispute. Our team reviews within 3-5 business days."},
        {"q": "What are your loan interest rates?", "a": "Personal loans start at 8.5% APR, home loans from 6.5% APR, subject to credit approval."},
        {"q": "How do I block my card?", "a": "Immediately call 1-800-SECURE or use the app: Cards > Block Card. It takes effect instantly."},
        {"q": "What is the transfer limit?", "a": "Online transfers are limited to $10,000/day. Visit a branch for larger transfers."},
    ]
}
