import os
import time
import logging
from typing import List, Optional
import openai
from tenacity import retry, stop_after_attempt, wait_exponential
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TextSummarizer:
    def __init__(self, api_key=None, model="gpt-3.5-turbo", max_tokens=4096, max_summary_tokens=1000):
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY", None))
        if not api_key:
            raise ValueError("OpenAI API key not found.")
        openai.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.max_summary_tokens = max_summary_tokens

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _call_openai_api(self, messages):
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_summary_tokens,
                temperature=0.5,
                top_p=1.0,
                frequency_penalty=0.0,
            )
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            raise

    def _chunk_text(self, text, chunk_size=2000):
        words = text.split()
        chunks, current_chunk, current_length = [], [], 0
        for word in words:
            length = len(word) + 1
            if current_length + length > chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = length
            else:
                current_chunk.append(word)
                current_length += length
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        return chunks

    def summarize(self, text):
        if not text:
            return ""
        if len(text.split()) < 100:
            return text

        if len(text) > self.max_tokens * 2:
            chunks = self._chunk_text(text)
            logger.info(f"Text split into {len(chunks)} chunks.")
            chunk_summaries = []
            for i, chunk in enumerate(chunks):
                logger.info(f"Summarizing chunk {i+1}/{len(chunks)}")
                messages = [
                    {"role": "system", "content": "You are a concise summarizer. Extract key points only."},
                    {"role": "user", "content": f"Summarize this text:\n\n{chunk}"}
                ]
                chunk_summary = self._call_openai_api(messages)
                chunk_summaries.append(chunk_summary)
                time.sleep(1)

            combined_summary = "\n\n".join(chunk_summaries)

            if len(combined_summary) > self.max_tokens:
                logger.info("Summarizing combined result.")
                messages = [
                    {"role": "system", "content": "Create a unified summary."},
                    {"role": "user", "content": combined_summary}
                ]
                return self._call_openai_api(messages)

            return combined_summary

        messages = [
            {"role": "system", "content": "You are a concise summarizer. Extract key points only."},
            {"role": "user", "content": f"Summarize this text:\n\n{text}"}
        ]
        return self._call_openai_api(messages)

@st.cache_data
def summarize_text(text, api_key=None, model="gpt-3.5-turbo"):
    summarizer = TextSummarizer(api_key=api_key, model=model)
    return summarizer.summarize(text)
