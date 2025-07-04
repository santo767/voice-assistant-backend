from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import datetime
import re
import pyjokes
import pytz

app = Flask(__name__)
CORS(app)

@app.route("/command", methods=["POST"])
def handle_command():
    data = request.get_json()
    command = data.get("command", "").lower()
    
    response = "I'm not sure how to respond to that."
    navigate = None  # to be sent to frontend if YouTube or Google needed
    
    # Debug logging
    print(f"Received command: {command}")
    
    if any(greet in command for greet in ["hello", "hi", "hey", "good morning", "good evening"]):
        response = "Hello! How can I help you?"
    
    elif "time" in command:
        india_time = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
        response = f"The current time is {india_time.strftime('%I:%M %p')}"
    
    elif "date" in command:
        india_date = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
        response = f"Today's date is {india_date.strftime('%B %d, %Y')}"
    
    elif "joke" in command:
        response = pyjokes.get_joke()
    
    elif re.search(r"[\d+\-*/.]+", command):
        try:
            # Safer evaluation - only allow basic math operations
            allowed_chars = set('0123456789+-*/.() ')
            if all(c in allowed_chars for c in command):
                result = eval(command)
                response = f"The result is {result}"
            else:
                response = "Sorry, I can only perform basic math operations."
        except Exception as e:
            print(f"Math error: {e}")
            response = "Sorry, I couldn't solve that."
    
    elif command.startswith("play "):
        topic = command.replace("play", "").strip()
        response = f"Playing {topic} on YouTube."
        navigate = f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}"
    
    elif command.startswith(("what is", "who is", "how does", "how is", "tell me", "search", "define", "explain", "what do you mean by", "what's")):
        query = command
        response = f"Here's what I found for '{query}' on Google."
        navigate = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    
    # Debug logging
    print(f"Response: {response}")
    print(f"Navigate: {navigate}")
    
    return jsonify({"reply": response, "navigate": navigate})

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Voice Assistant Backend is running!", "status": "active"})

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.datetime.now().isoformat()})

if __name__ == "__main__":
    from waitress import serve
    print("Starting Voice Assistant Backend...")
    serve(app, host="0.0.0.0", port=5000)