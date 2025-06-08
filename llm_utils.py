import requests
import os
def analyze_resume_with_llm(text, api_key):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are an expert resume coach."},
            {"role": "user", "content": f"Analyze this resume and give improvement suggestions:\n\n{text}"}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()

    if 'choices' in data:
        return data['choices'][0]['message']['content']
    else:
        return f"Error from Groq: {data}"
