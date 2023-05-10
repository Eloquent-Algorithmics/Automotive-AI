"""
This module loads environment variables from a .env file.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GRAPH_EMAIL_ADDRESS = os.getenv("GRAPH_EMAIL_ADDRESS")
GRAPH_CLIENT_ID = os.getenv("GRAPH_CLIENT_ID")
GRAPH_CLIENT_SECRET = os.getenv("GRAPH_CLIENT_SECRET")
GRAPH_TENANT_ID = os.getenv("GRAPH_TENANT_ID")
SERIAL_PORT = os.getenv("SERIAL_PORT")
BAUD_RATE = int(os.getenv("BAUD_RATE"))
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_PHONE_NUMBER = os.getenv("TWILIO_FROM_PHONE_NUMBER")
TEXT_TO_PHONE_NUMBER = os.getenv("TEXT_TO_PHONE_NUMBER")
