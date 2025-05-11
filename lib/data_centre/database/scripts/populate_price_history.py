"""Price History Population Module

This module populates historical price data for all tickers across exchanges.
"""

# Standard library imports
from datetime import datetime
from typing import List

# Third-party imports
import pandas as pd

# Local application imports
from utils import database_utils, eodhd_utils
from config.database_access_config import DB_CONFIG
from config.eodhd_access_config import EODHD_CONFIG
from lib.data_centre.database.config.database_logging_config import logger

def _get_exchange_codes() -> List[str]:
    """Retrieve list of exchange codes from database."""
    query = 'SELECT Code FROM global_exchanges;'
    data = database_utils.retrieve_table(DB_CONFIG, query)
    return pd.DataFrame(data, columns=['Code'])['Code'].tolist()

def _get_ticker_codes(exchange: str) -> List[str]:
    """Retrieve ticker codes for a specific exchange."""
    query = f"SELECT Code FROM global_tickers WHERE Exchange='{exchange}';"
    data = database_utils.retrieve_table(DB_CONFIG, query)
    return pd.DataFrame(data, columns=['Code'])['Code'].tolist()

def _create_price_table(exchange: str, year: int) -> None:
    """Create price table for specific exchange and year if not exists."""
    query = f"""
        CREATE TABLE IF NOT EXISTS prices_{exchange}_{year} (
            Ticker_ID VARCHAR(255),
            Date DATE,
            Open DECIMAL(20,6),
            High DECIMAL(20,6),
            Low DECIMAL(20,6),
            Close DECIMAL(20,6),
            Adjusted_Close DECIMAL(20,6),
            Volume BIGINT
        );
    """
    database_utils.execute_query(DB_CONFIG, query)

def populate_price_history() -> None:
    """Populate historical price data for all tickers across exchanges."""
    today = datetime.now().strftime('%Y-%m-%d')
    
    for exchange in _get_exchange_codes():
        updates = 0
        total = 0
        
        for ticker in _get_ticker_codes(exchange):
            total += 1
            
            # Get historical price data
            price_data = eodhd_utils.retrieve_historical_price(
                exchange, ticker, today, EODHD_CONFIG['api_key']
            )
            
            if price_data is None:
                continue
            updates += 1
            # Process each year's data
            price_data['Date'] = pd.to_datetime(price_data['Date'])
            for year in sorted(price_data['Date'].dt.year.unique(), reverse=True):
                _create_price_table(exchange, year)
                
                yearly_data = price_data[price_data['Date'].dt.year == year]
                database_utils.add_stock_price(yearly_data, exchange, year, DB_CONFIG)
                logger.debug(f"Added historical prices for {ticker} ({year})")
                
        logger.info(f"Updated {updates}/{total} historical prices for {exchange}")

if __name__ == "__main__":
    populate_price_history()