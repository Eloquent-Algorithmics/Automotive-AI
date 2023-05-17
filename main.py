"""
This is the main module.
"""
import argparse
import openai
import serial
from api.gpt_chat import chat_gpt
import api.graph_api as graph_api
import api.ms_authserver as ms_authserver
from voice.elm327 import handle_voice_commands_elm327
from voice.j2534 import create_j2534_connection, handle_voice_commands_j2534
from voice.voice_recognition import handle_common_voice_commands
from audio.audio_output import tts_output, initialize_audio
from config import OPENAI_API_KEY, SERIAL_PORT, BAUD_RATE

openai.api_key = OPENAI_API_KEY
authorization_code = ms_authserver.get_auth_code()
graph_api.perform_graph_api_request(authorization_code)
initialize_audio()

response_text = chat_gpt("Hello")
print(response_text)
tts_output(response_text)


# Add command-line argument parsing
parser = argparse.ArgumentParser(description="Choose the device type")
parser.add_argument(
    "--device",
    choices=["none", "elm327", "j2534"],
    default="none",
    help="Select the device type (default: none)",
)
args = parser.parse_args()

# Modify the main part of the script to use the selected device
if args.device == "none":
    handle_common_voice_commands(graph_api.user_object_id)
elif args.device == "elm327":
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    handle_voice_commands_elm327(ser, graph_api.user_object_id)
    ser.close()
elif args.device == "j2534":
    channel = create_j2534_connection()
    handle_voice_commands_j2534(channel, graph_api.user_object_id)
    channel.close()
