import requests

url = "https://api.elevenlabs.io/v1/text-to-speech/TxGEqnHWrfWFTfGW9XjX/stream"

querystring = {"optimize_streaming_latency":"3"}

payload = {
    "model_id": "eleven_turbo_v2",
    "text": "f{user_input}",
    "voice_settings": {
        "similarity_boost": 10,
        "stability": 10,
        "style": -1
    }
}
headers = {
    "xi-api-key": "api_key",
    "Content-Type": "application/json"
}

response = requests.request("POST", url, json=payload, headers=headers, params=querystring)

print(response.text)