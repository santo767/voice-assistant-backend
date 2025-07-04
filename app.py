from flask import Flask, request, jsonify, session
from flask_cors import CORS
from datetime import datetime
import datetime
import re
import pyjokes
import pytz
import math
from googletrans import Translator

app = Flask(__name__)
CORS(app)
app.secret_key = "your_secure_secret_key_here"  # Replace with a secure secret key

# Initialize translator
translator = Translator()

# Multilingual responses with {name} placeholder
MULTILINGUAL_RESPONSES = {
    'greeting': {
        'en': "Hello {name}! How can I help you?",
        'hi': "नमस्ते {name}! मैं आपकी कैसे सहायता कर सकता हूं?",
        'ta': "வணக்கம் {name}! நான் உங்களுக்கு எப்படி உதவ முடியும்?",
        'te': "నమస్కారం {name}! నేను మీకు ఎలా సహాయం చేయగలను?",
        'ml': "ഹലോ {name}! എനിക്ക് നിങ്ങളെ എങ്ങനെ സഹായിക്കാം?",
        'kn': "ಹಲೋ {name}! ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
        'ur': "السلام علیکم {name}! میں آپ کی کیسے مدد کر سکتا ہوں؟",
        'ja': "こんにちは {name}！どのようにお手伝いできますか？"
    },
    'time_response': {
        'en': "{name}, the current time is",
        'hi': "{name}, वर्तमान समय है",
        'ta': "{name}, தற்போதைய நேரம்",
        'te': "{name}, ప్రస్తుత సమయం",
        'ml': "{name}, നിലവിലെ സമയം",
        'kn': "{name}, ಪ್ರಸ್ತುತ ಸಮಯ",
        'ur': "{name}, موجودہ وقت ہے",
        'ja': "{name}、現在の時刻は"
    },
    'date_response': {
        'en': "{name}, today's date is",
        'hi': "{name}, आज की तारीख है",
        'ta': "{name}, இன்றைய தேதி",
        'te': "{name}, నేటి తేదీ",
        'ml': "{name}, ഇന്നത്തെ തീയതി",
        'kn': "{name}, ಇಂದಿನ ದಿನಾಂಕ",
        'ur': "{name}, آج کی تاریخ ہے",
        'ja': "{name}、今日の日付は"
    },
    'math_result': {
        'en': "{name}, the result is",
        'hi': "{name}, परिणाम है",
        'ta': "{name}, முடிவு",
        'te': "{name}, ఫలితం",
        'ml': "{name}, ഫലം",
        'kn': "{name}, ಫಲಿತಾಂಶ",
        'ur': "{name}, نتیجہ ہے",
        'ja': "{name}、結果は"
    },
    'app_opening': {
        'en': "{name}, opening {app} for you",
        'hi': "{name}, {app} खोल रहा हूं",
        'ta': "{name}, உங்களுக்காக {app} ஐ திறக்கிறேன்",
        'te': "{name}, మీ కోసం {app} ను తెరుస్తున్నాను",
        'ml': "{name}, നിങ്ങൾക്കായി {app} തുറക്കുന്നു",
        'kn': "{name}, ನಿಮಗಾಗಿ {app} ಅನ್ನು ತೆರೆಯುತ್ತಿದ್ದೇನೆ",
        'ur': "{name}, آپ کے لیے {app} کھول رہا ہوں",
        'ja': "{name}、あなたのために{app}を開いています"
    },
    'location_response': {
        'en': "{name}, here's the location of {location} on Google Maps.",
        'hi': "{name}, यहाँ Google Maps पर {location} का स्थान है।",
        'ta': "{name}, Google Maps இல் {location} இன் இருப்பிடம் இதோ.",
        'te': "{name}, Google Maps లో {location} యొక్క స్థానం ఇదిగో.",
        'ml': "{name}, Google Maps ൽ {location} ന്റെ സ്ഥാനം ഇതാ.",
        'kn': "{name}, Google Maps ನಲ್ಲಿ {location} ಅವರ ಸ್ಥಾನ ಇದು.",
        'ur': "{name}, Google Maps پر {location} کا مقام یہ ہے۔",
        'ja': "{name}、Google Mapsでの{location}の場所です。"
    },
    'current_location_response': {
        'en': "{name}, I can't access your current location directly. Please share your location from your device.",
        'hi': "{name}, मैं सीधे आपका वर्तमान स्थान एक्सेस नहीं कर सकता। कृपया अपने डिवाइस से अपना स्थान साझा करें।",
        'ta': "{name}, நான் நேரடியாக உங்கள் தற்போதைய இடத்தை அணுக முடியாது. உங்கள் சாதனத்தில் இருந்து உங்கள் இடத்தை பகிரவும்.",
        'te': "{name}, నేను నేరుగా మీ ప్రస్తుత స్థానాన్ని యాక్సెస్ చేయలేను. దయచేసి మీ పరికరం నుండి మీ స్థానాన్ని పంచుకోండి.",
        'ml': "{name}, ഞാൻ നേരിട്ട് നിങ്ങളുടെ നിലവിലെ സ്ഥാനം ആക്സസ് ചെയ്യാൻ കഴിയില്ല. നിങ്ങളുടെ ഉപകരണത്തിൽ നിന്നുള്ള സ്ഥലം പങ്കിടുക.",
        'kn': "{name}, ನಾನು ನೇರವಾಗಿ ನಿಮ್ಮ ಪ್ರಸ್ತುತ ಸ್ಥಳವನ್ನು ಪ್ರವೇಶಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ. ದಯವಿಟ್ಟು ನಿಮ್ಮ ಸಾಧನದಿಂದ ನಿಮ್ಮ ಸ್ಥಳವನ್ನು ಹಂಚಿಕೊಳ್ಳಿ.",
        'ur': "{name}, میں آپ کا موجودہ مقام براہ راست حاصل نہیں کر سکتا۔ براہ کرم اپنے آلے سے اپنا مقام شیئر کریں۔",
        'ja': "{name}、私はあなたの現在地に直接アクセスできません。デバイスから位置情報を共有してください。"
    },
    'play_response': {
        'en': "{name}, playing {topic} on YouTube.",
        'hi': "{name}, YouTube पर {topic} चला रहा है।",
        'ta': "{name}, YouTube இல் {topic} ஐ இயக்குகிறது.",
        'te': "{name}, YouTube లో {topic} ను ప్లే చేస్తోంది.",
        'ml': "{name}, YouTube ൽ {topic} പ്ലേ ചെയ്യുന്നു.",
        'kn': "{name}, YouTube ನಲ್ಲಿ {topic} ಅನ್ನು ಪ್ಲೇ ಮಾಡುತ್ತಿದೆ.",
        'ur': "{name}, YouTube پر {topic} چل رہا ہے۔",
        'ja': "{name}、YouTubeで{topic}を再生しています。"
    },
    'search_response': {
        'en': "{name}, here's what I found for '{query}' on Google.",
        'hi': "{name}, यहाँ Google पर '{query}' के लिए मुझे जो मिला है।",
        'ta': "{name}, Google இல் '{query}' க்காக நான் கண்டறிந்தது இது.",
        'te': "{name}, Google లో '{query}' కోసం నేను కనుగొన్నది ఇది.",
        'ml': "{name}, Google ൽ '{query}' നു വേണ്ടി ഞാൻ കണ്ടെത്തിയത് ഇതാ.",
        'kn': "{name}, Google ನಲ್ಲಿ '{query}' ಗಾಗಿ ನಾನು ಕಂಡುಕೊಂಡಿದ್ದು ಇದು.",
        'ur': "{name}, یہ وہ ہے جو میں نے Google پر '{query}' کے لیے پایا ہے۔",
        'ja': "{name}、Googleで'{query}'について見つけたものです。"
    },
    'default_response': {
        'en': "{name}, I'm not sure how to respond to that.",
        'hi': "{name}, मुझे नहीं पता कि इसका क्या जवाब दूँ।",
        'ta': "{name}, அதற்கு எப்படி பதிலளிப்பது என்று எனக்குத் தெரியவில்லை.",
        'te': "{name}, దానికి ఎలా స్పందించాలో నాకు తెలియదు.",
        'ml': "{name}, അതിനോട് എങ്ങനെ പ്രതികരിക്കണമെന്ന് എനിക്കറിയില്ല.",
        'kn': "{name}, ಅದಕ್ಕೆ ಹೇಗೆ ಪ್ರತಿಕ್ರಿಯಿಸಬೇಕು ಎಂದು ನನಗೆ ತಿಳಿದಿಲ್ಲ.",
        'ur': "{name}, مجھے نہیں معلوم کہ اس کا کیا جواب دوں۔",
        'ja': "{name}、それにどう答えたらいいかわかりません。"
    },
    'math_error': {
        'en': "{name}, sorry, I couldn't solve that mathematical expression.",
        'hi': "{name}, क्षमा करें, मैं उस गणितीय अभिव्यक्ति को हल नहीं कर सका।",
        'ta': "{name}, மன்னிக்கவும், அந்த கணித வெளிப்பாட்டை என்னால் தீர்க்க முடியவில்லை.",
        'te': "{name}, క్షమించండి, ఆ గణిత వ్యక్తీకరణను నేను పరిష్కరించలేకపోయాను.",
        'ml': "{name}, ക്ഷമിക്കണം, ആ ഗണിത പ്രയോഗം എനിക്ക് പരിഹരിക്കാൻ കഴിഞ്ഞില്ല.",
        'kn': "{name}, ಕ್ಷಮಿಸಿ, ಆ ಗಣಿತದ ಅಭಿವ್ಯಕ್ತಿಯನ್ನು ನನಗೆ ಪರಿಹರಿಸಲಾಗಲಿಲ್ಲ.",
        'ur': "{name}, معذرت، میں اس ریاضی کی تعبیر کو حل نہیں کر سکا۔",
        'ja': "{name}、申し訳ございませんが、その数式を解くことができませんでした。"
    },
    'location_error': {
        'en': "{name}, please specify a location to search for.",
        'hi': "{name}, कृपया खोजने के लिए कोई स्थान निर्दिष्ट करें।",
        'ta': "{name}, தேடுவதற்கான இடத்தைக் குறிப்பிடவும்.",
        'te': "{name}, దయచేసి వెతకడానికి ఒక స్థానాన్ని పేర్కొనండి.",
        'ml': "{name}, ദയവായി തിരയാൻ ഒരു സ്ഥലം വ്യക്തമാക്കുക.",
        'kn': "{name}, ದಯವಿಟ್ಟು ಹುಡುಕಲು ಒಂದು ಸ್ಥಳವನ್ನು ನಿರ್ದಿಷ್ಟಪಡಿಸಿ.",
        'ur': "{name}, براہ کرم تلاش کرنے کے لیے کوئی مقام بتائیں۔",
        'ja': "{name}、検索する場所を指定してください。"
    },
    'joke_response': {
        'en': "{name}, here's a joke for you: {joke}",
        'hi': "{name}, यहाँ आपके लिए एक चुटकुला है: {joke}",
        'ta': "{name}, உங்களுக்கான ஒரு நகைச்சுவை: {joke}",
        'te': "{name}, మీ కోసం ఒక జోక్: {joke}",
        'ml': "{name}, നിങ്ങൾക്കുള്ള ഒരു തമാശ: {joke}",
        'kn': "{name}, ನಿಮಗಾಗಿ ಒಂದು ಜೋಕ್: {joke}",
        'ur': "{name}, آپ کے لیے ایک لطیفہ: {joke}",
        'ja': "{name}、あなたのためのジョーク: {joke}"
    }
}

# Mapping app names to URLs or special identifiers for mobile apps
APP_URLS = {
    "calculator": "https://www.google.com/search?q=calculator",
    "instagram": "https://www.instagram.com",
    "whatsapp": "whatsapp://send",  # WhatsApp mobile URI scheme
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "chatgpt": "https://chat.openai.com",
    "facebook": "https://www.facebook.com",
    "vlc": "vlc://",  # VLC URI scheme (may not work on all devices)
    "filemanager": "file://",  # File manager URI (depends on device)
    # Add more apps and their URIs or URLs here as needed
}

# Helper to get or set user name in session
def get_user_name(command, detected_lang):
    name = session.get('user_name')
    # Patterns to detect name introductions in various languages
    patterns = [
        r"my name is ([\w\s]+)",
        r"i am ([\w\s]+)",
        r"i'm ([\w\s]+)",
        r"मेरा नाम ([\w\s]+) है",
        r"मैं ([\w\s]+) हूँ",
        r"நான் ([\w\s]+) என்று",
        r"నా పేరు ([\w\s]+)",
        r"എന്റെ പേര് ([\w\s]+)",
        r"ನನ್ನ ಹೆಸರು ([\w\s]+)",
        r"میرا نام ([\w\s]+) ہے",
        r"私の名前は([\w\s]+)です"
    ]
    for pat in patterns:
        match = re.search(pat, command, re.IGNORECASE)
        if match:
            name_candidate = match.group(1).strip().split()[0]
            session['user_name'] = name_candidate
            return name_candidate
    if name:
        return name
    # Default friendly fallback per language
    return {
        'en': "Friend", 'hi': "मित्र", 'ta': "நண்பர்", 'te': "స్నేహితుడు",
        'ml': "സുഹൃത്ത്", 'kn': "ಸ್ನೇಹಿತ", 'ur': "دوست", 'ja': "友達"
    }.get(detected_lang, "Friend")

# Language detection and translation helper
def detect_and_translate(text):
    try:
        detection = translator.detect(text)
        detected_lang = detection.lang
        confidence = detection.confidence
        # Translate to English only if not English and confidence > 0.3
        if detected_lang != 'en' and confidence > 0.3:
            translated = translator.translate(text, src=detected_lang, dest='en')
            return translated.text, detected_lang
        else:
            return text, detected_lang
    except Exception as e:
        print(f"Translation error: {e}")
        return text, 'en'

def translate_response(text, target_lang):
    if target_lang == 'en':
        return text
    try:
        translated = translator.translate(text, src='en', dest=target_lang)
        return translated.text
    except Exception as e:
        print(f"Response translation error: {e}")
        return text

def get_localized_response(response_key, lang, name, **kwargs):
    if lang in MULTILINGUAL_RESPONSES.get(response_key, {}):
        template = MULTILINGUAL_RESPONSES[response_key][lang]
    else:
        template = MULTILINGUAL_RESPONSES[response_key].get('en', '')
    # Format with name and other keyword args
    return template.format(name=name, **kwargs)

@app.route("/command", methods=["POST"])
def handle_command():
    data = request.get_json()
    original_command = data.get("command", "")
    translated_command, detected_lang = detect_and_translate(original_command)
    command = translated_command.lower()
    name = get_user_name(command, detected_lang)
    response = get_localized_response('default_response', detected_lang, name)
    navigate = None

    # App opening commands with improved app handling
    if any(app_cmd in command for app_cmd in [
        "open calculator", "open instagram", "open whatsapp", "open youtube", "open google",
        "launch calculator", "launch instagram", "launch whatsapp", "launch youtube", "launch google",
        "open chatgpt", "open facebook", "open vlc", "open filemanager",
        "launch chatgpt", "launch facebook", "launch vlc", "launch filemanager"
    ]):
        app_key = None
        for key in APP_URLS.keys():
            if key in command:
                app_key = key
                break
        if app_key:
            app_name = app_key.capitalize() if app_key != "filemanager" else "File Manager"
            # Special handling for mobile app URIs
            navigate = APP_URLS[app_key]
            # For WhatsApp, if on mobile, whatsapp://send opens app; else fallback to web
            if app_key == "whatsapp":
                # Detect if request is from mobile user-agent (optional)
                user_agent = request.headers.get('User-Agent', '').lower()
                if "mobile" not in user_agent:
                    navigate = "https://web.whatsapp.com"
            # VLC and File Manager URIs may not work on all devices, fallback to Google search
            if app_key in ["vlc", "filemanager"]:
                # Fallback URL (Google search)
                navigate = f"https://www.google.com/search?q={app_key}"
            response = get_localized_response('app_opening', detected_lang, name, app=app_name)

    # Greetings
    elif any(greet in command for greet in [
        "hello", "hi", "hey", "good morning", "good evening", "namaste", "vanakkam"
    ]):
        response = get_localized_response('greeting', detected_lang, name)

    # Time query
    elif "time" in command:
        india_time = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
        time_str = india_time.strftime('%I:%M %p')
        time_response = get_localized_response('time_response', detected_lang, name)
        response = f"{time_response} {time_str}"

    # Date query
    elif "date" in command:
        india_date = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
        date_str = india_date.strftime('%B %d, %Y')
        date_response = get_localized_response('date_response', detected_lang, name)
        response = f"{date_response} {date_str}"

    # Joke request
    elif "joke" in command:
        joke = pyjokes.get_joke()
        if detected_lang != 'en':
            joke = translate_response(joke, detected_lang)
        response = get_localized_response('joke_response', detected_lang, name, joke=joke)

    # Enhanced math operations
    elif any(math_keyword in command for math_keyword in [
        "calculate", "compute", "solve", "math", "square root", "sin", "cos", "tan", "log", "factorial", "power", "sqrt"
    ]) or re.search(r"[\d+\-*/.^%]+", command):
        try:
            result = solve_complex_math(command)
            if result is not None:
                math_response = get_localized_response('math_result', detected_lang, name)
                response = f"{math_response} {result}"
            else:
                response = get_localized_response('math_error', detected_lang, name)
        except Exception as e:
            print(f"Math error: {e}")
            response = get_localized_response('math_error', detected_lang, name)

    # Location queries including current location
    elif any(location_keyword in command for location_keyword in [
        "where is", "location of", "find location", "where can i find", "directions to", "how to get to", "where does", "located"
    ]):
        # Special case: current location queries
        if any(phrase in command for phrase in ["my location", "current location", "where am i", "where am I"]):
            response = get_localized_response('current_location_response', detected_lang, name)
            navigate = None
        else:
            location_query = extract_location_query(command)
            if location_query:
                response = get_localized_response('location_response', detected_lang, name, location=location_query)
                navigate = f"https://www.google.com/maps/search/{location_query.replace(' ', '+')}"
            else:
                response = get_localized_response('location_error', detected_lang, name)

    # Play command for YouTube
    elif command.startswith("play "):
        topic = command.replace("play", "").strip()
        response = get_localized_response('play_response', detected_lang, name, topic=topic)
        navigate = f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}"

    # Search queries
    elif command.startswith((
        "what is", "who is", "how does", "how is", "tell me", "search", "define", "explain", "what do you mean by", "what's"
    )):
        query = command
        response = get_localized_response('search_response', detected_lang, name, query=query)
        navigate = f"https://www.google.com/search?q={query.replace(' ', '+')}"

    return jsonify({"reply": response, "navigate": navigate})

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
    # Handle sqrt and square root
    if "square root" in cmd or "sqrt" in cmd:
        match = re.search(r'(?:square root of|sqrt of|sqrt)\s*(\d+(?:\.\d+)?)', cmd)
        if not match:
            match = re.search(r'(?:sqrt|square root)\s*(\d+(?:\.\d+)?)', cmd)
        if match:
            num = float(match.group(1))
            return round(math.sqrt(num), 6)
    # Trigonometric functions
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
    # Logarithm
    if "log" in cmd:
        match = re.search(r'log\s*(?:of\s*)?(\d+(?:\.\d+)?)', cmd)
        if match:
            num = float(match.group(1))
            if num > 0:
                return round(math.log(num), 6)
    # Factorial
    if "factorial" in cmd:
        match = re.search(r'factorial\s*(?:of\s*)?(\d+)', cmd)
        if match:
            num = int(match.group(1))
            if 0 <= num <= 20:
                return math.factorial(num)
    # Power operations
    if "power" in cmd or "raised to" in cmd:
        match = re.search(r'(\d+(?:\.\d+)?)\s*(?:to the power of|raised to|power)\s*(\d+(?:\.\d+)?)', cmd)
        if match:
            base = float(match.group(1))
            exponent = float(match.group(2))
            return round(math.pow(base, exponent), 6)
    # Basic arithmetic
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
