import logging
import os
from pathlib import Path

# Create a named logger instance for the database operations
logger = logging.getLogger('global_logger')
logger.setLevel(logging.INFO)

# Define log paths using Path for cross-platform compatibility
LOG_DIR = Path('global_logs')
LOG_FILE = LOG_DIR / 'global_event.log'

def setup_logger():
    # Ensure log directory exists
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Create formatters
    formatter = logging.Formatter(
        'Datetime:%(asctime)s - Level:%(levelname)s - Module:%(module)s - Function:%(funcName)s - Message:%(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Add both handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Initialize the logger
logger = setup_logger()
