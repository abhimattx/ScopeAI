import re
import tiktoken
from typing import List, Dict, Any, Optional

def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and normalizing formatting
    
    Args:
        text: The input text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    # Normalize newlines
    text = re.sub(r'\n+', '\n', text)
    
    return text

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Split long text into overlapping chunks of specified size
    
    Args:
        text: The input text to chunk
        chunk_size: Maximum size of each chunk in characters
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    text = clean_text(text)
    
    # If text is shorter than chunk_size, return it as a single chunk
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Find the end position of the current chunk
        end = start + chunk_size
        
        # If we're not at the end of the text, try to find a good break point
        if end < len(text):
            # Look for natural break points (sentence endings, paragraphs)
            breakpoint = text.rfind('.', start, end)
            if breakpoint == -1 or breakpoint < start + chunk_size // 2:
                breakpoint = text.rfind(' ', start, end)
            
            if breakpoint != -1 and breakpoint > start + chunk_size // 2:
                end = breakpoint + 1
        else:
            end = len(text)
        
        # Add the chunk to our list
        chunks.append(text[start:end])
        
        # Move start position accounting for overlap
        start = end - overlap if end < len(text) else len(text)
    
    return chunks

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    Count the number of tokens in a text string
    
    Args:
        text: The input text
        model: The model name to use for tokenization
        
    Returns:
        Number of tokens
    """
    if not text:
        return 0
    
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Fall back to cl100k_base encoding if model-specific encoding not found
        encoding = tiktoken.get_encoding("cl100k_base")
    
    return len(encoding.encode(text))

def estimate_tokens_from_messages(messages: List[Dict[str, Any]], model: str = "gpt-3.5-turbo") -> int:
    """
    Estimate token count for a list of chat messages
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        model: The model name to use for tokenization
        
    Returns:
        Estimated token count for the messages
    """
    if not messages:
        return 0
    
    token_count = 0
    
    # Add tokens for each message
    for message in messages:
        # Add tokens for message metadata (role, etc.) - approximately 4 tokens per message
        token_count += 4
        
        # Add tokens for the content
        if "content" in message and message["content"]:
            token_count += count_tokens(message["content"], model)
    
    # Add tokens for the model's reply format (approximately 3 tokens)
    token_count += 3
    
    return token_count