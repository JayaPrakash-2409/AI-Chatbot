"""
AI Chatbot with Contextual Memory
Flask Backend + REST API
All files in a single flat folder
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import uuid
import os
from datetime import datetime
from chatbot_engine import ContextualChatbot

# Serve everything from the same flat directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE_DIR, template_folder=BASE_DIR)
app.secret_key = os.environ.get("SECRET_KEY", "chatbot-secret-key-2024")
CORS(app)

chatbot = ContextualChatbot()
session_store = {}


def get_or_create_session(session_id=None):
    if not session_id or session_id not in session_store:
        session_id = str(uuid.uuid4())
        session_store[session_id] = {
            "id": session_id,
            "created_at": datetime.now().isoformat(),
            "messages": [],
            "context_window": [],
            "user_profile": {}
        }
    return session_id, session_store[session_id]


@app.route("/")
def index():
    return send_file(os.path.join(BASE_DIR, "index.html"))


@app.route("/<path:filename>")
def static_files(filename):
    return send_file(os.path.join(BASE_DIR, filename))


@app.route("/api/chat", methods=["POST"])
def chat():
    """Main chat endpoint with contextual memory"""
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Message is required"}), 400

    user_message = data["message"].strip()
    session_id = data.get("session_id")
    domain = data.get("domain", "ecommerce")

    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    session_id, sess = get_or_create_session(session_id)
    sess["messages"].append({
        "role": "user",
        "content": user_message,
        "timestamp": datetime.now().isoformat()
    })

    response_data = chatbot.generate_response(
        message=user_message,
        context_window=sess["context_window"],
        domain=domain,
        session_history=sess["messages"]
    )

    sess["context_window"].append({"role": "user", "content": user_message})
    sess["context_window"].append({"role": "assistant", "content": response_data["response"]})
    if len(sess["context_window"]) > 20:
        sess["context_window"] = sess["context_window"][-20:]

    sess["messages"].append({
        "role": "assistant",
        "content": response_data["response"],
        "timestamp": datetime.now().isoformat(),
        "intent": response_data.get("intent", "general"),
        "confidence": response_data.get("confidence", 1.0)
    })

    return jsonify({
        "session_id": session_id,
        "response": response_data["response"],
        "intent": response_data.get("intent", "general"),
        "confidence": response_data.get("confidence", 1.0),
        "suggestions": response_data.get("suggestions", []),
        "context_length": len(sess["context_window"]) // 2
    })


@app.route("/api/session/<session_id>", methods=["GET"])
def get_session(session_id):
    if session_id not in session_store:
        return jsonify({"error": "Session not found"}), 404
    sess = session_store[session_id]
    return jsonify({
        "session_id": session_id,
        "created_at": sess["created_at"],
        "message_count": len(sess["messages"]),
        "messages": sess["messages"]
    })


@app.route("/api/session/<session_id>", methods=["DELETE"])
def clear_session(session_id):
    if session_id in session_store:
        session_store[session_id]["messages"] = []
        session_store[session_id]["context_window"] = []
        return jsonify({"message": "Session cleared", "session_id": session_id})
    return jsonify({"error": "Session not found"}), 404


@app.route("/api/sessions", methods=["GET"])
def list_sessions():
    sessions = [
        {"session_id": sid, "created_at": s["created_at"], "message_count": len(s["messages"])}
        for sid, s in session_store.items()
    ]
    return jsonify({"sessions": sessions, "total": len(sessions)})


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "active_sessions": len(session_store),
        "model": "claude-sonnet-4-20250514",
        "version": "1.0.0"
    })


@app.route("/api/domains", methods=["GET"])
def get_domains():
    return jsonify({"domains": [
        {"id": "ecommerce", "name": "E-Commerce Support", "icon": "🛒"},
        {"id": "banking",   "name": "Banking & Finance",  "icon": "🏦"},
        {"id": "general",   "name": "General Assistant",  "icon": "🤖"}
    ]})


if __name__ == "__main__":
    print("🤖 Contextual Memory Chatbot starting...")
    print("📍 Visit: http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
