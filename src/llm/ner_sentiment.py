from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

"""
Named Entity Recognition and Sentiment Analysis module.
Uses TextBlob for basic NER and TextBlob/VADER for sentiment scoring.
"""

def extract_entities_with_textblob(text):
    """
    Extract named entities from text using TextBlob.
    This is a fallback method when spaCy is not available.
    
    Args:
        text (str): Input text for entity extraction
        
    Returns:
        dict: Dictionary with entity types as keys and lists of entities as values
    """
    blob = TextBlob(text)
    entities = {
        "PERSON": [],
        "ORGANIZATION": [],
        "LOCATION": [],
        "DATE": [],
        "OTHER": []
    }
    
    # Extract noun phrases as potential entities
    for np in blob.noun_phrases:
        # Capitalize each word in the noun phrase
        entity = ' '.join(word.capitalize() for word in np.split())
        
        # Simple rules to categorize entities (not as accurate as spaCy but works as fallback)
        if re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December|\d{1,2}/\d{1,2}/\d{2,4}|\d{4})\b', entity, re.IGNORECASE):
            if entity not in entities["DATE"]:
                entities["DATE"].append(entity)
        elif re.search(r'\b(Inc|Corp|LLC|Company|Organization|Ltd|Limited|Association)\b', entity, re.IGNORECASE):
            if entity not in entities["ORGANIZATION"]:
                entities["ORGANIZATION"].append(entity)
        elif re.search(r'\b(Street|Avenue|Road|Boulevard|Lane|Drive|Place|Square|Park|City|Town|County|State|Country|River|Mountain|Ocean|Sea|Lake)\b', entity, re.IGNORECASE):
            if entity not in entities["LOCATION"]:
                entities["LOCATION"].append(entity)
        elif re.search(r'^[A-Z][a-z]+ [A-Z][a-z]+$', entity):  # Simple pattern for full names
            if entity not in entities["PERSON"]:
                entities["PERSON"].append(entity)
        else:
            if entity not in entities["OTHER"]:
                entities["OTHER"].append(entity)
    
    # Remove empty categories
    return {k: v for k, v in entities.items() if v}

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
        "entities": extract_entities_with_textblob(text),
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