import requests
import os
from dotenv import load_dotenv

load_dotenv()
TTS_API_KEY = os.getenv("PLAYAI_TTS_API_KEY")

def playai_tts(text, output="output.mp3"):
    url = "https://api.play.ht/api/v2/tts"
    headers = {
        "Authorization": f"Bearer {TTS_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "voice": "playai-tts",
        "text": text
    }
    res = requests.post(url, headers=headers, json=data)
    with open(output, "wb") as f:
        f.write(res.content)
    os.system(f"start {output}")
