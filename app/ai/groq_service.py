import os
from groq import Groq
from app.config import settings

client = None
if settings.GROQ_API_KEY:
    client = Groq(api_key=settings.GROQ_API_KEY)

def generate_podcast_script(topic: str) -> str:
    if not client:
        return f"Mock Script for {topic}. (Groq API Key missing)"
        
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert podcast script writer. Write a engaging, natural-sounding podcast script. Do not include sound effects or speaker labels like 'Host:'. Just the raw spoken content."
                },
                {
                    "role": "user",
                    "content": f"Write a short podcast script about: {topic}"
                }
            ],
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Groq API Error: {e}")
        return f"Error generating script for {topic}: {str(e)}"
