import os
from io import BytesIO
from typing import Union

import pygame
import pyttsx4
from gtts import gTTS
import azure.cognitiveservices.speech as speechsdk

from config import TTS_ENGINE, TTS_RATE, TTS_VOICE_ID


def initialize_audio():
    """
    Initializes the audio mixer with specific settings.

    This function sets up the audio mixer with the following parameters:
    - Frequency: 44100 Hz
    - Size: -16 (16-bit signed samples)
    - Channels: 2 (stereo)
    - Buffer size: 4096

    It first pre-initializes the mixer with the specified settings and then initializes it.
    """
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.mixer.init()


def play_audio(audio: Union[bytes, BytesIO]):
    if not isinstance(audio, (bytes, BytesIO)):
        return
    if isinstance(audio, bytes):
        audio = BytesIO(audio)

    pygame.mixer.music.load(audio)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.wait(10)


def tts_output(response_text):
    if TTS_ENGINE == "gtts":
        tts_output_gtts(response_text)
    elif TTS_ENGINE == "pyttsx4":
        tts_output_pyttsx4(response_text)
    elif TTS_ENGINE == "azure":
        tts_output_azure(response_text)
    else:
        raise ValueError(f"Invalid TTS_ENGINE value: {TTS_ENGINE}")


def tts_output_gtts(response_text):
    tts = gTTS(text=response_text, lang="en")

    audio_data = BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)

    play_audio(audio_data)


def tts_output_pyttsx4(response_text):
    engine = pyttsx4.init("sapi5")

    voices = engine.getProperty("voices")

    if TTS_VOICE_ID:
        for voice in voices:
            if voice.name == TTS_VOICE_ID:
                engine.setProperty("voice", voice.id)
                break
    else:
        print("TTS_VOICE_ID not set, using default voice")

    try:
        rate = int(TTS_RATE)
    except ValueError:
        print("Invalid TTS_RATE value. Using default rate.")
        rate = 150

    engine.setProperty("rate", rate)

    engine.say(response_text)
    engine.runAndWait()


def tts_output_azure(response_text):

    speech_key = os.getenv("AZURE_SPEECH_KEY")
    service_region = os.getenv("AZURE_SPEECH_REGION")
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, region=service_region
    )

    speech_config.speech_synthesis_voice_name = os.getenv("AZURE_SPEECH_VOICE")

    text = response_text

    # use the default speaker as audio output.
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

    result = speech_synthesizer.speak_text_async(text).get()
    # Check result
    if result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")
