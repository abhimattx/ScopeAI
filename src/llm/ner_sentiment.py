import spacy
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os
import sys
import subprocess

"""
Named Entity Recognition and Sentiment Analysis module.
Uses spaCy for NER and TextBlob/VADER for sentiment scoring.
"""

# Load spaCy model with error handling
try:
    nlp = spacy.load("en_core_web_sm")
except IOError:
    # If model not found, try to install it
    print("Downloading spaCy model...")
    try:
        # First try using pip directly
        subprocess.check_call([sys.executable, "-m", "pip", "install", "en-core-web-sm==3.5.0", "--no-deps"])
        nlp = spacy.load("en_core_web_sm")
    except:
        # If that fails, try using spacy download command
        try:
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            nlp = spacy.load("en_core_web_sm")
        except:
            # Last resort: use a blank model
            print("Could not load spaCy model. Using blank model instead.")
            nlp = spacy.blank("en")

def extract_entities(text):
    """
    Extract named entities from text using spaCy.
    
    Args:
        text (str): Input text for entity extraction
        
    Returns:
        dict: Dictionary with entity types as keys and lists of entities as values
    """
    doc = nlp(text)
    entities = {}
    
    for ent in doc.ents:
        if ent.label_ not in entities:
            entities[ent.label_] = []
        if ent.text not in entities[ent.label_]:
            entities[ent.label_].append(ent.text)
            
    return entities

def get_textblob_sentiment(text):
    """
    Get sentiment scores using TextBlob.
    
    Args:
        text (str): Input text for sentiment analysis
        
    Returns:
        dict: Dictionary with polarity and subjectivity scores
    """
    blob = TextBlob(text)
    return {
        "polarity": blob.sentiment.polarity,  # Range: -1.0 to 1.0 (negative to positive)
        "subjectivity": blob.sentiment.subjectivity  # Range: 0.0 to 1.0 (objective to subjective)
    }

def get_vader_sentiment(text):
    """
    Get sentiment scores using VADER.
    
    Args:
        text (str): Input text for sentiment analysis
        
    Returns:
        dict: Dictionary with negative, neutral, positive, and compound scores
    """
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)
    return scores

def analyze_text(text):
    """
    Perform both NER and sentiment analysis on input text.
    
    Args:
        text (str): Input text for analysis
        
    Returns:
        dict: Dictionary containing entities and sentiment scores
    """
    result = {
        "entities": extract_entities(text),
        "sentiment": {
            "textblob": get_textblob_sentiment(text),
            "vader": get_vader_sentiment(text)
        }
    }
    return result

if __name__ == "__main__":
    # Example usage
    sample_text = "Apple is planning to open a new store in New York City next month. The CEO Tim Cook is very excited about this expansion."
    analysis = analyze_text(sample_text)
    print(analysis)