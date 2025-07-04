from flask import Flask, request, jsonify, session
from flask_cors import CORS
from datetime import datetime
import datetime
import re
import pyjokes
import pytz
import math
import requests
import random

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = "your_very_secure_secret_key"

# App URIs for mobile/web
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

# Fun facts list
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
    patterns = [
        r"my name is ([\w\s]+)",
        r"i am ([\w\s]+)",
        r"i'm ([\w\s]+)"
    ]
    for pat in patterns:
        match = re.search(pat, command, re.IGNORECASE)
        if match:
            name_candidate = match.group(1).strip().split()[0]
            session['user_name'] = name_candidate
            return name_candidate
    if 'user_name' in session:
        return session['user_name']
    return "Friend"

def get_response(response_key, name, **kwargs):
    RESPONSES = {
        'greeting': f"Hello {name}! How can I help you?",
        'time_response': f"{name}, the current time is",
        'date_response': f"{name}, today's date is",
        'math_result': f"{name}, the result is",
        'app_opening': f"{name}, opening {kwargs.get('app','the app')} for you.",
        'location_response': f"{name}, here's the location of {kwargs.get('location','the place')} on Google Maps.",
        'current_location_response': f"{name}, I can't access your current location directly. Please share your location from your device.",
        'play_response': f"{name}, playing {kwargs.get('topic','your request')} on YouTube.",
        'search_response': f"{name}, here's what I found for '{kwargs.get('query','your query')}' on Google.",
        'default_response': f"{name}, I'm not sure how to respond to that.",
        'math_error': f"{name}, sorry, I couldn't solve that mathematical expression.",
        'location_error': f"{name}, please specify a location to search for.",
        'joke_response': f"{name}, here's a joke for you: {kwargs.get('joke','')}",
        'weather_response': f"{name}, the weather in {kwargs.get('city','your city')} is {kwargs.get('weather','unavailable')}.",
        'reminder_set': f"{name}, reminder set: {kwargs.get('reminder','')}",
        'fun_fact': f"{name}, did you know? {kwargs.get('fact','')}"
    }
    return RESPONSES.get(response_key, RESPONSES['default_response'])

def extract_location_query(command):
    location_keywords = [
        "where is", "location of", "find location", "where can i find", "directions to", "how to get to", "where does", "located"
    ]
    query = command.lower()
    for keyword in location_keywords:
        if keyword in query:
            query = query.replace(keyword, "").strip()
            break
    query = query.replace("the ", "").strip()
    return query if query else None

def solve_complex_math(command):
    cmd = command.lower()
    if "square root" in cmd or "sqrt" in cmd:
        match = re.search(r'(?:square root of|sqrt of|sqrt)\s*(\d+(?:\.\d+)?)', cmd)
        if not match:
            match = re.search(r'(?:sqrt|square root)\s*(\d+(?:\.\d+)?)', cmd)
        if match:
            num = float(match.group(1))
            return round(math.sqrt(num), 6)
    if "sin" in cmd:
        match = re.search(r'sin\s*(?:of\s*)?(\d+(?:\.\d+)?)', cmd)
        if match:
            angle = float(match.group(1))
            return round(math.sin(math.radians(angle)), 6)
    if "cos" in cmd:
        match = re.search(r'cos\s*(?:of\s*)?(\d+(?:\.\d+)?)', cmd)
        if match:
            angle = float(match.group(1))
            return round(math.cos(math.radians(angle)), 6)
    if "tan" in cmd:
        match = re.search(r'tan\s*(?:of\s*)?(\d+(?:\.\d+)?)', cmd)
        if match:
            angle = float(match.group(1))
            return round(math.tan(math.radians(angle)), 6)
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
            if 0 <= num <= 20:
                return math.factorial(num)
    if "power" in cmd or "raised to" in cmd:
        match = re.search(r'(\d+(?:\.\d+)?)\s*(?:to the power of|raised to|power)\s*(\d+(?:\.\d+)?)', cmd)
        if match:
            base = float(match.group(1))
            exponent = float(match.group(2))
            return round(math.pow(base, exponent), 6)
    replacements = {
        "calculate": "",
        "compute": "",
        "solve": "",
        "math": "",
        "what is": "",
        "the": "",
        "result": "",
        "of": "",
        "times": "*",
        "divided by": "/",
        "plus": "+",
        "minus": "-",
        "multiply": "*",
        "divide": "/",
        "pi": str(math.pi),
        "e": str(math.e)
    }
    for old, new in replacements.items():
        cmd = cmd.replace(old, new)
    cmd = re.sub(r'\s+', ' ', cmd).strip()
    math_expression = re.search(r'[\d+\-*/.()^%\s]+', cmd)
    if math_expression:
        expr = math_expression.group(0).strip()
        expr = expr.replace('^', '**')
        allowed_chars = set('0123456789+-*/.() ')
        if all(c in allowed_chars for c in expr):
            try:
                result = eval(expr)
                return round(result, 6) if isinstance(result, float) else result
            except Exception as e:
                print(f"Eval error: {e}")
                return None
    return None

# Weather API (OpenWeatherMap, free tier)
def get_weather(city):
    API_KEY = "your_openweathermap_api_key"  # <-- Replace with your API key
    if not city:
        return "City not specified"
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        resp = requests.get(url)
        data = resp.json()
        if data.get("weather"):
            desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            return f"{desc}, {temp}°C"
        else:
            return "Weather data unavailable"
    except Exception as e:
        return "Weather data unavailable"

@app.route("/command", methods=["POST"])
def handle_command():
    data = request.get_json()
    original_command = data.get("command", "")
    command = original_command.lower()
    name = get_user_name(original_command)
    response = get_response('default_response', name)
    navigate = None

    # App opening
    for app in APP_URIS.keys():
        if f"open {app}" in command or f"launch {app}" in command:
            app_name = app.capitalize() if app != "filemanager" else "File Manager"
            uri = APP_URIS[app]["uri"]
            web = APP_URIS[app]["web"]
            navigate = {"uri": uri, "web": web}
            response = get_response('app_opening', name, app=app_name)
            break

    # Greetings
    if any(greet in command for greet in [
        "hello", "hi", "hey", "good morning", "good evening"
    ]):
        response = get_response('greeting', name)

    # Time query
    elif "time" in command:
        india_time = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
        time_str = india_time.strftime('%I:%M %p')
        time_response = get_response('time_response', name)
        response = f"{time_response} {time_str}"

    # Date query
    elif "date" in command:
        india_date = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
        date_str = india_date.strftime('%B %d, %Y')
        date_response = get_response('date_response', name)
        response = f"{date_response} {date_str}"

    # Joke request
    elif "joke" in command:
        joke = pyjokes.get_joke()
        response = get_response('joke_response', name, joke=joke)

    # Fun fact
    elif "fun fact" in command or "tell me something interesting" in command:
        fact = random.choice(FUN_FACTS)
        response = get_response('fun_fact', name, fact=fact)

    # Reminder
    elif "remind me to" in command or "set a reminder" in command:
        reminder = re.sub(r".*remind me to |.*set a reminder (for|to)?", "", command, flags=re.IGNORECASE).strip()
        response = get_response('reminder_set', name, reminder=reminder)

    # Weather
    elif "weather" in command:
        city_match = re.search(r"weather in ([\w\s]+)", command)
        city = city_match.group(1).strip() if city_match else "Delhi"
        weather = get_weather(city)
        response = get_response('weather_response', name, city=city, weather=weather)

    # Math
    elif any(math_keyword in command for math_keyword in [
        "calculate", "compute", "solve", "math", "square root", "sin", "cos", "tan", "log", "factorial", "power", "sqrt"
    ]) or re.search(r"[\d+\-*/.^%]+", command):
        try:
            result = solve_complex_math(command)
            if result is not None:
                math_response = get_response('math_result', name)
                response = f"{math_response} {result}"
            else:
                response = get_response('math_error', name)
        except Exception as e:
            print(f"Math error: {e}")
            response = get_response('math_error', name)

    # Location features
    elif any(location_keyword in command for location_keyword in [
        "where is", "location of", "find location", "where can i find", "directions to", "how to get to", "where does", "located"
    ]):
        if any(phrase in command for phrase in ["my location", "current location", "where am i", "where am I"]):
            response = get_response('current_location_response', name)
            navigate = None
        else:
            location_query = extract_location_query(command)
            if location_query:
                response = get_response('location_response', name, location=location_query)
                navigate = f"https://www.google.com/maps/search/{location_query.replace(' ', '+')}"
            else:
                response = get_response('location_error', name)

    # Play command for YouTube
    elif command.startswith("play "):
        topic = command.replace("play", "").strip()
        response = get_response('play_response', name, topic=topic)
        navigate = f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}"

    # Search queries
    elif command.startswith((
        "what is", "who is", "how does", "how is", "tell me", "search", "define", "explain", "what do you mean by", "what's"
    )):
        query = command
        response = get_response('search_response', name, query=query)
        navigate = f"https://www.google.com/search?q={query.replace(' ', '+')}"

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
