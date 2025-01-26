import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
BING_API_KEY = os.getenv("BING_API_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
