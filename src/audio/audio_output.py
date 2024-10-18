"""
This module contains functions for audio output.
"""
import os
import azure.cognitiveservices.speech as speechsdk
from api.openai_functions.gpt_chat import get_azure_credential


def tts_output(response_text):
    """
    Converts the given text to speech using Azure's Text-to-Speech service.
    """
    region = os.getenv("AZURE_SPEECH_REGION")
    print(region)

    # Obtain the token string from azure_credential
    azure_credential = get_azure_credential()
    token_result = azure_credential.get_token(
        'https://cognitiveservices.azure.com/.default'
    )
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
