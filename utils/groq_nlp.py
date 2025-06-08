import requests

def analyze_resume_with_groq(text, api_key):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "mixtral-8x7b-32768",  # or a supported one by Groq
        "messages": [
            {"role": "system", "content": "You are an expert resume analyzer."},
            {"role": "user", "content": f"Extract skills, education, and experience from this resume:\n{text}"}
        ]
    }

    response = requests.post(url, json=body, headers=headers)
    return response.json()['choices'][0]['message']['content']
