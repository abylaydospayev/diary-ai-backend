"""
app.py
Flask API server for AI memory system.
Provides REST endpoints for storing diary entries, searching similar entries, and retrieving journal data.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from embed_store import add_entry, search_memory, load_entries

from openai import OpenAI # ✅ 1. Import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

# ✅ 2. Create an OpenAI client. It will automatically use the OPENAI_API_KEY from your .env file
client = OpenAI() 


app = Flask(__name__)
CORS(app)  # Enables CORS for all routes

@app.route("/memory", methods=["POST"])
def memory():
    """
    Store a new diary entry with AI reflection and return similar past entries.
    Expected JSON: {"entry": "diary text", "reflection": "AI response"}
    """
    data = request.get_json()
    if not data or "entry" not in data:
        return jsonify({"error": "Missing entry text"}), 400

    entry_text = data["entry"]
    reflection = data.get("reflection", "")  # AI reflection is optional
    similar = add_entry(entry_text, reflection)
    return jsonify(similar)

@app.route("/search", methods=["POST"])
def search():
    """
    Search for semantically similar past diary entries.
    Expected JSON: {"entry": "current diary text"}
    """
    data = request.get_json()
    if not data or "entry" not in data:
        return jsonify({"error": "Missing entry text"}), 400

    entry_text = data["entry"]
    matches = search_memory(entry_text)
    return jsonify(matches)

@app.route("/entries", methods=["GET"])
def get_entries():
    try:
        entries = load_entries()
        return jsonify(entries)
    except Exception as e:
        print("❌ Error loading entries:", e)
        return jsonify({"error": "Failed to load entries", "details": str(e)}), 500

@app.route("/generate", methods=["POST"])
def generate_reflection():
    try:
        data = request.get_json()
        prompt = data.get("prompt", "")
        if not prompt:
            return jsonify({"error": "Missing prompt"}), 400

        # ✅ 3. Use the new client.chat.completions.create method
        response = client.chat.completions.create(
            model="gpt-4o",  # <- or gpt-3.5-turbo, whichever you're using
            messages=[
                {"role": "system", "content": "You are a kind, thoughtful reflection companion."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        return jsonify({"response": response.choices[0].message.content.strip()})
    except Exception as e:
        print("❌ OpenAI error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)