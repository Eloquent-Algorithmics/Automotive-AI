import openai
import serial
from api.gpt_chat import chat_gpt
import api.graph_api as graph_api
import api.ms_authserver as ms_authserver
from voice.voice_recognition import handle_voice_commands_elm327, handle_voice_commands_j2534, handle_voice_commands_without_device
from audio.audio_output import tts_output, initialize_audio
from config import OPENAI_API_KEY, SERIAL_PORT, BAUD_RATE
import argparse
from j2534_cffi import find_j2534_passthru_dlls, J2534PassThru

openai.api_key = OPENAI_API_KEY
authorization_code = ms_authserver.get_auth_code()
graph_api.perform_graph_api_request(authorization_code)
initialize_audio()

response_text = chat_gpt("Hello")
print(response_text)
tts_output(response_text)

def create_j2534_connection():
    # Find the J2534 passthru DLLs
    passthru_dlls = find_j2534_passthru_dlls()
    if not passthru_dlls:
        raise Exception("No J2534 passthru DLL found")
    device_name, passthru_dll = passthru_dlls[0]

    # Load the J2534 library
    j2534_lib = J2534PassThru(passthru_dll)

    # Open a J2534 device
    device = j2534_lib.open()

    # Set up the protocol configuration for ISO 15765 (CAN)
    config = {
        'ProtocolID': j2534_lib.PROTOCOL_ISO15765,
        'Flags': j2534_lib.PROTOCOL_ISO15765_FRAME_PAD,
        'BaudRate': 500000,  # You may need to adjust the baud rate depending on your device
    }

    # Connect to the J2534 device
    channel = device.connect(config)
    return channel

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
    handle_voice_commands_without_device(graph_api.user_object_id)
elif args.device == "elm327":
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    handle_voice_commands_elm327(ser, graph_api.user_object_id)
    ser.close()
elif args.device == "j2534":
    channel = create_j2534_connection()
    handle_voice_commands_j2534(channel, graph_api.user_object_id)
    channel.close()
