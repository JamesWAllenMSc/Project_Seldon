"""
Exchange Update Module

This module handles the synchronization of exchange data between EODHD API
and the local database. It checks for new exchanges and adds them to the database.
"""

# Standard library imports
from pathlib import Path
import sys
from typing import Dict, List

# Third-party imports
import numpy as np
import pandas as pd

# Local application imports
from lib.data_centre.database.config.database_config import PATHS
from lib.data_centre.database.config.eodhd_access_config import EODHD_CONFIG
from lib.data_centre.database.utils import eodhd_utils, database_utils
from lib.data_centre.database.config.database_logging_config import logger


# Constants
EXCLUDED_EXCHANGES = ['MONEY', 'BRVM']
TABLE_COLUMNS = [
    'Name', 'Code', 'OperatingMIC', 'Country',
    'Currency', 'CountryISO2', 'CountryISO3',
    'Source', 'Date_Updated'
]


# SQL Queries
CREATE_TABLE_QUERY = """
    CREATE TABLE IF NOT EXISTS global_exchanges (
        Name VARCHAR(255),
        Code VARCHAR(255),
        OperatingMIC VARCHAR(255),
        Country VARCHAR(255),
        Currency VARCHAR(255),
        CountryISO2 VARCHAR(255),
        CountryISO3 VARCHAR(255),
        Source VARCHAR(255),
        Date_Updated DATETIME,
        PRIMARY KEY (Code)
    );
"""


def _get_db_exchanges(db_config: Dict[str, str]) -> pd.DataFrame:
    """Retrieve current exchanges from database.
    
    Args:
        db_config: Database configuration dictionary
    
    Returns:
        DataFrame containing current exchange data
    """
    query = 'SELECT * FROM global_exchanges;'
    data = database_utils.retrieve_table(db_config, query)
    return pd.DataFrame(data, columns=TABLE_COLUMNS)


def _get_eodhd_exchanges(api_key: str) -> pd.DataFrame:
    """Retrieve and clean exchange data from EODHD.
    
    Args:
        api_key: EODHD API key
    
    Returns:
        DataFrame containing filtered EODHD exchange data
    """
    df = eodhd_utils.retrieve_exchanges(api_key)
    return df[~df['Code'].isin(EXCLUDED_EXCHANGES)]


def _validate_headers(eod_data: pd.DataFrame) -> bool:
    """Validate that EODHD data headers match expected columns.
    
    Args:
        eod_data: DataFrame from EODHD API
    
    Returns:
        True if headers match, False otherwise
    """
    return np.array_equal(eod_data.columns.values, TABLE_COLUMNS)


def _find_missing_exchanges(eod_data: pd.DataFrame, db_data: pd.DataFrame) -> pd.DataFrame:
    """Identify exchanges present in EODHD but missing from database.
    
    Args:
        eod_data: DataFrame from EODHD API
        db_data: DataFrame from database
    
    Returns:
        DataFrame containing missing exchanges
    """
    eod_codes = eod_data['Code']
    # eod_codes = pd.Series(['IR', 'LUSE', 'USA Stocks']) # TESTING ONLY REMOVE AT DEPLOYMENT
    db_codes = db_data['Code']
    stacked_codes = pd.concat([eod_codes, db_codes], axis=0)
    missing_codes = stacked_codes.drop_duplicates(keep=False)
    return eod_data[eod_data['Code'].isin(missing_codes)]


def _prepare_for_upload(df: pd.DataFrame) -> tuple[str, str]:
    """Format exchange data for SQL insert.
    
    Args:
        df: DataFrame to format
    
    Returns:
        Tuple of (column_string, values_string) for SQL INSERT
    """
    columns = ', '.join(df.columns.values)
    values = (df.replace({np.nan: 'None'})
             .values.tolist()
             .__str__()
             .replace('[', '(')
             .replace(']', ')')
             [1:-1])
    return columns, values

def exchanges_update(db_config: Dict[str, str]) -> None:
    """Update database with new exchanges from EODHD.
    
    This function compares the current database exchange list with EODHD's
    exchange list and adds any missing exchanges to the database.
    
    Args:
        db_config: Database configuration dictionary
        
    Raises:
        Exception: If any step of the update process fails
    """
    try:
        # Initialize database table if needed
        database_utils.execute_query(db_config, CREATE_TABLE_QUERY)
        logger.debug("Ensured global_exchanges table exists")
        
        # Get current database data
        db_exchanges = _get_db_exchanges(db_config)
        logger.debug("Retrieved current exchange data from database")
        
        # Get EODHD data
        eod_exchanges = _get_eodhd_exchanges(EODHD_CONFIG['api_key'])
        logger.debug("Retrieved and filtered EODHD exchange data")
        
        # Validate data structure
        if not _validate_headers(eod_exchanges):
            logger.error("EODHD exchange headers do not match expected format")
            raise ValueError("Exchange column headers mismatch")
        
        # Find missing exchanges
        missing_exchanges = _find_missing_exchanges(eod_exchanges, db_exchanges)
        
        # Update database if needed
        if not missing_exchanges.empty:
            columns, values = _prepare_for_upload(missing_exchanges)
            query = f'INSERT INTO global_exchanges ({columns}) VALUES {values};'
            database_utils.execute_query(db_config, query)
            logger.info(f"Added {len(missing_exchanges)} new exchanges to database")
        else:
            logger.info("No new exchanges to add")
            
    except Exception as e:
        logger.error("Failed to update exchanges", exc_info=True)
        raise


if __name__ == "__main__":
    # For testing/direct execution
    from config.database_access_config import DB_CONFIG
    exchanges_update(DB_CONFIG)