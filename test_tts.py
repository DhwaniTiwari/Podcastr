import asyncio
import edge_tts
import os

async def test_gen():
    text = "This is a test of the emergency broadcast system."
    file_path = "static/uploads/test_audio.mp3"
    voice = "en-US-ChristopherNeural"
    
    print(f"Generating audio to {file_path}...")
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(file_path)
        print("Success! File saved.")
        print(f"File size: {os.path.getsize(file_path)} bytes")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gen())
