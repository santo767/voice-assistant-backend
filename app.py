from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import pyjokes
import re
import math
import os

app = Flask(__name__)
CORS(app)

def get_current_time():
    now = datetime.datetime.now()
    return now.strftime("The current time is %I:%M %p")

def get_current_date():
    today = datetime.date.today()
    return today.strftime("Today's date is %B %d, %Y")

def tell_joke():
    return pyjokes.get_joke()

def solve_math(expression):
    try:
        # Replace words with symbols
        expression = expression.lower().replace("plus", "+").replace("minus", "-").replace("into", "*").replace("by", "/")
        result = eval(expression)
        return f"The answer is {result}"
    except:
        return "Sorry, I couldn't calculate that."

def needs_google_search(command):
    keywords = ["who is", "what is", "how is", "how does", "what is meant by", "tell me", "search"]
    return any(command.lower().startswith(k) for k in keywords)

@app.route("/command", methods=["POST"])
def handle_command():
    data = request.get_json()
    command = data.get("command", "").lower()

    if "time" in command:
        return jsonify(reply=get_current_time())
    elif "date" in command:
        return jsonify(reply=get_current_date())
    elif "joke" in command:
        return jsonify(reply=tell_joke())
    elif re.search(r"\d+ [\+\-\*/] \d+", command) or any(op in command for op in ["plus", "minus", "into", "by"]):
        return jsonify(reply=solve_math(command))
    elif command.startswith("play"):
        search_query = command.replace("play", "").strip().replace(" ", "+")
        youtube_url = f"https://www.youtube.com/results?search_query={search_query}"
        return jsonify(reply=f"Playing {search_query.replace('+', ' ')} on YouTube.", navigate=youtube_url)
    elif needs_google_search(command):
        search_query = command.replace("search", "").strip().replace(" ", "+")
        google_url = f"https://www.google.com/search?q={search_query}"
        return jsonify(reply="Let me search that for you.", navigate=google_url)
    else:
        return jsonify(reply="I'm not sure, let me search that for you.", navigate=f"https://www.google.com/search?q={command.replace(' ', '+')}")

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
