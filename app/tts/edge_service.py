import asyncio
import edge_tts

VOICE_MAP = {
    "spanish": "es-ES-AlvaroNeural",
    "french": "fr-FR-HenriNeural",
    "german": "de-DE-KillianNeural",
    "hindi": "hi-IN-MadhurNeural",
    "japanese": "ja-JP-KeitaNeural",
    "original": "en-US-ChristopherNeural"
}

# Async wrapper for Edge TTS
async def generate_edge_audio(text: str, file_path: str, voice: str = "en-US-ChristopherNeural"):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(file_path)

def generate_audio_from_text(text: str, file_path: str, language: str = "original"):
    """
    Generates audio using Microsoft Edge TTS (Cloud, Free, High Quality).
    This acts as a synchronous wrapper for the async Edge TTS library.
    """
    try:
        voice = VOICE_MAP.get(language.lower(), "en-US-ChristopherNeural")
        # standard asyncio.run() creates a new loop and closes it, mostly safe in threadpools (Py3.7+)
        asyncio.run(generate_edge_audio(text, file_path, voice=voice))
        return file_path
    except Exception as e:
        print(f"CRITICAL ERROR in Edge TTS Generation: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback: Delete the file if it exists so we don't serve junk
        import os
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return None # Return None to signal failure
