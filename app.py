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
    user_command = data.get("command", "").lower()
    print("User Command:", user_command)

    reply = process_command(user_command)
    return jsonify({"reply": reply})


def process_command(command):
    # Play on YouTube
    if command.startswith("play "):
        song = command.replace("play", "").strip()
        url = f"https://www.youtube.com/results?search_query={song}"
        webbrowser.open(url)
        return f"Playing {song} on YouTube."

    # Get current time
    elif "time" in command:
        now = datetime.datetime.now().strftime("%I:%M %p")
        return f"The time is {now}."

    # Simple math (e.g., 2+2 or 10 divided by 2)
    elif any(op in command for op in ["+", "-", "*", "x", "÷", "/", "divided by"]):
        return solve_math(command)

    # Greeting with name
    elif "my name is" in command:
        name = command.split("my name is")[-1].strip()
        return f"Hello {name}, nice to meet you!"

    # Google search for questions
    elif any(command.startswith(q) for q in ["who is", "what is", "how does", "how is", "tell me", "what's", "explain", "define", "what is meant by"]):
        query = command.strip()
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return f"Here's what I found on Google for '{query}'."

    else:
        return "Sorry, I didn't understand that."


def solve_math(command):
    # Replace words with symbols
    command = command.replace("divided by", "/").replace("x", "*").replace("÷", "/")

    try:
        # Only allow numbers and operators
        expression = re.sub(r"[^0-9\.\+\-\*/]", "", command)
        result = eval(expression)
        return f"The answer is {result}"
    except:
        return "Sorry, I couldn't solve that."

if __name__ == "__main__":
    app.run(debug=True)
