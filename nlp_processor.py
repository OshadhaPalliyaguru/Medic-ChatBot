import nltk 
import json 
import random 
import os 
import sys 
from nltk.stem import WordNetLemmatizer 

lemmatizer = WordNetLemmatizer() 

# Common stop words that should be ignored during matching 
STOP_WORDS = { 
    'i', 'me', 'my', 'we', 'our', 'you', 'your', 'he', 'she', 'it', 
    'is', 'am', 'are', 'was', 'were', 'be', 'been', 'being', 
    'a', 'an', 'the', 'and', 'or', 'but', 'if', 'so', 
    'do', 'does', 'did', 'have', 'has', 'had', 
    'what', 'which', 'who', 'whom', 'this', 'that', 
    'in', 'on', 'at', 'to', 'for', 'of', 'with', 'about', 
    'can', 'could', 'would', 'should', 'will', 'shall', 
    'not', 'no', 'there', 'here', 'where', 'when', 'how', 
    'tell', 'please', 'know', 'want', 'need', 'get', 
    '?', '!', '.', ',' 
} 

# Helper for PyInstaller resource paths 
def resource_path(relative_path): 
    try: 
        base_path = sys._MEIPASS 
    except Exception: 
        base_path = os.path.abspath(".") 
    return os.path.join(base_path, relative_path) 

def process_text(text): 
    """Tokenize and lemmatize the input text.""" 
    tokens = nltk.word_tokenize(text.lower()) 
    return [lemmatizer.lemmatize(w) for w in tokens] 

def get_keywords(text): 
    """Tokenize, lemmatize, and remove stop words to extract meaningful keywords.""" 
    tokens = process_text(text) 
    return set(word for word in tokens if word not in STOP_WORDS) 

def calculate_similarity(input_keywords, pattern_keywords): 
    """Calculate Jaccard similarity: overlap over total unique keywords.""" 
    if not pattern_keywords or not input_keywords: 
        return 0.0 
    union = input_keywords.union(pattern_keywords) 
    overlap = input_keywords.intersection(pattern_keywords) 
    return len(overlap) / len(union) 

class CovidEngine: 
    SIMILARITY_THRESHOLD = 0.5  # At least 50% of pattern keywords must match 
    
    def __init__(self): 
        with open(resource_path('intents.json')) as file: 
            self.intents = json.load(file) 
            
    def get_response(self, user_input, db): 
        input_keywords = get_keywords(user_input) 
        
        # 1. Search static intents (JSON) using similarity scoring 
        best_score = 0.0 
        best_intent = None 
        for intent in self.intents['intents']: 
            for pattern in intent['patterns']: 
                pattern_keywords = get_keywords(pattern) 
                score = calculate_similarity(input_keywords, pattern_keywords) 
                if score > best_score: 
                    best_score = score 
                    best_intent = intent 
                    
        if best_score >= self.SIMILARITY_THRESHOLD and best_intent: 
            res = random.choice(best_intent['responses']) 
            db.log_chat(user_input, res) 
            return res, False  # Response found in static intents 
            
        # 2. Search dynamic database (Learned facts) using NLP matching 
        all_facts = db.get_all_learned_facts() 
        best_fact_score = 0.0 
        best_fact_response = None 
        for pattern, response in all_facts: 
            pattern_keywords = get_keywords(pattern) 
            score = calculate_similarity(input_keywords, pattern_keywords) 
            if score > best_fact_score: 
                best_fact_score = score 
                best_fact_response = response 
                
        if best_fact_score >= self.SIMILARITY_THRESHOLD and best_fact_response: 
            db.log_chat(user_input, best_fact_response) 
            return best_fact_response, False  # Response found in learned facts 
            
        # 3. Fallback: Trigger learning mode 
        return "I don't have information on that yet. What should I say in response?", True