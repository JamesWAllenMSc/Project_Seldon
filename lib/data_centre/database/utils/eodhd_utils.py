"""EODHD API Integration Module

This module provides utilities for interacting with the EODHD API,
handling data retrieval and transformation for exchanges, tickers, and price data.
"""

from typing import Optional, Dict, Any
import datetime
from dataclasses import dataclass

import pandas as pd
import requests

from lib.data_centre.database.config.database_logging_config import logger

# Constants
PRICE_COLUMNS = [
    'Ticker_ID', 'Date', 'Open', 'High', 'Low', 
    'Close', 'Adjusted_Close', 'Volume'
]

US_EXCHANGES = {
    'NYSE': {
        'Name': 'New York Stock Exchange',
        'OperatingMIC': 'XNYS',
        'Country': 'US',
        'Currency': 'USD',
        'CountryISO2': 'US',
        'CountryISO3': 'USA',
    },
    'NASDAQ': {
        'Name': 'NASDAQ',
        'OperatingMIC': 'XNAS',
        'Country': 'US',
        'Currency': 'USD',
        'CountryISO2': 'US',
        'CountryISO3': 'USA',
    }
}


@dataclass
class APIEndpoints:
    """EODHD API endpoint configurations."""
    BASE_URL = "https://eodhd.com/api"
    EXCHANGES = f"{BASE_URL}/exchanges-list"
    TICKERS = f"{BASE_URL}/exchange-symbol-list"
    HISTORICAL = f"{BASE_URL}/eod"
    DAILY = f"{BASE_URL}/eod-bulk-last-day"


def _make_api_request(url: str) -> Optional[Dict[str, Any]]:
    """Make API request with error handling."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}", exc_info=True)
        return None


def retrieve_tickers(api_key: str, exchange: str) -> Optional[pd.DataFrame]:
    """Retrieve ticker data for a specific exchange.
    
    Args:
        api_key: EODHD API key
        exchange: Exchange code
    
    Returns:
        DataFrame containing ticker data or None if request fails
    """
    url = f"{APIEndpoints.TICKERS}/{exchange}?api_token={api_key}&fmt=json"
    data = _make_api_request(url)
    if not data or not isinstance(data, list):
        return None
        
    try:
        df = pd.DataFrame(data)
        df['Source'] = f'EoDHD.com - Exchange {exchange}'
        df['Date_Updated'] = datetime.datetime.now()
        df['Ticker_ID'] = df['Code'] + f'_{exchange}'
        
        return df[['Ticker_ID', 'Code', 'Name', 'Country', 'Exchange',
                  'Currency', 'Type', 'Isin', 'Source', 'Date_Updated']]
    except Exception as e:
        logger.error(f"Failed to process ticker data for {exchange}: {e}")
        return None


def retrieve_exchanges(api_key: str) -> Optional[pd.DataFrame]:
    """Retrieve all available exchanges with US exchange handling.
    
    Args:
        api_key: EODHD API key
    
    Returns:
        DataFrame containing exchange data or None if request fails
    """
    url = f"{APIEndpoints.EXCHANGES}/?api_token={api_key}&fmt=json"
    data = _make_api_request(url)
    
    if not data:
        return None
        
    try:
        # Process EODHD exchanges
        df = pd.DataFrame(data)
        df['Source'] = 'EoDHD.com'
        df['Date_Updated'] = datetime.datetime.now()
        
        # Add US exchanges
        us_exchanges = pd.DataFrame([
            {**exchange_data, 'Code': code, 'Source': 'Manual_Input', 
             'Date_Updated': datetime.datetime.now()}
            for code, exchange_data in US_EXCHANGES.items()
        ])
        
        return pd.concat([df, us_exchanges], ignore_index=True)
    except Exception as e:
        logger.error(f"Failed to process exchange data: {e}", exc_info=True)
        return None


def retrieve_historical_price(exchange, ticker, date_to, eodhd_api):
    """ Takes api credentials for eodhd.com, a ticker and date range and returns a pandas dataframe containing 
    all historical prices for the target ticker
    """
    eod_ticker = f'{ticker}.{exchange}' # EoDHD.com ticker format
    url = f'https://eodhd.com/api/eod/{eod_ticker}?api_token={eodhd_api}&from={'1900-01-01'}&to={date_to}&fmt=json'
    try:
        price_data = requests.get(url).json()
        price_data = pd.DataFrame(price_data)
        if price_data.empty:
            logger.debug(f"No data returned for Ticker: {ticker} on Exchange: {exchange}")
            return None
        id = f'{eod_ticker}'.replace('.', '_')  # Replace '.' with '_' to create a valid Ticker_ID
        price_data['Ticker_ID'] = id
        price_data_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adjusted_Close',
                        'Volume', 'Ticker_ID'] 
        price_data.columns = price_data_columns[:len(price_data.columns)]
        price_data_columns_order = ['Ticker_ID', 'Date', 'Open', 'High', 'Low', 'Close', 'Adjusted_Close',
                        'Volume'] # Rearranging columns
        price_data = price_data[price_data_columns_order] # Specyfying column order to support db upload
        return price_data
    except Exception as e:
        logger.error(f'Updating historical price data -Ticker: {ticker} -  {e}')
