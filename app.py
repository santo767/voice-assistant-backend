from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import datetime
import re
import pyjokes
import pytz
import math
import operator
from googletrans import Translator

app = Flask(__name__)
CORS(app)

# Initialize translator
translator = Translator()

# Language detection and translation helper
def detect_and_translate(text):
    """Detect language and translate to English if needed"""
    try:
        detection = translator.detect(text)
        detected_lang = detection.lang
        confidence = detection.confidence
        
        # If it's not English, translate to English
        if detected_lang != 'en' and confidence > 0.5:
            translated = translator.translate(text, src=detected_lang, dest='en')
            return translated.text, detected_lang
        else:
            return text, 'en'
    except Exception as e:
        print(f"Translation error: {e}")
        return text, 'en'

def translate_response(text, target_lang):
    """Translate response back to the detected language"""
    if target_lang == 'en':
        return text
    
    try:
        translated = translator.translate(text, src='en', dest=target_lang)
        return translated.text
    except Exception as e:
        print(f"Response translation error: {e}")
        return text

# Multilingual greetings and responses
MULTILINGUAL_RESPONSES = {
    'greeting': {
        'en': "Hello! How can I help you?",
        'hi': "नमस्ते! मैं आपकी कैसे सहायता कर सकता हूं?",
        'ta': "வணக்கம்! நான் உங்களுக்கு எப்படி உதவ முடியும்?",
        'te': "నమస్కారం! నేను మీకు ఎలా సహాయం చేయగలను?",
        'ml': "ഹലോ! എനിക്ക് നിങ്ങളെ എങ്ങനെ സഹായിക്കാം?",
        'kn': "ಹಲೋ! ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
        'ur': "السلام علیکم! میں آپ کی کیسے مدد کر سکتا ہوں؟",
        'ja': "こんにちは！どのようにお手伝いできますか？"
    },
    'time_response': {
        'en': "The current time is",
        'hi': "वर्तमान समय है",
        'ta': "தற்போதைய நேரம்",
        'te': "ప్రస్తుత సమయం",
        'ml': "നിലവിലെ സമയം",
        'kn': "ಪ್ರಸ್ತುತ ಸಮಯ",
        'ur': "موجودہ وقت ہے",
        'ja': "現在の時刻は"
    },
    'date_response': {
        'en': "Today's date is",
        'hi': "आज की तारीख है",
        'ta': "இன்றைய தேதி",
        'te': "నేటి తేదీ",
        'ml': "ഇന്നത്തെ തീയതി",
        'kn': "ಇಂದಿನ ದಿನಾಂಕ",
        'ur': "آج کی تاریخ ہے",
        'ja': "今日の日付は"
    },
    'math_result': {
        'en': "The result is",
        'hi': "परिणाम है",
        'ta': "முடிவு",
        'te': "ఫలితం",
        'ml': "ഫലം",
        'kn': "ಫಲಿತಾಂಶ",
        'ur': "نتیجہ ہے",
        'ja': "結果は"
    },
    'location_response': {
        'en': "Here's the location of {} on Google Maps.",
        'hi': "यहाँ Google Maps पर {} का स्थान है।",
        'ta': "Google Maps இல் {} இன் இருப்பிடம் இதோ.",
        'te': "Google Maps లో {} యొక్క స్థానం ఇదిగో.",
        'ml': "Google Maps ൽ {} ന്റെ സ്ഥാനം ഇതാ.",
        'kn': "Google Maps ನಲ್ಲಿ {} ಅವರ ಸ್ಥಾನ ಇದು.",
        'ur': "Google Maps پر {} کا مقام یہ ہے۔",
        'ja': "Google Mapsでの{}の場所です。"
    },
    'play_response': {
        'en': "Playing {} on YouTube.",
        'hi': "YouTube पर {} चला रहा है।",
        'ta': "YouTube இல் {} ஐ இயக்குகிறது.",
        'te': "YouTube లో {} ను ప్లే చేస్తోంది.",
        'ml': "YouTube ൽ {} പ്ലേ ചെയ്യുന്നു.",
        'kn': "YouTube ನಲ್ಲಿ {} ಅನ್ನು ಪ್ಲೇ ಮಾಡುತ್ತಿದೆ.",
        'ur': "YouTube پر {} چل رہا ہے۔",
        'ja': "YouTubeで{}を再生しています。"
    },
    'search_response': {
        'en': "Here's what I found for '{}' on Google.",
        'hi': "यहाँ Google पर '{}' के लिए मुझे जो मिला है।",
        'ta': "Google இல் '{}' க்காக நான் கண்டறிந்தது இது.",
        'te': "Google లో '{}' కోసం నేను కనుగొన్నది ఇది.",
        'ml': "Google ൽ '{}' നു വേണ്ടി ഞാൻ കണ്ടെത്തിയത് ഇതാ.",
        'kn': "Google ನಲ್ಲಿ '{}' ಗಾಗಿ ನಾನು ಕಂಡುಕೊಂಡಿದ್ದು ಇದು.",
        'ur': "یہ وہ ہے جو میں نے Google پر '{}' کے لیے پایا ہے۔",
        'ja': "Googleで'{}'について見つけたものです。"
    },
    'default_response': {
        'en': "I'm not sure how to respond to that.",
        'hi': "मुझे नहीं पता कि इसका क्या जवाब दूँ।",
        'ta': "அதற்கு எப்படி பதிலளிப்பது என்று எனக்குத் தெரியவில்லை.",
        'te': "దానికి ఎలా స్పందించాలో నాకు తెలియదు.",
        'ml': "അതിനോട് എങ്ങനെ പ്രതികരിക്കണമെന്ന് എനിക്കറിയില്ല.",
        'kn': "ಅದಕ್ಕೆ ಹೇಗೆ ಪ್ರತಿಕ್ರಿಯಿಸಬೇಕು ಎಂದು ನನಗೆ ತಿಳಿದಿಲ್ಲ.",
        'ur': "مجھے نہیں معلوم کہ اس کا کیا جواب دوں۔",
        'ja': "それにどう答えたらいいかわかりません。"
    },
    'math_error': {
        'en': "Sorry, I couldn't solve that mathematical expression.",
        'hi': "क्षमा करें, मैं उस गणितीय अभिव्यक्ति को हल नहीं कर सका।",
        'ta': "மன்னிக்கவும், அந்த கணித வெளிப்பாட்டை என்னால் தீர்க்க முடியவில்லை.",
        'te': "క్షమించండి, ఆ గణిత వ్యక్తీకరణను నేను పరిష్కరించలేకపోయాను.",
        'ml': "ക്ഷമിക്കണം, ആ ഗണിത പ്രയോഗം എനിക്ക് പരിഹരിക്കാൻ കഴിഞ്ഞില്ല.",
        'kn': "ಕ್ಷಮಿಸಿ, ಆ ಗಣಿತದ ಅಭಿವ್ಯಕ್ತಿಯನ್ನು ನನಗೆ ಪರಿಹರಿಸಲಾಗಲಿಲ್ಲ.",
        'ur': "معذرت، میں اس ریاضی کی تعبیر کو حل نہیں کر سکا۔",
        'ja': "申し訳ございませんが、その数式を解くことができませんでした。"
    },
    'location_error': {
        'en': "Please specify a location to search for.",
        'hi': "कृपया खोजने के लिए कोई स्थान निर्दिष्ट करें।",
        'ta': "தேடுவதற்கான இடத்தைக் குறிப்பிடவும்.",
        'te': "దయచేసి వెతకడానికి ఒక స్థానాన్ని పేర్కొనండి.",
        'ml': "ദയവായി തിരയാൻ ഒരു സ്ഥലം വ്യക്തമാക്കുക.",
        'kn': "ದಯವಿಟ್ಟು ಹುಡುಕಲು ಒಂದು ಸ್ಥಳವನ್ನು ನಿರ್ದಿಷ್ಟಪಡಿಸಿ.",
        'ur': "براہ کرم تلاش کرنے کے لیے کوئی مقام بتائیں۔",
        'ja': "検索する場所を指定してください。"
    },
    'joke_response': {
        'en': "Here's a joke for you: {}",
        'hi': "यहाँ आपके लिए एक चुटकुला है: {}",
        'ta': "உங்களுக்கான ஒரு நகைச்சுவை: {}",
        'te': "మీ కోసం ఒక జోక్: {}",
        'ml': "നിങ്ങൾക്കുള്ള ഒരു തമാശ: {}",
        'kn': "ನಿಮಗಾಗಿ ಒಂದು ಜೋಕ್: {}",
        'ur': "آپ کے لیے ایک لطیفہ: {}",
        'ja': "あなたのためのジョーク: {}"
    }
}

def get_localized_response(response_key, lang, *args):
    """Get localized response based on language"""
    if lang in MULTILINGUAL_RESPONSES.get(response_key, {}):
        template = MULTILINGUAL_RESPONSES[response_key][lang]
    else:
        template = MULTILINGUAL_RESPONSES[response_key].get('en', '')
    
    if args:
        return template.format(*args)
    return template

@app.route("/command", methods=["POST"])
def handle_command():
    data = request.get_json()
    original_command = data.get("command", "")
    
    # Detect and translate command if needed
    translated_command, detected_lang = detect_and_translate(original_command)
    command = translated_command.lower()
    
    response = get_localized_response('default_response', detected_lang)
    navigate = None  # to be sent to frontend if YouTube or Google needed
    
    # Debug logging
    print(f"Original command: {original_command}")
    print(f"Detected language: {detected_lang}")
    print(f"Translated command: {translated_command}")
    
    # Greetings
    if any(greet in command for greet in ["hello", "hi", "hey", "good morning", "good evening", "namaste", "vanakkam"]):
        response = get_localized_response('greeting', detected_lang)
    
    # Time query
    elif "time" in command:
        india_time = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
        time_str = india_time.strftime('%I:%M %p')
        time_response = get_localized_response('time_response', detected_lang)
        response = f"{time_response} {time_str}"
    
    # Date query
    elif "date" in command:
        india_date = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
        date_str = india_date.strftime('%B %d, %Y')
        date_response = get_localized_response('date_response', detected_lang)
        response = f"{date_response} {date_str}"
    
    # Joke request
    elif "joke" in command:
        joke = pyjokes.get_joke()
        if detected_lang != 'en':
            joke = translate_response(joke, detected_lang)
        joke_response = get_localized_response('joke_response', detected_lang)
        response = joke_response.format(joke)
    
    # Enhanced math operations with complex functions
    elif any(math_keyword in command for math_keyword in ["calculate", "compute", "solve", "math", "square root", "sin", "cos", "tan", "log", "factorial", "power", "sqrt"]) or re.search(r"[\d+\-*/.^%]+", command):
        try:
            result = solve_complex_math(command)
            if result is not None:
                math_response = get_localized_response('math_result', detected_lang)
                response = f"{math_response} {result}"
            else:
                response = get_localized_response('math_error', detected_lang)
        except Exception as e:
            print(f"Math error: {e}")
            response = get_localized_response('math_error', detected_lang)
    
    # Location search for Google Maps
    elif any(location_keyword in command for location_keyword in ["where is", "location of", "find location", "where can I find", "directions to", "how to get to", "where does", "located"]):
        location_query = extract_location_query(command)
        if location_query:
            response = get_localized_response('location_response', detected_lang, location_query)
            navigate = f"https://www.google.com/maps/search/{location_query.replace(' ', '+')}"
        else:
            response = get_localized_response('location_error', detected_lang)
    
    # Play command for YouTube
    elif command.startswith("play "):
        topic = command.replace("play", "").strip()
        response = get_localized_response('play_response', detected_lang, topic)
        navigate = f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}"
    
    # Search queries
    elif command.startswith(("what is", "who is", "how does", "how is", "tell me", "search", "define", "explain", "what do you mean by", "what's")):
        query = command
        response = get_localized_response('search_response', detected_lang, query)
        navigate = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    
    # Translate response back if needed
    if detected_lang != 'en' and response == get_localized_response('default_response', 'en'):
        response = translate_response(response, detected_lang)
    
    # Debug logging
    print(f"Response: {response}")
    print(f"Navigate: {navigate}")
    
    return jsonify({"reply": response, "navigate": navigate})

def extract_location_query(command):
    """Extract location from various command formats"""
    # Remove common location keywords
    location_keywords = ["where is", "location of", "find location", "where can i find", "directions to", "how to get to", "where does", "located"]
    
    query = command.lower()
    for keyword in location_keywords:
        if keyword in query:
            query = query.replace(keyword, "").strip()
            break
    
    # Clean up the query
    query = query.replace("the ", "").strip()
    return query if query else None

def solve_complex_math(command):
    """Solve complex mathematical expressions"""
    # Convert command to lowercase for processing
    cmd = command.lower()
    
    # Replace common mathematical terms
    replacements = {
        "square root of": "sqrt(",
        "square root": "sqrt(",
        "sqrt of": "sqrt(",
        "sin of": "sin(",
        "cos of": "cos(",
        "tan of": "tan(",
        "log of": "log(",
        "ln of": "log(",
        "factorial of": "factorial(",
        "power": "**",
        "to the power of": "**",
        "raised to": "**",
        "times": "*",
        "divided by": "/",
        "plus": "+",
        "minus": "-",
        "multiply": "*",
        "divide": "/",
        "pi": str(math.pi),
        "e": str(math.e)
    }
    
    # Apply replacements
    for old, new in replacements.items():
        cmd = cmd.replace(old, new)
    
    # Remove non-mathematical words
    words_to_remove = ["calculate", "compute", "solve", "math", "what", "is", "the", "of", "result"]
    for word in words_to_remove:
        cmd = cmd.replace(word, "")
    
    # Clean up extra spaces
    cmd = re.sub(r'\s+', ' ', cmd).strip()
    
    # Handle special functions
    if "sqrt(" in cmd and not cmd.endswith(")"):
        # Add closing parenthesis for sqrt if missing
        cmd = cmd.replace("sqrt(", "sqrt(") + ")"
    
    if "factorial(" in cmd:
        # Handle factorial
        factorial_match = re.search(r'factorial\((\d+)\)', cmd)
        if factorial_match:
            num = int(factorial_match.group(1))
            factorial_result = math.factorial(num)
            cmd = cmd.replace(factorial_match.group(0), str(factorial_result))
    
    # Handle trigonometric functions (convert to radians if needed)
    trig_functions = ["sin(", "cos(", "tan("]
    for func in trig_functions:
        if func in cmd:
            # Find the number inside the function
            pattern = f'{func[:-1]}\\((\\d+(?:\\.\\d+)?)\\)'
            match = re.search(pattern, cmd)
            if match:
                angle = float(match.group(1))
                # Convert degrees to radians
                radians = math.radians(angle)
                if func == "sin(":
                    result = math.sin(radians)
                elif func == "cos(":
                    result = math.cos(radians)
                elif func == "tan(":
                    result = math.tan(radians)
                cmd = cmd.replace(match.group(0), str(result))
    
    # Handle square root
    if "sqrt(" in cmd:
        sqrt_pattern = r'sqrt\((\d+(?:\.\d+)?)\)'
        match = re.search(sqrt_pattern, cmd)
        if match:
            num = float(match.group(1))
            result = math.sqrt(num)
            cmd = cmd.replace(match.group(0), str(result))
    
    # Handle logarithms
    if "log(" in cmd:
        log_pattern = r'log\((\d+(?:\.\d+)?)\)'
        match = re.search(log_pattern, cmd)
        if match:
            num = float(match.group(1))
            result = math.log(num)
            cmd = cmd.replace(match.group(0), str(result))
    
    # Clean up the expression
    cmd = cmd.replace(" ", "")
    
    # Basic safety check
    allowed_chars = set('0123456789+-*/.()^%')
    if not all(c in allowed_chars for c in cmd):
        return None
    
    # Replace ^ with ** for power operations
    cmd = cmd.replace('^', '**')
    
    try:
        # Evaluate the expression
        result = eval(cmd)
        return round(result, 6) if isinstance(result, float) else result
    except:
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