"""
This is the main script of the application.
"""
import os
import argparse
import sys
import time

import azure.identity.aio
import redis.asyncio as redis
from dotenv import load_dotenv

import api.google_functions.google_api as google_api
import api.microsoft_functions.ms_authserver as ms_authserver
from api.microsoft_functions import graph_api
from api.openai_functions.gpt_chat import chat_gpt, configure_openai
from audio.audio_output import initialize_audio, tts_output
from config import EMAIL_PROVIDER
from voice.elm327 import handle_voice_commands_elm327
from voice.voice_recognition import handle_common_voice_commands


def get_azure_credential():
    if not hasattr("azure_credential"):
        azure_credential = azure.identity.aio.DefaultAzureCredential(exclude_shared_token_cache_credential=True)
    return azure_credential


async def setup_redis():
    azure_scope = "https://redis.azure.com/.default"
    use_azure_redis = os.getenv("AZURE_REDIS_HOST") is not None
    if use_azure_redis:
        host = os.getenv("AZURE_REDIS_HOST")
        redis_username = os.getenv("AZURE_REDIS_USER")
        port = 6380
        ssl = True
    else:
        host = "localhost"
        port = 6379
        redis_username = None
        password = None
        ssl = False
    if use_azure_redis:
        redis_token = await get_azure_credential().get_token(azure_scope)
        password = redis_token.token
    else:
        print("Using Redis with username and password")
    return redis.Redis(
        host=host, ssl=ssl, port=port, username=redis_username, password=password, decode_responses=True
    )


async def ensure_redis_token():
    if not hasattr("redis_token"):
        return
    redis_cache = cache
    redis_token = redis_token
    if redis_token.expires_on < time.time() + 60:
        print("Refreshing token...")
        tmp_token = await get_azure_credential().get_token("https://redis.azure.com/.default")
        if tmp_token:
            azure_token = tmp_token
        await redis_cache.execute_command("AUTH", redis_username, azure_token.token)
        print("Successfully refreshed token.")


def main():
    """
    Main function to encapsulate the script logic.
    """
    load_dotenv()

    configure_openai()

    email_provider = EMAIL_PROVIDER

    initialize_audio()

    response_text = chat_gpt("Hello")
    print(response_text)
    tts_output(response_text)

    parser = argparse.ArgumentParser(description="Choose the device type")
    parser.add_argument(
        "--device",
        choices=["none", "elm327"],
        default="none",
        help="Select the device type (default: none)",
    )

    args = parser.parse_args()

    api_module = None
    if email_provider == "365":
        authorization_code = ms_authserver.get_auth_code()
        graph_api.perform_graph_api_request(authorization_code)
        api_module = graph_api
    elif email_provider == "Google":
        api_module = google_api

    if args.device == "none":
        if email_provider == "365":
            handle_common_voice_commands(
                args, api_module.user_object_id, email_provider
            )
        elif email_provider == "Google":
            handle_common_voice_commands(
                args, api_module.user_object_id, email_provider
            )
    elif args.device == "elm327":
        handle_voice_commands_elm327(api_module.user_object_id)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye for now ...\n")
        sys.exit(0)
