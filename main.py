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
"""
Project Seldon
Main application entry point

"The larger the mass of humanity being dealt with, the greater 
the accuracy of psychohistorical predictions."
- Second Foundation Theorem

Author: James Allen
Email: project_seldon@protonmail.com
Creation Date: May 8, 2025
Version: 0.1.0
"""

import os
import sys
from pathlib import Path

# Add project root to Python path before other imports
PROJECT_ROOT = Path(__file__).resolve().parent


# Now we can safely import our modules
from lib.data_centre.database.database_manager import main as database_manager
from config.global_logging_config import logger


def main() -> int:
    """
    Main entry point for Project Seldon.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    try:
        logger.info("Starting Project Seldon...")
        logger.info(f"Project root: {PROJECT_ROOT}")
        
        # Initialize database manager
        database_manager()
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Shutting down Project Seldon gracefully...")
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error in Project Seldon: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())