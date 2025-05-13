"""
Project Seldon
Main application entry point

"The larger the mass of humanity being dealt with, the greater 
the accuracy of psychohistorical predictions."
- Second Foundation Theorem

Author: James Allen
Twitter: @JamesAllenMSc
Creation Date: May 8, 2025
"""

from lib.data_centre.database.database_manager import main as db_manager
from lib.data_centre.database.config.database_logging_config import logger

def main():
    """Main entry point for Project Seldon."""
    try:
        logger.info("Starting Project Seldon...")
        db_manager()
    except KeyboardInterrupt:
        logger.info("Shutting down Project Seldon...")
    except Exception as e:
        logger.error(f"Fatal error in main program: {e}")
        raise

if __name__ == "__main__":
    main()