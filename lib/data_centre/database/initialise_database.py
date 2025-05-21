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

# Add project root to Python path before other imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT))
# print(f"Project root path: {PROJECT_ROOT}")


# Third-party imports
from mysql.connector import connect, Error

# Local application imports
from config.settings.paths import PATHS
from config.connections.database_access import DB_CONFIG
from lib.data_centre.database.utils import database_utils
from config.settings.logging import logger_factory
from lib.data_centre.database.scripts import (
    exchanges_update,
    tickers_update,
    populate_price_history,
    update_all_views,
)

logger = logger_factory.get_logger('database', module_name=__name__)

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