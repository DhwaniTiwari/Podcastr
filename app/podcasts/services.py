# from app.ai.google_service import generate_podcast_script
from app.ai.groq_service import generate_podcast_script
from app.tts.edge_service import generate_audio_from_text
import os
import uuid

def generate_script_content(topic: str) -> str:
    return generate_podcast_script(topic)

def generate_audio_content(script: str, output_path: str):
    return generate_audio_from_text(script, output_path)
