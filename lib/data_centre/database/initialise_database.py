""" Start up script to set up all database tables and initial historical
    data.
"""

# Standard library imports
import sys
from pathlib import Path

# Third-party imports
from mysql.connector import connect, Error

# Local application imports
from config.database_config import PATHS
from config.database_access_config import DB_CONFIG
from utils import database_utils
from lib.data_centre.database.config.database_logging_config import logger
from lib.data_centre.database.scripts import exchanges_update, tickers_update

# Set sys.path modification
project_root = PATHS['DATABASE']

# Main initialization
#database_utils.clear_all_tables(DB_CONFIG) # Clears all database tables
exchanges_update(DB_CONFIG) # Updates the exchanges table
tickers_update()