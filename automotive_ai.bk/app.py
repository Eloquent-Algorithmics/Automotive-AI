"""
This is the main script of the application.
"""

import argparse
import sys

from _api._msal import _graph_api, _ms_authserver
from _audio._audio_output import ssml_output, tts_output
from dotenv import load_dotenv
from main import main_conversation
from rich.console import Console

console = Console()

load_dotenv()


def main_intro():
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

    console.print(
        "Allow me to introduce myself... I am Winston, your in car Virtual Assistant... Importing all preferences and settings.",
        style="bold green",
    )

    parser = argparse.ArgumentParser(description="Choose the device type")

    parser.add_argument(
        "--device",
        choices=["none", "elm327"],
        default="none",
        help="Select the device type (default: none)",
    )

    args = parser.parse_args()

    authorization_code = _ms_authserver.get_auth_code()
    _graph_api.perform_graph_api_request(authorization_code)
    email_module = _graph_api

    # Determine if ELM327 is to be used
    use_elm327 = args.device == "elm327"

    tts_output("Systems now fully operational. How may I assist you today?")
    console.print(
        "Systems now fully operational. How may I assist you today?", style="bold green"
    )

    main_conversation(args, email_module.user_object_id, use_elm327)


if __name__ == "__main__":
    try:
        main_intro()
    except KeyboardInterrupt:
        print("\nGoodbye for now ...\n")
        sys.exit(0)
