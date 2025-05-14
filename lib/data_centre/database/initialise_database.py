"""Database initialization script.

This script sets up all database tables and loads initial historical data.
It performs the following operations:
1. Clears existing tables
2. Updates exchange information
3. Updates ticker symbols
4. Populates historical price data
5. Refreshes database views
"""

# Standard library imports
import sys
from pathlib import Path

# Third-party imports
from mysql.connector import connect, Error

# Local application imports
from config.database_config import PATHS
from config.database_access_config import DB_CONFIG
from lib.data_centre.database.utils import database_utils
from lib.data_centre.database.config.database_logging_config import logger
from lib.data_centre.database.scripts import (
    exchanges_update,
    tickers_update,
    populate_price_history,
    update_all_views,
)

def main():
    """Execute the database initialization sequence."""
    try:
        # Clear existing data
        database_utils.clear_all_tables(DB_CONFIG)
        database_utils.clear_all_views(DB_CONFIG)

        # Update core data
        exchanges_update(DB_CONFIG)
        tickers_update()
        populate_price_history()

        # Refresh views
        update_all_views(DB_CONFIG)

        logger.info("Database initialization completed successfully")
        return 0

    except Error as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return 1

if __name__ == "__main__":
    # Set project root path
    project_root = PATHS['DATABASE']
    sys.exit(main())