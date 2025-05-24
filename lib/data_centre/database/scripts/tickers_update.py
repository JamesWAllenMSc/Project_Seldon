"""
Ticker Update Module

This module handles the synchronization of ticker data between EODHD API
and the local database, adding any missing tickers.
"""

# Standard library imports
from typing import List, Dict, Any

# Third-party imports
import numpy as np
import pandas as pd

# Local application imports
from lib.data_centre.database.utils import database_utils, eodhd_utils
from config.connections.database_access import DB_CONFIG
from config.connections.eodhd_access import EODHD_CONFIG
from config.settings.logging import logger_factory

logger = logger_factory.get_logger('database', module_name=__name__)

# Constants
TICKER_COLUMNS = [
    'Ticker_ID', 'Code', 'Name', 'Country', 'Exchange', 'EoDHD_Exchange',
    'Currency', 'Type', 'Isin', 'Source', 'Date_Updated'
]

CREATE_TABLE_QUERY = """
    CREATE TABLE IF NOT EXISTS global_tickers (
        Ticker_ID VARCHAR(255),
        Code VARCHAR(255),
        Name VARCHAR(255),
        Country VARCHAR(255),
        Exchange VARCHAR(255),
        EoDHD_Exchange VARCHAR(255),
        Currency VARCHAR(255),
        Type VARCHAR(255),
        Isin VARCHAR(255),
        Source VARCHAR(255),
        Date_Updated DATETIME,
        PRIMARY KEY (Ticker_ID)
    );
"""

def _get_exchange_list(db_config: Dict[str, Any]) -> List[str]:
    """Retrieve list of exchange codes from database."""
    query = 'SELECT Code FROM global_exchanges;'
    table = database_utils.retrieve_table(db_config, query)
    return pd.DataFrame(table, columns=['Code'])['Code'].tolist()

def _get_db_tickers(db_config: Dict[str, Any], exchange: str) -> pd.DataFrame:
    """Retrieve tickers for specific exchange from database."""
    query = f"SELECT * FROM global_tickers WHERE Exchange='{exchange}';"
    table = database_utils.retrieve_table(db_config, query)
    return pd.DataFrame(table, columns=TICKER_COLUMNS)

def _prepare_tickers_for_upload(df: pd.DataFrame) -> tuple[str, str]:
    """Format ticker data for SQL insert."""
    columns = ', '.join(df.columns.values)
    values = (df.replace({np.nan: 'None'})
             .values.tolist()
             .__str__()
             .replace('[', '(')
             .replace(']', ')')
             [1:-1])
    return columns, values

def _find_missing_tickers(eod_data: pd.DataFrame, db_data: pd.DataFrame) -> pd.DataFrame:
    """Identify tickers present in EODHD but missing from database."""
    eod_codes = eod_data['Ticker_ID']
    db_codes = db_data['Ticker_ID']
    stacked_codes = pd.concat([eod_codes, db_codes], axis=0)
    missing_codes = stacked_codes.drop_duplicates(keep=False)
    return eod_data[eod_data['Ticker_ID'].isin(missing_codes)]

def tickers_update() -> None:
    """Update database with new tickers from EODHD."""
    try:
        # Initialize database table
        database_utils.execute_query(DB_CONFIG, CREATE_TABLE_QUERY)
        logger.debug("Ensured global_tickers table exists")

        # Get exchange list from database
        exchange_list = _get_exchange_list(DB_CONFIG)
        logger.debug(f"Retrieved {len(exchange_list)} exchanges from database")

        total_tickers = 0
        for exchange_code in exchange_list:
            try:
                # Get current database tickers
                db_tickers = _get_db_tickers(DB_CONFIG, exchange_code)
                logger.debug(f"Retrieved tickers for exchange {exchange_code}")

                # Get EODHD tickers
                eod_tickers = eodhd_utils.retrieve_tickers(
                    EODHD_CONFIG['api_key'], 
                    exchange_code
                )

                # Skip if no data retrieved
                if eod_tickers is None:
                    logger.warning(f"No ticker data for exchange {exchange_code}")
                    continue

                # Validate data structure
                if not np.array_equal(eod_tickers.columns.values, TICKER_COLUMNS):
                    logger.error(f"Column mismatch for exchange {exchange_code}")
                    continue

                # Find and add missing tickers
                missing_tickers = _find_missing_tickers(eod_tickers, db_tickers)
                
                if not missing_tickers.empty:
                    columns, values = _prepare_tickers_for_upload(missing_tickers)
                    query = f'INSERT INTO global_tickers ({columns}) VALUES {values};'
                    database_utils.execute_query(DB_CONFIG, query)
                    total_tickers += len(missing_tickers)
                    logger.debug(f"Added {len(missing_tickers)} tickers for {exchange_code}")

            except Exception as e:
                logger.error(f"Error processing exchange {exchange_code}: {str(e)}")
                continue

        if total_tickers > 0:
            logger.info(f"Added {total_tickers} new tickers to database")
        else:
            logger.info("No new tickers found")

    except Exception as e:
        logger.error("Failed to update tickers", exc_info=True)
        raise

if __name__ == "__main__":
    tickers_update()