"""
This is the main script of the application.
"""
import argparse
import sys

import api.google_functions.google_api as google_api
import api.microsoft_functions.ms_authserver as ms_authserver
from api.microsoft_functions import graph_api
from api.openai_functions.gpt_chat import configure_openai
from config import EMAIL_PROVIDER
from voice.elm327 import handle_voice_commands_elm327
from voice.voice_recognition import handle_common_voice_commands
from audio.audio_output import tts_output


def main():
    """
    Main function to encapsulate the script logic.
    """

    email_provider = EMAIL_PROVIDER

    tts_output("Allow me to introduce myself... I am Winston, a virtual Artificial Intelligence Assistant ... Importing all preferences and settings ... Systems now fully operational.")

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
        configure_openai()
        main()
    except KeyboardInterrupt:
        print("\nGoodbye for now ...\n")
        sys.exit(0)
