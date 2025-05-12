""" Runs the database manager for the data center.
    Includes the following:
        - Daily updates of price and stock data
        - Monthly updates of global exchanges and new tickers
"""

# Standard library imports
from pathlib import Path

# Local application imports
from config.database_config import PATHS
from lib.data_centre.database.scripts import daily_price_update

# Set sys.path modification
project_root = PATHS['DATABASE']



daily_price_update()