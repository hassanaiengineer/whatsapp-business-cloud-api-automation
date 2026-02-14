import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # App Settings
    APP_NAME = "WhatsApp Business Automation"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Demo Mode (CRITICAL for demo purposes)
    DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
    
    # Meta WhatsApp API Settings
    META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
    PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")
    WHATSAPP_VERSION = "v19.0"
    
    # Database Settings
    DATABASE_URL = "sqlite:///./whatsapp_demo.db"

settings = Config()
