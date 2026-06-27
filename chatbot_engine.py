"""
Chatbot Engine with Contextual Memory
Uses Claude API as the transformer backbone
Supports E-Commerce, Banking, and General domains
"""

import json
import re
from typing import List, Dict, Optional
from domain_configs import DOMAIN_CONFIGS, INTENT_PATTERNS


class ContextualChatbot:
    """
    AI Chatbot Engine with:
    - Sliding context window memory
    - Domain-specific personas
    - Intent detection
    - Suggested follow-up questions
    """

    def __init__(self):
        self.domain_configs = DOMAIN_CONFIGS
        self.intent_patterns = INTENT_PATTERNS
        self.max_context_tokens = 4000

    def detect_intent(self, message: str, domain: str) -> tuple[str, float]:
        """Detect user intent from message"""
        message_lower = message.lower()
        patterns = self.intent_patterns.get(domain, self.intent_patterns["general"])

        best_intent = "general_query"
        best_score = 0.0

        for intent, keywords in patterns.items():
            score = sum(1 for kw in keywords if kw in message_lower)
            if score > best_score:
                best_score = score
                best_intent = intent

        confidence = min(best_score / 3.0, 1.0) if best_score > 0 else 0.3
        return best_intent, confidence

    def build_system_prompt(self, domain: str, context_summary: str = "") -> str:
        """Build domain-specific system prompt"""
        config = self.domain_configs.get(domain, self.domain_configs["general"])

        base_prompt = f"""You are {config['name']}, an AI customer support assistant for {config['company']}.

PERSONALITY: {config['personality']}

YOUR EXPERTISE:
{chr(10).join(f"- {item}" for item in config['expertise'])}

IMPORTANT RULES:
1. Always maintain context from previous messages in the conversation
2. Reference earlier parts of the conversation when relevant (e.g., "As you mentioned earlier...")
3. Be concise but thorough — answer in 2-4 sentences unless complexity requires more
4. If you don't know something specific, say so and offer alternatives
5. Always end with a helpful follow-up question or offer further assistance
6. Use a warm, professional tone

DOMAIN-SPECIFIC POLICIES:
{chr(10).join(f"- {policy}" for policy in config['policies'])}

RESPONSE FORMAT:
- Start with acknowledging any context from earlier in conversation if relevant
- Provide clear, actionable answer
- Offer 1-2 follow-up options or next steps"""

        if context_summary:
            base_prompt += f"\n\nCONVERSATION CONTEXT SO FAR:\n{context_summary}"

        return base_prompt

    def build_context_summary(self, context_window: List[Dict]) -> str:
        """Summarize context window for system prompt"""
        if not context_window:
            return ""

        summary_parts = []
        for msg in context_window[-6:]:  # Last 3 exchanges
            role = "Customer" if msg["role"] == "user" else "Assistant"
            summary_parts.append(f"{role}: {msg['content'][:200]}")

        return "\n".join(summary_parts)

    def get_suggestions(self, intent: str, domain: str) -> List[str]:
        """Get contextual follow-up suggestions"""
        suggestions_map = {
            "ecommerce": {
                "order_status": ["Track my order", "Cancel my order", "Request a refund"],
                "return_refund": ["Start a return", "Refund timeline", "Exchange instead"],
                "product_inquiry": ["Check availability", "Compare products", "Read reviews"],
                "shipping": ["Shipping costs", "Express delivery", "International shipping"],
                "general_query": ["View my orders", "Browse products", "Contact support"]
            },
            "banking": {
                "account_inquiry": ["Check balance", "View transactions", "Account settings"],
                "transaction_issue": ["Dispute a charge", "Report fraud", "Transaction history"],
                "loan_inquiry": ["Loan calculator", "Apply for loan", "Current rates"],
                "card_services": ["Block my card", "Set spending limit", "Card benefits"],
                "general_query": ["View accounts", "Transfer money", "Find ATM"]
            },
            "general": {
                "general_query": ["Tell me more", "Related topics", "Get help"]
            }
        }

        domain_suggestions = suggestions_map.get(domain, suggestions_map["general"])
        return domain_suggestions.get(intent, domain_suggestions.get("general_query", []))

    def generate_response(
        self,
        message: str,
        context_window: List[Dict],
        domain: str = "ecommerce",
        session_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Generate contextual response using Claude API
        This function is called from app.py and makes the API call via the frontend
        """
        # Detect intent
        intent, confidence = self.detect_intent(message, domain)

        # Get suggestions
        suggestions = self.get_suggestions(intent, domain)

        # Build context summary
        context_summary = self.build_context_summary(context_window)

        # Build system prompt
        system_prompt = self.build_system_prompt(domain, context_summary)

        # Return structured data for the frontend to use
        return {
            "system_prompt": system_prompt,
            "intent": intent,
            "confidence": confidence,
            "suggestions": suggestions,
            "context_window": context_window,
            "response": "__NEEDS_API_CALL__"  # Frontend handles actual API call
        }

    def get_api_payload(
        self,
        message: str,
        context_window: List[Dict],
        domain: str = "ecommerce"
    ) -> Dict:
        """Build complete API payload for Claude"""
        intent, confidence = self.detect_intent(message, domain)
        context_summary = self.build_context_summary(context_window)
        system_prompt = self.build_system_prompt(domain, context_summary)
        suggestions = self.get_suggestions(intent, domain)

        # Build messages array with full context
        messages = []
        for msg in context_window:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        messages.append({"role": "user", "content": message})

        return {
            "system_prompt": system_prompt,
            "messages": messages,
            "intent": intent,
            "confidence": confidence,
            "suggestions": suggestions
        }
