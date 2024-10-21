"""
This is the main script of the application.
"""

import argparse
import sys

import src.api.microsoft_functions.ms_authserver as ms_authserver
from src.api.microsoft_functions import graph_api
from src.api.openai_functions.gpt_chat import configure_openai
from src.voice.elm327 import handle_voice_commands_elm327
from src.voice.voice_recognition import handle_common_voice_commands
from src.audio.audio_output import tts_output


def main():
    """
    Main function to encapsulate the script logic.
    """

    tts_output(
        "Allow me to introduce myself... I am Winston, a virtual Artificial Intelligence Assistant ... Importing all preferences and settings ... Systems now fully operational."
    )

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

    if args.device == "none":

        handle_common_voice_commands(args, email_module.user_object_id)

    elif args.device == "elm327":
        handle_voice_commands_elm327(email_module.user_object_id)

if __name__ == "__main__":
    try:
        configure_openai()
        main()
    except KeyboardInterrupt:
        print("\nGoodbye for now ...\n")
        sys.exit(0)
