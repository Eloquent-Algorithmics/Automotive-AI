"""
This is the main conversation module for the automotive AI assistant.
"""

import os
import serial

from utils.commands import voice_commands
from api._openai.gpt_chat import (
    chat_gpt,
    chat_gpt_conversation,
    load_conversation_history,
    save_conversation_history,
    summarize_conversation_history_direct,
    extract_vin,
)
from api._msal.graph_api import (
    create_new_appointment,
    get_emails,
    get_next_appointment,
    send_email_with_attachments,
)
from utils.commands import ELM327_COMMANDS
from utils.serial_commands import (
    send_command,
    process_data,
    send_diagnostic_report,
    parse_vin_response
)
from api._nhtsa.vin_decoder import decode_vin
from voice.voice_recognition import recognize_speech, recognize_command
from audio.audio_output import tts_output
from openai import OpenAI, AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

openai_client = None
openai_model_arg = None

azure_credential = None


def get_azure_credential():
    """
    Retrieves the Azure credential for authentication.
    """
    global azure_credential
    if azure_credential is None:
        azure_credential = DefaultAzureCredential(
            exclude_shared_token_cache_credential=True
        )
    return azure_credential


def configure_openai():
    """
    Configures the OpenAI client based on environment variables.

    This function sets up the OpenAI client using different configurations depending on
    the environment variables provided. It supports Azure OpenAI endpoints, and OpenAI API keys.

    Raises:
        ValueError: If required environment variables for Azure OpenAI are missing or
        if no OpenAI configuration is provided.

    Environment Variables:
        AZURE_OPENAI_ENDPOINT: The Azure endpoint for OpenAI.
        AZURE_OPENAI_API_KEY: The API key for Azure OpenAI.
        AZURE_OPENAI_CHATGPT_DEPLOYMENT_NAME: The deployment name for Azure OpenAI ChatGPT.
        AZURE_OPENAI_API_VERSION: The API version for Azure OpenAI.
        OPENAICOM_API_KEY: The API key for OpenAI.
        OPENAICOM_MODEL: The model name for OpenAI (default is "gpt-4o-mini").

    """
    global openai_client, openai_model_arg

    client_args = {}
    if os.getenv("AZURE_OPENAI_ENDPOINT"):
        if os.getenv("AZURE_OPENAI_API_KEY"):
            client_args["api_key"] = os.getenv("AZURE_OPENAI_API_KEY")
        else:
            client_args["azure_ad_token_provider"] = get_bearer_token_provider(
                get_azure_credential(), "https://cognitiveservices.azure.com/.default"
            )
        if not os.getenv("AZURE_OPENAI_ENDPOINT"):
            raise ValueError("AZURE_OPENAI_ENDPOINT is required for Azure OpenAI")
        if not os.getenv("AZURE_OPENAI_CHATGPT_DEPLOYMENT_NAME"):
            raise ValueError(
                "AZURE_OPENAI_CHATGPT_DEPLOYMENT_NAME is required for Azure OpenAI"
            )
        openai_client = AzureOpenAI(
            api_version=os.getenv("AZURE_OPENAI_API_VERSION") or "2024-10-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            **client_args,
        )
        openai_model_arg = os.getenv("AZURE_OPENAI_CHATGPT_DEPLOYMENT_NAME")

    elif os.getenv("OPENAI_API_KEY"):
        client_args["api_key"] = os.getenv("OPENAI_API_KEY")
        openai_client = OpenAI(
            **client_args,
        )
        openai_model_arg = os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
    else:
        raise ValueError(
            "No OpenAI configuration provided. Check your environment variables."
        )


def main_conversation(args, user_object_id=None, use_elm327=False):
    """
    Unified handler for voice commands, with optional ELM327 support.

    Args:
        args: Parsed command-line arguments.
        user_object_id: The user object ID for Microsoft Graph API.
        use_elm327: Boolean indicating whether to use ELM327 functionalities.

    Returns:
        None
    """
    standby_phrases = ["enter standby mode", "go to sleep", "stop listening"]
    wakeup_phrases = ["wake up", "i need your help", "start listening"]

    standby_mode = False
    conversation_history = load_conversation_history()
    conversation_active = True

    # Initialize ELM327 resources if needed
    ser = None
    if use_elm327:
        try:
            ser = serial.Serial(
                port=os.getenv("SERIAL_PORT"),
                baudrate=os.getenv("BAUD_RATE"),
                timeout=10,
            )
            print("ELM327 device connected.")
        except serial.SerialException as e:
            print(f"Failed to connect to ELM327 device: {e}")
            use_elm327 = False  # Disable ELM327 features if connection fails

    configure_openai()

    while True:
        if not standby_mode:
            print("\nPlease say a command:")
        text = recognize_speech()
        if text:
            lower_text = text.lower()
            if any(phrase in lower_text for phrase in standby_phrases):
                standby_mode = True
                print("Entering standby mode.")
                tts_output("Entering standby mode.")
                continue

            if standby_mode and any(phrase in lower_text for phrase in wakeup_phrases):
                standby_mode = False
                print("Exiting standby mode.")
                tts_output("Exiting standby mode.")
                continue

            if standby_mode:
                continue

            if not standby_mode and conversation_active:
                if "summarize the conversation history" in lower_text:
                    conversation_history = summarize_conversation_history_direct(conversation_history)
                    save_conversation_history(conversation_history)
                    print("Conversation history summarized.")
                    tts_output("The current conversation has been summarized.")
                    continue

                if "clear all history" in lower_text:
                    conversation_history = [
                        {"role": "system", "content": "You are Winston, an in car AI assistant."}
                    ]
                    save_conversation_history(conversation_history)
                    print("Conversation history cleared.")
                    tts_output("The history of the current conversation has been cleared.")
                    continue

                if "delete the last message" in lower_text:
                    if len(conversation_history) > 1:
                        conversation_history.pop()
                        save_conversation_history(conversation_history)
                        print("Last message removed.")
                        tts_output("The last message has been deleted.")
                    else:
                        print("No messages to remove.")
                    continue

                if "end the conversation" in lower_text:
                    conversation_active = False
                    print("Ending the conversation.")
                    continue

            if not standby_mode and not conversation_active and "start a conversation" in lower_text:
                conversation_active = True
                print("Starting a conversation.")
                continue

            if not standby_mode and conversation_active:
                if openai_client is None:
                    print("OpenAI client is not configured, main.py.")
                    tts_output("The OpenAI client is not configured.")
                    continue
                chatgpt_response = chat_gpt_conversation(text, conversation_history)
                conversation_history.append({"role": "user", "content": text})
                conversation_history.append({"role": "assistant", "content": chatgpt_response})
                save_conversation_history(conversation_history)
                print(f"Assistant: {chatgpt_response}")
                tts_output(chatgpt_response)
                continue

            # Handle ELM327-specific commands if enabled
            if use_elm327:
                if any(cmd in lower_text for cmd in ELM327_COMMANDS):
                    # Assuming recognize_command extracts a command from the text
                    recognized_command = recognize_command(lower_text, ELM327_COMMANDS)
                    if recognized_command:
                        if recognized_command == "send_diagnostic_report":
                            send_diagnostic_report(ser)
                            print("Diagnostic report sent to your email.")
                        else:
                            response = send_command(ser, recognized_command)
                            print(f"Raw response: {response}")
                            if "NO DATA" not in response:
                                value = None
                                if recognized_command == "0105":
                                    value = int(response.split()[2], 16) - 40
                                    value = (value * 9 / 5) + 32
                                    print(f"Engine Coolant Temperature (F): {value}")
                                    processed_data = (
                                        f"{text}: {response} - Engine Coolant Temperature (F): {value}"
                                    )
                                elif recognized_command == "010C":
                                    value = (
                                        int(response.split()[2], 16) * 256
                                        + int(response.split()[3], 16)
                                    ) / 4
                                    print(f"Engine RPM: {value}")
                                    processed_data = (
                                        f"{text}: {response} - Engine RPM: {value}"
                                    )
                                elif recognized_command == "0902":
                                    vin_response = parse_vin_response(response)
                                    print(f"VIN response: {vin_response}")
                                    vehicle_data = decode_vin(vin_response)
                                    print(f"Decoded VIN: {vehicle_data}")
                                    processed_data = (
                                        f"VIN response: {vin_response}\nDecoded VIN: {vehicle_data}"
                                    )
                                else:
                                    processed_data = process_data(text, response, value)

                                chatgpt_response = extract_vin(processed_data)
                                print(f"ChatGPT Response: {chatgpt_response}")
                                # Optionally, uncomment the following line to enable TTS
                                tts_output(chatgpt_response)
                            else:
                                print(f"{text} not available.")
                    else:
                        print("ELM327 command not recognized. Please try again.")
                    continue

            # Handle voice commands
            recognized_command = recognize_command(lower_text, list(voice_commands.keys()))

            if recognized_command:
                cmd = voice_commands[recognized_command]

                if cmd == "next_appointment":
                    next_appointment = get_next_appointment(user_object_id)
                    print(f"{next_appointment}")

                elif cmd == "create_appointment":
                    create_new_appointment(recognize_speech)
                    print("New appointment created.")

                elif cmd == "check_outlook_email":
                    emails = get_emails(user_object_id)
                    if emails:
                        for email in emails:
                            print(f"\nSubject: {email['subject']}")
                            print(f"From: {email['from']['emailAddress']['address']}")
                            print(f"Date: {email['receivedDateTime']}")
                            print(f"Body: {email['body']['content']}")
                    else:
                        print("No emails found.")

                elif cmd == "send_email":
                    email_to = "example@example.com"
                    subject = "Test email"
                    body = "This is a test email."
                    attachments = ["file1.txt", "file2.txt"]
                    send_email_with_attachments(email_to, subject, body, attachments)

                elif cmd == "ASK_CHATGPT_QUESTION":
                    print("Please ask your question:")
                    question = recognize_speech()
                    if question:
                        chatgpt_response = chat_gpt(question)
                        print(f"Answer: {chatgpt_response}")
                    else:
                        print("I didn't catch your question. Please try again.")
            else:
                if not standby_mode and not conversation_active:
                    print("Command not recognized. Please try again.")
                elif conversation_active:
                    print("Unrecognized input. Please try again.")
        else:
            print("No speech detected. Please try again.")
