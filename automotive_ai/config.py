# automotive_ai\config.py

"""
Centralized configuration management for the automotive_ai application.

Loads environment variables and initializes shared clients/configurations.
"""

import logging
import os

import msal
import serial
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from openai import AzureOpenAI, OpenAI
from rich.console import Console
from twilio.rest import Client as TwilioClient

# --- Logging ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(module)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Load Environment Variables ---
load_dotenv()

# --- Caching ---
_azure_credential = None
_openai_client = None
_openai_model_arg = None
_msal_app = None
_msal_tokens = None
_twilio_client = None
_serial_connection = None

# --- Console ---
console = Console()

# --- Azure OpenAI Credentials ---
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_CHATGPT_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_0")
AZURE_OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION", "2025-03-01-preview")

# --- OpenAI.com Credentials ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL_0", "gpt-4o-mini-realtime-preview-2024-12-17")

# --- Microsoft Authentication Library (MSAL) / Graph API ---
AUTH_TENANT_ID = os.getenv("AUTH_TENANT_ID")
AUTH_CLIENT_ID = os.getenv("AUTH_CLIENT_ID")
AUTH_CLIENT_SECRET = os.getenv("AUTH_CLIENT_SECRET")
GRAPH_API_SCOPES = ["https://graph.microsoft.com/.default"]
MS_REDIRECT_URI = "http://localhost:8000"
MS_AUTHORITY = (
    f"https://login.microsoftonline.com/{AUTH_TENANT_ID}" if AUTH_TENANT_ID else None
)

# --- Twilio ---
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_PHONE_NUMBER = os.getenv("TWILIO_FROM_PHONE_NUMBER")
TEXT_TO_PHONE_NUMBER = os.getenv("TEXT_TO_PHONE_NUMBER")

# --- Search APIs ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
BING_API_KEY = os.getenv("BING_API_KEY")

# --- ELM327 / Serial ---
SERIAL_PORT = os.getenv("SERIAL_PORT")
BAUD_RATE = int(os.getenv("BAUD_RATE", 500000))

# --- User Specific ---
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")


# --- Helper Functions to Check Configuration ---
def is_elm327_configured():
    """Checks if serial port is configured for ELM327."""
    return bool(SERIAL_PORT)


def is_graph_enabled():
    """Checks if Microsoft Graph (MSAL) is configured."""
    return bool(AUTH_CLIENT_ID and AUTH_CLIENT_SECRET and AUTH_TENANT_ID)


def is_openai_enabled():
    """Checks if any OpenAI service is configured."""
    return bool(AZURE_OPENAI_ENDPOINT or OPENAI_API_KEY)


def is_twilio_enabled():
    """Checks if Twilio is configured."""
    return bool(
        TWILIO_ACCOUNT_SID
        and TWILIO_AUTH_TOKEN
        and TWILIO_FROM_PHONE_NUMBER
        and TEXT_TO_PHONE_NUMBER
    )


def is_google_search_enabled():
    """Checks if Google Search is configured."""
    return bool(GOOGLE_API_KEY and GOOGLE_CSE_ID)


def is_bing_search_enabled():
    """Checks if Bing Search is configured."""
    return bool(BING_API_KEY)


# --- Client/Config Functions ---
def get_azure_credential():
    """
    Retrieves the Azure credential for authentication, caching the result.
    Uses DefaultAzureCredential. Returns None if unable to get credentials.
    """
    global _azure_credential

    if _azure_credential is None:

        try:
            console.print("Attempting to get Azure credentials...", style="bold blue")
            logger.info("Attempting to get Azure credentials...")
            _azure_credential = DefaultAzureCredential(
                exclude_shared_token_cache_credential=True
            )
            # Perform a quick check to ensure the credential is valid
            _azure_credential.get_token("https://management.azure.com/.default")
            console.print("Azure credential obtained successfully.", style="bold green")
            logger.info("Azure credential obtained successfully.")

        except Exception as e:
            console.print(f"Error obtaining Azure credential: {e}", style="bold red")
            logger.error(f"Warning: Error obtaining Azure credential: {e}.")
            _azure_credential = None

    return _azure_credential


def get_openai_client_config():
    """
    Configures and returns the OpenAI client (Azure or OpenAI.com) and model argument.
    Caches initialized client and model argument. Returns (None, None) if config fails.
    """
    global _openai_client, _openai_model_arg

    if _openai_client is not None and _openai_model_arg is not None:
        return _openai_client, _openai_model_arg

    if not is_openai_enabled():
        logger.info("Warning: No OpenAI configuration found (Azure or OpenAI.com).")
        return None, None

    client_args = {}
    try:
        if AZURE_OPENAI_ENDPOINT:
            logger.info("Configuring Azure OpenAI client...")
            if not AZURE_OPENAI_CHATGPT_DEPLOYMENT_NAME:
                logger.error("AZURE_OPENAI_DEPLOYMENT_0 is not set.")
                return None, None

            if AZURE_OPENAI_API_KEY:
                client_args["api_key"] = AZURE_OPENAI_API_KEY
                logger.info("Using API Key for Azure OpenAI.")
            else:
                logger.info("Using Azure AD Token Provider for Azure OpenAI.")
                try:
                    credential = get_azure_credential()
                    if not credential:
                        logger.error("Azure AD/Entra ID authentication failed.")
                    client_args["azure_ad_token_provider"] = get_bearer_token_provider(
                        credential, "https://cognitiveservices.azure.com/.default"
                    )
                except Exception as e:
                    logger.error(f"Azure AD authentication failed: {e}", exc_info=True)
                    return None, None

            try:
                _openai_client = AzureOpenAI(
                    api_version=AZURE_OPENAI_API_VERSION,
                    azure_endpoint=AZURE_OPENAI_ENDPOINT,
                    **client_args,
                )
                _openai_model_arg = AZURE_OPENAI_CHATGPT_DEPLOYMENT_NAME

            except Exception as e:
                logger.error(
                    f"Error initializing Azure OpenAI client: {e}", exc_info=True
                )
                _openai_client = None
                _openai_model_arg = None

        elif OPENAI_API_KEY:
            logger.info("Configuring OpenAI.com client...")
            client_args["api_key"] = OPENAI_API_KEY
            try:
                _openai_client = OpenAI(**client_args)
                _openai_model_arg = OPENAI_MODEL

                logger.info(
                    f"OpenAI.com client configured for model '{_openai_model_arg}'."
                )

            except Exception as e:
                logger.error(
                    f"Error initializing OpenAI.com client: {e}", exc_info=True
                )
                _openai_client = None
                _openai_model_arg = None
        else:
            _openai_client = None
            _openai_model_arg = None
            logger.warning(
                "No OpenAI configuration found (Azure or OpenAI.com)."
            )

    except Exception as e:
        logger.info(f"Error initializing OpenAI client: {e}")
        _openai_client = None
        _openai_model_arg = None

    return _openai_client, _openai_model_arg


# def get_speech_config():
#     """
#     Creates and returns the Azure Speech SDK configuration, caching the result.
#     Returns None if configuration fails or is disabled.
#     """
#     global _speech_config
#     if not is_speech_enabled():
#         logger.info(
#             "Warning: Speech services are not configured. Speech features disabled."
#         )
#         return None
#
#     if _speech_config is None:
#         try:
#             _speech_config = speechsdk.SpeechConfig(
#                 subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION
#             )
#             _speech_config.speech_synthesis_voice_name = AZURE_SPEECH_VOICE
#             logger.info(
#                 f"Speech config initialized."
#             )
#         except Exception as e:
#             logger.error(f"Error initializing Speech Config: {e}")
#             _speech_config = None
#
#     return _speech_config


def get_msal_app():
    """
    Initializes and returns the MSAL Confidential Client Application, caching result.
    Returns None if configuration fails or is disabled.
    """
    global _msal_app
    if not is_graph_enabled():
        logger.warning(
            "Warning: MSAL/Graph configuration incomplete."
        )
        return None

    if _msal_app is None:
        try:
            _msal_app = msal.ConfidentialClientApplication(
                client_id=AUTH_CLIENT_ID,
                client_credential=AUTH_CLIENT_SECRET,
                authority=MS_AUTHORITY,
            )
            logger.info("MSAL Confidential Client Application initialized.")
        except Exception as e:
            logger.error(f"Error initializing MSAL application: {e}")
            _msal_app = None  # Reset cache on error

    return _msal_app


def store_msal_tokens(token_result):
    """Stores MSAL tokens globally after successful acquisition."""
    global _msal_tokens
    if token_result and "access_token" in token_result:
        _msal_tokens = {
            "access_token": token_result["access_token"],
            "refresh_token": token_result.get(
                "refresh_token"
            ),  # May not always be present
        }
        logger.info("MSAL tokens stored.")
        # Consider storing user_object_id here if available in token claims
        # or from a /me call
    else:
        _msal_tokens = None
        logger.info("Warning: Attempted to store invalid MSAL token result.")


def get_msal_tokens():
    """Retrieves the stored MSAL tokens."""
    return _msal_tokens


def get_twilio_client():
    """Initializes and returns the Twilio client, caching result."""
    global _twilio_client
    if not is_twilio_enabled():
        logger.info("Warning: Twilio configuration incomplete. SMS features disabled.")
        return None

    if _twilio_client is None:
        try:
            _twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            logger.info("Twilio client initialized.")
        except Exception as e:
            logger.info(f"Error initializing Twilio client: {e}")
            _twilio_client = None
    return _twilio_client


def get_serial_connection():
    """Initializes and returns the Serial connection, caching result."""
    global _serial_connection
    if not is_elm327_configured():
        logger.info(
            "Info: ELM327 serial port not configured. ELM327 features disabled."
        )
        return None

    if _serial_connection is None:
        try:
            _serial_connection = serial.Serial(
                port=SERIAL_PORT,
                baudrate=BAUD_RATE,
                timeout=10,  # Consider making timeout configurable
            )
            logger.info(
                f"Serial connection established on {SERIAL_PORT} at {BAUD_RATE} baud."
            )
        except serial.SerialException as e:
            logger.info(f"Error: Failed to connect to serial port {SERIAL_PORT}: {e}")
            _serial_connection = None  # Reset cache on error
    return _serial_connection


def close_serial_connection():
    """Closes the cached serial connection if it's open."""
    global _serial_connection
    if _serial_connection and _serial_connection.is_open:
        try:
            _serial_connection.close()
            _serial_connection = None  # Clear cache
            logger.info("Serial connection closed.")
        except Exception as e:
            logger.info(f"Error closing serial connection: {e}")


# --- Initial Configuration Summary ---
def print_config_summary():
    logger.info("-" * 30)
    logger.info("Configuration Loading Summary:")
    logger.info(f"OpenAI Enabled: {is_openai_enabled()}")
    if is_openai_enabled():
        logger.info(
            f"  - Provider: {'Azure' if AZURE_OPENAI_ENDPOINT else 'OpenAI.com'}"
        )
    # logger.info(f"Speech Enabled: {is_speech_enabled()}")
    # if is_speech_enabled():
    #     logger.info(f"  - Region: {AZURE_SPEECH_REGION}, Voice: {AZURE_SPEECH_VOICE}")
    logger.info(f"Graph Enabled: {is_graph_enabled()}")
    if is_graph_enabled():
        logger.info(f"  - Tenant ID: {AUTH_TENANT_ID}, Client ID: {AUTH_CLIENT_ID}")
    logger.info(f"ELM327 Configured: {is_elm327_configured()}")
    if is_elm327_configured():
        logger.info(f"  - Port: {SERIAL_PORT}, Baud Rate: {BAUD_RATE}")
    logger.info(f"Twilio Enabled: {is_twilio_enabled()}")
    logger.info(f"Google Search Enabled: {is_google_search_enabled()}")
    logger.info(f"Bing Search Enabled: {is_bing_search_enabled()}")
    logger.info("-" * 30)


# Print summary when module is loaded
print_config_summary()

# --- Perform essential initializations ---
get_openai_client_config()  # Can be deferred until needed
get_msal_app()  # Definitely defer this until after auth code is obtained
