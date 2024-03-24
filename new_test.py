import os
import requests
import openai
import json
import asyncio
from openai import AsyncOpenAI
from elevenlabs.client import AsyncElevenLabs

openai_client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    http_client=httpx.AsyncClient(
        limits=httpx.Limits(
            max_connections=10,
            max_keepalive_connections=10,
        )
    )
)

elevenlabs_client = AsyncElevenLabs(
    api_key=os.environ.get("ELEVENLABS_API_KEY"),
    httpx=httpx.AsyncClient(
        limits=httpx.Limits(
            max_connections=10,
            max_keepalive_connections=10,
        )
    )
)

messages = [
    {"role": "system", "content": "You are an AI Assistant"},
    {"role": "user", "content": f"{user_input}"}
]

async def get_response_from_openai(user_input):
    try:
        openai_stream = await openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",

            messages=messages,
            stream=True,
        )
        for chunk in openai_stream:
            if chunk.choices[0].delta.content is not None:
                return(chunk.choices[0].delta.content, end="")
    except Exception as e:
        print(f"Error getting response from OpenAI: {e}")
        return None

response_text = openai_stream

async def text_to_speech_with_elevenlabs(response_text):
    elevenlabs_stream = await elevenlabs_client.generate(
        model_id="eleven_turbo_v2",
        voice_id=ELEVENLABS_VOICE_ID
        text=response_text,
        stream=True
    )

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        stream(audio_stream)
    else:
        print("Failed to convert text to speech.")
        print(response_text)

async def main(

    while True:

    user_input = input("Please enter your question: ")
    
    openai_response = get_response_from_openai(user_input)
    
    if openai_response:
        print("OpenAI Response:", openai_response)
        text_to_speech_with_elevenlabs(response_text)
    else:
        print("Failed to get a response.")
)


if __name__ == "__main__":
    asyncio.run(main())
