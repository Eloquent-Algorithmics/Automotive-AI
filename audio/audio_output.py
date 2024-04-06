import os
from typing import Union
from io import BytesIO
import pyttsx4
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame
from gtts import gTTS

from config import TTS_ENGINE, TTS_VOICE_ID, TTS_RATE


def initialize_audio():
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


def tts_output(text):
    if TTS_ENGINE == "gtts":
        tts_output_gtts(text)
    elif TTS_ENGINE == "pyttsx4":
        tts_output_pyttsx4(text)
    else:
        raise ValueError(f"Invalid TTS_ENGINE value: {TTS_ENGINE}")


def tts_output_gtts(text):
    tts = gTTS(text=text, lang="en")

    audio_data = BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)

    play_audio(audio_data)


def tts_output_pyttsx4(text):
    engine = pyttsx4.init('sapi5')

    voices = engine.getProperty('voices')

    if TTS_VOICE_ID:
        for voice in voices:
            if voice.name == TTS_VOICE_ID:
                engine.setProperty('voice', voice.id)
                break
    else:
        print("TTS_VOICE_ID not set, using default voice")

    try:
        rate = int(TTS_RATE)
    except ValueError:
        print("Invalid TTS_RATE value. Using default rate.")
        rate = 150

    engine.setProperty('rate', rate)

    engine.say(text)
    engine.runAndWait()
