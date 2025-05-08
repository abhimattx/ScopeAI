from typing import List, Dict, Optional
import re
import spacy

def generate_insights(summarized_text: str, use_gpt_for_topics: bool = False) -> Dict:
    """
    Generate insights from summarized text including follow-up questions and topic classification.
    
    Args:
        summarized_text: The summarized text to analyze
        use_gpt_for_topics: Whether to use GPT for topic classification (if False, uses keyword matching)
        
    Returns:
        Dictionary containing follow-up questions and topic classifications
    """
    # Generate follow-up questions
    questions = generate_followup_questions(summarized_text)
    
    # Identify topics
    topics = classify_topics(summarized_text, use_gpt=use_gpt_for_topics)
    
    return {
        "follow_up_questions": questions,
        "topics": topics
    }

def generate_followup_questions(text: str) -> List[str]:
    """Generate better follow-up questions using spaCy NLP"""
    
    # Load spaCy model
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    
    questions = []
    
    # Process first few sentences
    for sent_idx, sent in enumerate(list(doc.sents)[:3]):
        if len(sent) < 3:
            continue
            
        # Extract subject-verb-object using dependency parsing
        subject = None
        verb = None
        obj = None
        
        for token in sent:
            # Find the root verb
            if token.dep_ == "ROOT" and token.pos_ == "VERB":
                verb = token.text
                
                # Find subject
                for child in token.children:
                    if child.dep_ in ["nsubj", "nsubjpass"]:
                        subject = child.text
                        # Get full noun phrase if available
                        for chunk in sent.noun_chunks:
                            if chunk.root == child:
                                subject = chunk.text
                                break
                
                # Find object
                for child in token.children:
                    if child.dep_ in ["dobj", "pobj"]:
                        obj = child.text
                        # Get full noun phrase if available
                        for chunk in sent.noun_chunks:
                            if chunk.root == child:
                                obj = chunk.text
                                break
        
        if subject and verb:
            obj_text = obj if obj else "this"
            
            templates = [
                f"What if {subject} {verb} differently?",
                f"Why did {subject} {verb} {obj_text}?",
                f"How might {subject} improve upon {obj_text}?",
                f"What are the implications of {subject} {verb}ing {obj_text}?",
            ]
            
            questions.extend(templates[:2])  # Add 2 questions per sentence
    
    # Add generic questions if needed
    generic_questions = [
        "What are the key takeaways from this?",
        "How might this situation evolve in the future?",
        "What alternative approaches could be considered?",
    ]
    
    if len(questions) < 3:
        questions.extend(generic_questions[:3 - len(questions)])
        
    return questions[:5]  # Return at most 5 questions

def classify_topics(text: str, use_gpt: bool = False) -> List[str]:
    """
    Classify the topics present in the summarized text.
    
    Args:
        text: The summarized text
        use_gpt: Whether to use GPT for classification (otherwise use keyword matching)
        
    Returns:
        List of identified topics
    """
    if use_gpt:
        # In a real implementation, you would call a GPT model here
        # For now, we'll return a placeholder
        return ["GPT topic classification not implemented"]
    
    # Simple keyword-based topic classification
    topic_keywords = {
        "Finance": ["money", "financial", "budget", "cost", "profit", "revenue", "investment"],
        "Technology": ["software", "hardware", "tech", "algorithm", "data", "digital", "computer"],
        "Healthcare": ["health", "medical", "patient", "doctor", "hospital", "treatment", "care"],
        "Education": ["school", "student", "learn", "teach", "education", "academic", "university"],
        "Business": ["company", "business", "market", "strategy", "customer", "product", "service"],
        "Politics": ["government", "policy", "political", "law", "regulation", "election", "vote"]
    }
    
    identified_topics = []
    
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    for topic, keywords in topic_keywords.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                identified_topics.append(topic)
                break  # Found one keyword for this topic, move to next topic
    
    return identified_topics

if __name__ == "__main__":
    # Example usage
    sample_text = "The company announced a new AI product yesterday. Their CEO explained that this technology would revolutionize customer service automation. Early market reactions have been positive."
    insights = generate_insights(sample_text)
    print("Follow-up Questions:")
    for q in insights["follow_up_questions"]:
        print(f"- {q}")
    print("\nTopics:")
    for t in insights["topics"]:
        print(f"- {t}")