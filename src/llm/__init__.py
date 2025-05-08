import os
import streamlit as st  # Only if used in Streamlit context
from openai import OpenAI  # Ensure you have the OpenAI library installed
...

def __init__(self, api_key=None, model="gpt-3.5-turbo", max_tokens=4096, max_summary_tokens=1000):
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY", None))

    if not api_key:
        raise ValueError("OpenAI API key not found. Please set it in .env or Streamlit secrets.")

    client = OpenAI(api_key=api_key)
    ...
    self.model = model
    self.max_tokens = max_tokens    