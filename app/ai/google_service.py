import google.generativeai as genai
from app.config import settings
import os

if settings.GOOGLE_API_KEY:
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro-latest')
else:
    model = None

def generate_podcast_script(topic: str) -> str:
    if not model:
        return f"Mock Script for {topic}. (Google API Key missing)"
        
    try:
        prompt = f"You are a podcast script writer. Write a short, engaging script about {topic}. Do not include speaker labels like 'Host:', just the text."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Google AI Error: {e}")
        return f"Error generation script for {topic}: {str(e)}"
