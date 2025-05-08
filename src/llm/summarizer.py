import os
import time
import logging
from typing import List, Optional
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import streamlit as st

"""
Text summarization module using OpenAI's GPT API.
"""


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TextSummarizer:
    """Class to handle text summarization using OpenAI's GPT API."""
    
    def __init__(self, api_key=None, model="gpt-3.5-turbo", max_tokens=4096, max_summary_tokens=1000):
        """
        Initialize the summarizer with API credentials and parameters.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use
            max_tokens: Maximum tokens the model can process
            max_summary_tokens: Maximum tokens for the summary
        """
        # Try to get API key from environment if not provided
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
            
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set it in .env or pass directly.")
            
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.max_summary_tokens = max_summary_tokens
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _call_openai_api(self, messages):
        """
        Call OpenAI API with retry logic.
        
        Args:
            messages: List of message dictionaries for the conversation
            
        Returns:
            Summary text from API response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_summary_tokens,
                temperature=0.5,
                top_p=1.0,
                frequency_penalty=0.0,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            raise
    
    def _chunk_text(self, text, chunk_size=2000):
        """
        Split text into chunks that fit within token limits.
        
        Args:
            text: The input text to chunk
            chunk_size: Approximate number of tokens per chunk
            
        Returns:
            List of text chunks
        """
        # Simple chunking by character count (approximation)
        # In practice, you might want a more sophisticated tokenizer
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length
                
        if current_chunk:
            chunks.append(' '.join(current_chunk))
            
        return chunks
    
    def summarize(self, text):
        """
        Summarize the input text.
        
        Args:
            text: The input text to summarize
            
        Returns:
            A concise summary of the text
        """
        if not text:
            return ""
            
        # For very short texts, no need to summarize
        if len(text.split()) < 100:
            return text
            
        # Handle long text by chunking
        if len(text) > self.max_tokens * 2:  # Rough character estimation
            chunks = self._chunk_text(text)
            logger.info(f"Text split into {len(chunks)} chunks for processing")
            
            # Summarize each chunk
            chunk_summaries = []
            for i, chunk in enumerate(chunks):
                logger.info(f"Summarizing chunk {i+1}/{len(chunks)}")
                
                messages = [
                    {"role": "system", "content": "You are a concise summarizer. Extract the key points only."},
                    {"role": "user", "content": f"Summarize this text:\n\n{chunk}"}
                ]
                
                chunk_summary = self._call_openai_api(messages)
                chunk_summaries.append(chunk_summary)
                time.sleep(1)  # Avoid rate limits
                
            # Combine chunk summaries for final summary
            combined_summary = "\n\n".join(chunk_summaries)
            
            # If combined summaries are still too long, summarize again
            if len(combined_summary) > self.max_tokens:
                logger.info("Generating final summary from chunk summaries")
                messages = [
                    {"role": "system", "content": "You are a concise summarizer. Create a unified summary."},
                    {"role": "user", "content": f"Create a unified summary from these section summaries:\n\n{combined_summary}"}
                ]
                return self._call_openai_api(messages)
            
            return combined_summary
        
        # For text within token limits, summarize directly
        messages = [
            {"role": "system", "content": "You are a concise summarizer. Extract the key points only."},
            {"role": "user", "content": f"Summarize this text:\n\n{text}"}
        ]
        
        return self._call_openai_api(messages)

@st.cache_data
def summarize_text(text, api_key=None, model="gpt-3.5-turbo"):
    """
    Simple function interface for text summarization.
    
    Args:
        text: Text to summarize
        api_key: OpenAI API key
        model: Model to use for summarization
        
    Returns:
        Summarized text
    """
    summarizer = TextSummarizer(api_key=api_key, model=model)
    return summarizer.summarize(text)

