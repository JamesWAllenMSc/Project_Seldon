"""Daily Price Update Module

This module handles the daily updates of price data for all tickers across exchanges.
"""

# Standard library imports
from datetime import datetime, date
from typing import List, Optional, Dict, Any

# Third-party imports
import pandas as pd

# Local application imports
from lib.data_centre.database.utils import database_utils, eodhd_utils
from config.connections.database_access import DB_CONFIG
from config.connections.eodhd_access import EODHD_CONFIG
from config.settings.logging import logger_factory

logger = logger_factory.get_logger('database', module_name=__name__)


# Constants
PRICE_TABLE_SCHEMA = """
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

LATEST_PRICE_DATE_QUERY = """
    SELECT MAX(Date) AS LatestDate
    FROM prices_{exchange}_{year};
"""

TICKER_COLUMNS = [
    'Ticker_ID', 'Ticker', 'Name', 'Country', 'Exchange', 'EoDHD_Exchange',
    'Currency', 'Type', 'Isin', 'Source', 'Date_Updated'
]

PRICE_COLUMNS_SORTED = [
    'Ticker_ID', 'Ticker', 'Exchange', 'EoDHD_Exchange', 'Date', 'Open', 'High', 'Low', 
    'Close', 'Adjusted_Close', 'Volume'
]


def _get_exchange_codes() -> List[str]:
    """Retrieve list of exchange codes from database."""
    query = 'SELECT Exchange, EoDHD_Exchange FROM global_exchanges;'
    data = database_utils.retrieve_table(DB_CONFIG, query)
    data = pd.DataFrame(data, columns=['Exchange', 'EoDHD_Exchange'])
    return data

def _ensure_price_table(exchange: str, year: int) -> None:
    """Create price table for exchange and year if it doesn't exist."""
    query = PRICE_TABLE_SCHEMA.format(exchange=exchange, year=year)
    database_utils.execute_query(DB_CONFIG, query)

def _get_latest_price_date(exchange: str, year: int) -> Optional[datetime.date]:
    """Get the most recent price date for an exchange from the database.
    
    Args:
        exchange (str): Exchange code
        year (int): Year to check
        
    Returns:
        Optional[date]: The latest price date if exists, None otherwise
    """
    
    query = LATEST_PRICE_DATE_QUERY.format(exchange=exchange, year=year)
    latest_price_date = database_utils.retrieve_table(DB_CONFIG, query)
    # Handle empty list or None result
    if not latest_price_date or latest_price_date[0][0] is None:
        return None
    return pd.to_datetime(latest_price_date[0][0]).date()
    

def _get_db_tickers(db_config: Dict[str, Any], exchange: str) -> pd.DataFrame:
    """Retrieve tickers for specific exchange from database."""
    query = f"SELECT Ticker FROM global_tickers WHERE Exchange='{exchange}';"
    table = database_utils.retrieve_table(db_config, query)
    return pd.DataFrame(table, columns=['Ticker'])


def daily_price_update() -> None:
    """Update daily prices for all exchanges."""
    current_year = datetime.now().year

    # Get code and eod_code from global exchanges table iterate over
    exchanges = _get_exchange_codes()
    
    for exchange_code in exchanges.itertuples():
        
        exchange = exchange_code.Exchange
        eod_exchange = exchange_code.EoDHD_Exchange
        
        try:
            # Get new price data from EoDHD for whole exchange. US stocks ('NASDAQ', 'NYSE') handled as 'US'
            new_prices = eodhd_utils.retrieve_daily_price(
                eod_exchange, exchange,
                EODHD_CONFIG['api_key']
            )
            tickers = _get_db_tickers(DB_CONFIG, exchange)
            df = new_prices.merge(tickers, on='Ticker', how='left')
            
            df['Ticker_ID'] = f'{df['Ticker'].iloc[0]}_{exchange}' 
            new_prices_final = df[PRICE_COLUMNS_SORTED]
            
            if new_prices_final is None:
                logger.warning(f"No new price data for {exchange}, using EoD Code {eod_exchange}")
                continue
            
            new_price_date = pd.to_datetime(new_prices['Date'].iloc[0]).date()
            # Ensure price table exists
            _ensure_price_table(exchange, current_year)
           
            # Get latest existing price data from local database
            latest_price_date = _get_latest_price_date(exchange, current_year)
                        
            if latest_price_date is None:
                logger.info(f"No existing prices for {exchange}. Consider historical update")
                continue
            
            # Update if new data available
            if new_price_date > latest_price_date:
                              
                database_utils.add_stock_price(
                    new_prices_final, 
                    exchange, 
                    current_year, 
                    DB_CONFIG
                )
                logger.debug(f"Updated prices for {exchange} for {new_price_date}")
            else:
                logger.info(f"Prices for {exchange} already up to date")
                
                
        except Exception as e:
            logger.error(f"Error updating {exchange} using EoD Code {eod_exchange}: {str(e)}", exc_info=True)
            continue

if __name__ == "__main__":
    daily_price_update()