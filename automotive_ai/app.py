"""
This is the main script of the application.
"""
import os
import argparse
import sys
from openai import OpenAI, AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from api._msal import ms_authserver
from api._msal import graph_api
from audio.audio_output import tts_output, ssml_output
from dotenv import load_dotenv
from rich.console import Console

console = Console()

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
            api_version=os.getenv("AZURE_OPENAI_API_VERSION") or "2024-10-21",
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


def main():
    """
    Main function to encapsulate the script logic.
    """

    ssml_text = """
                <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-GB">
                    <voice name="en-GB-OllieMultilingualNeural">
                        <prosody rate="medium" pitch="medium">
                            Allow me to introduce myself...
                            <break time="300ms"/>
                            I am Winston, your in-car Virtual Assistant...
                            <break time="300ms"/>
                            Importing all preferences and settings now.
                        </prosody>
                    </voice>
                </speak>
                """

    ssml_output(ssml_text)
    
    configure_openai()

    console.print("Allow me to introduce myself... I am Winston, your in car Virtual Assistant... Importing all preferences and settings.", style="bold green")

    parser = argparse.ArgumentParser(description="Choose the device type")
    parser.add_argument(
        "--device",
        choices=["none", "elm327"],
        default="none",
        help="Select the device type (default: none)",
    )

    args = parser.parse_args()

    authorization_code = ms_authserver.get_auth_code()
    graph_api.perform_graph_api_request(authorization_code)
    email_module = graph_api

    # Determine if ELM327 is to be used
    use_elm327 = args.device == "elm327"

    tts_output("Systems now fully operational. How may I assist you today?")
    console.print("Systems now fully operational. How may I assist you today?", style="bold green")

    from main import main_conversation
    main_conversation(args, email_module.user_object_id, use_elm327)

    if openai_client is None:
        console.log("OpenAI client is not configured in app.py")
        return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye for now ...\n")
        sys.exit(0)
