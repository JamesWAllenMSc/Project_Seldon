"""Price History Population Module

This module populates historical price data for all tickers across exchanges.
"""

# Standard library imports
from datetime import datetime
from typing import List

# Third-party imports
import pandas as pd

# Local application imports
from lib.data_centre.database.utils import database_utils, eodhd_utils
from config.connections.database_access import DB_CONFIG
from config.connections.eodhd_access import EODHD_CONFIG
from config.settings.logging import logger_factory

logger = logger_factory.get_logger('database', module_name=__name__)

# Constants
TABLE_COLUMNS_SORTED = [
    'Ticker_ID', 'Ticker', 'Exchange', 'EoDHD_Exchange',
    'Date', 'Open', 'High', 'Low', 'Close', 'Adjusted_Close', 'Volume'
]

def _get_exchange_codes() -> List[str]:
    """Retrieve list of exchange codes from database."""
    query = 'SELECT Code FROM global_exchanges;'
    data = database_utils.retrieve_table(DB_CONFIG, query)
    return pd.DataFrame(data, columns=['Code'])['Code'].tolist()

def _get_ticker_codes():
    """Retrieve ticker codes for a specific exchange."""
    query = f"SELECT Ticker, Exchange, EoDHD_Exchange FROM global_tickers;"
    data = database_utils.retrieve_table(DB_CONFIG, query)
    data = pd.DataFrame(data, columns=['Ticker', 'Exchange', 'EoDHD_Exchange'])
    return data

def _create_price_table(exchange: str, year: int) -> None:
    """Create price table for specific exchange and year if not exists."""
    query = f"""
        CREATE TABLE IF NOT EXISTS prices_{exchange}_{year} (
            Ticker_ID VARCHAR(255),
            Ticker VARCHAR(255),
            Exchange VARCHAR(255),
            EoDHD_Exchange VARCHAR(255),
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
           
    ticker = _get_ticker_codes()
    for tickers in ticker.itertuples():
        ticker = tickers.Ticker
        eod_exchange = tickers.EoDHD_Exchange
        exchange = tickers.Exchange
            
        # Get historical price data
        price_data = eodhd_utils.retrieve_historical_price(
            eod_exchange, ticker, today, EODHD_CONFIG['api_key']
        )
        
        if price_data is None:
            logger.info(f"Unable to retrieve historical prices for ({ticker}) using ({eod_exchange}) from EODHD.com")
            continue
        price_data['Ticker'] = ticker
        price_data['Exchange'] = exchange
        price_data['EoDHD_Exchange'] = eod_exchange
        price_data['Ticker_ID'] = f'{ticker}_{exchange}'
        price_data = price_data[TABLE_COLUMNS_SORTED]
                
        # Process each year's data
        price_data['Date'] = pd.to_datetime(price_data['Date'])
        
        for year in sorted(price_data['Date'].dt.year.unique(), reverse=True):
            _create_price_table(exchange, year)
            yearly_data = price_data[price_data['Date'].dt.year == year]
            
            database_utils.add_stock_price(yearly_data, exchange, year, DB_CONFIG)
        
        logger.debug(f"Updated historical prices for {ticker} on {exchange}")

if __name__ == "__main__":
    populate_price_history()