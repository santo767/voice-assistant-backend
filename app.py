from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import webbrowser
import re

app = Flask(__name__)
CORS(app)

@app.route("/command", methods=["POST"])
def command():
    data = request.get_json()
    command = data.get("command", "").lower()

    reply = "I'm not sure how to respond to that."
    action = None
    url = None

    # Greeting
    if any(greet in command for greet in ["hello", "hi", "hey", "good morning", "good evening"]):
        reply = "Hello! How can I assist you today?"

    # Time
    elif "time" in command:
        now = datetime.datetime.now().strftime("%I:%M %p")
        reply = f"The current time is {now}."

    # Date
    elif "date" in command:
        today = datetime.datetime.now().strftime("%B %d, %Y")
        reply = f"Today's date is {today}."

    # Joke
    elif "joke" in command:
        reply = "Why did the computer catch a cold? Because it left its Windows open!"

    # Math calculation
    elif re.search(r'\d+[\+\-\*/]\d+', command):
        try:
            result = eval(command)
            reply = f"The answer is {result}"
        except:
            reply = "Sorry, I couldn't solve that."

    # YouTube Search
    elif command.startswith("play "):
        query = command.replace("play ", "")
        reply = f"Playing {query} on YouTube."
        action = "open_youtube"
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"

    # Google Search for general queries
    elif any(command.startswith(q) for q in ["who is", "what is", "how does", "how is", "what is meant by", "tell me", "search", "find"]):
        reply = f"Searching Google for {command}."
        action = "open_google"
        url = f"https://www.google.com/search?q={command.replace(' ', '+')}"

    return jsonify({
        "reply": reply,
        "action": action,
        "url": url
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
