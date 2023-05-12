import openai
import serial
from gpt_chat import chat_gpt
import graph_api
import ms_authserver
from voice_recognition import handle_voice_commands, handle_voice_commands_j2534
from audio_output import tts_output, initialize_audio
from config import OPENAI_API_KEY, SERIAL_PORT, BAUD_RATE
import argparse
from j2534 import J2534

# Use the OPENAI_API_KEY variable from the config.py file
openai.api_key = OPENAI_API_KEY

# Get the authorization code from ms_authserver
authorization_code = ms_authserver.get_auth_code()

# Perform the Graph API request using the authorization code
graph_api.perform_graph_api_request(authorization_code)

initialize_audio()

response_text = chat_gpt("Hello")
print(response_text)

# Call the tts_output function with the generated response
tts_output(response_text)

# Add a function to create a J2534 connection
def create_j2534_connection():
    j2534_devices = J2534().detect_devices()
    if not j2534_devices:
        raise Exception("No J2534 device found")
    device = j2534_devices[0]
    
    # Set up the protocol configuration for ISO 15765 (CAN)
    config = {
        'ProtocolID': J2534.PROTOCOL.ISO15765,
        'Flags': J2534.PROTOCOL.ISO15765_FRAME_PAD,
        'BaudRate': 500000,  # You may need to adjust the baud rate depending on your device
    }
    
    channel = device.connect(config)
    return channel

# Add command-line argument parsing
parser = argparse.ArgumentParser(description="Choose the device type")
parser.add_argument(
    "--device",
    choices=["elm327", "j2534"],
    default="elm327",
    help="Select the device type (default: elm327)",
)
args = parser.parse_args()

# Modify the main part of the script to use the selected device
if args.device == "elm327":
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    handle_voice_commands(ser, graph_api.user_object_id)
    ser.close()
elif args.device == "j2534":
    channel = create_j2534_connection()
    handle_voice_commands_j2534(channel, graph_api.user_object_id)
    channel.close()
