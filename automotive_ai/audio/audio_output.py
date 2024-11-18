"""
This module contains functions for audio output.
"""

import os
import azure.cognitiveservices.speech as speechsdk


def tts_output(response_text):
    """
    Converts the given text to speech using Azure's Text-to-Speech service.
    """
    region = os.getenv("AZURE_SPEECH_REGION")
    # print(region)

    speech_key = os.getenv("AZURE_SPEECH_KEY")

    # Create the SpeechConfig with the Azure Speech API Key and region
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=region)
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
