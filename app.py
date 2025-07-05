from flask import Flask, request, jsonify, session
from flask_cors import CORS
from datetime import datetime
import pytz
import re
import pyjokes
import math
import requests
import random

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = "your_very_secure_secret_key"

APP_URIS = {
    "whatsapp": {"uri": "whatsapp://send", "web": "https://web.whatsapp.com"},
    "chatgpt": {"uri": "https://chat.openai.com", "web": "https://chat.openai.com"},
    "facebook": {"uri": "fb://facewebmodal/f?href=https://facebook.com", "web": "https://facebook.com"},
    "vlc": {"uri": "vlc://", "web": "https://www.videolan.org/vlc/"},
    "filemanager": {"uri": "file:///sdcard/", "web": "file:///sdcard/"},
    "calculator": {"uri": "calculator://", "web": "https://www.google.com/search?q=calculator"},
    "instagram": {"uri": "instagram://user?username=", "web": "https://www.instagram.com"},
    "youtube": {"uri": "vnd.youtube://", "web": "https://www.youtube.com"},
    "google": {"uri": "https://www.google.com", "web": "https://www.google.com"}
}

FUN_FACTS = [
    "Honey never spoils. Archaeologists have found edible honey in ancient Egyptian tombs.",
    "Bananas are berries, but strawberries are not.",
    "A day on Venus is longer than a year on Venus.",
    "Octopuses have three hearts.",
    "The Eiffel Tower can be 15 cm taller during hot days."
]

def get_user_name(command):
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    if name:
        session['user_name'] = name
        return name
    for pat in [r"my name is ([\w\s]+)", r"i am ([\w\s]+)", r"i'm ([\w\s]+)"]:
        match = re.search(pat, command, re.IGNORECASE)
        if match:
            session['user_name'] = match.group(1).strip().split()[0]
            return session['user_name']
    return session.get('user_name', "Friend")

def get_response(key, name, **kwargs):
    responses = {
        'greeting': f"Hello {name}! How can I assist you?",
        'good_morning': f"Good morning, {name}!",
        'good_night': f"Good night, {name}!",
        'time': f"{name}, the time is {kwargs.get('time')}",
        'date': f"{name}, today's date is {kwargs.get('date')}",
        'joke': f"{name}, here's a joke: {kwargs.get('joke')}",
        'fun_fact': f"{name}, did you know? {kwargs.get('fact')}",
        'math_result': f"{name}, the result is {kwargs.get('result')}",
        'math_error': f"{name}, I couldn't solve that.",
        'weather': f"{name}, here's the weather in {kwargs.get('city')} on Google.",
        'reminder_set': f"{name}, I have set a reminder: {kwargs.get('reminder')}",
        'app_open': f"{name}, opening {kwargs.get('app')} for you.",
        'location_found': f"{name}, here's {kwargs.get('location')} on Google Maps.",
        'location_unknown': f"{name}, please tell me which location to search.",
        'search': f"{name}, here's what I found for '{kwargs.get('query')}' on Google.",
        'default': f"{name}, I didn't understand that. Searching it for you..."
    }
    return responses.get(key, responses['default'])

def solve_complex_math(command):
    cmd = command.lower()
    if "square root" in cmd or "sqrt" in cmd:
        match = re.search(r'(?:square root of|sqrt of|sqrt)\s*(\d+(?:\.\d+)?)', cmd)
        if match:
            return round(math.sqrt(float(match.group(1))), 6)
    if "sin" in cmd:
        match = re.search(r'sin\s*(?:of\s*)?(\d+(?:\.\d+)?)', cmd)
        if match:
            return round(math.sin(math.radians(float(match.group(1)))), 6)
    if "cos" in cmd:
        match = re.search(r'cos\s*(?:of\s*)?(\d+(?:\.\d+)?)', cmd)
        if match:
            return round(math.cos(math.radians(float(match.group(1)))), 6)
    if "tan" in cmd:
        match = re.search(r'tan\s*(?:of\s*)?(\d+(?:\.\d+)?)', cmd)
        if match:
            return round(math.tan(math.radians(float(match.group(1)))), 6)
    if "log" in cmd:
        match = re.search(r'log\s*(?:of\s*)?(\d+(?:\.\d+)?)', cmd)
        if match:
            num = float(match.group(1))
            if num > 0:
                return round(math.log(num), 6)
    if "factorial" in cmd:
        match = re.search(r'factorial\s*(?:of\s*)?(\d+)', cmd)
        if match:
            num = int(match.group(1))
            if 0 <= num <= 100:
                return math.factorial(num)
    if "power" in cmd or "raised to" in cmd:
        match = re.search(r'(\d+(?:\.\d+)?)\s*(?:to the power of|raised to|power)\s*(\d+(?:\.\d+)?)', cmd)
        if match:
            return round(math.pow(float(match.group(1)), float(match.group(2))), 6)

    replacements = {
        "plus": "+", "minus": "-", "times": "*", "multiply": "*", "divide": "/", "divided by": "/",
        "power": "**", "pi": str(math.pi), "e": str(math.e)
    }
    for word, symbol in replacements.items():
        cmd = cmd.replace(word, symbol)
    cmd = re.sub(r"[^0-9+\-*/().e\s]", "", cmd)
    try:
        result = eval(cmd.strip())
        return round(result, 6)
    except:
        return None

def extract_location_query(command):
    command = command.lower()
    keywords = ["where is", "location of", "directions to", "navigate to", "map of", "how to go to"]
    for kw in keywords:
        if kw in command:
            return command.replace(kw, "").strip()
    return None

@app.route("/command", methods=["POST"])
def handle_command():
    data = request.get_json()
    command = data.get("command", "").strip().lower()
    name = get_user_name(command)
    navigate = None
    response = ""

    if any(kw in command for kw in ["hello", "hi", "hey"]):
        response = get_response('greeting', name)
    elif "good morning" in command:
        response = get_response('good_morning', name)
    elif "good night" in command:
        response = get_response('good_night', name)
    elif "time" in command:
        now = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%I:%M %p')
        response = get_response('time', name, time=now)
    elif "date" in command:
        today = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%B %d, %Y')
        response = get_response('date', name, date=today)
    elif "joke" in command:
        response = get_response('joke', name, joke=pyjokes.get_joke())
    elif "fun fact" in command or "something interesting" in command:
        response = get_response('fun_fact', name, fact=random.choice(FUN_FACTS))
    elif "remind me" in command or "set a reminder" in command:
        reminder = re.sub(r".*remind me to |.*set a reminder (for|to)?", "", command).strip()
        response = get_response('reminder_set', name, reminder=reminder)
    elif "weather" in command:
        match = re.search(r"weather in ([\w\s]+)", command)
        city = match.group(1).strip() if match else "your city"
        response = get_response('weather', name, city=city)
        navigate = f"https://www.google.com/search?q=weather+in+{city.replace(' ', '+')}"
    elif any(f"open {app}" in command or f"launch {app}" in command for app in APP_URIS):
        for app, urls in APP_URIS.items():
            if f"open {app}" in command or f"launch {app}" in command:
                navigate = urls
                response = get_response('app_open', name, app=app.capitalize())
                break
    elif command.startswith("play "):
        topic = command.replace("play", "").strip()
        navigate = f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}"
        response = f"{name}, playing {topic} on YouTube."
    elif any(kw in command for kw in ["where is", "directions to", "navigate to", "map of", "location of"]):
        place = extract_location_query(command)
        if place:
            navigate = f"https://www.google.com/maps/search/{place.replace(' ', '+')}"
            response = get_response('location_found', name, location=place)
        else:
            response = get_response('location_unknown', name)
    elif any(op in command for op in ["plus", "minus", "times", "multiply", "divide", "power", "sqrt", "square root", "sin", "cos", "tan", "log", "factorial"]) or re.search(r"[0-9\+\-*/]+", command):
        result = solve_complex_math(command)
        if result is not None:
            response = get_response('math_result', name, result=result)
        else:
            response = get_response('math_error', name)
    elif command.startswith(("what is", "who is", "how is", "how does", "tell me", "search", "define", "explain", "can you")) or True:
        query = command
        navigate = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        response = get_response('search', name, query=query)

    return jsonify({"reply": response, "navigate": navigate})

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Voice Assistant Backend is running!"})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == "__main__":
    from waitress import serve
    print("Starting server...")
    serve(app, host="0.0.0.0", port=5000)
