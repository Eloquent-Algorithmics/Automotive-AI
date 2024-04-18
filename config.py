"""
This module loads environment variables from the .env file.
"""
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Get environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY environment variable is not set")
OPENAI_ORG_ID = os.getenv("OPENAI_ORG_ID")
if OPENAI_ORG_ID is None:
    raise ValueError("OPENAI_ORG_ID environment variable is not set")
OPENAI_PROJECT_ID = os.getenv("OPENAI_PROJECT_ID")
if OPENAI_PROJECT_ID is None:
    raise ValueError("OPENAI_PROJECT_ID environment variable is not set")

EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER")
if EMAIL_PROVIDER is None:
    raise ValueError("EMAIL_PROVIDER environment variable is not set")

GRAPH_EMAIL_ADDRESS = os.getenv("GRAPH_EMAIL_ADDRESS")
if GRAPH_EMAIL_ADDRESS is None:
    raise ValueError("GRAPH_EMAIL_ADDRESS environment variable is not set")
GRAPH_CLIENT_ID = os.getenv("GRAPH_CLIENT_ID")
if GRAPH_CLIENT_ID is None:
    raise ValueError("GRAPH_CLIENT_ID environment variable is not set")
GRAPH_CLIENT_SECRET = os.getenv("GRAPH_CLIENT_SECRET")
if GRAPH_CLIENT_SECRET is None:
    raise ValueError("GRAPH_CLIENT_SECRET environment variable is not set")
GRAPH_TENANT_ID = os.getenv("GRAPH_TENANT_ID")
if GRAPH_TENANT_ID is None:
    raise ValueError("GRAPH_TENANT_ID environment variable is not set")

SERIAL_PORT = os.getenv("SERIAL_PORT")
if SERIAL_PORT is None:
    raise ValueError("SERIAL_PORT environment variable is not set")
baud_rate_str = os.getenv("BAUD_RATE")
if baud_rate_str is None:
    raise ValueError("BAUD_RATE environment variable is not set")
BAUD_RATE = int(baud_rate_str)

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_PHONE_NUMBER = os.getenv("TWILIO_FROM_PHONE_NUMBER")
TEXT_TO_PHONE_NUMBER = os.getenv("TEXT_TO_PHONE_NUMBER")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
GOOGLE_CUSTOM_SEARCH_ID = os.getenv("GOOGLE_CUSTOM_SEARCH_ID")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

TTS_ENGINE = os.getenv("TTS_ENGINE", "pyttsx4")
TTS_VOICE_ID = os.getenv("TTS_VOICE_ID")
TTS_RATE = os.getenv("TTS_RATE")
INPUT_MODE = os.getenv('INPUT_MODE', 'text')
