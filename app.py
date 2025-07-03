from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import re
import pyjokes

app = Flask(__name__)
CORS(app)

@app.route("/command", methods=["POST"])
def handle_command():
    data = request.get_json()
    command = data.get("command", "").lower()

    response = "I'm not sure how to respond to that."
    navigate = None  # to be sent to frontend if YouTube or Google needed

    if any(greet in command for greet in ["hello", "hi", "hey", "good morning", "good evening"]):
        response = "Hello! How can I help you?"

    elif "time" in command:
        now = datetime.datetime.now().strftime("%I:%M %p")
        response = f"The current time is {now}"

    elif "date" in command:
        today = datetime.datetime.now().strftime("%B %d, %Y")
        response = f"Today's date is {today}"

    elif "joke" in command:
        response = pyjokes.get_joke()

    elif re.search(r"[\d+\-*/.]+", command):
        try:
            result = eval(command)
            response = f"The result is {result}"
        except:
            response = "Sorry, I couldn't solve that."

    elif command.startswith("play "):
        topic = command.replace("play", "").strip()
        response = f"Playing {topic} on YouTube."
        navigate = f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}"

    elif command.startswith(("what is", "who is", "how does", "how is", "tell me", "search", "define", "explain", "what do you mean by", "what's")):
        query = command
        response = f"Here's what I found for '{query}' on Google."
        navigate = f"https://www.google.com/search?q={query.replace(' ', '+')}"

    return jsonify({"reply": response, "navigate": navigate})
from waitress import serve

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000)
