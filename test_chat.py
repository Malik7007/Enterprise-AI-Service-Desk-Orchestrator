import requests
import json

url = "http://127.0.0.1:8000/chat"
payload = {
    "message": "what policy?",
    "provider": "openai",
    "model": "gpt-4o",
    "api_key": "sk-placeholder"
}

try:
    response = requests.post(url, json=payload, stream=True, timeout=10)
    print(f"Status: {response.status_code}")
    for line in response.iter_lines():
        if line:
            print(line.decode('utf-8'))
except Exception as e:
    print(f"Error: {e}")
