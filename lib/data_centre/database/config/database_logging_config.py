import logging
import os
from pathlib import Path

# Create a named logger instance for the database operations
logger = logging.getLogger('database_logger')

# Define log paths using Path for cross-platform compatibility
LOG_DIR = Path('logs/database_logs')
LOG_FILE = LOG_DIR / 'database_event.log'

def setup_logging():
    # Ensure log directory exists
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Configure the root logger
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='Datetime:%(asctime)s - Level:%(levelname)s - Module:%(module)s - Function:%(funcName)s - Message:%(message)s'
    )
    
    # Add console handler for development visibility
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    
    return logger

# Initialize the logger
logger = setup_logging()