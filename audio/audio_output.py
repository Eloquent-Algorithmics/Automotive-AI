"""
This module provides functionality related to audio playback.
"""
import os
from typing import Union
from io import BytesIO
import pygame
from gtts import gTTS

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

def initialize_audio():
    """
    Initialize the pygame mixer.
    """
    pygame.mixer.init()


def play_audio(audio: Union[bytes, BytesIO]):
    """
    Play audio data using pygame.mixer.

    Args:
        audio (Union[bytes, BytesIO]): The audio data played.
    """

    if not isinstance(audio, (bytes, BytesIO)):
        return
    if isinstance(audio, bytes):
        audio = BytesIO(audio)

    pygame.mixer.music.load(audio)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.wait(10)


def tts_output(text):
    """
    Convert text to speech using gTTS.

    Args:
        text (str): The text to be converted to speech.
    """
    tts = gTTS(text=text, lang="en")  # You can change the language if needed

    # Save the generated speech to a BytesIO object
    audio_data = BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)

    # Play the generated speech using pygame.mixer
    play_audio(audio_data)
