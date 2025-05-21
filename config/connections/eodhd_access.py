from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Database configuration
EODHD_CONFIG = {
    'api_key': os.getenv('EODHD_API_KEY'),
    
}