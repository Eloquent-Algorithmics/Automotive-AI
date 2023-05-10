"""
This module demonstrates usage of the OpenAI API with environment variables.
"""
import os
import openai
import serial
from gpt_chat import chat_gpt
import graph_api
import ms_authserver
from voice_recognition import handle_voice_commands
from audio_output import tts_output, initialize_audio
from config import OPENAI_API_KEY, GRAPH_EMAIL_ADDRESS, GRAPH_CLIENT_ID, GRAPH_CLIENT_SECRET, SERIAL_PORT, BAUD_RATE, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_PHONE_NUMBER, TEXT_TO_PHONE_NUMBER

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

# Read the values from the environment variables
PORT = os.getenv("SERIAL_PORT")
BAUD_RATE = int(os.getenv("BAUD_RATE"))

# Create a serial connection to the ELM327 device
ser = serial.Serial(PORT, BAUD_RATE, timeout=1)

# Call the function to handle voice commands and pass the 'ser' object
handle_voice_commands(ser,graph_api.user_object_id)

# Close the serial connection
ser.close()
