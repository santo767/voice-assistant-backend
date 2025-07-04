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
app.secret_key = "your_secret_key_here"  # Needed for session

# Initialize translator
translator = Translator()

# Multilingual greetings and responses with name placeholders
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
        'en': "{name}, opening {} for you",
        'hi': "{name}, {} खोल रहा हूं",
        'ta': "{name}, உங்களுக்காக {} ஐ திறக்கிறேன்",
        'te': "{name}, మీ కోసం {} ను తెరుస్తున్నాను",
        'ml': "{name}, നിങ്ങൾക്കായി {} തുറക്കുന്നു",
        'kn': "{name}, ನಿಮಗಾಗಿ {} ಅನ್ನು ತೆರೆಯುತ್ತಿದ್ದೇನೆ",
        'ur': "{name}, آپ کے لیے {} کھول رہا ہوں",
        'ja': "{name}、あなたのために{}を開いています"
    },
    'location_response': {
        'en': "{name}, here's the location of {} on Google Maps.",
        'hi': "{name}, यहाँ Google Maps पर {} का स्थान है।",
        'ta': "{name}, Google Maps இல் {} இன் இருப்பிடம் இதோ.",
        'te': "{name}, Google Maps లో {} యొక్క స్థానం ఇదిగో.",
        'ml': "{name}, Google Maps ൽ {} ന്റെ സ്ഥാനം ഇതാ.",
        'kn': "{name}, Google Maps ನಲ್ಲಿ {} ಅವರ ಸ್ಥಾನ ಇದು.",
        'ur': "{name}, Google Maps پر {} کا مقام یہ ہے۔",
        'ja': "{name}、Google Mapsでの{}の場所です。"
    },
    'play_response': {
        'en': "{name}, playing {} on YouTube.",
        'hi': "{name}, YouTube पर {} चला रहा है।",
        'ta': "{name}, YouTube இல் {} ஐ இயக்குகிறது.",
        'te': "{name}, YouTube లో {} ను ప్లే చేస్తోంది.",
        'ml': "{name}, YouTube ൽ {} പ്ലേ ചെയ്യുന്നു.",
        'kn': "{name}, YouTube ನಲ್ಲಿ {} ಅನ್ನು ಪ್ಲೇ ಮಾಡುತ್ತಿದೆ.",
        'ur': "{name}, YouTube پر {} چل رہا ہے۔",
        'ja': "{name}、YouTubeで{}を再生しています。"
    },
    'search_response': {
        'en': "{name}, here's what I found for '{}' on Google.",
        'hi': "{name}, यहाँ Google पर '{}' के लिए मुझे जो मिला है।",
        'ta': "{name}, Google இல் '{}' க்காக நான் கண்டறிந்தது இது.",
        'te': "{name}, Google లో '{}' కోసం నేను కనుగొన్నది ఇది.",
        'ml': "{name}, Google ൽ '{}' നു വേണ്ടി ഞാൻ കണ്ടെത്തിയത് ഇതാ.",
        'kn': "{name}, Google ನಲ್ಲಿ '{}' ಗಾಗಿ ನಾನು ಕಂಡುಕೊಂಡಿದ್ದು ಇದು.",
        'ur': "{name}, یہ وہ ہے جو میں نے Google پر '{}' کے لیے پایا ہے۔",
        'ja': "{name}、Googleで'{}'について見つけたものです。"
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
        'en': "{name}, here's a joke for you: {}",
        'hi': "{name}, यहाँ आपके लिए एक चुटकुला है: {}",
        'ta': "{name}, உங்களுக்கான ஒரு நகைச்சுவை: {}",
        'te': "{name}, మీ కోసం ఒక జోక్: {}",
        'ml': "{name}, നിങ്ങൾക്കുള്ള ഒരു തമാശ: {}",
        'kn': "{name}, ನಿಮಗಾಗಿ ಒಂದು ಜೋಕ್: {}",
        'ur': "{name}, آپ کے لیے ایک لطیفہ: {}",
        'ja': "{name}、あなたのためのジョーク: {}"
    }
}

# Helper to get or set user name in session
def get_user_name(command, detected_lang):
    # Try to extract name from command
    name = session.get('user_name')
    # Look for "my name is ..." or "I am ..." or "I'm ..." in any language
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
            name = match.group(1).strip().split()[0]
            session['user_name'] = name
            return name
    # If not found, return last name or default
    if name:
        return name
    # Default fallback
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

def get_localized_response(response_key, lang, name, *args):
    if lang in MULTILINGUAL_RESPONSES.get(response_key, {}):
        template = MULTILINGUAL_RESPONSES[response_key][lang]
    else:
        template = MULTILINGUAL_RESPONSES[response_key].get('en', '')
    if args:
        return template.format(name=name, *args)
    return template.format(name=name)

@app.route("/command", methods=["POST"])
def handle_command():
    data = request.get_json()
    original_command = data.get("command", "")
    translated_command, detected_lang = detect_and_translate(original_command)
    command = translated_command.lower()
    name = get_user_name(command, detected_lang)
    response = get_localized_response('default_response', detected_lang, name)
    navigate = None

    # App opening commands
    if any(app_cmd in command for app_cmd in [
        "open calculator", "open instagram", "open whatsapp", "open youtube", "open google",
        "launch calculator", "launch instagram", "launch whatsapp", "launch youtube", "launch google"
    ]):
        app_name = ""
        if "calculator" in command:
            app_name = "Calculator"
            navigate = "https://www.google.com/search?q=calculator"
        elif "instagram" in command:
            app_name = "Instagram"
            navigate = "https://www.instagram.com"
        elif "whatsapp" in command:
            app_name = "WhatsApp"
            navigate = "https://web.whatsapp.com"
        elif "youtube" in command:
            app_name = "YouTube"
            navigate = "https://www.youtube.com"
        elif "google" in command:
            app_name = "Google"
            navigate = "https://www.google.com"
        response = get_localized_response('app_opening', detected_lang, name, app_name)

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
        joke_response = get_localized_response('joke_response', detected_lang, name)
        response = joke_response.format(joke)

    # Enhanced math operations with complex functions
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

    # Location search for Google Maps
    elif any(location_keyword in command for location_keyword in [
        "where is", "location of", "find location", "where can i find", "directions to", "how to get to", "where does", "located"
    ]):
        location_query = extract_location_query(command)
        if location_query:
            response = get_localized_response('location_response', detected_lang, name, location_query)
            navigate = f"https://www.google.com/maps/search/{location_query.replace(' ', '+')}"
        else:
            response = get_localized_response('location_error', detected_lang, name)

    # Play command for YouTube
    elif command.startswith("play "):
        topic = command.replace("play", "").strip()
        response = get_localized_response('play_response', detected_lang, name, topic)
        navigate = f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}"

    # Search queries
    elif command.startswith((
        "what is", "who is", "how does", "how is", "tell me", "search", "define", "explain", "what do you mean by", "what's"
    )):
        query = command
        response = get_localized_response('search_response', detected_lang, name, query)
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
            # Try to extract number after 'sqrt' or 'square root'
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
