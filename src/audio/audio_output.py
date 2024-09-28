"""
This module contains functions for audio output using text-to-speech (TTS) engines.
"""
import os
from io import BytesIO
from typing import Union

import pygame
import pyttsx4
from gtts import gTTS
import azure.cognitiveservices.speech as speechsdk
from api.openai_functions.gpt_chat import get_azure_credential

from config import TTS_ENGINE, TTS_RATE, TTS_VOICE_ID


def initialize_audio():
    """
    Initializes the audio mixer with specific settings.

    This function sets up the audio mixer with the following parameters:
    - Frequency: 44100 Hz
    - Size: -16 (16-bit signed samples)
    - Channels: 2 (stereo)
    - Buffer size: 4096

    It first pre-initializes the mixer with the specified settings
    and then initializes it.
    """
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.mixer.init()


def play_audio(audio: Union[bytes, BytesIO]):
    """
    Plays audio from a bytes object or a BytesIO stream using pygame.
    Args:
        audio (Union[bytes, BytesIO]): The audio data to be played.
        It can be either a bytes object or a BytesIO stream.
    Returns:
        None
    """
    if not isinstance(audio, (bytes, BytesIO)):
        return
    if isinstance(audio, bytes):
        audio = BytesIO(audio)

    pygame.mixer.music.load(audio)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.wait(10)


def tts_output(response_text):
    """
    Generates text-to-speech (TTS) output using the specified TTS engine.

    This function selects the appropriate TTS engine based on the global
    TTS_ENGINE variable and generates speech from the provided response text.

    Args:
        response_text (str): The text to be converted to speech.

    Raises:
        ValueError: If the TTS_ENGINE value is not recognized.
    """
    if TTS_ENGINE == "gtts":
        tts_output_gtts(response_text)
    elif TTS_ENGINE == "pyttsx4":
        tts_output_pyttsx4(response_text)
    elif TTS_ENGINE == "azure":
        tts_output_azure(response_text)
    else:
        raise ValueError(f"Invalid TTS_ENGINE value: {TTS_ENGINE}")


def tts_output_gtts(response_text):
    """
    Converts the given text to speech using the Google Text-to-Speech (gTTS) library
    and plays the audio.
    Args:
        response_text (str): The text to be converted to speech.
    Returns:
        None
    """
    tts = gTTS(text=response_text, lang="en")

    audio_data = BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)

    play_audio(audio_data)


def tts_output_pyttsx4(response_text):
    """
    Converts text to speech using the pyttsx4 library.
    This function initializes the pyttsx4 engine with the "sapi5" driver,
    sets the voice and rate properties,
    and then speaks the provided response text.
    Args:
        response_text (str): The text to be converted to speech.
    Environment Variables:
        TTS_VOICE_ID (str): The name of the voice to be used.
        If not set, the default voice is used.
        TTS_RATE (str): The rate of speech. If not set or invalid,
        the default rate of 150 is used.
    Raises:
        ValueError: If the TTS_RATE environment variable is not a valid integer.
    """
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
    """
    Converts the given text to speech using Azure's Text-to-Speech service.
    """
    region = os.getenv("AZURE_SPEECH_REGION")
    print(region)

    # Obtain the token string from azure_credential
    azure_credential = get_azure_credential()
    token_result = azure_credential.get_token('https://cognitiveservices.azure.com/.default')
    auth_token = token_result.token
    print(auth_token)

    # Create the SpeechConfig with the token and region
    speech_config = speechsdk.SpeechConfig(auth_token=auth_token, region=region)
    speech_config.speech_synthesis_voice_name = os.getenv("AZURE_SPEECH_VOICE")

    # Use the default speaker as audio output.
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    result = speech_synthesizer.speak_text_async(response_text).get()

    # Check result
    if result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")
