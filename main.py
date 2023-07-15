"""
This is the main script of the application doc string.
"""
import argparse
import openai
from dotenv import load_dotenv

from api.openai_functions.gpt_chat import chat_gpt
from voice.elm327 import handle_voice_commands_elm327
from voice.voice_recognition import handle_common_voice_commands
from audio.audio_output import tts_output, initialize_audio
from config import OPENAI_API_KEY, EMAIL_PROVIDER

import api.microsoft_functions.graph_api as graph_api
import api.microsoft_functions.ms_authserver as ms_authserver
import api.google_functions.google_api as google_api

load_dotenv()

email_provider = EMAIL_PROVIDER

openai.api_key = OPENAI_API_KEY

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

if email_provider == "365":
    authorization_code = ms_authserver.get_auth_code()
    graph_api.perform_graph_api_request(authorization_code)

if email_provider == "Google":
    graph_api = google_api

if args.device == "none":
    if email_provider == "365":
        handle_common_voice_commands(args, graph_api.user_object_id, email_provider)
    elif email_provider == "Google":
        handle_common_voice_commands(args, email_provider=email_provider)
elif args.device == "elm327":
    handle_voice_commands_elm327(graph_api.user_object_id)
