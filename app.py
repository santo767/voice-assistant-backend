from flask import Flask, request, jsonify
from flask_cors import CORS
import webbrowser
import re
import openai
import os
import time

app = Flask(__name__)
CORS(app)

# 🔑 Put your real OpenAI API key here (keep it secret!)
openai.api_key = "sk-..."

@app.route("/")
def home():
    return jsonify({"message": "Voice Assistant Backend is running"})

@app.route("/command", methods=["POST"])
def handle_command():
    data = request.get_json()
    command = data.get("command", "").lower()
    print("Received command:", command)

    try:
        # ✅ Greeting
        if "my name is" in command:
            name = command.split("my name is")[-1].strip().title()
            return jsonify({"reply": f"Nice to meet you, {name}!"})

        # ✅ Play on YouTube
        elif command.startswith("play"):
            query = command.replace("play", "").strip()
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            return jsonify({"reply": f"Playing {query} on YouTube."})

        # ✅ Google Search (for questions like who, what, how, etc.)
        elif command.startswith(("who is", "what is", "how is", "how does", "what is meant by", "tell me")):
            webbrowser.open(f"https://www.google.com/search?q={command}")
            return jsonify({"reply": f"Searching Google for: {command}"})

        # ✅ GPT response
        elif command.startswith("use gpt"):
            prompt = command.replace("use gpt", "").strip()
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            gpt_reply = response.choices[0].message.content.strip()
            return jsonify({"reply": gpt_reply})

        # ✅ Math calculation (basic)
        elif re.match(r"^[\d\s\+\-\*\/\.\(\)]+$", command):
            try:
                result = eval(command)
                return jsonify({"reply": f"The answer is {result}"})
            except:
                return jsonify({"reply": "I couldn't solve that math expression."})

        # ❌ Unknown command fallback
        else:
            webbrowser.open(f"https://www.google.com/search?q={command}")
            return jsonify({"reply": f"I'm not sure, but I searched Google for: {command}"})

    except Exception as e:
        print("Error:", e)
        return jsonify({"reply": "⚠️ An error occurred while processing your request."})

# ✅ For Render (Production) - Use waitress server
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=10000)
