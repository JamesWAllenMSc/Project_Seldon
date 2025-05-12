""" Database utility functions for Project Seldon.
Provides common database operations and helper functions.
"""

from .database_utils import (
    execute_query,
    retrieve_table,
    add_stock_price,
    clear_all_views
)

from .eodhd_utils import (
    retrieve_daily_price,
    retrieve_historical_price,
    retrieve_exchanges,
    retrieve_tickers
)

# Define what should be available when using "from utils import *"
__all__ = [
    'execute_query',
    'retrieve_table',
    'add_stock_price',
    'clear_all_views',
    'retrieve_daily_price',
    'retrieve_historical_price',
    'retrieve_exchanges',
    'retrieve_tickers'
]