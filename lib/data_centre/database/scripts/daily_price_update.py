"""Daily Price Update Module

This module handles the daily updates of price data for all tickers across exchanges.
"""

# Standard library imports
from datetime import datetime
from typing import List, Optional

# Third-party imports
import pandas as pd

# Local application imports
from lib.data_centre.database.utils import database_utils, eodhd_utils
from lib.data_centre.database.config.database_access_config import DB_CONFIG
from lib.data_centre.database.config.eodhd_access_config import EODHD_CONFIG
from lib.data_centre.database.config.database_logging_config import logger

# Constants
PRICE_TABLE_SCHEMA = """
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

PRICE_QUERY = """
    SELECT 
        global_tickers.Code,
        global_tickers.Exchange,
        prices_{exchange}_{year}.*
    FROM global_tickers
    JOIN prices_{exchange}_{year} 
        ON global_tickers.Ticker_ID = prices_{exchange}_{year}.Ticker_ID
    WHERE global_tickers.Exchange = '{exchange}'
    AND prices_{exchange}_{year}.Date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
    ORDER BY prices_{exchange}_{year}.Date DESC;
"""

def _get_exchange_codes() -> List[str]:
    """Retrieve list of exchange codes from database."""
    query = 'SELECT Code FROM global_exchanges;'
    data = database_utils.retrieve_table(DB_CONFIG, query)
    return [code[0] for code in data]

def _ensure_price_table(exchange: str, year: int) -> None:
    """Create price table for exchange and year if it doesn't exist."""
    query = PRICE_TABLE_SCHEMA.format(exchange=exchange, year=year)
    database_utils.execute_query(DB_CONFIG, query)

def _get_latest_price(exchange: str, year: int) -> Optional[datetime.date]:
    """Get the most recent price date for an exchange."""
    query = PRICE_QUERY.format(exchange=exchange, year=year)
    data = database_utils.retrieve_table(DB_CONFIG, query)
    
    if not data:
        return None
        
    df = pd.DataFrame(data, columns=[
        'Ticker', 'Exchange', 'Ticker_ID', 'Date', 'Open', 'High', 
        'Low', 'Close', 'Adjusted_Close', 'Volume'
    ])
    return df['Date'].max()

def daily_price_update() -> None:
    """Update daily prices for all exchanges."""
    current_year = datetime.now().year
    
    for exchange in _get_exchange_codes():
        try:
            # Get new price data
            new_prices = eodhd_utils.retrieve_daily_price(
                exchange, 
                EODHD_CONFIG['api_key']
            )
            if new_prices is None:
                logger.warning(f"No new price data for {exchange}")
                continue
                
            new_price_date = pd.to_datetime(new_prices['Date'].iloc[0]).date()
            
            # Ensure price table exists
            _ensure_price_table(exchange, current_year)
            
            # Get latest existing price
            latest_price_date = _get_latest_price(exchange, current_year)
            
            if latest_price_date is None:
                logger.info(f"No existing prices for {exchange}. Consider historical update")
                continue
                
            # Update if new data available
            if new_price_date > latest_price_date:
                database_utils.add_stock_price(
                    new_prices, 
                    exchange, 
                    current_year, 
                    DB_CONFIG
                )
                logger.info(f"Updated prices for {exchange} to {new_price_date}")
            else:
                logger.info(f"Prices for {exchange} already up to date")
                
        except Exception as e:
            logger.error(f"Error updating {exchange}: {str(e)}", exc_info=True)
            continue

if __name__ == "__main__":
    daily_price_update()